import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_103" 
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
    "age": ["49", "52", "56", "59", "61", "64", "68", "72"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Smith", "Dr. Chen", "Dr. Ingraham", "Dr. Bowers", "Self", "Dr. Miller"],
    "attending": ["Dr. A. Johnson", "Dr. B. Williams", "Dr. C. Davis"],
    "fellow": ["Dr. K. Lee", "Dr. M. Patel", "Dr. J. Doe"],
    "rn_name": ["Sarah", "Mike", "Jessica", "Tom"],
    "rt_name": ["David", "Linda", "Robert", "Emily"],
    "procedure_date": ["January 12", "February 4", "March 20", "April 15", "May 10"],
    
    # Clinical Findings Variations
    "rms_dehiscence_status": [
        "continues to be healed and remains closed",
        "shows complete closure with healthy mucosa",
        "remains well-approximated without air leak",
        "appears stable with no new separation"
    ],
    "foreign_object": [
        "A small metallic object, consistent with a likely hemoclip",
        "A piece of suture material",
        "A small fragment of stent wire",
        "A retained suture"
    ],
    "foreign_object_action": [
        "was noted protruding from the posterior membrane",
        "was visualized along the medial wall",
        "was seen embedded in the granulation tissue",
        "was noted near the anastomosis site"
    ],
    "rul_finding": [
        "fully covered by fibrinous exudate, suggesting early healing",
        "showing significant epithelialization with minimal fibrin",
        "covered in healthy granulation tissue",
        "healing well with decreased exudate compared to prior exam"
    ],
    "lms_status": [
        "mild stenosis",
        "moderate stenosis",
        "slight narrowing",
        "patent lumen with minimal scarring"
    ],
    "bal_location": ["RLL", "LLL", "RML"],
    "bal_volumes": [
        ("20", "10"),
        ("30", "15"),
        ("40", "20"),
        ("50", "25")
    ],
    "secretion_load": [
        "mild mucus",
        "moderate purulent secretions",
        "thick mucoid secretions",
        "copious secretions"
    ],
    "plan_frequency": ["1-2 days", "2-3 days", "daily", "every 48 hours"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_md}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with a bilateral lung transplant with complications of anastomosis dehiscence and ischemic lung injury.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 
Right mainstem anastomosis dehiscence (healed) 
Bronchial stenosis ({lms_status}, LMS) 

PROCEDURE
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS) 
31646 Therapeutic aspiration, subsequent episodes 
31624 Diagnostic bronchoscopy with bronchoalveolar lavage (BAL) 

ATTENDING {attending}
ASSISTANT {fellow}
SUPPORT STAFF RN: {rn} RT: {rt}

ANESTHESIA Local 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope 

ESTIMATED BLOOD LOSS None 
COMPLICATIONS None 

PROCEDURE IN DETAIL A timeout was performed (confirming the patient's name, procedure type, and procedure location).
The flexible therapeutic bronchoscope was advanced for airway evaluation. Endobronchial topical lidocaine was applied to the main carina, RMS, BI, and LC2.

Initial Airway Inspection Findings:

Trachea: Distal trachea normal.

Right Mainstem (RMS): The anastomosis dehiscence {rms_status}.
{foreign_obj}, {foreign_obj_loc} near the RMS anastomosis site.
This appeared slightly more prominent than the bronchoscopy performed 1 week prior.
Fibrinous exudate and desired granulation tissue were present in the donor RMS, proximal RUL bronchus, BI, overlying RML take-off, and overlying RB6 take-off.
All areas appear improved from previous exams. Some mildly heaped, non-obstructing granulation tissue was noted along the medial aspect of the RMS.

Right Upper Lobe (RUL): The previously seen area of full-thickness erosion/ulceration along the RUL anterior wall now appears {rul_status}.
This is greatly improved from 1 week ago.

Right Middle Lobe (RML): The take-off is narrowed but able to be traversed with the "regular" size disposable bronchoscope.

Right Lower Lobe (RLL): Basilar segments appear healthy. Moderate secretions were noted in the BI and RLL.

Left Mainstem (LMS): Anastomosis is intact with visible sutures and {lms_status}.

Left Upper Lobe (LUL): Evidence of continued healing with fibrin exudates and desired granulation tissue.
The underlying mediastinum/pulmonary artery is no longer visible along the medial aspect of the LUL.
This entire area continues to look improved from 1 week ago.

Left Lower Lobe (LLL): The Lingula take-off is narrowed but able to be traversed with the "regular" size disposable bronchoscope.
LLL bronchus and segments appear healthy.

Interventions:

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clear {secretion_load} from the trachea, right mainstem bronchus, right-sided stent, bronchus intermedius, right lower lobe bronchus, left mainstem bronchus, left upper lobe, and left lower lobe.
Residual secretions were suctioned to clear.

Bronchoalveolar Lavage (BAL): BAL was performed at the {bal_loc}.
{bal_in} cc of NS was instilled, with a return of {bal_out} cc.
The disposable bronchoscope was removed and the procedure completed. The patient tolerated the procedure well. There were no immediate complications.

SPECIMENS
BAL of {bal_loc} – Microbiology (Cultures/Viral/Fungal) 

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for airway evaluation, therapeutic aspiration, and stent removal.
Right Mainstem: Anastomosis dehiscence remains closed.
Right Upper Lobe: Prior full-thickness erosion/ulceration is now covered with fibrinous exudate/granulation tissue.

Plan:
Patient will remain in ICU.
Encourage ongoing aggressive secretion clearance practices.
Recommend bronchoscopic secretion clearance {plan_freq}, deferring to the transplant team's expertise.
Ongoing discussions with the transplant team regarding timing for the next IP bronchoscopy.
Replacement of stent remains possible if there are any signs of worsening at the RMS dehiscence site."""

prompt_styles = [
    # Style 1: Telegraphic / Checklist
    "Bronch report. Pt: {age}{gender_short}. Ref: {ref_md}. Dx: Lung Tx, dehiscence. RMS: {rms_status}. RUL: {rul_status}. Found {foreign_obj_short}. LMS: {lms_status}. BAL {bal_loc}. Plan: Scope {plan_freq}.",
    
    # Style 2: Dictation
    "Generate a procedure note for Dr. {attending}. Patient is a {age} year old {gender_long} status post lung transplant. We performed therapeutic aspiration and BAL of the {bal_loc}. Findings included healed RMS dehiscence and {lms_status} on the left. A {foreign_obj_short} was seen in the RMS.",
    
    # Style 3: Sloppy / Quick Handoff
    "{age}yo {gender_short} bronch. Check airway. RMS dehiscence looks {rms_status_short}. RUL improved. LMS {lms_status}. Cleared {secretion_load}. BAL {bal_loc} ({bal_in}/{bal_out}).",
    
    # Style 4: Structured Request
    "Procedure: Bronchoscopy with BAL ({bal_loc}) and Aspiration.\nPatient: {age} {gender_short}\nKey Findings: RMS anastomosis {rms_status}, {foreign_obj_short} present. RUL healing. LMS {lms_status}.\nPlan: clearance {plan_freq}.",
    
    # Style 5: Clinical Narrative
    "Please document the bronchoscopy for this {age}-year-old {gender_long} referred by {ref_md}. The RMS anastomosis {rms_status}. We noted a {foreign_obj_short}. RUL is {rul_status}. We washed the {bal_loc} with {bal_in}cc."
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        ref_md = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        fellow = random.choice(data_pool["fellow"])
        rn = random.choice(data_pool["rn_name"])
        rt = random.choice(data_pool["rt_name"])
        date = random.choice(data_pool["procedure_date"])
        
        # Clinical Variables
        rms_status = random.choice(data_pool["rms_dehiscence_status"])
        # Helper for short prompt
        rms_status_short = "healed" if "healed" in rms_status or "closed" in rms_status else "stable"
        
        foreign_obj = random.choice(data_pool["foreign_object"])
        foreign_obj_loc = random.choice(data_pool["foreign_object_action"])
        # Helper for short prompt (extract noun phrase roughly)
        foreign_obj_short = "hemoclip" if "hemoclip" in foreign_obj else "suture" if "suture" in foreign_obj else "stent wire"
        
        rul_status = random.choice(data_pool["rul_finding"])
        lms_status = random.choice(data_pool["lms_status"])
        
        secretion_load = random.choice(data_pool["secretion_load"])
        
        bal_loc = random.choice(data_pool["bal_location"])
        bal_vol_tup = random.choice(data_pool["bal_volumes"])
        bal_in = bal_vol_tup[0]
        bal_out = bal_vol_tup[1]
        
        plan_freq = random.choice(data_pool["plan_frequency"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            ref_md=ref_md,
            attending=attending,
            rms_status=rms_status,
            rms_status_short=rms_status_short,
            rul_status=rul_status,
            foreign_obj_short=foreign_obj_short,
            lms_status=lms_status,
            bal_loc=bal_loc,
            bal_in=bal_in,
            bal_out=bal_out,
            secretion_load=secretion_load,
            plan_freq=plan_freq
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date=date,
            ref_md=ref_md,
            age=age,
            gender_long=gender_long,
            lms_status=lms_status,
            attending=attending,
            fellow=fellow,
            rn=rn,
            rt=rt,
            rms_status=rms_status,
            foreign_obj=foreign_obj,
            foreign_obj_loc=foreign_obj_loc,
            rul_status=rul_status,
            secretion_load=secretion_load,
            bal_loc=bal_loc,
            bal_in=bal_in,
            bal_out=bal_out,
            plan_freq=plan_freq
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