import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_002"
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
    "age": ["62", "65", "68", "71", "74", "77", "81", "85"],
    "gender_tuple": [("female", "F", "she", "her"), ("male", "M", "he", "his")],
    "doctor": ["Dr. Smith", "Dr. Patel", "Dr. Chen", "Dr. Rodriguez", "Dr. Weiss"],
    "patient_name_placeholder": ["The patient", "Mr. X", "Ms. Y"], 
    
    # Nodule 1 Variables (Apical)
    "n1_size": ["0.6 cm", "0.8 cm", "0.9 cm", "1.2 cm"],
    "n1_desc": ["peripheral subsolid nodule", "ground glass opacity", "solid nodule", "spiculated nodule"],
    "n1_rose": ["Atypical cells, few inflammatory cells", "Malignant cells consistent with adenocarcinoma", "Lymphocytes only", "Granulomatous inflammation"],
    
    # Nodule 2 Variables (Central)
    "n2_size": ["1.0 cm", "1.1 cm", "1.4 cm", "1.8 cm"],
    "n2_rose": ["Blood", "Necrotic debris", "Atypical cells", "Suspicious for malignancy"],
    
    # Nodule 3 Variables (Posterior)
    "n3_size": ["0.9 cm", "1.1 cm", "1.3 cm"],
    "n3_rose": ["Atypical cells - similar in morphology to site RUL #1", "Positive for malignancy", "Nondiagnostic", "Inflammatory cells"],
    
    # Lymph Node / EBUS Variables
    "ln_sample_stations": ["11L, 7, 11Rs, 11Ri", "7, 4R, 4L", "11L and 7 only", "10R and 11Rs"],
    "ln_elastography": ["Type 1 elastograpic pattern (soft)", "Type 2 elastographic pattern (mixed)", "Type 3 elastographic pattern (stiff)"],
    
    # Adrenal Variables
    "adrenal_size": [">10mm", "1.5 cm", "2.2 cm", "12mm"],
    "adrenal_rose": ["Lesional", "Adequate - cortical cells", "Metastatic Adenocarcinoma", "Benign adrenal tissue"],
    
    # Complications / Blood Loss
    "blood_loss": ["Minimal", "5 cc", "10 cc", "Negligible"],
    "complications": ["None", "Minor bleeding controlled with suction", "Desaturation requiring temporary increase in FiO2"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt 
INDICATION FOR OPERATION:  [REDACTED] is a {age} year old-year-old {gender_long} who presents with multiple lung nodule, borderline lymphadenopathy, and left adrenal mass.  The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient or surrogate in detail.  Patient or surrogate indicated a wish to proceed with surgery and informed consent was signed.
 
CONSENT: Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient or surrogate.
 
PREOPERATIVE DIAGNOSIS: R91.8 Other nonspecific abnormal finding of lung field.; lymphadenopathy; left adrenal mass
POSTOPERATIVE DIAGNOSIS:  R91.8 Other nonspecific abnormal finding of lung field.; lymphadenopathy; left adrenal mass
 
PROCEDURE:  
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)
31645 Therapeutic aspiration initial episode
31627 Navigational Bronchoscopy (computer assisted)
77012 Radiology / radiologic guidance for CT guided needle placement (CIOS)
31654 Radial EBUS for peripheral lesion
31653 EBUS sampling 3 or more nodes
43238 EGD and EUS guided biopsies
 
IP CODE MOD DETAILS: 
Unusual Procedure (22 MODIFIER):
This patient required the following at 3 different/discrete sites. This resulted in >150% increased work due to Increased intensity, Time, Technical difficulty of procedure, and Physical and mental effort required.
 
ANESTHESIA: General Anesthesia
 
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored.
 
INSTRUMENT(S): 
Flexible Therapeutic Bronchoscope
Linear EBUS 
Radial EBUS
Ion Robotic Bronchoscope
 
PROCEDURE IN DETAIL:
A timeout was performed. After the successful induction of anesthesia, anesthesia placed an ETT.
 
Initial Airway Examination Findings:
Trachea: Distal 1/3 normal.
Main Carina: Sharp
Right Lung Proximal Airways: Normal anatomic branching to the first subsegmental level.
Left Lung Proximal Airways:  Mildly tortuous LMSB. Evidence of LUL lobectomy - stump in excellent condition.
Mucosa: Normal.
Secretions: Moderate, thin, and clear.
 
The Flexible Therapeutic Bronchoscope was removed and the robotic-assisted navigational platform was set-up.
 
Right upper lobe apical segment nodule #1 (labeled as RUL #1):
Robotic navigation bronchoscopy was performed with Intuitive Ion platform. Target lesion is about {n1_size} in diameter.  
Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. Cios Spin system was used. Cone beam CT confirmed tool-in-lesion.
Transbronchial needle aspiration was performed. Samples sent for Cytology and Cultures. Radial EBUS showed Concentric pattern.
Transbronchial cryobiopsy was performed. 
ROSE from ION procedure was noted to be: {n1_rose}
Fiducial marker was placed.
Transbronchial brushing and Mini BAL performed.
 
Right upper lobe apical segment nodule #2 - more central (labeled as RUL #2):
Robotic navigation bronchoscopy was performed. Target lesion is about {n2_size} in diameter.  
Cone Beam CT confirmed tool-in-lesion.
Transbronchial needle aspiration was performed. Radial EBUS showed Eccentric pattern.
Transbronchial cryobiopsy was performed.
ROSE from ION procedure was noted to be: {n2_rose}
Fiducial marker was placed.
Transbronchial brushing and Mini BAL performed.
 
Right upper lobe posterior segment (RB2) subpleural nodule (labeled as RUL #3):
Robotic navigation bronchoscopy was performed. Target lesion is about {n3_size} in diameter.  
Cone Beam CT confirmed tool-in-lesion.
Transbronchial needle aspiration performed. Radial EBUS showed Concentric pattern.
Transbronchial cryobiopsy performed.
ROSE from ION procedure was noted to be: {n3_rose}.
Fiducial marker was placed.
Transbronchial brushing and Mini BAL performed.
 
The robotic catheter was withdrawn. Post-biopsy fluoroscopy images negative for pneumothorax.
 
EBUS-Findings
Indications: Diagnostic and Staging
Technique: All lymph node stations were assessed.
Lymph Nodes Sampled ({ln_sample_stations}):
Elastography: Endobronchial ultrasound (EBUS) elastography mode was performed. Analysis demonstrated a {ln_elastography}. 
Sampling: The sites were sampled. Endobronchial ultrasound guided transbronchial biopsies were performed.
 
EGD findings:
EGD was performed to assess for esophageal or gastric pathology. The esophagus was normal, GEJ normal, stomach was normal.
 
EUS-B Findings
EUS-B was performed to assess concerning left adrenal mass.
The left adrenal mass was assessed. It was {adrenal_size} in size, and was sampled.
Overall EUS-B transesophageal/transgastric ROSE Diagnosis: "{adrenal_rose}"
Evidence of small hematoma forming around the adrenal mass on EUS-B evaluation. Therefore, no further tissue obtained.
 
The patient tolerated the procedure well. There were {complications_lower}.
 
ESTIMATED BLOOD LOSS:   {blood_loss}
COMPLICATIONS:     {complications}
 
IMPRESSION/PLAN: [REDACTED] is a {age} year old-year-old {gender_long} who presents for bronchoscopy for biopsy of multiple lung nodules, lymph node assessment, and left adrenal mass assessment.
-Obtain post-procedure CXR (ordered)
-Follow-up in IP clinic to review results in 1-2 weeks."""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Generate op note: {age}{gender_short}, robotic bronch RUL x3 nodules ({n1_size}, {n2_size}, {n3_size}). EBUS staging ({ln_sample_stations}) and EUS-B left adrenal ({adrenal_size}). ROSE: {n1_rose_short}, {adrenal_rose}.",
    
    # Style 2: Dictation
    "Please write a procedure note for a {age}-year-old {gender_long}. We did a robotic bronchoscopy for three RUL nodules, EBUS for staging, and EUS-B for a left adrenal mass. Complications: {complications}. Findings included {n1_desc} and {n1_rose} on ROSE.",
    
    # Style 3: Sloppy / Quick Handover
    "{age}yo {gender_short} robotic ion case. RUL nodules x3, EBUS, EUS adrenal. ROSE showed {n1_rose_short} and {adrenal_rose}. {blood_loss} EBL.",
    
    # Style 4: Billing / Coding Focus
    "Codes 31627, 31654, 31653, 43238. {age} {gender_short}. 3 discrete sites in RUL sampled via robot. EBUS staging and EUS-B of {adrenal_size} adrenal mass. 22 modifier justified.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nProcedures: Robotic Bronchoscopy (Ion), EBUS, EUS-B\nTargets: RUL Nodules ({n1_size}, {n2_size}), Left Adrenal ({adrenal_size})\nROSE Findings: {n1_rose}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, he/she, his/her)
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        n1_size = random.choice(data_pool["n1_size"])
        n1_desc = random.choice(data_pool["n1_desc"])
        n1_rose = random.choice(data_pool["n1_rose"])
        n1_rose_short = n1_rose.split(',')[0] # Brief version for telegraphic prompts
        
        n2_size = random.choice(data_pool["n2_size"])
        n2_rose = random.choice(data_pool["n2_rose"])
        
        n3_size = random.choice(data_pool["n3_size"])
        n3_rose = random.choice(data_pool["n3_rose"])
        
        ln_sample_stations = random.choice(data_pool["ln_sample_stations"])
        ln_elastography = random.choice(data_pool["ln_elastography"])
        
        adrenal_size = random.choice(data_pool["adrenal_size"])
        adrenal_rose = random.choice(data_pool["adrenal_rose"])
        
        blood_loss = random.choice(data_pool["blood_loss"])
        complications = random.choice(data_pool["complications"])
        complications_lower = complications.lower() if complications != "None" else "no immediate complications"
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            n1_size=n1_size, n2_size=n2_size, n3_size=n3_size,
            n1_rose=n1_rose, n1_rose_short=n1_rose_short,
            n1_desc=n1_desc,
            ln_sample_stations=ln_sample_stations,
            adrenal_size=adrenal_size, adrenal_rose=adrenal_rose,
            blood_loss=blood_loss, complications=complications
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_long,
            n1_size=n1_size, n1_rose=n1_rose,
            n2_size=n2_size, n2_rose=n2_rose,
            n3_size=n3_size, n3_rose=n3_rose,
            ln_sample_stations=ln_sample_stations,
            ln_elastography=ln_elastography,
            adrenal_size=adrenal_size, adrenal_rose=adrenal_rose,
            blood_loss=blood_loss, complications=complications,
            complications_lower=complications_lower
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