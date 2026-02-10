import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_102"
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
    "age": ["34", "45", "52", "56", "58", "61", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication_detail": [
        "bilateral lung transplant with complication of anastomosis dehiscence and ischemic lung injury",
        "bilateral lung transplant with airway stricture and secretion retention",
        "single right lung transplant with anastomotic granulation tissue",
        "bilateral lung transplant surveillance for dehiscence healing",
        "post-transplant airway monitoring for known ischemic injury"
    ],
    "anesthesia": [
        "Local anesthesia",
        "Moderate sedation (MAC)",
        "General anesthesia via LMA"
    ],
    "rms_finding": [
        "The dehiscence continues to be healed and remains closed",
        "The anastomotic site appears stable with no new dehiscence",
        "The dehiscence site shows robust granulation tissue but remains patent",
        "Minimal granulation tissue is noted at the anastomosis, otherwise closed"
    ],
    "foreign_body_text": [
        "A small metallic object, likely a hemoclip, was noted protruding from the posterior membrane near the anastomosis site, slightly more prominent than the bronchoscopy 1 week prior.",
        "A loose suture was noted along the medial wall, non-obstructing.",
        "No foreign bodies, clips, or loose sutures were identified at the anastomotic site.",
        "A small piece of surgical material was visible at the posterior membrane."
    ],
    "rul_finding": [
        "Previously seen area of full-thickness erosion/ulceration along the anterior wall now appears fully covered by fibrinous exudate, suggesting early healing",
        "The anterior wall ulceration is clean with decreasing size compared to prior exam",
        "Granulation tissue has replaced the previous erosion site, indicating positive healing",
        "The bronchial mucosa is erythematous but the previous ulceration is resolved"
    ],
    "lms_finding": [
        "Anastomosis is intact with visible sutures and mild stenosis",
        "Anastomosis is widely patent with healthy mucosa",
        "Mild circumferential granulation tissue is present at the anastomosis",
        "Anastomosis is intact, sutures are covered, no stenosis noted"
    ],
    "bal_loc": ["RLL", "LLL", "RML", "LUL", "RLL and LLL"],
    "secretions_status": [
        "Moderate secretions were noted in the BI and RLL",
        "Copious thick secretions were noted bilaterally",
        "Mild serous secretions were found in the lower lobes",
        "Purulent secretions were suctioned from the right mainstem"
    ],
    "plan_action": [
        "Right mainstem anastomosis dehiscence remains closed. Recommend bronchoscopic secretion clearance every 1-2 days.",
        "Airway stable. We will extend the interval for the next bronchoscopy to 3-4 days.",
        "Granulation tissue manageable. Continue current secretion clearance protocol.",
        "Anastomosis healing well. Follow up bronchoscopy in 1 week."
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication_detail}.
The patient presents for bronchoscopy for airway evaluation, therapeutic aspiration, and potential stent removal.
CONSENT The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

Bilateral lung transplant airway complications (anastomosis dehiscence, ischemic injury) 

PROCEDURE

31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS) 

31646 Therapeutic aspiration, subsequent episodes 

31624 Bronchoalveolar lavage (BAL) 

ANESTHESIA {anesthesia}.
MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS None.

SPECIMEN(S)

BAL of {bal_loc} - cultures/micro 

PROCEDURE IN DETAIL A timeout was performed confirming the patient's name, procedure type, and procedure location.
The Flexible Therapeutic Bronchoscope was advanced for airway evaluation. Endobronchial topical lidocaine was applied to the main carina, right mainstem (RMS), bronchus intermedius (BI), and LC2.
Airway Inspection Findings


Trachea: Distal trachea appeared normal.

Right Lung:


RMS: {rms_finding}.
{foreign_body_text}
Granulation/Exudate: Fibrinous exudate and granulation tissue persist in the donor RMS, proximal RUL bronchus, BI, overlying RML take-off, and overlying RB6 take-off, though all areas appear improved from previous exams.
Mildly heaped nonobstructing granulation tissue was noted along the medial aspect of the right mainstem bronchus.
RUL: {rul_finding};
this is greatly improved from 1 week ago.


RML: Take-off is narrowed but able to be traversed with the "regular" size disposable bronchoscope.
RLL: Basilar segments appear healthy.

Left Lung:


LMS: {lms_finding}.
LUL: Evidence of continued healing with fibrin exudates and granulation tissue.
The underlying mediastinum/pulmonary artery is no longer visible along the medial aspect, indicating the entire area is improved from 1 week ago.
Lingula: Take-off is narrowed but able to be traversed with the "regular" size disposable bronchoscope.
LLL: Bronchus and segments appear healthy.

Interventions


Therapeutic Aspiration: {secretions_status}.
Successful therapeutic aspiration was performed to clear mild mucus from the trachea, right mainstem bronchus, right-sided stent, bronchus intermedius, right lower lobe bronchus, left mainstem bronchus, left upper lobe, and left lower lobe.
Bronchoalveolar Lavage (BAL): Performed at the {bal_loc}. 20 cc of normal saline was instilled, and 10 cc was returned via suction.
Samples were sent for Microbiology (Cultures/Viral/Fungal).

Completion Residual secretions were suctioned to clear.
The disposable bronchoscope was removed and the procedure completed. The patient tolerated the procedure well with no immediate complications.
The patient will remain in the ICU afterward.

IMPRESSION / PLAN

{plan_action}
Prior RUL full-thickness erosion/ulceration is now covered with fibrinous exudate/granulation tissue.

Encourage ongoing aggressive secretion clearance practices.
Recommend bronchoscopic secretion clearance every 1-2 days, deferring to the transplant team's expertise.
Ongoing discussions with the transplant team regarding timing for the next IP bronchoscopy.
Replacement of stent remains possible if there are signs of worsening at the RMS dehiscence site.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Pt: {age}{gender_short}, post-transplant. Indication: {indication_short}. Findings: RMS {rms_short}, RUL {rul_short}, LMS {lms_short}. BAL {bal_loc}. Plan: {plan_short}.",
    
    # Style 2: Dictation
    "Please generate a bronchoscopy note for a {age} year old {gender_long}. The patient has {indication_detail}. We found that {rms_finding_lower}. In the RUL, {rul_finding_lower}. The left mainstem {lms_finding_lower}. We performed a BAL in the {bal_loc}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} txp airway check. RMS: {rms_short}. {foreign_body_short}. RUL healing. LMS {lms_short}. BAL {bal_loc}. {secretions_short}.",
    
    # Style 4: Billing Focus
    "Procedure 31624, 31646. Dx: J98.09. {age} {gender_short}. Indication: {indication_short}. RMS: {rms_short}. Lungs cleared. BAL {bal_loc}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication_detail}\nAnesthesia: {anesthesia}\nFindings:\n- RMS: {rms_finding}\n- RUL: {rul_finding}\n- LMS: {lms_finding}\nIntervention: BAL {bal_loc}"
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
        indication_detail = random.choice(data_pool["indication_detail"])
        anesthesia = random.choice(data_pool["anesthesia"])
        rms_finding = random.choice(data_pool["rms_finding"])
        foreign_body_text = random.choice(data_pool["foreign_body_text"])
        rul_finding = random.choice(data_pool["rul_finding"])
        lms_finding = random.choice(data_pool["lms_finding"])
        bal_loc = random.choice(data_pool["bal_loc"])
        secretions_status = random.choice(data_pool["secretions_status"])
        plan_action = random.choice(data_pool["plan_action"])
        
        # Helper vars for prompts (short versions)
        indication_short = "airway complications" if "complication" in indication_detail else "airway check"
        rms_short = "dehiscence healed" if "healed" in rms_finding else "stable"
        rul_short = "ulcer covered" if "covered" in rul_finding else "healing"
        lms_short = "intact" if "intact" in lms_finding else "patent"
        plan_short = "cont clearance"
        foreign_body_short = "FB noted" if "metallic" in foreign_body_text else "no FB"
        secretions_short = "mod secretions" if "Moderate" in secretions_status else "secretions managed"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication_detail=indication_detail,
            indication_short=indication_short,
            rms_short=rms_short,
            rms_finding_lower=rms_finding.lower().rstrip('.'),
            rul_short=rul_short,
            rul_finding_lower=rul_finding.lower().rstrip('.'),
            lms_short=lms_short,
            lms_finding_lower=lms_finding.lower().rstrip('.'),
            bal_loc=bal_loc,
            plan_short=plan_short,
            anesthesia=anesthesia,
            rms_finding=rms_finding,
            rul_finding=rul_finding,
            lms_finding=lms_finding,
            foreign_body_short=foreign_body_short,
            secretions_short=secretions_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            indication_detail=indication_detail,
            anesthesia=anesthesia,
            rms_finding=rms_finding,
            foreign_body_text=foreign_body_text,
            rul_finding=rul_finding,
            lms_finding=lms_finding,
            bal_loc=bal_loc,
            secretions_status=secretions_status,
            plan_action=plan_action
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