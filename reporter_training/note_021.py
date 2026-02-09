import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_021"
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
    "age": ["62", "65", "68", "71", "74", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller"],
    "surgeon": ["Dr. Thistlethwaite", "Dr. Harrison", "Dr. Gomez", "Dr. Al-Fayed"],
    "diagnosis_code": ["J93.82", "J93.9", "J93.12"],
    "diagnosis_text": ["Other airleaks", "Persistent airleak", "Bronchopleural fistula", "Prolonged post-op air leak"],
    
    # Anatomy logic: Target Lobe for Valve + A secondary lobe for BAL
    "anatomy_scenarios": [
        {
            "target_lobe": "RLL",
            "target_segments_desc": "Lateral and Posterior subsegment",
            "seg_1": "RB9",
            "seg_2": "RB10",
            "bal_loc_1": "Lingula (Superior Segment LB4 and Inferior Segment LB5)",
            "bal_loc_2": "Lateral-basal Segment of RLL (RB9)",
            "blocker_loc": "RLL posterior branch"
        },
        {
            "target_lobe": "LLL",
            "target_segments_desc": "Lateral and Posterior subsegment",
            "seg_1": "LB9",
            "seg_2": "LB10",
            "bal_loc_1": "RML (Medial Segment RB5)",
            "bal_loc_2": "Lateral-basal Segment of LLL (LB9)",
            "blocker_loc": "LLL posterior branch"
        },
        {
            "target_lobe": "RUL",
            "target_segments_desc": "Apical and Posterior subsegment",
            "seg_1": "RB1",
            "seg_2": "RB2",
            "bal_loc_1": "LUL (Apical-Posterior LB1+2)",
            "bal_loc_2": "Posterior Segment of RUL (RB2)",
            "blocker_loc": "RUL posterior branch"
        }
    ],
    
    # Procedure Details
    "fluid_in": ["50", "60", "100", "120"],
    "fluid_out": ["10", "15", "20", "30"],
    "valve_size_fail": ["7", "8", "9"],
    "valve_size_success": ["5", "6", "7"],
    "fail_reason": ["too large for the airway", "migrated proximally", "showed poor apposition", "was unstable"],
    "sealant_vol": ["2cc", "4cc", "1.5cc"],
    "pleurovac_setting": ["-20", "-15", "-10", "-25"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]
INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {diagnosis_text}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient or surrogate. The patient or surrogate read and signed the provided consent form / provided consent over the phone. The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
{dx_code} {diagnosis_text}

POSTOPERATIVE DIAGNOSIS
{dx_code} {diagnosis_text}

PROCEDURE
Therapeutic aspiration (initial episode) (CPT 31645)
Bronchoalveolar lavage (BAL) (CPT 31624) – Done in multiple lobes
Bronchial valve insertion (initial lobe) (CPT 31647)
Balloon occlusion (CPT 31634)
Foreign body removal (valve removal/exchange) (CPT 31635)
Endobronchial sealant application

ATTENDING
{attending}

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS
None

COMPLICATIONS
None

PROCEDURE IN DETAIL

General
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location. Patient Position: Supine.

Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus and mucus plugs.

Bronchoalveolar Lavage (First Site)
BAL was performed in the {bal_loc_1} with saline instilled and returned. Instilled {fluid_in} cc of NS, suction returned with {fluid_out} cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Bronchoalveolar Lavage ({target_lobe})
BAL was performed in the {bal_loc_2} with saline instilled and returned. Instilled {fluid_in} cc of NS, suction returned with {fluid_out} cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Bronchopleural Fistula (BPF) Localization and Occlusion
Serial occlusion with an endobronchial blocker (Arndt 7Fr) and Fogarty balloon was performed to isolate the airleak to the {target_lobe} ({target_segments_desc}). The airleak was reproduced with inspiratory hold at 30 and suction on pleurovac on {pleurovac_setting} cmH2O.

Endobronchial Sealant Application
Tisseel ({sealant_vol}) was used to block off a subsegment of the {blocker_loc}.

Endobronchial Valve Placement and Exchange
Based on localization, Spiration valves were selected for deployment.

Attempt 1: A Size {size_fail} Spiration valve was placed in {seg_2} but noted to be {fail_reason}; this was subsequently removed.

Placement: A Size {size_success} Spiration valve was placed in {seg_1} in good position.

Attempt 2: A Size {size_success} Spiration valve was placed in {seg_2} but noted to be in poor position; this was removed.

Placement: A replacement Size {size_success} Spiration valve was placed in {seg_2} in a better angle.

Final Valve Configuration:
{seg_1}: Size {size_success} Spiration valve.
{seg_2}: Size {size_success} Spiration valve.

Result
Airleak was significantly decreased following intervention. See {surgeon}'s note for VATS and pleurodesis.

Conclusion
The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
BAL (x2)

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for BAL and valve placement.
Follow-up on BAL results.
Follow-up in 6 weeks for valve removal.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Interventional Pulmonology note for {age}yo {gender_short}. Dx: {diagnosis_text}. Proc: BAL x2 ({bal_loc_1}, {target_lobe}), Valve placement {target_lobe} ({seg_1}, {seg_2}). Required exchange of {seg_2} valve due to sizing ({fail_reason}). Tisseel used.",

    # Style 2: Dictation / Narrative
    "Please generate an operative report for Dr. {attending}. Patient is a {age} year old {gender_long} with {diagnosis_text}. We performed therapeutic aspiration, BAL in the {bal_loc_1} and {target_lobe}. We localized the leak to the {target_lobe}, placed sealant, and deployed Spiration valves in {seg_1} and {seg_2}. Note that the first valve in {seg_2} was {fail_reason} and had to be exchanged.",

    # Style 3: Sloppy / Quick Input
    "{age}M {diagnosis_text}. Bronchoscopy with valves. Target {target_lobe} segments {seg_1}/{seg_2}. Had to swap out the {seg_2} valve because it was {fail_reason}. Also did BAL and Tisseel. {surgeon} managing VATS.",

    # Style 4: Billing / CPT Focus
    "Create Op Report. CPTs: 31645, 31624 (BAL x2), 31647 (Valve initial), 31634 (Balloon), 31635 (Removal/Exchange). Dx: {dx_code}. Loc: {target_lobe}. Valve exchange required in {seg_2}.",

    # Style 5: Structured Request
    "PROCEDURE: Airleak Management\nPATIENT: {age} / {gender_short}\nATTENDING: {attending}\nTARGET: {target_lobe} ({seg_1}, {seg_2})\nDETAILS: Multiple BALs. Sealant used. Valve sizing issue in {seg_2} ({fail_reason}) requiring removal and replacement."
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
        surgeon = random.choice(data_pool["surgeon"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        dx_text = random.choice(data_pool["diagnosis_text"])
        
        # Anatomy Logic (ensure consistency between lobes and segments)
        anatomy = random.choice(data_pool["anatomy_scenarios"])
        
        fluid_in = random.choice(data_pool["fluid_in"])
        fluid_out = random.choice(data_pool["fluid_out"])
        size_fail = random.choice(data_pool["valve_size_fail"])
        size_success = random.choice(data_pool["valve_size_success"])
        fail_reason = random.choice(data_pool["fail_reason"])
        sealant_vol = random.choice(data_pool["sealant_vol"])
        pleurovac = random.choice(data_pool["pleurovac_setting"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            attending=attending,
            diagnosis_text=dx_text,
            dx_code=dx_code,
            target_lobe=anatomy["target_lobe"],
            seg_1=anatomy["seg_1"],
            seg_2=anatomy["seg_2"],
            bal_loc_1=anatomy["bal_loc_1"],
            fail_reason=fail_reason,
            surgeon=surgeon
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            diagnosis_text=dx_text,
            dx_code=dx_code,
            attending=attending,
            surgeon=surgeon,
            
            # Anatomy Variables
            target_lobe=anatomy["target_lobe"],
            target_segments_desc=anatomy["target_segments_desc"],
            seg_1=anatomy["seg_1"],
            seg_2=anatomy["seg_2"],
            bal_loc_1=anatomy["bal_loc_1"],
            bal_loc_2=anatomy["bal_loc_2"],
            blocker_loc=anatomy["blocker_loc"],
            
            # Procedural Details
            fluid_in=fluid_in,
            fluid_out=fluid_out,
            pleurovac_setting=pleurovac,
            sealant_vol=sealant_vol,
            size_fail=size_fail,
            size_success=size_success,
            fail_reason=fail_reason
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