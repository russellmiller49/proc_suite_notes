import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_022"
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
    "patient_name": ["James Smith", "Maria Garcia", "Robert Johnson", "Linda Martinez", "Michael Brown", "Sarah Wilson", "David Lee", "Jennifer Clark"],
    "age": ["34", "45", "52", "58", "62", "68", "71", "77"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Patel"],
    "attending": ["Dr. H. Reynolds", "Dr. S. Gupta", "Dr. L. Knope", "Dr. B. Wayne"],
    "assistant": ["Dr. T. Haverford", "Dr. A. Dwyer", "Dr. C. Traeger"],
    
    "indication": [
        "surveillance bronchoscopy", 
        "evaluation of new onset cough", 
        "evaluation of drop in FEV1", 
        "suspicion of acute rejection",
        "routine post-transplant monitoring"
    ],
    
    # Sedation variations
    "sedation_tuple": [
        ("Fentanyl 50 mcg and Versed 2.5 mg", "24"),
        ("Fentanyl 75 mcg and Versed 3 mg", "30"),
        ("Fentanyl 100 mcg and Versed 4 mg", "35"),
        ("Fentanyl 25 mcg and Versed 1 mg", "18")
    ],
    
    # Findings variations
    "anastomosis_status": [
        "Normal anastomoses bilaterally",
        "Mild granulation tissue at right anastomosis, normal left",
        "Slight telescoping of right anastomosis, patent left",
        "Widely patent anastomoses bilaterally"
    ],
    
    "distortion_status": [
        "Mild airway distortion bilaterally",
        "No airway distortion noted",
        "Moderate distortion in RLL bronchus",
        "Mild malacia noted in LMB"
    ],
    
    "secretions": [
        "Secretions were minimal; therapeutic aspiration was performed to clear.",
        "Moderate thick white secretions noted in RLL; cleared with suction.",
        "Trace clear secretions bilaterally.",
        "Thick mucus plugging in LLL, cleared with saline lavage."
    ],
    
    # BAL Locations and returns
    "bal_scenario": [
        {
            "loc": "RML and LLL", 
            "detail": "RML: 60 cc instilled, 20 cc returned.\nLLL: 60 cc instilled, 20 cc returned."
        },
        {
            "loc": "RUL and LUL", 
            "detail": "RUL: 50 cc instilled, 15 cc returned.\nLUL: 50 cc instilled, 18 cc returned."
        },
        {
            "loc": "RLL and Lingula", 
            "detail": "RLL: 100 cc instilled, 40 cc returned.\nLingula: 60 cc instilled, 25 cc returned."
        }
    ],
    
    # Biopsy variations
    "biopsy_target": [
        "RLL lateral basal segment",
        "LLL posterior basal segment",
        "RUL apical segment",
        "RML medial segment"
    ],
    
    "num_samples": ["6", "8", "10", "12"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION {patient_name} is a {age}-year-old {gender_long} with a history of lung transplant presenting for {indication}.
CONSENT Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient.
The patient read and signed the provided consent form. The consent was witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

Lung Transplant status

POSTOPERATIVE DIAGNOSIS

Lung Transplant status

{distortion_status}

{anastomosis_status}

PROCEDURE

Flexible bronchoscopy

Bronchoalveolar Lavage (BAL) of {bal_locs}

Transbronchial Biopsy (TBBX) of {biopsy_target} ({num_samples} samples)

Fluoroscopic guidance

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF

RN: [Name]

RT: [Name]

ANESTHESIA Moderate IV sedation with: {sedation_drugs}.
Local anesthesia with: Lidocaine 2% Solution ~20mL intratracheal. Sedation time: {sedation_time} minutes.
MONITORING Continuous telemetry, blood pressure, and oxygen saturation were monitored throughout the procedure.
INSTRUMENTATION Olympus Video Bronchoscope

ESTIMATED BLOOD LOSS 5 mL

COMPLICATIONS None

PROCEDURE IN DETAIL Immediately prior to the procedure a "time out" was called to verify the correct patient, procedure, equipment, support staff, and site/side marked as required.
After the patient was properly positioned and sedated and topical anesthesia applied, the bronchoscope was introduced through the mouth with O2 being administered at all times.
This was done without difficulty.

Airway Inspection The bronchoscope was passed by the carina, which was examined for sharpness, position, and texture.
The bronchial orifices were systematically identified, evaluated, and suctioned free of secretions.
Close attention was paid to color, texture, positions, size, and patency.

General Findings: {distortion_status}.
No evidence of mass, lesions, bleeding, or other intra-bronchial pathology. Mucosa was normal. {secretions}


Upper Airway: Pharynx, Larynx, Vocal Cords, and Trachea were all normal. Carina was sharp.
Right Lung: See diagnosis; no strictures, ischemia, or black eschar.

Left Lung: See diagnosis; no strictures, ischemia, or black eschar.
Bronchoalveolar Lavage (BAL) BAL was performed in the following segments with saline instilled and returned:

{bal_details} Specimens were sent for microbiology and pathology.
Transbronchial Biopsy (TBBX) Transbronchial forceps biopsies were performed under fluoroscopic guidance (Fluoro time: 28 seconds).

Target: {biopsy_target}.
Samples: {num_samples} attempts were made and {num_samples} samples were successfully obtained.
SPECIMENS

BAL {bal_locs} – Microbiology/Pathology

{biopsy_target} TBBX ({num_samples} samples) – Pathology

IMPRESSION / PLAN

Flexible bronchoscopy with BAL and TBBX performed under moderate sedation.
{anastomosis_status} with {distortion_status}; no signs of ischemia or stricture.
Post-procedure exam: CTA over the area of the lavage and biopsy. No voice change, crepitus, dyspnea, or chest pain noted.
Samples sent for microbiology and pathology.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Bronch report for {patient_name} ({age}{gender_short}). Indication: {indication}. Ref: {ref_physician}. Done under conscious sedation ({sedation_drugs}). Findings: {anastomosis_status}, {distortion_status}. BAL done in {bal_locs}, TBBX in {biopsy_target} x{num_samples}. No complications.",
    
    # Style 2: Dictation
    "Write an operative report for patient {patient_name}, age {age}. History of lung transplant, here for {indication}. Attending {attending}. We performed a flex bronch with BAL of the {bal_locs} and transbronchial biopsy of the {biopsy_target}. We took {num_samples} samples. Airways showed {distortion_status} and {anastomosis_status}.",
    
    # Style 3: Sloppy / Quick Note
    "Lung tx surveillance note. Pt {patient_name} {age}yo {gender_short}. {ref_physician} sent them. sedation {sedation_drugs}. airway looked ok, {distortion_status}. BAL {bal_locs}. Bx {biopsy_target}, {num_samples} pieces. all good.",
    
    # Style 4: Billing / Coding Focus
    "Procedure: Bronchoscopy with BAL and Transbronchial Biopsy. Indication: {indication}. Patient: {patient_name}, {age}/{gender_short}. Diagnosis: Lung Transplant Status. Findings: {anastomosis_status}, {distortion_status}. Procedures: BAL ({bal_locs}), TBBX {biopsy_target} ({num_samples} samples).",
    
    # Style 5: Structured Request
    "PATIENT: {patient_name}\nAGE/SEX: {age}/{gender_short}\nREFERRING: {ref_physician}\nPROCEDURE: Surveillance Bronch\nSEDATION: {sedation_drugs}\nFINDINGS: {anastomosis_status}, {distortion_status}\nSAMPLES: BAL ({bal_locs}), Biopsy {biopsy_target} ({num_samples} samples)"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        patient_name = random.choice(data_pool["patient_name"])
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        indication = random.choice(data_pool["indication"])
        
        # Complex objects
        sedation = random.choice(data_pool["sedation_tuple"]) # (Drugs, Time)
        bal_data = random.choice(data_pool["bal_scenario"])   # {loc, detail}
        
        anastomosis = random.choice(data_pool["anastomosis_status"])
        distortion = random.choice(data_pool["distortion_status"])
        secretions = random.choice(data_pool["secretions"])
        
        biopsy_target = random.choice(data_pool["biopsy_target"])
        num_samples = random.choice(data_pool["num_samples"])
        
        date_str = datetime.date.today().strftime("%Y-%m-%d")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            patient_name=patient_name,
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            indication=indication,
            sedation_drugs=sedation[0],
            anastomosis_status=anastomosis,
            distortion_status=distortion,
            bal_locs=bal_data["loc"],
            biopsy_target=biopsy_target,
            num_samples=num_samples
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            patient_name=patient_name,
            age=age,
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            assistant=assistant,
            indication=indication,
            sedation_drugs=sedation[0],
            sedation_time=sedation[1],
            anastomosis_status=anastomosis,
            distortion_status=distortion,
            secretions=secretions,
            bal_locs=bal_data["loc"],
            bal_details=bal_data["detail"],
            biopsy_target=biopsy_target,
            num_samples=num_samples
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