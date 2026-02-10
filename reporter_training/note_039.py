import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_039"
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
    "age": ["34", "41", "45", "52", "58", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "referring_doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones"],
    "attending_doctor": ["Dr. Anderson", "Dr. Patel", "Dr. Wilson", "Dr. Lee"],
    "rn_name": ["Sarah RN", "Mike RN", "Jessica RN", "David RN"],
    "rt_name": ["Tom RT", "Lisa RT", "Karen RT", "John RT"],
    
    # Clinical Variations
    "indication_diagnosis": [
        "endobronchial obstruction", "malignant airway stenosis", 
        "endobronchial tumor", "obstructing bronchogenic carcinoma"
    ],
    "icd_code": ["J98.09", "C34.90", "D14.31"],
    
    # Anatomy / Site Logic (Tuple: Site Name, Affected Side, Unaffected Side, Specific Stalk Loc)
    "site_config": [
        ("Right mainstem bronchus (RMSB)", "Right Lung", "Left Lung", "RUL carina (RC1)"),
        ("Left mainstem bronchus (LMSB)", "Left Lung", "Right Lung", "LUL carina (LC1)"),
        ("Bronchus Intermedius", "Right Lung", "Left Lung", "RML carina"),
    ],
    
    # Procedure Details
    "patency_pre": ["0%", "1%", "5%", "10%"],
    "patency_post": ["100%", "95%", "90%"],
    "bal_site": ["LUL Lingula", "RML", "RLL", "LLL", "RUL"],
    
    # Tools/Settings
    "snare_size": ["2 cm", "1.5 cm", "2.5 cm"],
    "apc_settings": ["Forced, Flow 0.5 LPM, 40W", "Forced, Flow 0.8 LPM, 30W", "Pulsed, Flow 1.0 LPM, 50W"],
    "microwave_settings": [
        "1 kJ at 62°C for 1 min 20 sec; 2.5 kJ at 80°C for 3 min",
        "1.5 kJ at 70°C for 2 min; 2.0 kJ at 90°C for 2 min",
        "1 kJ at 60°C for 1 min"
    ],
    "cryo_probe_size": ["2.4 mm", "1.9 mm"],
    "cryo_time": ["15-30 second", "30-60 second", "10-20 second"],
    
    "follow_up_time": ["4 weeks", "2 weeks", "6 weeks", "3 months"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring_doctor}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{icd_code} Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS

{icd_code} Other diseases of bronchus, not elsewhere classified

PROCEDURE

31640 Bronchoscopy with excision (Tumor debulking) [Modifier -22 applied]

31641 Destruction of tumor OR relief of stenosis by any method other than excision (Cryotherapy, APC, Microwave) [Modifier -22 applied]

31645 Therapeutic aspiration, initial episode

31624 Bronchoalveolar lavage (BAL)

31625 Endobronchial Biopsy(s)

MODIFIER -22 DETAILS (INCREASED PROCEDURAL SERVICES) This patient required tumor debulking and relief of endobronchial obstruction via multiple modalities (mechanical debridement, cryotherapy, APC, electrocautery, and microwave ablation).
This resulted in >100% increased work due to increased intensity, time, technical difficulty of the procedure, and physical/mental effort required.
ATTENDING {attending_doctor}

SUPPORT STAFF RN: {rn_name} RT: {rt_name}

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Rigid Bronchoscope; Flexible Therapeutic Bronchoscope; Electrocautery Snare; Cryoprobe; Mini Microwave Catheter; APC Probe.
ESTIMATED BLOOD LOSS Minimal

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Rigid Bronchoscopy and Airway Inspection After induction of muscle relaxants, a tooth/gum protector was placed.
A black rigid bronchoscope barrel was introduced through the mouth and advanced in the midline, maintaining alignment with the tracheal axis and minimizing dental pressure.
The vocal cords were identified, and the rigid scope was advanced carefully to the mid-trachea.
Jet ventilation was initiated, and chest wall movement was confirmed.

Initial Airway Inspection Findings

Vocal Cords: Normal without mass or lesions.
Trachea: Normal.

Main Carina: Sharp.

{affected_side}: {site_name} completely obstructed by endobronchial mass.
{unaffected_side}: Normal anatomic branching to segmental level. No evidence of mass, lesions, bleeding, or other endobronchial pathology.
Mucosa: Normal in non-affected areas.

Secretions: Moderate thick and thin light yellow mucus/secretions.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clear mucus from the airways.
{site_name} Endobronchial Tumor Destruction & Excision Endobronchial obstruction was treated with multiple modalities to achieve patency.
Electrocautery/Excision: An electrocautery snare ({snare_size}) was utilized to ensnare the endobronchial tumor and remove the bulk of the lesion from its stalk emanating from the {stalk_loc}.
Cryo-Extraction: Once removed from its stalk, a {cryo_size} cryoprobe was used to freeze and grasp the endobronchial mass, removing it en bloc with the flexible bronchoscope through the rigid barrel.
Microwave Ablation: A mini microwave catheter was used to treat the residual tumor.
Two applications were administered ({microwave_set}).
Argon Plasma Coagulation (APC): A 1.5 mm Straightfire probe was used ({apc_set}) for hemostasis and further destruction.
Treatment Summary

Electrocautery: {snare_size} Snare (EndoCut Q); 3-5 second applications. Result: Good tumor destruction/debulking.

APC: 1.5mm Straightfire probe (40W);
2-3 second applications. Result: Good tumor destruction/debulking.

Microwave: Mini antenna; 2 applications. Result: Good tumor destruction/debulking.

Cryoprobe: {cryo_size} probe;
{cryo_time} freezes. Result: Good tumor destruction/debulking.

Airway Patency Results

Pre-treatment: {site_name} airway was noted to be {patency_pre} patent.
Post-treatment: The airway was {patency_post} patent.

Bronchoalveolar Lavage (BAL) BAL was performed in the {bal_site}.
60 cc of normal saline was instilled, and 20 cc was returned.
Specimens were submitted for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Conclusion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{site_name} endobronchial tumor (Pathology)

{bal_site} BAL (Cell count, Cytology, Microbiology)

IMPRESSION / PLAN

{age}-year-old {gender_long} presenting for evaluation and management of {site_name} endobronchial tumor.
Tumor was successfully debulked using a combination of mechanical debridement, cryotherapy, APC, electrocautery, and microwave ablation.
Total patency was restored to the {site_name} at the conclusion of the procedure.
Await final pathology and BAL results.

Post-procedure Chest X-Ray.

Recommend treatment for post-obstructive pneumonia (PNA) if not already initiated.
Repeat bronchoscopy with Interventional Pulmonology in {follow_up}."""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Interventional Pulmonology note: {age}yo {gender_short}, ref {referring_doctor}. {site_name} obstruction ({patency_pre} patent). Procedures: Rigid bronch, snare ({snare_size}), cryo ({cryo_size}), microwave, APC. Outcome: {patency_post} patent. BAL {bal_site}. Plan: Repeat in {follow_up}.",
    
    # Style 2: Dictation
    "Please write an operative report for a {age} year old {gender_long} referred by {referring_doctor}. We performed a rigid bronchoscopy for {indication} in the {site_name}. We used multiple modalities including snare, cryo, microwave, and APC. The airway went from {patency_pre} to {patency_post} patent. Also did a BAL in the {bal_site}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} with {site_name} tumor. Ref {referring_doctor}. Did rigid bronch with debulking. Used everything: snare, cryo, apc, microwave. opened it up to {patency_post} (was {patency_pre}). BAL {bal_site}. Mod 22 applied.",
    
    # Style 4: Billing Focus
    "Code 31640-22, 31641-22, 31645, 31624. Dx {icd_code}. {age} {gender_short}. Complex debulking of {site_name} mass using snare, cryo, microwave, APC. Pre-op patency {patency_pre}, post-op {patency_post}. Attending {attending_doctor}.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nIndication: {indication} ({site_name})\nProcedure: Rigid Bronchoscopy, Tumor Debulking (Snare, Cryo, Micro, APC)\nFindings: Improved from {patency_pre} to {patency_post}\nBAL: {bal_site}\nStaff: {attending_doctor}"
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
        referring_doctor = random.choice(data_pool["referring_doctor"])
        attending_doctor = random.choice(data_pool["attending_doctor"])
        rn_name = random.choice(data_pool["rn_name"])
        rt_name = random.choice(data_pool["rt_name"])
        indication = random.choice(data_pool["indication_diagnosis"])
        icd_code = random.choice(data_pool["icd_code"])
        
        # Site Logic
        site_config = random.choice(data_pool["site_config"])
        site_name = site_config[0]
        affected_side = site_config[1]
        unaffected_side = site_config[2]
        stalk_loc = site_config[3]
        
        # Procedure Vars
        patency_pre = random.choice(data_pool["patency_pre"])
        patency_post = random.choice(data_pool["patency_post"])
        bal_site = random.choice(data_pool["bal_site"])
        snare_size = random.choice(data_pool["snare_size"])
        apc_set = random.choice(data_pool["apc_settings"])
        microwave_set = random.choice(data_pool["microwave_settings"])
        cryo_size = random.choice(data_pool["cryo_probe_size"])
        cryo_time = random.choice(data_pool["cryo_time"])
        follow_up = random.choice(data_pool["follow_up_time"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            referring_doctor=referring_doctor, attending_doctor=attending_doctor,
            site_name=site_name, patency_pre=patency_pre, patency_post=patency_post,
            indication=indication, icd_code=icd_code, bal_site=bal_site,
            snare_size=snare_size, cryo_size=cryo_size, follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            referring_doctor=referring_doctor,
            attending_doctor=attending_doctor,
            rn_name=rn_name, rt_name=rt_name,
            indication=indication, icd_code=icd_code,
            site_name=site_name, affected_side=affected_side, unaffected_side=unaffected_side,
            stalk_loc=stalk_loc,
            patency_pre=patency_pre, patency_post=patency_post,
            bal_site=bal_site,
            snare_size=snare_size,
            apc_set=apc_set,
            microwave_set=microwave_set,
            cryo_size=cryo_size, cryo_time=cryo_time,
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