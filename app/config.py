import os

# --- Constants and Templates ---
LOGO_PATH = "app/logo.png"  

# Multiple YOLO model paths 
YOLO_MODELS = {
    'knee': "app/models/knee.pt",
    'spine': "app/models/spine.pt",
    'heel': "app/models/heel.pt",
    'wrist': "app/models/wrist.pt"
}

# Configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'app', 'processed')
REPORTS_FOLDER = os.path.join(BASE_DIR, 'app', 'reports')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}


body_part_findings = {
    'spine': {
        'surgical_implant': "- Surgical implant detected\n- Post-operative changes present\n- Hardware alignment assessed\n",
        'spondylolisthesis': "- Vertebral slippage identified\n- Grade assessment needed\n- Neural foraminal status noted\n",
        'other_lesion': "- Abnormal lesion detected\n- Further characterization needed\n- Location documented\n",
        'osteophytes': "- Osteophyte formation present\n- Affecting vertebral margins\n- Joint space impact noted\n",
        'foraminal_stenosis': "- Neural foraminal narrowing\n- Nerve root impingement risk\n- Level(s) documented\n",
        'disc_space_narrowing': "- Intervertebral disc space reduction\n- Degenerative changes noted\n- Level(s) affected\n",
        'vertebral_collapse': "- Vertebral body compression\n- Height loss measured\n- Alignment impact assessed\n",
        'scoliosis': "- Abnormal spinal curvature\n- Cobb angle measurement needed\n- Rotation component noted\n"
    },
    'wrist': {
        'boneanomaly': "- Bone abnormality detected\n- Location characterized\n- Joint impact assessed\n",
        'fracture': "- Wrist fracture identified\n- Fragment alignment noted\n- Joint involvement assessed\n",
        'metal': "- Orthopedic hardware present\n- Position evaluated\n- Surrounding bone status\n",
        'periostealreaction': "- Periosteal new bone formation\n- Pattern characterized\n- Underlying cause considered\n",
        'pronatorsign': "- Fat pad sign present\n- Associated findings noted\n- Clinical correlation needed\n",
        'softtissue': "- Soft tissue abnormality\n- Swelling/calcification noted\n- Adjacent structures assessed\n"
    },
    'knee': {
        'doubtful': "- Minor joint changes\n- Minimal space narrowing\n- Early osteophytes possible\n",
        'mild': "- Definite osteophytes\n- Possible joint space narrowing\n- Mild subchondral sclerosis\n",
        'moderate': "- Multiple osteophytes\n- Definite joint space narrowing\n- Moderate sclerosis\n",
        'osteoporosis': "- Decreased bone density\n- Trabecular pattern changes\n- Fracture risk assessment\n",
        'acl': "- ACL abnormality noted\n- Joint effusion status\n- Secondary signs assessed\n"
    },
    'heel': {
        'heel spur': "- Calcaneal spur identified\n- Size and location noted\n- Soft tissue impact assessed\n",
        'sever': "- Calcaneal apophysitis changes\n- Growth plate involvement\n- Soft tissue swelling status\n",
        'fractured': "- Calcaneal fracture detected\n- Bohler's angle affected\n- Joint involvement noted\n"
    }
}

findings_template = {
    # ---- Spine Conditions ----
    "surgical implant spine": "- Finding class is Surgical Implant (Spine)\n- Metallic fixation devices (screws, rods, cages) visible in spine.\n- No obvious loosening or migration on plain radiographs.\n",
    "spondylolisthesis": "- Finding class is Spondylolisthesis\n- Forward slippage of vertebra over the one below.\n- Most commonly at L4-L5 or L5-S1.\n",
    "other lesion spine": "- Finding class is Other Spinal Lesion\n- Abnormal vertebral/paraspinal lesion seen.\n- Could represent infection, tumor, or other pathology.\n",
    "Ostheophytes": "- Finding class is Ostheophytes\n- Bony outgrowths at vertebral margins.\n- Suggestive of spondylosis/degenerative changes.\n",
    "foraminal stenosis": "- Finding class is Foraminal Stenosis\n- Narrowing of intervertebral foramina.\n- Potential nerve root compression.\n",
    "disc space narrowing": "- Finding class is Disc Space Narrowing\n- Loss of intervertebral disc height.\n- Often associated with degeneration.\n",
    "Vertebral collapse": "- Finding class is Vertebral Collapse\n- Compression deformity of vertebral body.\n- May be due to osteoporosis, trauma, or malignancy.\n",
    "scoliosis": "- Finding class is Scoliosis\n- Abnormal lateral curvature of spine.\n- Cobb angle measurement recommended.\n",

    # ---- Wrist Conditions ----
    "boneanomaly": "- Finding class is Bone Anomaly (Wrist)\n- Irregular bone morphology or trabecular changes.\n",
    "fracture": "- Finding class is Wrist Fracture\n-  X-ray shows disruption of cortical continuity with possible displacement or angulation.\n",
    "metal": "- Finding class is Metal Implant (Wrist)\n- Presence of metallic implants, fixation devices, or foreign metallic bodies visible on imaging.\n",
    "periostealreaction": "- Finding class is Periosteal Reaction (Wrist)\n- New bone formation along periosteal surface.\n",
    "pronatorsign": "- Finding class is Pronator Sign\n- Suggests distal radius fracture with fat pad displacement.\n",
    "softtissue": "- Finding class is Soft Tissue Changes (Wrist)\n- Abnormal soft tissue swelling, edema, or density alterations adjacent to bone structures.\n",

    # ---- Knee Conditions ----
    "doubtful": "- Finding class is Osteoarthritis (Doubtful)\n- Minimal joint space narrowing, possible Ostheophytes.\n",
    "mild": "- Finding class is Osteoarthritis (Mild)\n- Small Ostheophytes, mild narrowing of joint space.\n",
    "moderate": "- Finding class is Osteoarthritis (Moderate)\n- Definite Ostheophytes, moderate joint space narrowing.\n",
    "osteoporosis": "- Finding class is Osteoporosis (Knee)\n- Reduced bone density with cortical thinning.\n",
    "acl": "- Finding class is ACL Injury\n- MRI usually confirms ligament tear or sprain.\n",

    # ---- Heel Conditions ----
    "heel spur": "- Finding class is Heel Spur\n- Bony outgrowth projecting from calcaneal tuberosity.\n",
    "sever": "- Finding class is Sever's Disease (Heel)\n-  X-ray may show irregularity or sclerosis at the calcaneal apophysis, consistent with traction-related changes.\n",
    "fractured": "- Finding class is Heel Fracture\n- Imaging reveals disruption in the calcaneal bone with possible comminution, displacement, or joint involvement.\n",
}

risks_template = {
    # ---- Spine ----
    "surgical implant spine": "- Hardware loosening/migration\n- Adjacent segment degeneration\n- Risk of infection around implant.\n",
    "spondylolisthesis": "- Progressive vertebral slippage\n- Spinal instability\n- Chronic pain, neurological deficits.\n",
    "other lesion spine": "- Pathological fracture\n- Spinal cord compression\n- Systemic spread (if malignant).\n",
    "Ostheophytes": "- Foraminal stenosis with radiculopathy\n- Spinal stiffness.\n",
    "foraminal stenosis": "- Chronic nerve root compression\n- Sensory and motor deficits.\n",
    "disc space narrowing": "- Chronic back pain\n- Increased degeneration.\n",
    "Vertebral collapse": "- Severe deformity\n- Cord compression.\n",
    "scoliosis": "- Progressive deformity\n- Pulmonary compromise (thoracic curves).\n",

    # ---- Wrist ----
    "boneanomaly": "- Pathological fractures\n- Chronic wrist pain.\n",
    "fracture": "- Malunion or nonunion\n- Arthritis risk.\n",
    "metal": "- Hardware failure\n- Infection around implant.\n",
    "periostealreaction": "- May indicate infection or tumor.\n",
    "pronatorsign": "- Suggests unstable distal radius fracture.\n",
    "softtissue": "- Hidden ligament/tendon injuries.\n",

    # ---- Knee ----
    "doubtful": "- Early degenerative changes.\n",
    "mild": "- Pain, stiffness with progression risk.\n",
    "moderate": "- Functional limitation, chronic pain.\n",
    "osteoporosis": "- Fragility fractures.\n",
    "acl": "- Instability, meniscal damage\n- Early osteoarthritis.\n",

    # ---- Heel ----
    "heel spur": "- Chronic heel pain\n- Altered gait.\n",
    "sever": "- Pain in children during growth.\n",
    "fractured": "- Deformity, subtalar arthritis.\n"
}

tests_template = {
    # ---- Spine ----
    "surgical implant spine": "- - CT scan (hardware integrity)\n- MRI (soft tissue evaluation)\n",
    "spondylolisthesis": "- - MRI (nerve compression)\n- CT scan (bony detail)\n",
    "other lesion spine": "- MRI (lesion characterization)\n- CT scan (bony involvement)\n- Biopsy (if suspicious)\n",
    "Ostheophytes": "- - CT scan (bone spurs)\n- MRI (nerve compression)\n",
    "foraminal stenosis": "- - CT myelogram\n- X-ray (dynamic views)\n",
    "disc space narrowing": "- - MRI (disc degeneration)\n- CT scan (bony changes)\n",
    "Vertebral collapse": "- - MRI (cord compression)\n- Bone density scan (DEXA)\n",
    "scoliosis": "- - MRI (cord anomalies)\n- Pulmonary function test\n",

    # ---- Wrist ----
    "boneanomaly": "- - MRI (soft tissue)\n- CT scan (bony anatomy)\n",
    "fracture": "- - CT scan (complex fractures)\n- MRI (ligament injury)\n",
    "metal": "- - CT scan (hardware assessment)\n- Blood tests (infection markers)\n",
    "periostealreaction": "- - MRI (infection/tumor)\n- Blood tests (ESR, CRP)\n",
    "pronatorsign": "- - CT scan (fracture detail)\n- MRI (ligament/tendon status)\n",
    "softtissue": "- MRI (ligaments, tendons)\n- Ultrasound (soft tissue)\n- X-ray (exclude fracture)\n",

    # ---- Knee ----
    "doubtful": "- \n- MRI (cartilage assessment)\n- Blood tests (rule out arthritis)\n",
    "mild": "-\n- MRI (cartilage/meniscus)\n- Ultrasound (effusion)\n",
    "moderate": "- \n- MRI (cartilage loss)\n- CT scan (alignment issues)\n",
    "osteoporosis": "- DEXA scan (bone density)\n- X-ray (fracture risk)\n- Blood tests (calcium, vitamin D)\n",
    "acl": "- MRI knee (gold standard)\n- X-ray (rule out fracture)\n- Lachman/clinical exam\n",

    # ---- Heel ----
    "heel spur": "-  Ultrasound (fascia assessment)\n- MRI (soft tissue detail)\n",
    "sever": "-- MRI (rule out other causes)\n- Clinical exam\n",
    "fractured": "-- CT scan (complex fractures)\n- MRI (soft tissue involvement)\n"
}