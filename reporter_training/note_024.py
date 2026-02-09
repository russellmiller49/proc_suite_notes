import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_024"
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
    "patient_name": ["John Doe", "Jane Smith", "Robert Brown", "Emily Davis", "Michael Wilson", "Sarah Johnson"],
    "age": ["45", "52", "59", "63", "67", "71", "74", "38"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Smith", "Dr. Jones", "Dr. Patel", "Dr. Weiss", "Dr. Ingraham"],
    "attending": ["Dr. Anderson", "Dr. Lee", "Dr. Gupta", "Dr. Martinez"],
    "assistant": ["Dr. Resident", "Dr. Fellow", "PA Miller", "NP Davis"],
    "nurse": ["R. Nurse", "S. Johnson", "M. Williams"],
    "rt": ["T. Therapist", "B. RT", "L. Respiratory"],
    
    # Medication Dosing
    "fentanyl_dose": ["25", "50", "75", "100"],
    "versed_dose": ["1", "2", "3", "4"],
    "lidocaine_vol": ["6", "8", "10", "12"],
    "sedation_time": ["12", "15", "18", "20", "25"],
    
    # BAL Variables (Bronchoalveolar Lavage)
    "bal_1_loc": ["LLL", "LUL", "RML", "Lingula"],
    "bal_1_in": ["40", "50", "60"],
    "bal_1_out": ["15", "20", "25", "30"],
    
    "bal_2_loc": ["RLL", "RUL", "RML"],
    "bal_2_in": ["40", "50", "60"],
    "bal_2_out": ["15", "20", "25", "30"],
    
    # Biopsy Variables
    "bx_loc": ["RLL", "LLL", "RUL", "LUL"],
    "bx_count": ["6", "8", "10", "11", "12"],
    
    # Findings
    "airway_desc": ["Normal", "Mild erythema", "Trace secretions"],
    "anastomosis_status": [
        "Normal anastomoses bilaterally", 
        "Normal anastomoses with mild scar tissue", 
        "Patent anastomoses bilaterally"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION {patient_name} is a patient who presents for flexible bronchoscopy with BAL and TBBX for lung transplant surveillance.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient.

The patient read and signed the provided consent form, and the consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

Lung Transplant 

POSTOPERATIVE DIAGNOSIS

Lung Transplant surveillance 

{anastomosis_status}

No evidence of rejection or infection on gross inspection

PROCEDURE

Flexible Bronchoscopy 

Bronchoalveolar Lavage (BAL) x2 

Transbronchial Biopsy (TBBX) 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: {nurse} RT: {rt}

ANESTHESIA Moderate IV sedation with: fentanyl {fentanyl_dose} mcg and Versed {versed_dose} mg;

Local anesthesia with: Lidocaine 2% Solution ~{lidocaine_vol}ml via atomizer. Sedation time was {sedation_time} min.

MONITORING Continuous telemetry, blood pressure, and oxygen saturation were monitored throughout the procedure. 

INSTRUMENTATION Olympus Video Bronchoscope.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, equipment, support staff, and site/side marked as required.

Airway Inspection The bronchoscope was introduced through the mouth with O2 administered at all times.

The bronchoscope was passed by the carina, which was examined for sharpness, position, and texture.

Pharynx, Larynx, Vocal Cords, Trachea: {airway_desc}. 

Right Lung: Normal anastomosis; no strictures, ischemia, or black eschar observed.

Left Lung: Normal anastomosis; no strictures, ischemia, or black eschar observed.

Mucosa: Normal throughout.

Secretions: None.

Bronchoalveolar Lavage (BAL) BAL was performed with saline instilled and returned. Specimens were sent for analysis.

BAL 1 ({bal_1_loc}): Instilled {bal_1_in} cc of NS, suction returned with {bal_1_out} cc.

BAL 2 ({bal_2_loc}): Instilled {bal_2_in} cc of NS, suction returned with {bal_2_out} cc.

Samples sent for cytology (to check for recurrent CA), microbiology, and pathology.

Transbronchial Lung Biopsy Transbronchial forceps biopsies were performed.

{bx_loc}: {bx_count} biopsies were attempted and {bx_count} samples were obtained from the {bx_loc}. 

Hemostasis was achieved. EBL: None.

Post-Procedure The patient tolerated the procedure well.  Post-procedure exam demonstrated the patient was CTA (Clear to Auscultation) over the area of lavage and biopsy, with no voice change or crepitus noted.

No dyspnea or chest pain was reported.

SPECIMENS

BAL 1 ({bal_1_loc}) — Microbiology, Pathology, Cytology 

BAL 2 ({bal_2_loc}) — Microbiology, Pathology, Cytology 

{bx_loc} Transbronchial Biopsy ({bx_count} samples) — Pathology 

IMPRESSION / PLAN

Flexible bronchoscopy with BAL and TBBX performed under moderate sedation.

{anastomosis_status}; no strictures, ischemia, or black eschar.

Lavage from both sides included cytology to rule out recurrent CA.

Await final microbiology and pathology results.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Bronch surveillance on {age}yo {gender_short}. Ref {ref_physician}. BAL x2 ({bal_1_loc}, {bal_2_loc}) and TBBX {bx_loc} x{bx_count}. No complications. Anesthesia: Fent {fentanyl_dose}/Versed {versed_dose}.",
    
    # Style 2: Dictation / Narrative
    "Please generate a procedure note for {patient_name}, {age} years old. We performed a flexible bronchoscopy for lung transplant surveillance. Lavage done in {bal_1_loc} and {bal_2_loc}. We took {bx_count} biopsies from the {bx_loc}. Patient tolerated well.",
    
    # Style 3: Sloppy / Quick Note
    "lung txp surv note. {age} {gender_short}. attending {attending}. bal {bal_1_loc} ({bal_1_in}/{bal_1_out}) and {bal_2_loc}. bx {bx_loc} got {bx_count} samples. all good.",
    
    # Style 4: Billing Focused
    "Procedure: Bronchoscopy with BAL and Transbronchial Biopsy. Indication: Txp Surveillance. Sedation: {sedation_time} min. BAL Sites: {bal_1_loc}, {bal_2_loc}. Biopsy: {bx_loc} ({bx_count} samples). Provider: {attending}.",
    
    # Style 5: Structured Request
    "PATIENT: {patient_name}\nAGE: {age}\nPROCEDURE: Bronchoscopy/BAL/TBBX\nBAL LOCATIONS: {bal_1_loc}, {bal_2_loc}\nBIOPSY: {bx_loc} ({bx_count} samples)\nATTENDING: {attending}"
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
        nurse = random.choice(data_pool["nurse"])
        rt = random.choice(data_pool["rt"])
        
        fentanyl_dose = random.choice(data_pool["fentanyl_dose"])
        versed_dose = random.choice(data_pool["versed_dose"])
        lidocaine_vol = random.choice(data_pool["lidocaine_vol"])
        sedation_time = random.choice(data_pool["sedation_time"])
        
        # BAL Logic - ensure distinct locations if needed, though list separates them roughly by side/lobe
        bal_1_loc = random.choice(data_pool["bal_1_loc"])
        bal_1_in = random.choice(data_pool["bal_1_in"])
        bal_1_out = random.choice(data_pool["bal_1_out"])
        
        bal_2_loc = random.choice(data_pool["bal_2_loc"])
        bal_2_in = random.choice(data_pool["bal_2_in"])
        bal_2_out = random.choice(data_pool["bal_2_out"])
        
        bx_loc = random.choice(data_pool["bx_loc"])
        bx_count = random.choice(data_pool["bx_count"])
        
        airway_desc = random.choice(data_pool["airway_desc"])
        anastomosis_status = random.choice(data_pool["anastomosis_status"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            patient_name=patient_name,
            age=age,
            gender_short=gender_tup[1],
            ref_physician=ref_physician,
            attending=attending,
            bal_1_loc=bal_1_loc,
            bal_1_in=bal_1_in,
            bal_1_out=bal_1_out,
            bal_2_loc=bal_2_loc,
            bx_loc=bx_loc,
            bx_count=bx_count,
            fentanyl_dose=fentanyl_dose,
            versed_dose=versed_dose,
            sedation_time=sedation_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_name=patient_name,
            ref_physician=ref_physician,
            attending=attending,
            assistant=assistant,
            nurse=nurse,
            rt=rt,
            fentanyl_dose=fentanyl_dose,
            versed_dose=versed_dose,
            lidocaine_vol=lidocaine_vol,
            sedation_time=sedation_time,
            airway_desc=airway_desc,
            anastomosis_status=anastomosis_status,
            bal_1_loc=bal_1_loc,
            bal_1_in=bal_1_in,
            bal_1_out=bal_1_out,
            bal_2_loc=bal_2_loc,
            bal_2_in=bal_2_in,
            bal_2_out=bal_2_out,
            bx_loc=bx_loc,
            bx_count=bx_count
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