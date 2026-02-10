import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_046"
OUTPUT_DIR = "reporter_training"
NUM_SAMPLES = 100
TRAIN_RATIO = 0.8

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")

# ==========================================
# 2. DATA POOLS (Medical Variations)
# ==========================================
data_pool = {
    "age": [str(x) for x in range(35, 85)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "diagnosis_code": ["R91.1", "R91.8", "C34.90", "D02.20"],
    "diagnosis_text": ["Solitary Lung Nodule", "Multiple Lung Nodules", "Lung Mass", "Pulmonary Nodule", "Ground Glass Opacity"],
    
    "anesthesia_type": ["General Anesthesia", "MAC with local"],
    "blood_loss": ["Minimal", "Moderate", "Trace", "< 10 cc"],
    
    # Target 1 Variations (Location Name, Segment, Segment Code)
    "target1_data": [
        ("Left Upper Lobe (Lingula)", "Superior Segment of the Lingula", "LB4"),
        ("Left Upper Lobe", "Anterior Segment", "LB3"),
        ("Left Lower Lobe", "Superior Segment", "LB6"),
    ],
    
    # Target 2 Variations
    "target2_data": [
        ("Left Upper Lobe (Apical-Posterior)", "Apical-Posterior Segment of the LUL", "LB1/2"),
        ("Left Lower Lobe", "Posterior Basal Segment", "LB10"),
        ("Left Upper Lobe", "Apical Segment", "LB1"),
    ],
    
    # Target 3 Variations
    "target3_data": [
        ("Right Upper Lobe (Apical)", "Apical Segment of the RUL", "RB1"),
        ("Right Lower Lobe", "Superior Segment", "RB6"),
        ("Right Middle Lobe", "Lateral Segment", "RB4"),
    ],

    "nodule_size": ["0.4 cm", "0.6 cm", "0.8 cm", "1.0 cm", "1.2 cm", "1.5 cm", "2.1 cm"],
    
    "ebus_stations": [
        "11L, 4L, 7",
        "4R, 7, 10R",
        "11R, 4R, 7",
        "7, 4L, 10L"
    ],
    
    "rose_findings": [
        "Macrophages noted.",
        "Atypical cells present.",
        "Lymphocytes and macrophages.",
        "Malignant cells consistent with adenocarcinoma.",
        "Granulomatous inflammation."
    ],
    
    "fiducial_marker": [
        "0.8mm x 3mm soft tissue gold CIVCO",
        "0.9mm x 4mm coil",
        "SuperDimension fiducial",
        "Gold seed marker"
    ],
    
    "complications": [
        "None",
        "Minor airway bleeding controlled with cold saline",
        "Transient desaturation recovered quickly"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors the structure of note_046.txt
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {diagnosis_text_lower}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_text} 

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_text} 

PROCEDURE

Robotic Navigational Bronchoscopy (Ion) 

Radial EBUS (rEBUS) 

Cone Beam CT (Cios Spin) with 3D rendering 

Transbronchial Needle Aspiration (TBNA) 

Transbronchial Cryobiopsy 

Transbronchial Brushing 

Bronchoalveolar Lavage (BAL) 

Fiducial Marker Placement 

Endobronchial Ultrasound (EBUS) Staging 

Therapeutic Aspiration 

ANESTHESIA {anesthesia} 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope.

ESTIMATED BLOOD LOSS {blood_loss} 

COMPLICATIONS {complications} 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Airway Inspection Initial airway inspection revealed normal appearing airway anatomy and mucosa bilaterally to the segmental level.

Secretions were noted and suctioned. A CT Chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target, and the navigational plan was reviewed and verified.

Target 1: {t1_loc} Robotic navigation bronchoscopy was performed with the Ion platform using partial registration.

The Ion robotic catheter was used to engage the {t1_seg} ({t1_code}).

The target lesion measured approximately {t1_size} in diameter. Under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.

rEBUS: Radial EBUS was performed; the location of the nodule was {rebus_desc}.

Imaging: Cone Beam CT (Cios Spin) was performed with 3D reconstructions on an independent workstation for evaluation of nodule location.

The 3D images were interpreted, and the Ion robotic system was adjusted to the new targeted location based on the reconstruction.

Sampling:

TBNA: Transbronchial needle aspiration was performed with a 21G needle (4 samples collected).

Cryobiopsy: Transbronchial cryobiopsy was performed with a 1.1mm cryoprobe (6 second freeze time, 6 samples collected).

Brushing: Transbronchial brushing was performed with a protected cytology brush (1 sample collected).

BAL: Bronchoalveolar lavage was performed (20 cc instilled, 5 cc returned).

Fiducial: A fiducial marker ({fiducial}) was loaded with bone wax and placed under fluoroscopy guidance prior to withdrawal.

ROSE: {rose}.

Target 2: {t2_loc} Robotic navigation bronchoscopy was performed with the Ion platform using partial registration to engage the {t2_seg} ({t2_code}).

The target lesion measured approximately {t2_size}.

rEBUS: Radial EBUS confirmed the location of the nodule was eccentric, with a continuous margin and absence of linear-discrete air bronchogram.

Imaging: Cone Beam CT (Cios Spin) was performed, and 3D reconstructions were used to adjust the Ion robotic system to the targeted location.

Sampling:

TBNA: Transbronchial needle aspiration was performed with a 21G needle (4 samples collected).

Cryobiopsy: Transbronchial cryobiopsy was performed with a 1.1mm cryoprobe (6 second freeze time, 6 samples collected).

Brushing: Transbronchial brushing was performed with a protected cytology brush (1 sample collected).

BAL: Bronchoalveolar lavage was performed (20 cc instilled, 5 cc returned).

ROSE: {rose}.

Target 3: {t3_loc} Robotic navigation bronchoscopy was performed with the Ion platform using partial registration to engage the {t3_seg} ({t3_code}).

The target lesion measured approximately {t3_size}.

rEBUS: Radial EBUS confirmed the location of the nodule was eccentric, with a continuous margin and absence of linear-discrete air bronchogram.

Imaging: Cone Beam CT (Cios Spin) was performed with 3D reconstructions used to adjust the Ion robotic system to the targeted location.

Sampling:

TBNA: Transbronchial needle aspiration was performed with a 21G needle (4 samples collected).

Cryobiopsy: Transbronchial cryobiopsy was performed with a 1.1mm cryoprobe (6 second freeze time, 6 samples collected).

Brushing: Transbronchial brushing was performed with a protected cytology brush (1 sample collected).

BAL: Bronchoalveolar lavage was performed (20 cc instilled, 5 cc returned).

ROSE: {rose}.

Additional Bronchoalveolar Lavage

Left Upper Lobe: Performed at Apical-Posterior (LB1/2) and Anterior (LB3) segments. Instilled 60 cc, returned 25 cc.

Left Lower Lobe: Performed at Superior (LB6), Anteromedial (LB7/8), Lateral-basal (LB9), and Posterior-Basal (LB10) segments.

Instilled 40 cc, returned 15 cc.

Right Upper Lobe: Performed at Apical (RB1), Posterior (RB2), and Anterior (RB3) segments.

Instilled 60 cc, returned 20 cc.

EBUS Staging All lymph node stations were assessed, and those 5 mm or greater were sampled.

Endobronchial ultrasound elastography was performed to assess lymph node stiffness and guide sampling.

Stations Assessed: {ebus_stations}.

Therapeutic Aspiration & Conclusion Successful therapeutic aspiration was performed to clean out the Trachea (Middle/Distal), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina, RML Carina, LUL Lingula Carina, and Left Carina from mucus and blood.

The patient tolerated the procedure well with {complications_lower}.

The patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS

Target 1 ({t1_code}): TBNA, cryobiopsy, brushing, sub-segmental BAL, lobar BAL 

Target 2 ({t2_code}): TBNA, cryobiopsy, brushing, sub-segmental BAL, lobar BAL 

Target 3 ({t3_code}): TBNA, cryobiopsy, brushing, sub-segmental BAL, lobar BAL 

EBUS-TBNA: Stations {ebus_stations} 

IMPRESSION/PLAN

{age}-year-old {gender_long} who presents for bronchoscopy for {diagnosis_text_lower}.

Follow up CXR.

Follow up bronchoscopic lab work.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Patient: {age} {gender_short}. Indication: {diagnosis_text}. Procedure: Ion bronch + EBUS. Targets: {t1_code}, {t2_code}, {t3_code}. Sizes: {t1_size}, {t2_size}, {t3_size}. EBUS stations: {ebus_stations}. Complications: {complications}.",
    
    # Style 2: Dictation
    "Generate an operative report for a {age} year old {gender_long} presenting with {diagnosis_text}. We used robotic navigation for three targets. First was in the {t1_loc}, size {t1_size}. Second in {t2_loc}, size {t2_size}. Third in {t3_loc}, size {t3_size}. We also did EBUS on {ebus_stations}. ROSE showed {rose_short}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {diagnosis_code}. Ion bronch 3 targets: {t1_code} {t1_size}, {t2_code} {t2_size}, {t3_code} {t3_size}. EBUS {ebus_stations}. Fiducials placed. {complications}.",
    
    # Style 4: Structured Input
    "DEMOGRAPHICS: {age}/{gender_short}\nINDICATION: {diagnosis_text}\nPROCEDURE: Robotic Bronchoscopy & EBUS\nTARGETS:\n1. {t1_loc} ({t1_size})\n2. {t2_loc} ({t2_size})\n3. {t3_loc} ({t3_size})\nEBUS: {ebus_stations}",
    
    # Style 5: Billing Focus
    "Procedure: Robotic Navigational Bronchoscopy (Ion), EBUS, CBCT. Dx: {diagnosis_code}. Patient {age} {gender_short}. Targets sampled: {t1_seg}, {t2_seg}, {t3_seg}. EBUS nodes: {ebus_stations}. ROSE: {rose_short}."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        dx_code = random.choice(data_pool["diagnosis_code"])
        dx_text = random.choice(data_pool["diagnosis_text"])
        
        anesthesia = random.choice(data_pool["anesthesia_type"])
        blood_loss = random.choice(data_pool["blood_loss"])
        complications = random.choice(data_pool["complications"])
        
        # Targets
        t1 = random.choice(data_pool["target1_data"])
        t2 = random.choice(data_pool["target2_data"])
        t3 = random.choice(data_pool["target3_data"])
        
        t1_size = random.choice(data_pool["nodule_size"])
        t2_size = random.choice(data_pool["nodule_size"])
        t3_size = random.choice(data_pool["nodule_size"])
        
        ebus_stations = random.choice(data_pool["ebus_stations"])
        rose = random.choice(data_pool["rose_findings"])
        rose_short = rose.split(" ")[0] # Just the first word for brief prompts
        fiducial = random.choice(data_pool["fiducial_marker"])
        
        rebus_desc = random.choice(["not well visualized", "well visualized, eccentric", "concentric view obtained"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            diagnosis_text=dx_text, diagnosis_code=dx_code,
            t1_code=t1[2], t2_code=t2[2], t3_code=t3[2],
            t1_loc=t1[0], t2_loc=t2[0], t3_loc=t3[0],
            t1_seg=t1[1], t2_seg=t2[1], t3_seg=t3[1],
            t1_size=t1_size, t2_size=t2_size, t3_size=t3_size,
            ebus_stations=ebus_stations, complications=complications,
            rose_short=rose_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age, gender_long=gender_long,
            diagnosis_text_lower=dx_text.lower(), dx_text=dx_text, dx_code=dx_code,
            anesthesia=anesthesia, blood_loss=blood_loss, complications=complications,
            complications_lower=complications.lower(),
            # Target 1
            t1_loc=t1[0], t1_seg=t1[1], t1_code=t1[2], t1_size=t1_size,
            # Target 2
            t2_loc=t2[0], t2_seg=t2[1], t2_code=t2[2], t2_size=t2_size,
            # Target 3
            t3_loc=t3[0], t3_seg=t3[1], t3_code=t3[2], t3_size=t3_size,
            # Extras
            rebus_desc=rebus_desc, fiducial=fiducial, rose=rose,
            ebus_stations=ebus_stations
        )
        
        dataset.append({"prompt": prompt, "completion": completion})
    
    return dataset

# ==========================================
# 5. EXECUTION & SAVING
# ==========================================
if __name__ == "__main__":
    print(f"Generating data for {NOTE_ID}...")
    full_data = generate_dataset()
    
    # Shuffle
    random.shuffle(full_data)
    
    # Split
    split_index = int(NUM_SAMPLES * TRAIN_RATIO)
    train_data = full_data[:split_index]
    valid_data = full_data[split_index:]
    
    # Define File Paths
    train_filename = os.path.join(OUTPUT_DIR, f"{NOTE_ID}_train.jsonl")
    valid_filename = os.path.join(OUTPUT_DIR, f"{NOTE_ID}_valid.jsonl")
    
    # Save Training Data
    with open(train_filename, "w", encoding="utf-8") as f:
        for entry in train_data:
            f.write(json.dumps(entry) + "\n")
            
    # Save Validation Data
    with open(valid_filename, "w", encoding="utf-8") as f:
        for entry in valid_data:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Done!")
    print(f" - Saved to: {train_filename} ({len(train_data)} examples)")
    print(f" - Saved to: {valid_filename} ({len(valid_data)} examples)")