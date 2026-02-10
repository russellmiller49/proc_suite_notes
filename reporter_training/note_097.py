import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_097"
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
    "age": ["42", "49", "54", "56", "59", "63", "67", "71", "75"],
    "gender_tuple": [("female", "F", "she", "her"), ("male", "M", "he", "his")],
    "doctor": ["Dr. Smith", "Dr. Patel", "Dr. Henderson", "Dr. Wei", "Dr. O'Malley", "Dr. Khan"],
    "cpt_code_1": ["31646", "31645"], # Therapeutic aspiration
    "cpt_code_2": ["31622", "31623"], # Diagnostic bronchoscopy
    
    # RMS Findings (Right Mainstem)
    "rms_status": [
        "Dehiscence continues to be healed and remains closed",
        "Anastomosis is completely healed with no signs of dehiscence",
        "Small 2mm area of dehiscence noted at the posterior wall, otherwise stable",
        "Granulation tissue noted at the anastomosis site, but dehiscence is resolved"
    ],
    
    # RML Stent Details (Right Middle Lobe)
    "rml_stent": [
        "Aero 8x15mm covered metallic stent",
        "Aero 6x10mm covered stent",
        "Boston Scientific 8x20mm hybrid stent",
        "uncovered metallic stent (8x15mm)"
    ],
    
    # LMS Findings (Left Mainstem)
    "lms_condition": [
        "overlying granulation tissue causing mild to moderate stenosis",
        "significant granulation tissue causing severe stenosis (approx 60%)",
        "patent anastomosis with minimal granulation tissue",
        "moderate stenosis due to scar tissue formation"
    ],
    
    # Secretion/Aspiration Details
    "secretions": [
        "moderate thin mucus/secretions",
        "copious thick purulent secretions",
        "mild serous secretions",
        "moderate mucopurulent plugging"
    ],
    
    # Plan Timing
    "follow_up": ["2 weeks", "4 weeks", "1 month", "1 week", "10 days"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with bilateral lung transplant and complications of anastomosis dehiscence, ischemic lung injury, and bronchial stenosis. The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail. The patient wished to proceed and informed consent was obtained.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate. Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE
Therapeutic aspiration, subsequent (CPT {cpt1})
Diagnostic bronchoscopy with cell washing (CPT {cpt2})

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Disposable Bronchoscope

ESTIMATED BLOOD LOSS
None

COMPLICATIONS
None

SPECIMEN(S)
None

PROCEDURE IN DETAIL
A timeout was performed (confirming the patient's name, procedure type, and procedure location). Sedation was initiated.

The disposable bronchoscope was advanced for airway examination. Endobronchial topical lidocaine was applied to the main carina, right carina 1, and left carina 2.

Initial Airway Inspection Findings:

Tracheostomy: Tube in good position.
Trachea: Distal trachea and main carina normal.

Right Mainstem (RMS): {rms_status}.
Stable fibrinous tan exudate/granulation tissue noted in the donor RMS, proximal RUL bronchus, bronchus intermedius (BI), overlying RML take-off, and overlying RB6 take-off.

Right Upper Lobe (RUL): Prior area of full-thickness erosion/ulceration along the anterior wall remains fully covered by fibrinous exudate/granulation tissue.
RB1-2 normal. RB3 mildly stenotic with swirling granulation tissue/scar forming around the segmental airway take-off.

Right Middle Lobe (RML): Stent ({rml_stent}) in good position and fully patent.
Able to traverse scope in the RML stent, but not into the segmental airways.

Right Lower Lobe (RLL): Able to see RB4-5 from stent; these segments were fully patent. RB6 patent.
The RLL basilar segments RB7-10 appear healthy and patent.

Left Mainstem (LMS): Anastomosis intact with visible sutures; {lms_condition}.

Left Upper Lobe (LUL): Prior area of full-thickness erosion/ulceration along the medial wall remains fully covered by fibrinous exudate/granulation tissue.
Lingula: Mildly stenotic but fully patent. Able to traverse scope into lingula. LB1-5 are patent.

Left Lower Lobe (LLL): Bronchus and segments appear healthy. LB6-10 are patent.

Therapeutic Interventions: Successful therapeutic aspiration was performed to clean out the RMS, BI, RLL, LMS, and LLL from {secretions}.

The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was returned to ICU in stable condition.

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for bronchial stenosis airway evaluation.
Plan for repeat bronchoscopy by IP in {follow_up}.

OK to restart anticoagulation.
"""

# 5 distinct prompt styles
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Bronch report for {age}yo {gender_short}, ref {doctor}. Hx lung txp. Findings: RMS {rms_short}, RML stent ({rml_stent_short}) patent. LMS has {lms_short}. Suctioned {secretions_short}. Plan rpt {follow_up}.",
    
    # Style 2: Dictation
    "Please generate an operative note for a {age}-year-old {gender_long} patient of {doctor}. Indication is lung transplant complications. During the procedure, we found the RMS {rms_status_lower}. There is a {rml_stent} in the RML which is patent. The LMS shows {lms_condition}. We performed therapeutic aspiration of {secretions}. Follow up in {follow_up}.",
    
    # Style 3: Sloppy / Quick Note
    "{age} {gender_short} post-txp bronch. rms {rms_short}. rml stent ok. lms {lms_short}. cleaned out {secretions_short}. back to icu. f/u {follow_up}.",
    
    # Style 4: Billing / Coding Focus
    "Procedure CPT {cpt1}, {cpt2}. Dx J98.09. Patient {age} {gender_short}. Findings include {rms_status_lower} and patent RML stent. LMS stenosis noted ({lms_condition}). Aspiration performed.",
    
    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nREFERRING: {doctor}\nPROCEDURE: Bronchoscopy\nFINDINGS:\n- RMS: {rms_status}\n- RML: Stent ({rml_stent})\n- LMS: {lms_condition}\nINTERVENTION: Aspiration of {secretions}\nPLAN: Repeat in {follow_up}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, subj, poss)
        doctor = random.choice(data_pool["doctor"])
        cpt1 = random.choice(data_pool["cpt_code_1"])
        cpt2 = random.choice(data_pool["cpt_code_2"])
        
        rms_status = random.choice(data_pool["rms_status"])
        rml_stent = random.choice(data_pool["rml_stent"])
        lms_condition = random.choice(data_pool["lms_condition"])
        secretions = random.choice(data_pool["secretions"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # Derived short forms for telegraphic prompts
        rms_short = "healed" if "healed" in rms_status else "dehiscence"
        rml_stent_short = rml_stent.split(" ")[0] + " stent"
        lms_short = "stenosis" if "stenosis" in lms_condition else "patent"
        secretions_short = "mucus" if "mucus" in secretions else "secretions"
        rms_status_lower = rms_status.lower()

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            rms_short=rms_short,
            rml_stent_short=rml_stent_short,
            lms_short=lms_short,
            secretions_short=secretions_short,
            rms_status_lower=rms_status_lower,
            rml_stent=rml_stent,
            lms_condition=lms_condition,
            secretions=secretions,
            follow_up=follow_up,
            cpt1=cpt1,
            cpt2=cpt2,
            rms_status=rms_status
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            cpt1=cpt1,
            cpt2=cpt2,
            rms_status=rms_status,
            rml_stent=rml_stent,
            lms_condition=lms_condition,
            secretions=secretions,
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