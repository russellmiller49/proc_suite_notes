import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_093"
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
    "age": ["45", "52", "57", "61", "68", "74", "79", "83"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "referring_doc": ["Dr. Smith", "Dr. Chen", "Dr. Bowers", "Dr. Miller", "Dr. Al-Fayed", "Dr. Jensen"],
    "attending_doc": ["Dr. Ingraham", "Dr. Stevens", "Dr. Patel", "Dr. O'Malley"],
    
    # Procedure specific variations
    "diagnosis_code": ["J98.09", "J98.8", "J95.850"],
    "target_lobe": [
        {"full": "Right Middle Lobe", "abbr": "RML", "seg1": "Lateral (RB4)", "seg2": "Medial (RB5)", "carina": "RML Carina (RC2)"},
        {"full": "Right Middle Lobe", "abbr": "RML", "seg1": "Lateral (RB4)", "seg2": "Medial (RB5)", "carina": "RML Carina (RC2)"}, # Weighted heavily for RML as segments match source
    ],
    "old_stent_size": ["7mm x 16mm", "6mm x 16mm", "8mm x 16mm"],
    "new_stent_size": ["7mm x 16mm", "7mm x 22mm", "6mm x 16mm"],
    "failed_trial_stent": ["7mm x 22mm", "8mm x 22mm", "7mm x 19mm"],
    "secretion_type": ["Frank pus", "Purulent secretions", "Thick mucopurulent material", "Inspissated mucus"],
    "antibiotic": ["Augmentin (875mg-125mg)", "Levofloxacin 500mg", "Doxycycline 100mg", "Amoxicillin 500mg"],
    "follow_up_time": ["2 weeks", "3 weeks", "4 weeks", "1 month"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring_doc}

INDICATION FOR OPERATION {gender_pronoun} is a {age}-year-old {gender_long} who presents with airway stenosis.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

{diagnosis_code} Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

{diagnosis_code} Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 
31624 Dx bronchoscope/lavage (BAL) 
31625 Endobronchial Biopsy(s) 
31629 TBNA single lobe 
31652 EBUS sampling 1 or 2 nodes 
31630 Balloon dilation 
31636 Dilate and bronchial stent initial bronchus 
31640 Bronchoscopy with excision 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 
31635 Foreign body removal 

Modifier 22: Substantially greater work than normal (increased intensity, time, technical difficulty, and severity of patient's condition).
This patient required multiple modalities and increased effort (>100% increased work) to access and open the {lobe_abbr}.
ATTENDING {attending_doc}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope; Linear EBUS.
ESTIMATED BLOOD LOSS Moderate 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Initial Airway Inspection

Laryngeal Mask Airway: Good position.
Pharynx/Larynx: Not fully assessed due to LMA introduction.
Vocal Cords: Normal without mass/lesions.
Trachea: Distal 1/3 normal.
Main Carina: Sharp.
Right Lung Proximal Airways: The {lobe_abbr} orifice was unable to be identified on initial inspection;
the airway had swallowed the prior {lobe_abbr} stent and was fused shut. No evidence of mass, lesions, or bleeding elsewhere.
Left Lung Proximal Airways: Normal anatomic branching to segmental level. No mass, lesions, or bleeding.
Therapeutic Aspiration: Successful aspiration was performed to clear mucus from the Trachea, Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina, LUL Lingula Carina, and Left Carina.
{lobe_abbr} Recanalization and Stent Removal The {lobe_abbr} was initially unidentifiable, with suspicion that the stent had migrated distally with tissue overgrowth.
Localization: The EBUS scope was utilized to identify the {lobe_abbr} orifice and distal stent.
Access: Transbronchial needle aspiration (TBNA) was utilized to re-create/re-open the {lobe_abbr} orifice.
{secretion_type} was aspirated from the {lobe_abbr} during this maneuver.
Dissection: Following the creation of a pinhole opening via TBNA, pulmonary forceps were used to probe and blunt dissect to widen the opening.
Biopsy/Excision: Endobronchial biopsy was performed at the {lobe_abbr}, and the lesion/tissue was successfully removed.
Dilation: A 4Fr Fogarty balloon was inserted to further open the {lobe_abbr}. Purulent secretions distal to the obstruction were aspirated.
Distal Inspection & Lavage: The hybrid scope was used to explore the distal {lobe_abbr}, successfully identifying the medial and lateral subsegments.
BAL was performed at the {seg1} and {seg2} segments.

Instilled 40 cc NS; returned 25 cc.
Balloon Dilation: Performed at {carina} using a 6/7/8 Elation balloon dilated to 8 mm (3 inflations, 60 seconds each).
Stent Removal: After excision and dilation, the {lobe_abbr} was patent and the foreign body/old stent (iCAST {old_stent}) was visualized.
It was grasped with rat tooth forceps and removed en bloc.
Hemostasis Bleeding/oozing noted from the {lobe_abbr} was treated with multiple modalities including cold saline, TXA, epinephrine, and electrocautery/coagulation.
Electrocautery: Probe used on forced coag mode (2-5 sec duration) for ablation/coagulation.
New Stent Placement To prevent recurrence of the stent being swallowed, a longer stent was initially selected.
Trial 1: iCAST {failed_stent} deployed; blocked off the RLL and was subsequently removed en bloc.
Trial 2: iCAST {new_stent} placed; noted to be too proximal and subsequently removed en bloc.
Final Placement: iCAST {new_stent} stent was placed in the {lobe_abbr} and seated appropriately.
Post-Deployment Dilation: Balloon dilation performed at {carina} through the stent using a 6/7/8 Elation balloon dilated to 8 mm (1 inflation, 30 seconds) to seat the stent .
Conclusion The patient tolerated the procedure well. There were no immediate complications.
The patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

iCAST {new_stent} stent (Pathology) 
{lobe_abbr} BAL (Cell count, Microbiology/Cultures/Viral/Fungal, Cytology) 
{lobe_abbr} Endobronchial Biopsy (Pathology) 

IMPRESSION / PLAN

{age}-year-old {gender_long} presenting for evaluation of airway stenosis.
Patient's {lobe_abbr} was closed off around the prior iCAST stent; the {lobe_abbr} was reopened and the stent removed.
New iCAST stent ({new_stent}) placed successfully.

Follow-up pathology and BAL results.
{antibiotic} 1 tab PO BID for 7 days.

Repeat bronchoscopy in {follow_up} for re-evaluation.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Operative note for {age}yo {gender_short}, ref {referring_doc}. Procedure: {lobe_abbr} recanalization, stent exchange. Old stent ({old_stent}) swallowed/fused. Used EBUS/TBNA to access. Found {secretion_type}. Replaced with iCAST {new_stent} after failed trial of {failed_stent}. Rx {antibiotic}.",
    
    # Style 2: Dictation
    "Please generate an IP op report for a {age}-year-old {gender_long} referred by {referring_doc}. Diagnosis {diagnosis_code}. The {lobe_abbr} was fused shut over the old {old_stent} stent. I used EBUS and TBNA to find the lumen, aspirated {secretion_type}, and removed the old stent. We placed a new {new_stent} iCAST. Prescribed {antibiotic} and f/u in {follow_up}.",
    
    # Style 3: Sloppy / Quick Input
    "{age} {gender_short} airway stenosis {lobe_abbr}. old stent {old_stent} migrated and covered by tissue. complex case >100% work. required tbna and balloon to open. {secretion_type} found. removed old hardware. placed new icast {new_stent} finally. script for {antibiotic}.",
    
    # Style 4: Billing & Technical Focus
    "Generate procedure note. Codes: 31645, 31624, 31625, 31629, 31630, 31636, 31640. Mod 22 for complex {lobe_abbr} access (fused airway). Pt {age} {gender_short}. Indication: swallowed stent ({old_stent}). Intervention: Recanalization, BAL, dilation, stent exchange to {new_stent}. {antibiotic} post-op.",
    
    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nATTENDING: {attending_doc}\nDIAGNOSIS: {diagnosis_code}\nISSUE: {lobe_abbr} stenosis, swallowed stent ({old_stent})\nACTION: TBNA recanalization, Balloon dilation, Stent removal\nOUTCOME: New iCAST {new_stent} placed\nMEDS: {antibiotic}"
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
        ref_doc = random.choice(data_pool["referring_doc"])
        att_doc = random.choice(data_pool["attending_doc"])
        
        lobe_data = random.choice(data_pool["target_lobe"])
        old_stent = random.choice(data_pool["old_stent_size"])
        new_stent = random.choice(data_pool["new_stent_size"])
        failed_stent = random.choice(data_pool["failed_trial_stent"])
        secretions = random.choice(data_pool["secretion_type"])
        abx = random.choice(data_pool["antibiotic"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        fu_time = random.choice(data_pool["follow_up_time"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            referring_doc=ref_doc,
            attending_doc=att_doc,
            lobe_abbr=lobe_data["abbr"],
            old_stent=old_stent,
            new_stent=new_stent,
            failed_stent=failed_stent,
            secretion_type=secretions,
            antibiotic=abx,
            diagnosis_code=dx_code,
            follow_up=fu_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            gender_pronoun=gender_tup[2],
            referring_doc=ref_doc,
            attending_doc=att_doc,
            diagnosis_code=dx_code,
            lobe_abbr=lobe_data["abbr"],
            seg1=lobe_data["seg1"],
            seg2=lobe_data["seg2"],
            carina=lobe_data["carina"],
            secretion_type=secretions,
            old_stent=old_stent,
            new_stent=new_stent,
            failed_stent=failed_stent,
            antibiotic=abx,
            follow_up=fu_time
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