import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_062" 
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
    "age": ["45", "52", "58", "61", "64", "68", "72", "75", "79"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "indication": [
        "lung transplant and airway stenosis",
        "post-transplant anastomotic stricture",
        "airway compromise post-transplant",
        "chronic rejection and bronchial stenosis"
    ],
    "larynx_finding": [
        "Normal without mass/lesions",
        "Mild erythema noted",
        "Slight edema of vocal cords",
        "Normal vocal cord mobility"
    ],
    "trachea_finding": [
        "Normal",
        "Mild tracheomalacia noted",
        "Scattered secretions noted",
        "Slight narrowing distally"
    ],
    "right_lung_finding": [
        "Slight stenosis at anastomosis site without evidence of dehiscence",
        "Mild narrowing at the RMSB anastomosis",
        "Scar tissue formation at the right mainstem anastomosis",
        "Web-like stenosis at the right bronchial anastomosis"
    ],
    "left_lung_finding": [
        "Stent in place at LMSB with thick mucus throughout",
        "Existing stent in LMSB with significant biofilm",
        "LMSB stent in situ with mucostasis",
        "Stent observed in Left Mainstem with granulation tissue at edges"
    ],
    "migration_detail": [
        "evidence of distal stent migration and occlusion of the LUL",
        "distal migration blocking the LUL orifice",
        "migration distally causing partial obstruction of the LUL",
        "malpositioning distally obscuring the upper lobe bronchus"
    ],
    "secretions_desc": [
        "Copious thick and thin secretions",
        "Thick, tenacious mucus plugs",
        "Moderate purulent secretions",
        "Mucoid secretions"
    ],
    "bal_location": [
        "Anteromedial Segment of LLL (Lb7/8)",
        "Left Lower Lobe (Basal segments)",
        "Right Middle Lobe",
        "Right Lower Lobe (Posterior segment)"
    ],
    "bal_vols": [
        ("60 cc", "20 cc"),
        ("80 cc", "20 cc"),
        ("100 cc", "40 cc"),
        ("120 cc", "50 cc")
    ],
    "stent_device": [
        ("Bonastent", "12 x 50mm", "covered"),
        ("AERO stent", "14 x 40mm", "fully covered"),
        ("Ultraflex", "12 x 40mm", "covered"),
        ("Dumon silicone stent", "12 x 50mm", "silicone")
    ],
    "balloon_device": [
        ("10/11/12 Elation", "12 mm"),
        ("8/9/10 CRE", "10 mm"),
        ("12/13.5/15 CRE", "13.5 mm"),
        ("11/12/13 Elation", "12 mm")
    ],
    "dilation_duration": ["10 seconds", "30 seconds", "45 seconds", "60 seconds"],
    "medication_regimen": [
        "1) Albuterol nebs, 2) Hypertonic saline (3%) nebs, 3) Flutter valve",
        "1) Duoneb, 2) 7% Hypertonic Saline, 3) Acapella device",
        "1) Levalbuterol, 2) Pulmozyme, 3) Chest physiotherapy"
    ],
    "oral_med": [
        "Guaifenesin 1200mg PO BID",
        "Mucinex 600mg PO BID",
        "Acetylcysteine 600mg PO BID"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] 
INDICATION FOR OPERATION {patient_name_redacted} is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient. Consent was signed.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

Rigid Bronchoscopy (Conversion required for stent removal/replacement) 

Therapeutic aspiration subsequent episodes (31646) 

Bronchoscopy with BAL (31624) 

Balloon dilation (31630) 

Dilate and bronchial stent initial bronchus (31636) 

Foreign body removal (stent removal) (31635) 

MODIFIERS / COMPLEXITY

Modifier 22: Substantially greater work than normal (increased intensity, time, technical difficulty, and physical/mental effort).
Patient required conversion to rigid bronchoscopy for stent removal and re-placement.

This resulted in >50% increased work.
Increased complexity due to bilateral mainstem interventions: 31630 completed in the right mainstem bronchus and 31636 performed in the left main stem bronchus.
ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Rigid Bronchoscope, Flexible Therapeutic Bronchoscope, Disposable Bronchoscope.

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Supine 

Initial Airway Inspection The laryngeal mask airway was in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.


Larynx/Vocal Cords: {larynx_finding}.


Trachea: {trachea_finding}.
Mucus was noted within the trachea at the outset of the procedure.


Main Carina: Sharp.
Right Lung Proximal Airways: {right_lung_finding}.
Normal anatomic branching to segmental level with no evidence of mass, lesions, or bleeding.
Left Lung Proximal Airways: {left_lung_finding}.
Granulation noted at the distal stent with {migration_detail}.
Secretions: {secretions_desc} throughout with left greater than right.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus.
Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {bal_location}.
Instilled {bal_instilled} of NS, suction returned with {bal_returned} of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Rigid Bronchoscopy and Stent Removal Given evidence of distal migration of the stent and occlusion of the left upper lobe, the decision was made to remove the patient's stent and place a larger stent.
After induction of muscle relaxants, a tooth or gum protector was placed.
The black rigid barrel was introduced through the mouth and advanced in the midline while keeping alignment with the axis of the trachea.
The vocal cords were identified and the rigid bronchoscope was advanced carefully to the mid-trachea.
Jet ventilation was initiated and chest wall movement confirmed.

The rigid bronchoscope was placed in the left mainstem bronchus.
The patient's stent was grasped with single-action rigid forceps and removed from the patient's airway through the rigid bronchoscope (foreign body removal).
Stent Placement (Left Mainstem)

A {stent_brand}, {stent_size} ({stent_type}), was placed in the Left Mainstem.
Balloon dilation was performed at the Left Mainstem through the stent to fully expand and seat the stent.
A {balloon_name} balloon was used to perform dilation to {balloon_target_size}.
Total 3 inflations were performed with a dilation time of {dilation_duration} each.
Balloon Dilation (Right Mainstem)

Balloon dilation was performed at the Right Mainstem at the stenotic anastomosis site.
A {balloon_name} balloon was used to perform dilation to {balloon_target_size}.
Total 1 inflation was performed with a dilation time of {dilation_duration}.

The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{bal_location_short} BAL (cell count, micro, cyto) 

LMSB stent (pathology) 

IMPRESSION / PLAN {patient_name_redacted} is a {age}-year-old {gender_long} who presents for bronchoscopy for evaluation of airway stenosis and stent evaluation.
Patient underwent stent removal and re-placement without immediate complication.

Continue stent hydration regimen TID: {medication_regimen}.
{oral_med}.

Follow up BAL results.

Repeat bronchoscopy in 2-4 weeks for re-evaluation.
Follow-up in outpatient Interventional Pulmonology clinic as scheduled on [REDACTED].
"""

# 5 distinct prompt styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Pt {age} {gender_short} {indication}. IP proc: Rigid bronch, stent removal/replace LMSB ({stent_brand}), balloon dilation RMSB. BAL {bal_location_short}. Comps: None.",
    
    # Style 2: Dictation
    "Write an operative report for Dr. {doctor}. Patient is a {age} year old {gender_long} with {indication}. We performed rigid bronchoscopy with stent exchange in the left main due to migration blocking the LUL. Also dilated the right mainstem. Used a {stent_brand} {stent_size} and {balloon_name} balloon.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} lung tx pt with stenosis. Did rigid bronch. Removed old stent left side (migrated), put in new {stent_brand} {stent_size}. Dilated right side too. BAL {bal_location_short}. All good.",
    
    # Style 4: Billing Focus
    "Codes: 31636 (Left), 31630 (Right), 31635, 31624, 31646. Mod 22 used for rigid conversion. Dx: J98.09. Pt {age} {gender_short}. Findings: {migration_detail}. Device: {stent_brand} {stent_size}.",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nINDICATION: {indication}\nPROCEDURE: Rigid Bronchoscopy, Stent Exchange (Left), Balloon Dilation (Right), BAL.\nFINDINGS: {right_lung_finding}; {left_lung_finding}.\nDETAILS: Stent {stent_brand} {stent_size}; Balloon {balloon_name}."
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
        doctor = random.choice(data_pool["doctor"])
        indication = random.choice(data_pool["indication"])
        larynx_finding = random.choice(data_pool["larynx_finding"])
        trachea_finding = random.choice(data_pool["trachea_finding"])
        right_lung_finding = random.choice(data_pool["right_lung_finding"])
        left_lung_finding = random.choice(data_pool["left_lung_finding"])
        migration_detail = random.choice(data_pool["migration_detail"])
        secretions_desc = random.choice(data_pool["secretions_desc"])
        
        # BAL Logic
        bal_loc_full = random.choice(data_pool["bal_location"])
        bal_loc_short = bal_loc_full.split(" (")[0] if "(" in bal_loc_full else bal_loc_full
        bal_vols = random.choice(data_pool["bal_vols"])
        
        # Stent/Balloon Logic
        stent_info = random.choice(data_pool["stent_device"]) # (Brand, Size, Type)
        balloon_info = random.choice(data_pool["balloon_device"]) # (Name, Target Size)
        dilation_duration = random.choice(data_pool["dilation_duration"])
        
        med_regimen = random.choice(data_pool["medication_regimen"])
        oral_med = random.choice(data_pool["oral_med"])
        
        # B. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            indication=indication,
            stent_brand=stent_info[0],
            stent_size=stent_info[1],
            balloon_name=balloon_info[0].split(" ")[-1], # Just "Elation" or "CRE" usually, or full string
            bal_location_short=bal_loc_short,
            migration_detail=migration_detail,
            right_lung_finding=right_lung_finding,
            left_lung_finding=left_lung_finding
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_name_redacted="[REDACTED]",
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            larynx_finding=larynx_finding,
            trachea_finding=trachea_finding,
            right_lung_finding=right_lung_finding,
            left_lung_finding=left_lung_finding,
            migration_detail=migration_detail,
            secretions_desc=secretions_desc,
            bal_location=bal_loc_full,
            bal_instilled=bal_vols[0],
            bal_returned=bal_vols[1],
            stent_brand=stent_info[0],
            stent_size=stent_info[1],
            stent_type=stent_info[2],
            balloon_name=balloon_info[0],
            balloon_target_size=balloon_info[1],
            dilation_duration=dilation_duration,
            bal_location_short=bal_loc_short,
            medication_regimen=med_regimen,
            oral_med=oral_med
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