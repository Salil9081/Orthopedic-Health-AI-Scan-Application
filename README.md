# Orthopedic X-ray Detection System

An AI-powered system for detecting and analyzing orthopedic conditions from X-ray images using multiple YOLO models.

## Features

- Multi-model detection system for different body parts:
  - Knee
  - Spine
  - Heel
  - Wrist
- Automatic body part detection
- Multiple condition detection per body part
- PDF report generation
- Web interface for easy use

## Prerequisites

- Python 3.8+
- Flask
- OpenCV
- PyTorch
- Ultralytics YOLO
- FPDF

## Installation

```bash
pip install -r requirements.txt
```

## Model Files

Place the following model files in the `app/models` directory:
- knee.pt
- spine.pt
- heel.pt
- wrist.pt

## Supported Conditions

### Spine Conditions
- Surgical implant
- Spondylolisthesis
- Other lesion
- Osteophytes
- Foraminal stenosis
- Disc space narrowing
- Vertebral collapse
- Scoliosis

### Wrist Conditions
- Bone anomaly
- Fracture
- Metal implant
- Periosteal reaction
- Pronator sign
- Soft tissue changes

### Knee Conditions
- Osteoarthritis (doubtful)
- Osteoarthritis (mild)
- Osteoarthritis (moderate)
- Osteoporosis
- ACL injury

### Heel Conditions
- Heel spur
- Sever condition
- Fracture

## Usage

1. Start the server:
```bash
python run.py
```

2. Access the web interface at `http://localhost:5000`

3. Upload X-ray images:
   - System automatically detects body part
   - Processes image through appropriate model
   - Shows detection results with confidence scores

4. Generate reports:
   - Select images for report
   - Add patient information
   - Download PDF report

## Directory Structure

```
FlaskApplication/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── models/
│   │   ├── heel.pt
│   │   ├── knee.pt
│   │   ├── spine.pt
│   │   └── wrist.pt
│   ├── static/
│   │   └── images/
│   │       └── logo.png
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       ├── pdf_generator.py
│       └── yolo_utils.py
├── run.py
├── requirements.txt
└── README.md
```

## Configuration

Adjust the following in `app/config.py`:
- `pixel_spacing_cm`: Calibration for measurements
- `severity_thresholds`: Condition-specific thresholds
- `YOLO_MODELS`: Paths to model files

## License

MIT License

## Authors

SETV.G Team