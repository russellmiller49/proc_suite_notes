import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_037"
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
    "age": ["65", "68", "71", "74", "76", "79", "82", "85"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Bowers", "Dr. Ingraham"],
    "dx_code": ["J98.09", "J95.5", "C34.90"],
    "dx_text": ["Other diseases of bronchus, not elsewhere classified", "Postprocedural subglottic stenosis", "Malignant neoplasm of unspecified part of bronchus or lung"],
    
    # Logic Bundles: To ensure the Location matches the Findings and the Healthy side remains healthy.
    "clinical_scenarios": [
        {
            "location": "distal trachea, right side",
            "findings_trachea": "Extrinsic compression from tumor at distal trachea, right side as well as some extruding tumor.",
            "findings_right_lung": "Obstructed airways at RUL and beyond the proximal bronchus intermedius secondary to extrinsic compression and tumor in-growth.",
            "findings_left_lung": "Normal anatomic branching to segmental level. No evidence of mass, lesions, bleeding or other endobronchial pathology.",
            "intervention_site": "Bronchus Intermedius",
            "stenosis_type": "extrinsic compression and tumor in-growth"
        },
        {
            "location": "distal trachea, left side",
            "findings_trachea": "Extrinsic compression from tumor at distal trachea, left side with significant luminal narrowing.",
            "findings_right_lung": "Normal anatomic branching to segmental level. No evidence of mass, lesions, bleeding or other endobronchial pathology.",
            "findings_left_lung": "Obstructed airways at LUL and beyond the proximal mainstem secondary to mixed tumor in-growth and compression.",
            "intervention_site": "Left Mainstem Bronchus",
            "stenosis_type": "tumor in-growth"
        },
        {
            "location": "proximal trachea",
            "findings_trachea": "Circumferential granulation tissue and web-like stenosis at the proximal trachea.",
            "findings_right_lung": "Normal anatomic branching. Secretions noted but cleared.",
            "findings_left_lung": "Normal anatomic branching. No endobronchial lesions.",
            "intervention_site": "Proximal Trachea",
            "stenosis_type": "complex granulation tissue"
        }
    ],

    "modalities": [
        "APC and Cryotherapy",
        "Laser excision and Balloon Dilation",
        "Electrocautery and Cryotherapy",
        "Mechanical debulking and APC"
    ],

    "patency_change": [
        ("5%", "15%"),
        ("10%", "40%"),
        ("0%", "25%"),
        ("20%", "60%")
    ],

    "hemostasis_drugs": [
        "epinephrine (total 1000mg) and tranexamic acid (total 1000mg)",
        "epinephrine (total 2ml 1:10000) and iced saline",
        "topical thrombin and cold saline lavage",
        "tranexamic acid (500mg) and oxymetazoline"
    ],
    
    "tube_size": ["7.5mm", "8.0mm", "8.5mm"],
    
    "dates": ["January 12", "February 28", "March 15", "April 10", "May 22", "June 05", "October 30"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} ATTENDING: {attending} INDICATION FOR OPERATION {last_name} is a {age}-year-old {gender_long} who presents with airway stenosis.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

PREOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

POSTOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

PROCEDURE
31645 Therapeutic aspiration initial episode
31640 Bronchoscopy with excision
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)

Procedure Note regarding Modifier 22: This patient required multiple modalities for debulking and to treat bronchial stenosis.
This resulted in >100% increased work due to Increased intensity, Time, Technical difficulty of procedure, and Physical and mental effort required.
Apply to: 31640 Bronchoscopy with excision and 31641 Destruction of tumor OR relief of stenosis by any method other than excision.

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS Moderate

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position: Supine

Initial Airway Inspection
LMA: The laryngeal mask airway is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.
Larynx: Normal.
Vocal Cords: Tissue/web at anterior commissure.
Trachea: {findings_trachea}
Main Carina: Sharp.

Right Lung Proximal Airways: {findings_right_lung}
Left Lung Proximal Airways: {findings_left_lung}

Mucosa: Erythematous and Friable.
Secretions: Minimal, thin, and clear mucus. Blood at the {intervention_site} and distal airways.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina from mucus.

Airway Management Bleeding/oozing was noted from the airways so decision was made to intubate patient with endotracheal tube.
Anesthesia placed {tube_size} ETT without issue.

Endobronchial Tumor Excision Endobronchial tumor was noted and excised with mechanical debridement using forceps.

Endobronchial Tumor Destruction Endobronchial obstruction was treated with {modalities}.
Performed at the {intervention_site} with the following modalities:
Mechanical: Forceps; Result: Tissue/tumor debulking.
Thermal/Cryo Modalities Used; Result: Tissue/tumor debulking and hemostasis.

Prior to treatment, affected airway was noted to be {patency_pre} patent.
After treatment, the airway was {patency_post} patent.

Hemostasis Hemostatic measures included: iced saline; {hemostasis_drugs} via bronchoscope.

Conclusion The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS None

IMPRESSION / PLAN
{last_name} is a {age}-year-old {gender_long} who presents for bronchoscopy for evaluation of airway stenosis.
Patient was noted to have {stenosis_type} at the {intervention_site}.
This was treated with multiple modalities including forceps and {modalities}.
At the conclusion of the case patent distal airways were identified.

Post procedure CXR.
Continued care per primary team.
If patient has scant hemoptysis, would treat with TXA 500mg NEB Q8h.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Pt {age} {gender_short}. Dx {dx_code}. Found {stenosis_type} at {intervention_site}. Used {modalities}. Patency improved {patency_pre} to {patency_post}. Mod 22 needed for complex debulking.",
    
    # Style 2: Dictation Start
    "Operative note for {age}yo {gender_long}. Pre-op dx {dx_text}. We performed therapeutic aspiration and excision. Findings: {findings_trachea} and {findings_right_lung}. Treated with {modalities}.",
    
    # Style 3: Billing/Coder Query
    "Please document IP bronchoscopy. Codes 31645, 31640, 31641 with modifier 22. Patient required switch from LMA to {tube_size} ETT due to bleeding. {intervention_site} opened from {patency_pre} to {patency_post}.",
    
    # Style 4: Sloppy / Quick Text
    "{age} {gender_short} airway stenosis case. {intervention_site} blocked by {stenosis_type}. Used forceps and {modalities}. Hard case, lots of work. Extubated stable.",
    
    # Style 5: Structured Request
    "Generate Op Report:\nPatient: {age} {gender_short}\nIndication: Airway Stenosis\nFindings: {findings_trachea}\nIntervention: {modalities} at {intervention_site}\nOutcome: {patency_post} patent"
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
        
        attending = random.choice(data_pool["attending"])
        date = random.choice(data_pool["dates"])
        last_name = "Patient" # Generic for HIPAA-safe synth data
        
        # Diagnosis
        dx_idx = random.randint(0, len(data_pool["dx_code"]) - 1)
        dx_code = data_pool["dx_code"][dx_idx]
        dx_text = data_pool["dx_text"][dx_idx]
        
        # Clinical Scenario (Ensures Logic Consistency)
        scenario = random.choice(data_pool["clinical_scenarios"])
        
        # Intervention Details
        modalities = random.choice(data_pool["modalities"])
        patency_tup = random.choice(data_pool["patency_change"])
        hemo_drugs = random.choice(data_pool["hemostasis_drugs"])
        tube_size = random.choice(data_pool["tube_size"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            dx_code=dx_code, 
            dx_text=dx_text,
            stenosis_type=scenario["stenosis_type"],
            intervention_site=scenario["intervention_site"],
            modalities=modalities,
            patency_pre=patency_tup[0],
            patency_post=patency_tup[1],
            findings_trachea=scenario["findings_trachea"],
            findings_right_lung=scenario["findings_right_lung"],
            tube_size=tube_size
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date=date,
            attending=attending,
            last_name=last_name,
            age=age,
            gender_long=gender_long,
            dx_code=dx_code,
            dx_text=dx_text,
            findings_trachea=scenario["findings_trachea"],
            findings_right_lung=scenario["findings_right_lung"],
            findings_left_lung=scenario["findings_left_lung"],
            intervention_site=scenario["intervention_site"],
            tube_size=tube_size,
            modalities=modalities,
            patency_pre=patency_tup[0],
            patency_post=patency_tup[1],
            hemostasis_drugs=hemo_drugs,
            stenosis_type=scenario["stenosis_type"]
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