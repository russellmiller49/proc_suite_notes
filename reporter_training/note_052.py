import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_052"
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
    "age": ["62", "65", "68", "71", "74", "79", "82", "85", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Vasquez", "Dr. Doe"],
    
    # Cleaning locations for therapeutic aspiration
    "mucus_locs": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Left Lower Lobe and Right Lower Lobe",
        "bilateral mainstems and distal airways",
        "Bronchus Intermedius and Right Lower Lobe"
    ],

    # Sets of 3 Lymph Node Stations to be sampled
    "station_sets": [
        ("11L", "4R", "11Rs"),
        ("7", "4R", "4L"),
        ("10R", "11R", "7"),
        ("4L", "2L", "11L"),
        ("2R", "4R", "10R")
    ],

    # CLINICAL SCENARIOS (Ensures logic connects Indication -> Findings -> Impression)
    "scenarios": [
        {
            "indication": "lymphadenopathy",
            "dx_code": "R59.0",
            "dx_text": "Localized enlarged lymph nodes",
            "elast_type": "Type 2",
            "elast_desc": "mixed soft and stiff regions",
            "rose_finding": "anthracotic pigments",
            "impression": "Suggestive of benign-appearing lymphoid tissue",
            "plan_note": "Preliminary cytology suggestive of anthracotic pigments"
        },
        {
            "indication": "mediastinal lymphadenopathy",
            "dx_code": "D86.0",
            "dx_text": "Sarcoidosis of lung",
            "elast_type": "Type 2",
            "elast_desc": "mixed patterns suggestive of inflammation",
            "rose_finding": "non-necrotizing granulomas",
            "impression": "Suggestive of granulomatous inflammation consistent with Sarcoidosis",
            "plan_note": "Preliminary cytology suggestive of granulomas"
        },
        {
            "indication": "lung mass with adenopathy",
            "dx_code": "C34.90",
            "dx_text": "Malignant neoplasm of unspecified part of bronchus or lung",
            "elast_type": "Type 3",
            "elast_desc": "predominantly stiff regions (blue mapping)",
            "rose_finding": "clusters of large atypical cells",
            "impression": "Positive for Malignancy",
            "plan_note": "Preliminary cytology positive for malignant cells"
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION
{patient_name} is a {age}-year-old {gender_long} who presents with {indication}. The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail. The patient indicated a wish to proceed with surgery and informed consent was signed.

PREOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

POSTOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

PROCEDURE
31645 Therapeutic aspiration initial episode
31653 EBUS sampling 3 or more nodes
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets (x2)

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; Linear EBUS.

ESTIMATED BLOOD LOSS
None

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection & Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out the {mucus_locs} from mucus.

EBUS Staging
Endobronchial ultrasound (EBUS) was performed. All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled. Lymph node sizing was performed by EBUS and sampling was performed using 25-gauge and 22-gauge needles.

Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. Elastography provided a semi-quantitative classification (Type 1–3), which was used to guide biopsy site selection and sampling strategy.

Lymph Nodes Evaluated:

Station {s1} (Site 1):
Appearance: The lymph node was $\ge$ 10 mm on CT and Hypermetabolic via PET-CT scan.
Elastography: The target lymph node demonstrated a {elast_type} elastographic pattern with {elast_desc}.
Sampling: Given this appearance, TBNA was directed at representative areas. The site was sampled with 4 endobronchial ultrasound-guided transbronchial biopsies.
ROSE: Preliminary ROSE Cytology was reported as adequate and suggestive of {rose_finding}.

Station {s2} (Site 2):
Appearance: The lymph node was $\ge$ 10 mm on CT and Hypermetabolic via PET-CT scan.
Elastography: The target lymph node demonstrated a {elast_type} elastographic pattern with {elast_desc}.
Sampling: Given this appearance, TBNA was directed at representative areas. The site was sampled with 4 endobronchial ultrasound-guided transbronchial biopsies.
ROSE: Preliminary ROSE Cytology was reported as adequate and suggestive of {rose_finding}.

Station {s3} (Site 3):
Appearance: The lymph node was $\ge$ 10 mm on CT and Hypermetabolic via PET-CT scan.
Elastography: The target lymph node demonstrated a {elast_type} elastographic pattern with {elast_desc}.
Sampling: Given this appearance, TBNA was directed at representative areas. The site was sampled with 4 endobronchial ultrasound-guided transbronchial biopsies.
ROSE: Preliminary ROSE Cytology was reported as adequate and suggestive of {rose_finding}.

Conclusion
The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
{s1} TBNA
{s2} TBNA
{s3} TBNA

IMPRESSION / PLAN
{age}-year-old {gender_long} who presents for bronchoscopy for {indication}.
Overall ROSE Diagnosis: {impression}.
Preliminary cytology for stations {s1}, {s2}, and {s3} {plan_note}; final results pending.
Follow-up final pathology.
Follow-up in clinic.
"""

# Prompt styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate EBUS report. {age}yo {gender_short}, {indication}. Stations {s1}, {s2}, {s3}. ROSE: {rose_finding}. Elastography {elast_type}. No complications.",
    
    # Style 2: Dictation
    "Please write a procedure note for Dr. {doctor}. Patient is a {age} year old {gender_long} presenting with {indication}. We performed EBUS TBNA on stations {s1}, {s2}, and {s3}. ROSE cytology showed {rose_finding}. Elastography was {elast_type}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} ebus for {indication}. sampled {s1} {s2} {s3}. found {rose_finding}, elastog type {elast_type_short}. pt stable.",
    
    # Style 4: Billing/Coding Focus
    "Op Report required. Codes 31645, 31653, 76982, 76983. Dx {dx_code}. Patient {age}/{gender_short}. Samples: {s1}, {s2}, {s3} showing {rose_finding}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedure: EBUS\nNodes: {s1}, {s2}, {s3}\nFindings: {elast_type}, {rose_finding}\nDoctor: {doctor}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select independent variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        doctor = random.choice(data_pool["doctor"])
        mucus_locs = random.choice(data_pool["mucus_locs"])
        
        # Select a set of 3 stations
        stations = random.choice(data_pool["station_sets"])
        s1, s2, s3 = stations[0], stations[1], stations[2]
        
        # B. Select a Coherent Clinical Scenario (Indication + Findings match)
        scenario = random.choice(data_pool["scenarios"])
        
        # C. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=scenario["indication"],
            s1=s1, s2=s2, s3=s3,
            rose_finding=scenario["rose_finding"],
            elast_type=scenario["elast_type"],
            elast_type_short=scenario["elast_type"][-1], # Gets "2" from "Type 2"
            dx_code=scenario["dx_code"]
        )
        
        # D. Generate Completion (Full Note)
        # Note: We simulate a redacted patient name or generic name
        patient_name = "[REDACTED]"
        
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_name=patient_name,
            age=age,
            gender_long=gender_tup[0],
            indication=scenario["indication"],
            dx_code=scenario["dx_code"],
            dx_text=scenario["dx_text"],
            mucus_locs=mucus_locs,
            s1=s1, s2=s2, s3=s3,
            elast_type=scenario["elast_type"],
            elast_desc=scenario["elast_desc"],
            rose_finding=scenario["rose_finding"],
            impression=scenario["impression"],
            plan_note=scenario["plan_note"]
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