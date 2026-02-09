import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_025"
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
    "age": ["29", "34", "41", "45", "52", "58", "63", "67", "71", "75"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": [
        "Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", 
        "Dr. Miller", "Dr. Jones", "Dr. Patel", "Dr. Weiss"
    ],
    "target_lobe": [
        ("RML", "Right Middle Lobe"),
        ("RUL", "Right Upper Lobe"),
        ("RLL", "Right Lower Lobe"),
        ("LUL", "Left Upper Lobe"),
        ("LLL", "Left Lower Lobe"),
        ("Lingula", "Lingula")
    ],
    "sedation_fentanyl": ["25", "50", "75", "100"],
    "sedation_versed": ["1", "2", "3", "4"],
    "lidocaine_vol": ["5", "8", "10", "12"],
    "instilled_vol": [30, 40, 50, 60], # Int for calculation
    "sample_count": ["6", "8", "10", "11", "12", "14"],
    "time_out_verifier": ["assisting medical professional", "circulating nurse", "anesthesiologist", "support staff"],
    "anastomosis_desc": [
        "Normal anastomosis, no strictures, ischemia or black eschar",
        "Patent anastomosis, well-healed, no signs of dehiscence",
        "Widely patent anastomosis without stenosis or malacia",
        "Anastomosis appears healthy with normal vascularity"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors note_025.txt structure exactly
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} INDICATION FOR OPERATION Lung Transplant.

CONSENT Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient.
The patient read and signed the provided consent form. The consent was witnessed by an {verifier}.

PREOPERATIVE DIAGNOSIS

Lung Transplant surveillance

POSTOPERATIVE DIAGNOSIS

Lung Transplant with normal anastomosis

No evidence of rejection or infection on gross inspection

PROCEDURE

Flexible bronchoscopy

Bronchoalveolar Lavage (BAL)

Transbronchial Biopsy (TBBX)

ATTENDING {attending}

ANESTHESIA Moderate IV sedation with: Fentanyl {fent} mcg and Versed {versed} mg;
Local anesthesia with: Lidocaine 2% Solution ~{lido_vol}ml via atomizer. Sedation time was {sed_time} min during this procedure.

MONITORING Continuous telemetry, BP and oxygen saturation monitored.

INSTRUMENTATION Olympus Video Bronchoscope.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS None.

PROCEDURE IN DETAIL Immediately prior to procedure a "time out" was called to verify the correct patient, procedure, equipment, support staff and site/side marked as required.
After the patient was properly positioned and sedated and topical anesthesia applied, the bronchoscope was introduced through the mouth with O2 being administered at all times.
This was done without difficulty.

Airway Inspection The bronchoscope was passed by the carina, which was examined for sharpness, position and texture.
The bronchial orifices were systematically identified, evaluated and suctioned free of secretions and close attention was paid to color, texture, positions, size and patency.

Pharynx: Normal

Larynx: Normal

Vocal Cords: Normal

Trachea: Normal

Carina: Sharp

Right Lung: {anastomosis_status}.
Left Lung: {anastomosis_status}.

Mucosa: Normal.

Secretions: None.

No evidence of mass, lesions, bleeding or other intra-bronchial pathology was observed.

Bronchoalveolar Lavage (BAL) BAL was performed in the {lobe_short} with saline instilled and returned. Specimens were submitted.
Instilled {instilled} cc of NS, suction returned with {returned} cc.

Transbronchial Lung Biopsy Transbronchial forceps biopsies were performed with a total of {samples} samples collected. Specimens were submitted.
Performed at the {lobe_short}.

{samples} TBBX attempted and {samples} samples obtained.

SPECIMENS

BAL: {lobe_short} (microbiology and pathology)

Biopsies: {lobe_short} (pathology)

IMPRESSION / PLAN

Flexible bronchoscopy with BAL and TBBX under moderate sedation.
Samples sent for microbiology and pathology.

Post-Procedure: No dyspnea, chest pain or changes to voice.
Exam: CTA (Clear To Auscultation) over the area of the lavage and biopsy, no voice change or crepitus noted."""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Lung tx surveillance for {age}yo {gender_short}. Attending: {attending}. Sedation: Fent {fent}/Versed {versed}. Findings: Normal airway/anastomosis. Procedures: BAL and TBBX x{samples} in {lobe_short}. No comps.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long}. Indication is lung transplant surveillance. We used {fent} mcg Fentanyl and {versed} mg Versed. The airway was normal. We did a lavage and biopsy in the {lobe_long}. Total {samples} samples taken.",
    
    # Style 3: Sloppy / Quick
    "post lung tx bronch. {lobe_short} bal ({instilled}cc in/{returned}cc out) and bx ({samples} samples). pt {age} {gender_short}. {attending}. all normal, no rejection.",
    
    # Style 4: Billing Focus
    "Procedure: Bronchoscopy with BAL and Transbronchial Biopsy. Diagnosis: Lung Transplant Surveillance. Site: {lobe_long}. Samples: {samples}. Anesthesia: Moderate ({fent}mcg Fent/{versed}mg Versed). Provider: {attending}.",
    
    # Style 5: Structured
    "PATIENT: {age} {gender_short}\nINDICATION: Lung Tx Surveillance\nPROCEDURE: Bronchoscopy, BAL, TBBX\nLOCATION: {lobe_short}\nANASTOMOSIS: Normal\nSEDATION: Fentanyl {fent}, Versed {versed}"
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
        attending = random.choice(data_pool["attending"])
        
        # Logic: Select Lobe tuple (Short Name, Long Name) to ensure consistency across note
        lobe_data = random.choice(data_pool["target_lobe"])
        lobe_short = lobe_data[0]
        lobe_long = lobe_data[1]
        
        # Logic: Fluids (Returned must be less than Instilled)
        instilled = random.choice(data_pool["instilled_vol"])
        returned = instilled - random.randint(10, 20)
        
        # Other vars
        fent = random.choice(data_pool["sedation_fentanyl"])
        versed = random.choice(data_pool["sedation_versed"])
        samples = random.choice(data_pool["sample_count"])
        lido_vol = random.choice(data_pool["lidocaine_vol"])
        sed_time = random.randint(12, 25)
        verifier = random.choice(data_pool["time_out_verifier"])
        anastomosis_status = random.choice(data_pool["anastomosis_desc"])
        
        # Date generation
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
        date_str = date_obj.strftime("%B %d, %Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            attending=attending,
            fent=fent, 
            versed=versed,
            samples=samples,
            lobe_short=lobe_short,
            lobe_long=lobe_long,
            instilled=instilled,
            returned=returned
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            verifier=verifier,
            attending=attending,
            fent=fent,
            versed=versed,
            lido_vol=lido_vol,
            sed_time=sed_time,
            anastomosis_status=anastomosis_status,
            lobe_short=lobe_short,
            instilled=instilled,
            returned=returned,
            samples=samples
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