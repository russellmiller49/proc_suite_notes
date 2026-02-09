import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_003"
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
    "age": ["19", "23", "29", "34", "41", "52", "65", "71", "22", "38"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "indication_disease": [
        "synovial cell sarcoma",
        "adenocarcinoma of the lung",
        "squamous cell carcinoma",
        "metastatic melanoma",
        "chronic airway obstruction",
        "recurrent lung nodule"
    ],
    "med_versed": ["1 mg", "2 mg", "3 mg", "4 mg"],
    "med_fentanyl": ["50 mcg", "75 mcg", "100 mcg", "125 mcg"],
    "procedure_duration": [
        ("09:00", "09:08", "8"),
        ("09:59", "10:08", "9"),
        ("10:15", "10:27", "12"),
        ("11:30", "11:45", "15"),
        ("13:00", "13:10", "10"),
        ("14:20", "14:31", "11")
    ],
    "airway_findings": [
        "normal appearing to the segmental level bilaterally",
        "showed mild erythema but was otherwise normal",
        "contained thin white secretions which were suctioned",
        "showed trace erythema in the main carina",
        "was patent with normal mucosal architecture"
    ],
    "biopsy_site_status": [
        "appeared to have healed well",
        "showed excellent healing with no granulation",
        "was identified and appeared stable",
        "showed expected post-procedural changes but was healing well"
    ],
    "date_of_procedure": [
        "January 12, 2026", "February 28, 2026", "March 15, 2026", 
        "April 02, 2026", "May 20, 2026", "June 10, 2026"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# <--- CONVERT USER'S NOTE INTO f-string TEMPLATE HERE --->
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 


DATE OF PROCEDURE: {date_proc}


INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication} requiring airway inspection.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained. 


CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.


PREOPERATIVE DIAGNOSIS 

R91.8 Other nonspecific abnormal finding of lung field 


POSTOPERATIVE DIAGNOSIS 

R91.8 Other nonspecific abnormal finding of lung field 


PROCEDURE 

Diagnostic Bronchoscopy with bronchial washing (CPT 31622)

Moderate Sedation (CPT 99152)


ANESTHESIA  Moderate sedation.
Start Time: {start_time}

Stop Time: {stop_time}

Total Time: {total_time} minutes

Medications Administered: Versed {versed}; Fentanyl {fentanyl}.
MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION  Disposable Bronchoscope.


ESTIMATED BLOOD LOSS None 


COMPLICATIONS None 


PROCEDURE IN DETAIL After induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Sedation Assessment The patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
Airway Inspection and Findings Lidocaine was applied to the vocal cords and airway for topical anesthesia.
The mouth and oropharynx were normal appearing. The bronchoscope was advanced, and the airway anatomy was {airway_finding}.
The airway was inspected and mucus was suctioned.

Site Inspection The previous biopsy site was inspected and {site_status}.
Conclusion The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was transported to the recovery room in stable condition.
SPECIMENS 

None


IMPRESSION / PLAN 

{age}-year-old {gender_long} with {indication} presented for airway inspection.
Airway anatomy {airway_finding_short}; previous biopsy site {site_status_short}.

Follow up as needed."""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Write an IP op report for {age}yo {gender_short}, dx {indication}. Meds: Versed {versed}/Fent {fentanyl}. Procedure time {total_time} mins. Findings: {airway_finding_short}, site {site_status_short}.",
    
    # Style 2: Dictation Style
    "Generate a bronchoscopy report. Patient is a {age} year old {gender_long} with {indication} coming in for airway inspection. We used {versed} of Versed and {fentanyl} of Fentanyl. The airway was {airway_finding_short} and the old biopsy site {site_status_short}. No complications.",
    
    # Style 3: Sloppy / Quick Note
    "{age} {gender_short} {indication} airway check. CPT 31622. {versed} versed {fentanyl} fent. Time {start_time} to {stop_time}. Site looks good, airway normal.",
    
    # Style 4: Billing & Coding Focus
    "Procedure 31622, 99152. Diagnosis R91.8. Indication: {indication}. Patient: {age} {gender_short}. Anesthesia time {total_time} min ({start_time}-{stop_time}). Meds: Midazolam {versed}, Fentanyl {fentanyl}. Findings: {airway_finding_short}.",
    
    # Style 5: Structured Request
    "Create Note.\nPatient Age: {age}\nGender: {gender_long}\nIndication: {indication}\nSedation: Versed {versed}, Fentanyl {fentanyl}\nKey Findings: {airway_finding_short}, biopsy site {site_status_short}."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        indication = random.choice(data_pool["indication_disease"])
        
        versed = random.choice(data_pool["med_versed"])
        fentanyl = random.choice(data_pool["med_fentanyl"])
        
        # Time logic
        time_tup = random.choice(data_pool["procedure_duration"])
        start_time, stop_time, total_time = time_tup
        
        date_proc = random.choice(data_pool["date_of_procedure"])
        
        # Findings logic
        airway_full = random.choice(data_pool["airway_findings"])
        # Create a shorter version for the Impression/Prompt
        if "normal" in airway_full:
            airway_short = "normal"
        elif "erythema" in airway_full:
            airway_short = "mild erythema"
        else:
            airway_short = "patent with secretions"
            
        site_full = random.choice(data_pool["biopsy_site_status"])
        # Create shorter version
        site_short = "healed well" if "healed" in site_full else "stable"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            versed=versed,
            fentanyl=fentanyl,
            start_time=start_time,
            stop_time=stop_time,
            total_time=total_time,
            airway_finding_short=airway_short,
            site_status_short=site_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_proc=date_proc,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            start_time=start_time,
            stop_time=stop_time,
            total_time=total_time,
            versed=versed,
            fentanyl=fentanyl,
            airway_finding=airway_full,
            site_status=site_full,
            airway_finding_short=airway_short, # Used in Impression
            site_status_short=site_short       # Used in Impression
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