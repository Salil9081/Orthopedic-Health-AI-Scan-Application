import cv2
import math
import tempfile
import os

pixel_spacing_cm = 0.05

severity_thresholds = {
    'spine': {
        'surgical_implant': 3.0,    # mm alignment deviation
        'spondylolisthesis': 4.0,   # mm slip
        'other_lesion': 5.0,        # mm size
        'osteophytes': 3.0,         # mm projection
        'foraminal_stenosis': 3.0,  # mm diameter
        'disc_space_narrowing': 3.0, # mm reduction
        'vertebral_collapse': 20.0,  # % height loss
        'scoliosis': 10.0           # degrees
    },
    'knee': {
        'knee osteoarthritis (moderate)': 3.0,  # mm joint space
        'knee osteoarthritis (mild)': 4.0,      # mm joint space
        'knee osteoarthritis (doubtful)': 5.0,  # mm joint space
        'osteoporosis': 3.0,                    # mm cortical thickness
        'acl': 2.0                              # mm displacement
    },
    'heel': {
        'heel spur': 5.0,    # mm length
        'sever': 3.0,        # mm irregularity
        'fractured': 2.0     # mm displacement
    },
    'wrist': {
        'boneanomaly': 3.0,         # mm irregularity
        'fracture': 2.0,            # mm displacement
        'metal': 2.0,               # mm misalignment
        'periostealreaction': 2.0,  # mm thickness
        'pronatorsign': 3.0,        # mm elevation
        'softtissue': 4.0           # mm swelling
    }
}

def custom_yolo_annotate(image_path, model, body_part):
    img = cv2.imread(image_path)
    if img is None:
        return "normal", None, 0.0, body_part
        
    results = model(image_path)[0]
    if len(results.boxes) > 0:
        best_box_idx = results.boxes.conf.argmax()
        box = results.boxes[best_box_idx]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        class_id = int(box.cls[0])
        predicted_class = model.names[class_id]
        
        # Add "knee osteoarthritis" prefix for specific knee conditions
        if body_part == 'knee' and predicted_class.lower() in ['doubtful', 'mild', 'moderate']:
            predicted_class = f"knee osteoarthritis ({predicted_class})"
        
        width = x2 - x1
        height = y2 - y1
        size_mm = math.sqrt(width**2 + height**2) * pixel_spacing_cm * 10
        
        # Get condition-specific threshold
        threshold = severity_thresholds.get(body_part, {}).get(predicted_class, 20.0)
        box_color = (0, 0, 255) if size_mm > threshold else (0, 255, 0)
        
        label = f"{body_part}-{predicted_class}\nSize: {size_mm:.1f}mm\nConf: {conf:.2f}"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        text_color = (255, 255, 255)
        
        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        
        rect_x1 = x1
        rect_y2 = y1 - 5
        rect_y1 = rect_y2 - (text_h + baseline + 10)
        rect_x2 = rect_x1 + text_w + 10
        
        if rect_y1 < 0:
            rect_y1 = y2 + 5
            rect_y2 = rect_y1 + (text_h + baseline + 10)
        
        cv2.rectangle(img, (rect_x1, rect_y1), (rect_x2, rect_y2), box_color, -1)
        cv2.putText(img, label, (rect_x1 + 5, rect_y2 - 5), font, font_scale, text_color, thickness)
        cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 2)
        
        return predicted_class.lower(), img, conf, body_part
    else:
        return "normal", img, 0.0, body_part



def save_annotated_image_cv2(annotated_img, output_path=None):
    if annotated_img is None:
        return None
        
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        output_path = temp_file.name
        temp_file.close()
    
    success = cv2.imwrite(output_path, annotated_img)
    if success:
        return output_path
    else:
        return None

def detect_body_part(image_path, models):
    """
    Run image through all models and return the body part with highest confidence detection.
    This function is designed to work with multiple models, each trained for a specific body part.
    It iterates through all the models and returns the result from the model with the highest confidence score.
    """
    best_confidence = 0
    best_result = None
    
    for body_part, model in models.items():
        try:
            label, annotated_img, conf, _ = custom_yolo_annotate(image_path, model, body_part)
            if conf > best_confidence:
                best_confidence = conf
                best_result = {
                    'body_part': body_part,
                    'label': label,
                    'annotated_img': annotated_img,
                    'confidence': conf
                }
        except Exception as e:
            print(f"Error processing {body_part} model: {str(e)}")
            continue
    
    if best_result:
        return (best_result['body_part'], best_result['label'], 
                best_result['annotated_img'], best_result['confidence'])
    return None, None, None, 0.0
