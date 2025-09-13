import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO

from app.utils.pdf_generator import generate_pdf_report
from app.utils.yolo_utils import detect_body_part, save_annotated_image_cv2
from app.config import (
    LOGO_PATH, YOLO_MODELS, UPLOAD_FOLDER, PROCESSED_FOLDER, REPORTS_FOLDER,
    ALLOWED_IMAGE_EXTENSIONS, body_part_findings,
    findings_template, risks_template, tests_template
)

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, REPORTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

def allowed_file(filename, file_type='image'):
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.route('/')
def index():
    # Initialize session variables if they don't exist
    if 'patient_info' not in session:
        session['patient_info'] = {}
    if 'img_results' not in session:
        session['img_results'] = []
    
    return render_template('index.html', 
                         patient_info=session.get('patient_info', {}),
                         img_results=session.get('img_results', []),
                         video_results=session.get('video_results', []))

@app.route('/save_patient_info', methods=['POST'])
def save_patient_info():
    patient_info = {
        'Name': request.form.get('name', ''),
        'Age': request.form.get('age', ''),
        'Gender': request.form.get('gender', ''),
        'Patient_ID': request.form.get('patient_id', f"PT{uuid.uuid4().hex[:6].upper()}"),
        'Radiologist_Name': "",
        'Radiologist_ID': ""
    }
    
    session['patient_info'] = patient_info
    flash('Patient information saved successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'images' not in request.files:
        flash('No images selected', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('images')
    
    # Load all models once
    models = {}
    for body_part, model_path in YOLO_MODELS.items():
        if not os.path.exists(model_path):
            flash(f'YOLO model not found for {body_part}', 'error')
            continue
        models[body_part] = YOLO(model_path)
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename, 'image'):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Store only the filename relative to UPLOAD_FOLDER, using forward slashes
            relative_filepath = f'uploads/{unique_filename}'

            # Auto-detect body part
            body_part, label, img, conf = detect_body_part(filepath, models)
            if body_part:
                # Generate unique filename for annotated image
                unique_filename_annotated = f"annotated_{uuid.uuid4().hex}_{filename}"
                annotated_abs_path = os.path.join(app.config['PROCESSED_FOLDER'], unique_filename_annotated)
                
                # Save annotated image to the processed folder
                saved_annotated_path = save_annotated_image_cv2(img, annotated_abs_path)

                uploaded_files.append({
                    'path': relative_filepath,
                    'body_part': body_part,
                    'initial_detection': {
                        'label': label,
                        'confidence': conf,
                        'annotated_img_path': f'processed/{unique_filename_annotated}' if saved_annotated_path else None
                    }
                })
    
    if uploaded_files:
        session['uploaded_images'] = uploaded_files
        flash(f'Successfully uploaded and analyzed {len(uploaded_files)} images', 'success')

        try:
            img_results = []
            for i, image_info in enumerate(session['uploaded_images']):
                image_path = image_info['path']
                body_part = image_info['body_part']
                initial_detection = image_info['initial_detection']

                saved_path = initial_detection['annotated_img_path']

                if saved_path:
                    result = {
                        'id': i,
                        'original_path': image_path,
                        'annotated_path': saved_path,
                        'label': initial_detection['label'],
                        'body_part': body_part,
                        'confidence': initial_detection['confidence'],
                        'type': 'image',
                        'findings': findings_template.get(initial_detection['label'], 'No specific findings available'),
                        'tests': tests_template.get(initial_detection['label'], 'No specific tests available')
                    }
                    img_results.append(result)

            session['img_results'] = img_results
            flash(f'Successfully processed {len(img_results)} images!', 'success')

            # --- Automatic Report Generation ---
            if session.get('patient_info') and img_results:
                selected_images_info = []
                for result in img_results:
                    selected_images_info.append({
                        'original_path': result['original_path'],
                        'annotated_path': result['annotated_path'],
                        'label': result['label']
                    })

                report_filename = f"report_{uuid.uuid4().hex}.pdf"
                report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)

                generated_path = generate_pdf_report(session['patient_info'], selected_images_info, report_path)

                if generated_path:
                    session['last_report_filename'] = report_filename
                    flash(f'Report generated successfully! Download here: {url_for("download_report", filename=report_filename)}', 'success')
                else:
                    flash('Failed to automatically generate report.', 'error')
            # --- End Automatic Report Generation ---

        except Exception as e:
            flash(f'Error processing images: {str(e)}', 'error')

    else:
        flash('No valid images were uploaded', 'error')

    return redirect(url_for('index'))




@app.route('/get_selection_options')
def get_selection_options():
    options = []
    
    # Add image options
    for i, result in enumerate(session.get('img_results', [])):
        options.append({
            'id': f"img_{i}",
            'label': f"Image {i+1} ({result['label']})",
            'type': 'image',
            'index': i,
            'original_path': result['original_path'],
            'annotated_path': result['annotated_path']
        })
    
    return jsonify(options)

@app.route('/get_clinical_details/<selection_type>/<int:index>')
def get_clinical_details(selection_type, index):
    try:
        if selection_type == 'image':
            results = session.get('img_results', [])
        else:
            # If selection_type is not image, it's an invalid selection now
            return jsonify({'error': 'Invalid selection type'}), 400
        
        if index >= len(results):
            return jsonify({'error': 'Invalid selection'}), 400
            
        result = results[index]
        label = result['label']
        
        details = {
            'findings': findings_template.get(label, 'No specific findings available'),
            'risks': risks_template.get(label, 'No specific risks available'),
            'tests': tests_template.get(label, 'No specific tests available')
        }
        
        return jsonify(details)
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Invalid selection: {str(e)}'}), 400

@app.route('/generate_report', methods=['POST'])
def generate_report():
    if not session.get('patient_info'):
        return jsonify({'success': False, 'error': 'Please save patient information first'}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400
            
        selected_items = data.get('selected_items', [])
        
        if not selected_items:
            return jsonify({'success': False, 'error': 'No items selected for report'}), 400
        
        
        
        selected_images_info = []

        for item in selected_items:
            try:
                item_type, index = item.split('_', 1)
                index = int(index)
                
                if item_type == 'img':
                    results = session.get('img_results', [])
                else:
                    # If item_type is not img, it's an invalid selection now
                    return jsonify({'success': False, 'error': f'Invalid item type: {item}'}), 400
                
                if index >= len(results):
                    return jsonify({'success': False, 'error': f'Invalid item index: {item}'}), 400
                    
                result = results[index]
                
                selected_images_info.append({
                    'original_path': result['original_path'],
                    'annotated_path': result['annotated_path'],
                    'label': result['label']
                })
            except (ValueError, IndexError) as e:
                return jsonify({'success': False, 'error': f'Invalid item format: {item}'}), 400
        
        # Generate PDF report
        report_filename = f"report_{uuid.uuid4().hex}.pdf"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        generated_path = generate_pdf_report(session['patient_info'], selected_images_info, report_path)
        
        if generated_path:
            return jsonify({
                'success': True, 
                'report_url': url_for('download_report', filename=report_filename)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to generate PDF report'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    try:
        file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        if not os.path.exists(file_path):
            flash('Report not found', 'error')
            return redirect(url_for('index'))
            
        return send_file(
            file_path,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error downloading report: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/serve_image/<path:filename>')
def serve_image(filename):
    """Serve processed images"""
    try:
        # Handle different path formats
        if filename.startswith('uploads/'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace('uploads/', ''))
        elif filename.startswith('processed/'):
            file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.replace('processed/', ''))
        else:
            # Fallback for any other unexpected path format
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        
        if os.path.exists(file_path):
            print(f"Serving file: {file_path}")
            return send_file(file_path)
        else:
            return "Image not found", 404
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear all session data"""
    session.clear()
    flash('Session cleared successfully', 'success')
    return redirect(url_for('index'))

@app.route('/delete_file/<file_type>/<int:index>', methods=['POST'])
def delete_file(file_type, index):
    """Delete uploaded files and results"""
    try:
        if file_type == 'image':
            results = session.get('img_results', [])
            if index < len(results):
                result = results[index]
                # Delete files if they exist
                for path_key in ['original_path', 'annotated_path']:
                    if path_key in result:
                        relative_path = result[path_key]
                        if relative_path.startswith('uploads/'):
                            abs_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path.replace('uploads/', ''))
                        elif relative_path.startswith('processed/'):
                            abs_path = os.path.join(app.config['PROCESSED_FOLDER'], relative_path.replace('processed/', ''))
                        else:
                            abs_path = None # Should not happen with current logic

                        if abs_path and os.path.exists(abs_path):
                            os.remove(abs_path)
                # Remove from session
                results.pop(index)
                session['img_results'] = results
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 100MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
