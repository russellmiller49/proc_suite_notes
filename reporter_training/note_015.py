import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_015"
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
    "age": ["28", "33", "39", "45", "52", "61", "67"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "date_offset": range(-10, 0), # Days in past
    
    "etiology": [
        "fungal ball (Aspergilloma)",
        "necrotizing pneumonia",
        "cavitary lesion",
        "mycetoma"
    ],
    
    "debris_desc": [
        "yellow hard debris—likely pieces of fungal ball—noted in RB1",
        "tan necrotic material noted in the right upper lobe",
        "friable fungal elements noted in the right bronchial tree",
        "purulent secretions mixed with fungal debris in RB1"
    ],
    
    "sedation_meds": [
        "Propofol (60 mcg/kg/min), Precedex (1.3 mcg/kg/hr), Fentanyl (250 mcg), and Dilaudid (1 mg)",
        "Propofol (50 mcg/kg/min), Remifentanil infusion, and Midazolam (2 mg)",
        "Propofol (75 mcg/kg/min), Ketamine (50 mg), and Fentanyl (100 mcg)",
        "Propofol infusion and Fentanyl pushes (total 300 mcg)"
    ],
    
    "blocker_type": [
        "9Fr Uniblocker",
        "7Fr Arndt Blocker",
        "9Fr Cohen Flexitip Blocker",
        "EZ-Blocker"
    ],
    
    "blocker_depth": ["24cm", "25-26cm", "27cm", "28cm"],
    
    "epi_dose": ["0.4mg", "0.5mg", "1ml of 1:10000", "0.3mg"],
    "txa_dose": ["1000mg", "500mg", "250mg", "2g"],
    
    "start_time": ["19:15 PM", "02:30 AM", "11:45 PM", "04:00 AM"],
    "duration": ["45 minutes", "60 minutes", "35 minutes", "55 minutes"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """Procedure report generator
Custom Gem
This is for informational purposes only. For medical advice or diagnosis, consult a professional.
INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {proc_date} INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with massive hemoptysis, endobronchial clot causing acute airway obstruction, and worsening of acute respiratory failure.
CONSENT This procedure was emergent. Serial consent was previously obtained before the procedure.
The nature, indications, purpose, benefits, risks, potential complications, and alternatives to the procedure were discussed with the patient or surrogate decision-maker in detail.
Patient or surrogate decision-maker previously agreed to proceed with the procedure.
PREOPERATIVE DIAGNOSIS

Massive hemoptysis

Acute airway obstruction

POSTOPERATIVE DIAGNOSIS

Massive hemoptysis

Acute airway obstruction

Suspected {etiology} LUL

PROCEDURE

Therapeutic aspiration of tracheobronchial tree (subsequent episodes) (CPT 31646)

Bronchoscopy with cell washing (CPT 31622)

Bronchoscopy with application of Tranexamic Acid (CPT 31899)

Placement of bronchial blocker (CPT 31634)

Foreign body removal (endobronchial clot) (CPT 31635)

NOTE ON PROCEDURAL DIFFICULTY (Modifier 22) This patient was exceptionally critically ill due to acute respiratory failure requiring max ventilator and ECMO support.
Patient required extensive therapeutic aspiration and removal of clot using forceps, which required substantially more time, mental/physical effort, and intensity (>100% increased work).
ANESTHESIA Moderate sedation was administered. Medications included {sedation_meds}.
Start Time: {start_time}

Total Time: {duration}

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Disposable Bronchoscope.

ESTIMATED BLOOD LOSS Minimal active bleeding; large amount of organized clot removed.

COMPLICATIONS None.
PROCEDURE IN DETAIL This was an emergency procedure due to rapid clinical decompensation with associated massive hemoptysis and endobronchial clot causing acute airway obstruction.
The patient already had a tracheostomy tube (ID 7.5mm) in place.
Airway Inspection The flexible therapeutic bronchoscope was advanced for airway examination.
Endobronchial topical lidocaine was applied to the vocal cords, main carina, right carina 1, and left carina 2.

Trachea: Clot extending from the left mainstem bronchus (LMSB) into the distal trachea without obstruction of the right mainstem bronchus (RMSB).
Trachea otherwise normal in anatomy.

Right Lung: Evidence of {debris_desc}.
Otherwise normal anatomic branching to the first subsegmental level. No evidence of mass, lesions, or bleeding.
Left Lung: Large clot completely obstructing the LMSB, extending to the main carina.
The left upper lobe (LUL) and left lower lobe (LLL) were also completely obstructed by clot.

Mucosa: Mildly friable.
Therapeutic Aspiration and Foreign Body Removal Successful therapeutic aspiration was performed to clear the trachea, RMSB, RUL, bronchus intermedius, RML, RLL, LMSB, LUL, and LLL of blood clot and mucus.
Technique: Endobronchial obstruction due to clot was mechanically excised and removed using bland alligator forceps, therapeutic aspiration utilizing Neptune suction, and numerous cold saline flushes.
Extraction: Able to remove all clot from the LMSB and the majority of the LLL and LB7/8-10.
This included a large cast of clot dislodged from the LLL truncus basalis.
Residual Clot: Some partially obstructing clot remained in the LLL superior segment (LB6). The LUL remained largely filled with clot.
As the LUL {etiology} is the suspected source of the bleed, the LUL clot was intentionally left in place to organize and prevent further bleeding.
Endobronchial Hemostasis To prevent recurrence of active bleeding, the following medications were instilled into the LUL targeting LB1/2 and LB3:

Epinephrine: {epi_dose}

Tranexamic Acid (TXA): {txa_dose}

Bronchial Blocker Placement A {blocker_type} was utilized.
The ventilator adaptor was attached to the tracheostomy tube. Using a parallel Slim disposable scope via the tracheostomy tube, the bronchial blocker balloon was guided into the distal LMSB under direct visualization.
Position: Secured at {blocker_depth} at the dark blue securement device.
Inflation Test: Confirmed that 8cc of air was required to adequately inflate the balloon and fully occlude the LMSB.
Status: The balloon was deflated and left in the distal LMSB for emergent use in case of recurrent massive hemoptysis.
Conclusion Residual secretions and saline were suctioned to clear. The patient tolerated the procedure well with no immediate complications.
Respiratory status was improved at the conclusion of the operation.

SPECIMENS None.
IMPRESSION / PLAN

Successful therapeutic aspiration and foreign body removal of clot from LMSB and LLL;
LUL clot left in situ to tamponade suspected fungal bleeding source.

Bronchial blocker placed in distal LMSB, currently deflated.
Post-Procedure Orders:

Nebulized TXA.

Hold all anticoagulation (including heparin gtt).

Maintain sedation to limit coughing.

Continue broad-spectrum antimicrobials.
Follow-up: Tentative plan for repeat bronchoscopy tomorrow for therapeutic aspiration/cryoextraction of clot."""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic / High Intensity
    "Emergency bronch. {age}{gender_short}. Massive hemoptysis on ECMO. Diagnosis: {etiology}. Clot in LMSB/Trachea. Actions: Removed clot LMSB/LLL, left LUL clot alone. Meds: Epi {epi_dose}, TXA {txa_dose}. Placed {blocker_type} at {blocker_depth} (deflated). Modifier 22 applied.",
    
    # Style 2: Dictation / Narrative
    "Generate an operative report for a {age} year old {gender_long} with massive hemoptysis and airway obstruction. Suspected source is {etiology} in the LUL. We cleared the trachea and LLL but left the LUL clot to tamponade. We instilled {epi_dose} epinephrine and {txa_dose} TXA. A {blocker_type} was placed in the LMSB for safety. Procedure was critical/complex (Mod 22).",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} emergent bronch hemoptysis. {etiology} LUL. Trach present. Clot removal from LMSB and LLL. LUL left packed. {blocker_type} dropped in LMSB. TXA {txa_dose} given. Pt on ECMO/Max vent.",
    
    # Style 4: Billing Focus
    "Procedure Codes: 31646, 31622, 31899, 31634, 31635-22. Patient {age} {gender_short}. Indication: Massive hemoptysis, {etiology}. Findings: Clot obstruction LMSB. Interventions: Clot extraction, {blocker_type} placement, TXA instillation.",
    
    # Style 5: Structured Request
    "PT: {age}/{gender_short}\nDX: Massive Hemoptysis / {etiology}\nPROCEDURE: Therapeutic bronch, clot removal, blocker placement.\nDETAILS: Critical illness (Mod 22). Removed clot from trachea/LLL. Left LUL clot. Meds: Epi {epi_dose}, TXA {txa_dose}. Device: {blocker_type} @ {blocker_depth}."
]

# ==========================================
# 5. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short)
        
        # Date generation
        days_ago = random.choice(data_pool["date_offset"])
        proc_date = (datetime.date.today() + datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        etiology = random.choice(data_pool["etiology"])
        debris_desc = random.choice(data_pool["debris_desc"])
        sedation_meds = random.choice(data_pool["sedation_meds"])
        blocker_type = random.choice(data_pool["blocker_type"])
        blocker_depth = random.choice(data_pool["blocker_depth"])
        epi_dose = random.choice(data_pool["epi_dose"])
        txa_dose = random.choice(data_pool["txa_dose"])
        start_time = random.choice(data_pool["start_time"])
        duration = random.choice(data_pool["duration"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            etiology=etiology,
            epi_dose=epi_dose,
            txa_dose=txa_dose,
            blocker_type=blocker_type,
            blocker_depth=blocker_depth
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            proc_date=proc_date,
            age=age, 
            gender_long=gender_tup[0],
            etiology=etiology,
            debris_desc=debris_desc,
            sedation_meds=sedation_meds,
            start_time=start_time,
            duration=duration,
            epi_dose=epi_dose,
            txa_dose=txa_dose,
            blocker_type=blocker_type,
            blocker_depth=blocker_depth
        )
        
        dataset.append({"prompt": prompt, "completion": completion})
    
    return dataset

# ==========================================
# 6. EXECUTION & SAVING
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