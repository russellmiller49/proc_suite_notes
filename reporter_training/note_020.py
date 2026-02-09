import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_020" 
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
    "age": ["34", "45", "52", "58", "59", "61", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "ref_doc": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel"],
    "attending": ["Dr. Henderson", "Dr. Wu", "Dr. Stevens", "Dr. Al-Fayed", "Dr. Ross"],
    "assistant": ["Dr. Jacobs", "Dr. Lee", "Dr. Martin", "PA Thompson"],
    "staff_rn": ["Sarah RN", "Mike RN", "Jessica RN", "David RN"],
    "staff_rt": ["Tom RT", "Linda RT", "Chris RT", "Amanda RT"],
    
    # Clinical Variations
    "indication": [
        "lung transplant and airway narrowing",
        "chronic rejection and mucous plugging",
        "shortness of breath and tracheal stenosis",
        "persistent cough and lung opacity",
        "surveillance post-lung transplant"
    ],
    "diagnosis_code": [
        "J98.09 Other diseases of bronchus, not elsewhere classified",
        "J95.811 Postprocedural pneumothorax",
        "Z94.2 Lung transplant status",
        "J44.9 Chronic obstructive pulmonary disease, unspecified"
    ],
    
    # Procedure Details
    "aspiration_locs": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Left Lower Lobe and Right Upper Lobe",
        "Bilateral lower lobes",
        "Trachea and Main Carina",
        "Right Middle Lobe and Lingula"
    ],
    "bal_loc": [
        "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)",
        "Superior Segment of LLL (LB6)",
        "Anterior Segment of RUL (RB3)",
        "Lingula (LB4/LB5)",
        "Posterior Basal Segment of RLL (RB10)"
    ],
    "bal_vols": [
        (60, 20), (100, 40), (120, 50), (50, 15), (80, 35)
    ],
    "biopsy_loc": [
        "Right Mainstem",
        "Anastomosis site",
        "Left Mainstem spur",
        "Bronchus Intermedius",
        "Right Upper Lobe orifice"
    ],
    "follow_up": [
        "4-6 weeks",
        "2-3 months",
        "3 months",
        "as needed",
        "6 weeks"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_doc}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained. 

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{diagnosis_code}

POSTOPERATIVE DIAGNOSIS

{diagnosis_code}

PROCEDURE

Therapeutic aspiration (initial episode)

Diagnostic bronchoscopy with Bronchoalveolar Lavage (BAL)

Endobronchial Biopsy(s)

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: {staff_rn} RT: {staff_rt}

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Disposable Bronchoscope

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {aspiration_locs} from mucus.
Bronchoalveolar Lavage (BAL) BAL was performed in the {bal_loc} with saline instilled and returned.
Specimens were submitted. Instilled {bal_in} cc of NS, suction returned with {bal_out} cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology. 

Endobronchial Biopsy Endobronchial biopsies were obtained with hemostasis achieved.
Tissue was submitted for pathology. No immediate bleeding was observed. Performed at {biopsy_loc}. Lesion was successfully removed.
Samples sent for Microbiology (Cultures/Viral/Fungal) and Pathology. 

The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

BAL ({bal_loc_short}) — Cell Count, Microbiology, Cytology

Endobronchial Biopsy ({biopsy_loc}) — Microbiology, Pathology

IMPRESSION / PLAN

{age}-year-old {gender_long} who presents for bronchoscopy for airway stenosis.
Follow-up BAL performed.

Airway noted to be in good condition.

Plan for repeat bronchoscopy in {follow_up}.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Bronch report. Pt {age} {gender_short}. Ref: {ref_doc}. Indication: {indication}. Asp: {aspiration_locs}. BAL: {bal_loc_short} ({bal_in}in/{bal_out}out). Bx: {biopsy_loc}. Plan: {follow_up}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age}-year-old {gender_long} referred by Dr. {ref_doc}. The patient has {indication}. We did a therapeutic aspiration of the {aspiration_locs}. We also did a BAL in the {bal_loc} and a biopsy of the {biopsy_loc}. Return interval is {follow_up}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. dx {diagnosis_code}. cleaned out {aspiration_locs}. bal done at {bal_loc_short}, {bal_in}cc in {bal_out}cc back. bx at {biopsy_loc}. dr {attending} attending.",
    
    # Style 4: Billing Focus
    "Procedure: Therapeutic Aspiration, BAL, Endobronchial Biopsy. Diagnosis: {diagnosis_code}. Patient: {age} {gender_short}. Locations: Asp ({aspiration_locs}), BAL ({bal_loc}), Bx ({biopsy_loc}). Fluid: {bal_in}/{bal_out}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nRef Doc: {ref_doc}\nIndication: {indication}\nProcedures:\n1. Aspiration ({aspiration_locs})\n2. BAL ({bal_loc}) - {bal_in}cc/{bal_out}cc\n3. Biopsy ({biopsy_loc})\nPlan: {follow_up}"
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
        
        ref_doc = random.choice(data_pool["ref_doc"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        staff_rn = random.choice(data_pool["staff_rn"])
        staff_rt = random.choice(data_pool["staff_rt"])
        
        indication = random.choice(data_pool["indication"])
        diagnosis_code = random.choice(data_pool["diagnosis_code"])
        
        aspiration_locs = random.choice(data_pool["aspiration_locs"])
        
        bal_loc = random.choice(data_pool["bal_loc"])
        # Create a short version of BAL loc for the specimen list/prompt
        bal_loc_short = bal_loc.split('(')[0].strip() if '(' in bal_loc else bal_loc
        
        bal_vol_tup = random.choice(data_pool["bal_vols"])
        bal_in = bal_vol_tup[0]
        bal_out = bal_vol_tup[1]
        
        biopsy_loc = random.choice(data_pool["biopsy_loc"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            ref_doc=ref_doc, attending=attending,
            indication=indication, diagnosis_code=diagnosis_code,
            aspiration_locs=aspiration_locs,
            bal_loc=bal_loc, bal_loc_short=bal_loc_short,
            bal_in=bal_in, bal_out=bal_out,
            biopsy_loc=biopsy_loc,
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_long,
            ref_doc=ref_doc, attending=attending,
            assistant=assistant, staff_rn=staff_rn, staff_rt=staff_rt,
            indication=indication, diagnosis_code=diagnosis_code,
            aspiration_locs=aspiration_locs,
            bal_loc=bal_loc, bal_loc_short=bal_loc_short,
            bal_in=bal_in, bal_out=bal_out,
            biopsy_loc=biopsy_loc,
            follow_up=follow_up
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