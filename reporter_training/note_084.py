import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_084"
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
    "age": ["62", "65", "69", "71", "74", "76", "79", "82", "85"],
    "gender_tuple": [("female", "F", "She", "her"), ("male", "M", "He", "his")],
    "referring_physician": [
        "Dr. Ingraham", "Dr. Chen", "Dr. Rossi", "Dr. Smith", 
        "Dr. Patel", "Dr. Bowers", "Dr. Weiss"
    ],
    "attending_physician": [
        "Dr. Johnson", "Dr. Miller", "Dr. Davis", "Dr. Wilson", "Dr. Thompson"
    ],
    "indication": [
        "Interstitial Lung Disease (ILD)", 
        "Idiopathic Pulmonary Fibrosis (IPF)", 
        "Hypersensitivity Pneumonitis", 
        "Sarcoidosis", 
        "Organizing Pneumonia"
    ],
    "bal_location": [
        "Medial Segment of the RML (RB5)", 
        "Lateral Segment of the RML (RB4)", 
        "Lingula (LB4)", 
        "Anterior Segment of RUL (RB3)"
    ],
    "biopsy_location": [
        ("Lateral-basal Segment of the RLL (RB9)", "RLL lateral subsegment"),
        ("Posterior-basal Segment of the RLL (RB10)", "RLL posterior subsegment"),
        ("Posterior-basal Segment of the LLL (LB10)", "LLL posterior subsegment"),
        ("Lateral-basal Segment of the LLL (LB9)", "LLL lateral subsegment")
    ],
    "blocker_size": ["7", "9"],
    "ebl": ["40", "50", "60", "75", "100"],
    "bal_instilled": ["30", "40", "50", "60"],
    "bal_return": ["15", "20", "25", "30", "35"],
    "ett_depth": ["20", "21", "22", "23"],
    "blocker_depth": ["28", "29", "30", "31"],
    "procedure_date": [
        "January 12, 2024", "February 04, 2024", "March 15, 2024", 
        "April 22, 2024", "May 10, 2024"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors the structure of note_084.txt
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_md}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}. The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate. Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{indication}

POSTOPERATIVE DIAGNOSIS

{indication}

Bleeding requiring endobronchial blocker placement

PROCEDURE

Flexible Bronchoscopy

Bronchoalveolar Lavage (BAL)

Radial Endobronchial Ultrasound (rEBUS)

Transbronchial Forceps Biopsy (TBBX)

Transbronchial Cryobiopsy

Endobronchial Blocker Placement for Hemostasis

Therapeutic Aspiration

ATTENDING {attending}

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope, Radial EBUS, 1.7 mm cryoprobe, Arndt bronchial blocker.

ESTIMATED BLOOD LOSS {ebl} cc but continued bleeding

COMPLICATIONS Bleeding requiring endobronchial blocker and ICU admission.

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Patient Position: Supine.

Initial Airway Inspection The patient was sedated by anesthesia. The bronchoscope was used to fiberoptically intubate the patient with a size {blocker_size} Arndt blocker alongside the endotracheal tube (ETT). The vocal cords were normal in structure and function. Evaluation of the airway was performed; there were no endobronchial lesions and the mucosa was normal. The loop of the endobronchial blocker was moved to the {blocker_loc}.

Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {bal_site}. {bal_in} cc of Normal Saline was instilled, and suction returned {bal_out} cc. Samples were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Radial EBUS Survey Radial EBUS was performed to confirm there were no enlarged blood vessels in the segment of the {biopsy_site}.

Transbronchial Biopsies

Forceps Biopsy: Transbronchial biopsy was performed with alligator forceps at the {biopsy_site}. Total 1 sample was collected and sent for pathology. There was no bleeding after this biopsy.

Cryobiopsy: Transbronchial biopsy was performed with a 1.7 mm cryoprobe with a 4-second freeze. The scope and the cryoprobe were removed together from the {biopsy_site}. Total 1 sample was collected and sent for pathology.

Hemostasis and Complication Management Immediately after removal of the bronchoscope following the cryobiopsy, significant bleeding occurred. The balloon on the blocker was inflated with 3 cc. The balloon was left inflated for a total of 2 minutes, but at the time of deflation, there was continued bleeding.

Intervention: A total of 1000 mg of Tranexamic Acid (TXA), 2 mg epinephrine, and 5 cc iced saline were given through the end of the inflated blocker.

Isolation: Additional isolation time was performed in intervals of 5 minutes, followed by 10 minutes, followed by another 10 minutes. Total time with blocker inflation was 24 minutes.

Conclusion The ETT is at {ett_cm} cm at the front teeth and the blocker is at {blocker_cm} cm at the front teeth. The patient tolerated the procedure well despite the bleeding event. At the conclusion of the operation, due to continued bleeding, the patient was transferred to the ICU for continued care.

SPECIMENS

BAL {bal_short}

TBBX {biopsy_short}

Cryo-TBBX {biopsy_short}

IMPRESSION / PLAN

{age}-year-old {gender_long} with {indication_short} underwent bronchoscopy for diagnosis. Transbronchial cryobiopsy of the {biopsy_short} resulted in bleeding requiring endobronchial blocker placement and pharmacologic hemostasis.

Transfer to ICU. Plan for repeat bronchoscopy in ICU if indicated.
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate Op Report. {age}{gender_short}, ILD workup. BAL {bal_short}, Cryo {biopsy_short}. Complication: Major bleed req Arndt blocker, TXA, Epi. Admit ICU. Attending {attending}.",
    
    # Style 2: Narrative / Dictation
    "Write a bronchoscopy note for a {age} year old {gender_long} referred by {ref_md}. Indication is {indication}. We did a BAL in the {bal_short} and cryobiopsy in the {biopsy_site}. Significant bleeding occurred post-cryo. We had to use a size {blocker_size} Arndt blocker, instilled TXA and Epi. Patient transferred to ICU intubated.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} {indication_short} bronch. {attending}. EBL {ebl}. Bleeding complication after RLL cryo. Blocker used + meds. ICU transfer. BAL done {bal_short}.",
    
    # Style 4: Structured / Form-fill
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nProcedure: Flex Bronch, EBUS, Cryo ({biopsy_short}), BAL ({bal_short})\nComplication: Hemorrhage. Required Arndt blocker, TXA, Epi, Iced saline. \nDisposition: ICU.",
    
    # Style 5: Medical Context / Resident Handover
    "Op Note Request: Interventional Pulm case. {age}y {gender_short} with {indication}. Standard airway inspection normal. BAL {bal_site}. EBUS cleared {biopsy_short} for biopsy. Forceps clear, but Cryo caused bleed. Managed with blocker inflation (24 mins total) + hemostatic cocktail. ETT {ett_cm}cm, Blocker {blocker_cm}cm. ICU for obs."
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
        
        ref_md = random.choice(data_pool["referring_physician"])
        attending = random.choice(data_pool["attending_physician"])
        indication = random.choice(data_pool["indication"])
        
        # Shorten indication for "Impression" and "Telegraphic prompts"
        indication_short = "ILD" if "ILD" in indication else "IPF" if "IPF" in indication else "Sarcoidosis"
        
        bal_site = random.choice(data_pool["bal_location"])
        # Create a short version of BAL site (e.g., "RML" from "Medial Segment of the RML")
        bal_short = "RML" if "RML" in bal_site else "LUL" if "Lingula" in bal_site else "RUL"
        
        # Tuple extraction for biopsy (Full Name, Blocker Location Description)
        biopsy_tup = random.choice(data_pool["biopsy_location"])
        biopsy_site = biopsy_tup[0]
        blocker_loc = biopsy_tup[1]
        
        # Short version for biopsy (e.g., "RLL" or "LLL")
        biopsy_short = "RLL" if "RLL" in biopsy_site else "LLL"
        
        blocker_size = random.choice(data_pool["blocker_size"])
        ebl = random.choice(data_pool["ebl"])
        bal_in = random.choice(data_pool["bal_instilled"])
        bal_out = random.choice(data_pool["bal_return"])
        ett_cm = random.choice(data_pool["ett_depth"])
        blocker_cm = random.choice(data_pool["blocker_depth"])
        date = random.choice(data_pool["procedure_date"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            indication=indication, indication_short=indication_short,
            bal_short=bal_short, bal_site=bal_site,
            biopsy_short=biopsy_short, biopsy_site=biopsy_site,
            attending=attending, ref_md=ref_md,
            blocker_size=blocker_size, ebl=ebl,
            ett_cm=ett_cm, blocker_cm=blocker_cm
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date=date,
            ref_md=ref_md,
            age=age,
            gender_long=gender_long,
            indication=indication,
            indication_short=indication_short,
            attending=attending,
            ebl=ebl,
            blocker_size=blocker_size,
            blocker_loc=blocker_loc,
            bal_site=bal_site,
            bal_in=bal_in,
            bal_out=bal_out,
            biopsy_site=biopsy_site,
            ett_cm=ett_cm,
            blocker_cm=blocker_cm,
            bal_short=bal_short,
            biopsy_short=biopsy_short
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