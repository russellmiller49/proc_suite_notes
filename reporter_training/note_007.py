import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_007"
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
    "age": ["55", "62", "68", "71", "74", "79", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Chen", "Dr. Gupta"],
    "attending": ["Dr. Thistlethwaite", "Dr. Anderson", "Dr. Rodriguez", "Dr. Kim"],
    "fellow": ["Dr. Lee", "Dr. Patel", "Dr. Davis", "Dr. White"],
    "support_rn": ["Sarah RN", "Mike RN", "Jessica RN", "David RN"],
    "support_rt": ["Tom RT", "Emily RT", "Chris RT", "Amanda RT"],
    
    # Clinical scenarios: (Lobe Name, Segment 1, Segment 2, Arndt Blocker Loc, Lavage Site 1, Lavage Site 2)
    "anatomy_scenarios": [
        {
            "target_lobe": "RLL",
            "target_lobe_full": "Right Lower Lobe",
            "seg1": "RB9",
            "seg2": "RB10",
            "blocker_loc": "RLL (Lateral and Posterior subsegment)",
            "lavage1": "Superior Segment of Lingula (LB4) and Inferior Segment of Lingula (LB5)",
            "lavage2": "Lateral-basal Segment of RLL (RB9)",
            "sealant_loc": "RLL posterior branch"
        },
        {
            "target_lobe": "LUL",
            "target_lobe_full": "Left Upper Lobe",
            "seg1": "LB1+2",
            "seg2": "LB3",
            "blocker_loc": "LUL (Apical and Posterior subsegment)",
            "lavage1": "Medial Segment of RML (RB5)",
            "lavage2": "Apical-posterior Segment of LUL (LB1+2)",
            "sealant_loc": "LUL apical branch"
        },
        {
            "target_lobe": "RUL",
            "target_lobe_full": "Right Upper Lobe",
            "seg1": "RB1",
            "seg2": "RB2",
            "blocker_loc": "RUL (Apical and Anterior subsegment)",
            "lavage1": "Superior Segment of LLL (LB6)",
            "lavage2": "Apical Segment of RUL (RB1)",
            "sealant_loc": "RUL anterior branch"
        }
    ],
    
    "valve_sizes": ["5", "6", "7", "9"],
    "diagnosis_code": ["J93.82", "J93.9", "J93.12"],
    "diagnosis_text": ["Other airleaks", "Pneumothorax, unspecified", "Secondary spontaneous pneumothorax"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {diagnosis_text}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{dx_code} {diagnosis_text}

POSTOPERATIVE DIAGNOSIS

{dx_code} {diagnosis_text}

PROCEDURE

31645 Therapeutic aspiration initial episode

31624 Dx bronchoscope/lavage (BAL)

31634 Balloon occlusion or placement of occlusive substance

31635 Foreign body removal

31647 Bronchial valve insert initial lobe

22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)

Note: BAL done in multiple lobes

ATTENDING {attending}

ASSISTANT {fellow}

SUPPORT STAFF RN: {rn} RT: {rt}

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Supine

Initial Airway Inspection and Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus and mucus plug.
Bronchoalveolar Lavage (Site 1) Bronchoalveolar lavage was performed at the {lavage1}.
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Bronchoalveolar Lavage (Site 2) Bronchoalveolar lavage was performed at the {lavage2}.
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Bronchopleural Fistula Localization Serial occlusion with endobronchial blocker (Arndt 7Fr) and Fogarty balloon was done to isolate the airleak to be at the {blocker_loc}.
Airleak was reproduced with inspiratory hold at 30 and suction on pleurovac on -20cmH20.
Endobronchial Sealant Application Tisseel 2cc was used to block off a subsegment of the {sealant_loc}.
Endobronchial Valve Placement

{seg2}: A Size {size_large} Spiration valve was placed but noted to be too large for the airway ({seg2}).
This was subsequently removed.

{seg1}: A Size {size_correct} Spiration valve was placed in {seg1}, in good position.
{seg2} (Exchange): Then a size {size_correct} Spiration valve was placed in {seg2}, noted to be in poor position;
this was removed again and replaced with another size {size_correct} Spiration valve in a better angle.
Final Valve Configuration

{seg1} - size {size_correct} Spiration valve

{seg2} - size {size_correct} Spiration valve

The airleak was significantly decreased.
See Dr. Thistlethwaite's note for VATS and pleurodesis.

The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

BAL (x2)

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for BAL and valve placement.
Follow-up on BAL results.

Follow-up in 6 weeks for valve removal.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Pt {age} {gender_short}. Ref {ref_physician}. Persistent airleak {dx_code}. Perform BAL {lavage1_short} and {lavage2_short}. Isolate leak {target_lobe}. Place valves {seg1}, {seg2} (had to exchange {seg2}). Use Tisseel. No comps.",

    # Style 2: Dictation / Narrative
    "Dictate an operative report for a {age}-year-old {gender_long} referred by {ref_physician}. Diagnosis is {diagnosis_text}. We did a therapeutic aspiration and BAL of the {lavage1_short} and {lavage2_short}. We localized the fistula to the {target_lobe} using balloon occlusion. We placed Spiration valves in {seg1} and {seg2}. Note that the first valve in {seg2} was too big and had to be downsized to a {size_correct}. Airleak decreased.",

    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronchoscopy. {target_lobe} air leak. BAL done x2. Valves placed in {seg1} and {seg2}. {seg2} took a few tries to fit right. Tisseel used. stable.",

    # Style 4: Billing Focus
    "Procedure codes: 31645, 31624, 31634, 31635, 31647-22. Patient: {age} {gender_short}. Dx: {dx_code}. Sites: {lavage1_short} (BAL), {target_lobe} (Valves). Mod 22 for valve exchange/resizing in {seg2}.",

    # Style 5: Structured Request
    "Generate Interventional Pulm Report:\nPatient: {age} {gender_short}\nDoctor: {attending}\nIndication: {diagnosis_text}\nFindings: Airleak isolated to {target_lobe}. Valves placed in {seg1} (size {size_correct}) and {seg2} (size {size_correct} after failing size {size_large})."
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
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        fellow = random.choice(data_pool["fellow"])
        rn = random.choice(data_pool["support_rn"])
        rt = random.choice(data_pool["support_rt"])
        
        # Diagnosis
        dx_idx = random.randint(0, len(data_pool["diagnosis_code"]) - 1)
        dx_code = data_pool["diagnosis_code"][dx_idx]
        diagnosis_text = data_pool["diagnosis_text"][dx_idx]
        
        # Anatomy Scenario
        scenario = random.choice(data_pool["anatomy_scenarios"])
        
        # Valve Sizes (Ensure logic: tried large, switched to correct)
        size_correct = random.choice(["5", "6"])
        size_large = "7" if size_correct == "6" else "6" # Logic: if correct is 6, large was 7. If correct is 5, large was 6.
        
        # Shorten lavage names for prompts
        lavage1_short = scenario["lavage1"].split(" (")[0]
        lavage2_short = scenario["lavage2"].split(" (")[0]

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            dx_code=dx_code,
            diagnosis_text=diagnosis_text,
            target_lobe=scenario["target_lobe"],
            seg1=scenario["seg1"],
            seg2=scenario["seg2"],
            lavage1_short=lavage1_short,
            lavage2_short=lavage2_short,
            size_correct=size_correct,
            size_large=size_large
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            ref_physician=ref_physician,
            dx_code=dx_code, 
            diagnosis_text=diagnosis_text,
            attending=attending,
            fellow=fellow,
            rn=rn,
            rt=rt,
            # Anatomy
            lavage1=scenario["lavage1"],
            lavage2=scenario["lavage2"],
            blocker_loc=scenario["blocker_loc"],
            sealant_loc=scenario["sealant_loc"],
            seg1=scenario["seg1"],
            seg2=scenario["seg2"],
            # Valves
            size_large=size_large,
            size_correct=size_correct
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