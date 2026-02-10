import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_092"
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
    "age": [str(x) for x in range(45, 85)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Williams", "Patel"],
    "diagnosis_code": ["J98.09", "J95.5", "J39.8"],
    "indication": [
        "airway stenosis", 
        "granulation tissue formation", 
        "stent migration", 
        "recurrent obstruction"
    ],
    "location": [
        "Right Middle Lobe (RML)", 
        "Right Lower Lobe (RLL)", 
        "Left Upper Lobe (LUL)", 
        "Left Lower Lobe (LLL)", 
        "Bronchus Intermedius"
    ],
    # Maps the location description to a shorter anatomy code for the narrative
    "location_map": {
        "Right Middle Lobe (RML)": ("RML", "proximal RML bronchus"),
        "Right Lower Lobe (RLL)": ("RLL", "proximal RLL bronchus"),
        "Left Upper Lobe (LUL)": ("LUL", "proximal LUL bronchus"),
        "Left Lower Lobe (LLL)": ("LLL", "proximal LLL bronchus"),
        "Bronchus Intermedius": ("BI", "distal Bronchus Intermedius")
    },
    "stent_type": ["iCAST", "Atrium", "Aero", "Covered Ultraflex"],
    "stent_dims": ["7mm x 16mm", "6mm x 20mm", "8mm x 20mm", "7mm x 22mm"],
    "pre_patent": ["50%", "60%", "70%", "75%"],
    "post_patent": ["90%", "95%", "100%"],
    "cryo_apps": ["3", "4", "5", "6"],
    "balloon_type": ["Elation", "CRE", "Hurricane"],
    "balloon_size": ["8/9/10", "10/11/12", "6/7/8"],
    "target_dilation": ["8 mm", "10 mm", "12 mm"],
    "meds_hemostasis": [
        "epinephrine 0.2mg, and tranexamic acid 200mg",
        "epinephrine 1:10000 and cold saline",
        "topical thrombin and cold saline",
        "tranexamic acid 500mg and epinephrine 0.5mg"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors the structure of note_092.txt
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: Monday, February 9, 2026

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate. The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{dx_code} Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
{dx_code} Other diseases of bronchus, not elsewhere classified

PROCEDURE
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing
31624 Dx bronchoscope/lavage (BAL)
31630 Balloon dilation
31640 Bronchoscopy with excision
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
31899NFD BRONCHOSCOPY W/ APPLICATION OF TRANEXAMIC ACID
31635 Foreign body removal
Modifier 22 (Unusual Procedural Services): Substantially greater work than normal (i.e., increased intensity, time, technical difficulty). This patient required multiple ({cryo_count}) separate applications of spray cryotherapy and required multiple forms of bronchoscopy (flexible and rigid) in order to adequately treat the patient. This resulted in >50% increased work due to time, technical difficulty, and physical/mental effort.

ATTENDING
[REDACTED] (Ref: Dr. {doctor})

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Rigid Bronchoscope; Flexible Therapeutic Bronchoscope.

ESTIMATED BLOOD LOSS
Minimum

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Flexible Bronchoscopy & Stent Removal
The flexible therapeutic bronchoscope was advanced through the Laryngeal Mask Airway (LMA), which was in good position.

Airway Inspection: The vocal cords were normal without mass/lesions. The anterior trachea showed a well-healed tracheostomy site but was otherwise normal. The main carina was sharp.

Right Lung: Anastomosis sutures were intact.
{lung_exam_text}

Left Lung: Normal anatomic branching and no endobronchial pathology.

Secretions: Minimal, thin, and clear.
Successful therapeutic aspiration was performed to clear mucus from the distal trachea, bilateral mainstems, and lobar carinas.

During initial gentle suctioning/therapeutic aspiration at the {loc_short}, the {stent_name} {stent_dims} stent became dislodged and completely extruded from the {loc_short} into the central airway.

Foreign Body Removal: The stent was grasped with pulmonary forceps and removed en bloc with the therapeutic bronchoscope.

Hemostasis: Oozing blood from the distal {loc_short} bronchus was noted after dislodgement. Bleeding was easily controlled with endobronchial cold saline, {meds}.

Rigid Bronchoscopy & Intervention
After induction of muscle relaxants, the LMA was removed and a tooth protector placed. The black bronchoscope ventilating rigid barrel was introduced and advanced to the mid-trachea; jet ventilation was initiated. The barrel was positioned into the proximal mainstem bronchus.

The area of stenosis at the {loc_long_desc} was treated with the following modalities:

Mechanical Debridement: Pulmonary alligator forceps were used for good granulation tissue removal from the distal {loc_short} bronchus.

Cryospray: A cryotherapy catheter was used (low-flow) for {cryo_count} applications of 10 seconds each, providing excellent application to the {loc_context} and around the take-off.

Balloon Dilation: An {balloon_size} {balloon_type} balloon was used to dilate the target airway to {target_dilation}. Two total inflations were performed with a dilation time of 60 seconds each.

Results: Prior to treatment, the affected airway was {pre_patent} patent; after treatment, it was {post_patent} patent. The {loc_short} was widely patent with patent segmental airways following extraction, excision, and dilation. The decision was made not to place another stent at this time to allow for a "stent vacation" to break the chain of bacterial colonization and observe tissue response to cryospray.

Final Flexible Bronchoscopy
The rigid bronchoscope was extubated and the LMA was replaced by the anesthesia team. The flexible therapeutic bronchoscope was advanced.

Bronchoalveolar Lavage (BAL): Performed at the {loc_short}. 40 cc of NS was instilled with a return of 20 cc. Samples were sent for Cell Count, Microbiology, and Cytology.

The patient tolerated the procedure well with no immediate complications. The patient was extubated in the operating room and transported to recovery in stable condition.

SPECIMENS
{loc_short} stent (pathology)
{loc_short} BAL (cell count, microbiology, cytology)

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for evaluation of {indication}. Patient underwent bronchoscopy with stent removal, application of spray cryotherapy, and balloon dilation without immediate complication.

Post-procedure CXR.
Follow-up BAL results.
Follow-up in outpatient Interventional Pulmonology clinic as scheduled.
Repeat bronchoscopy in 2-3 weeks to monitor airway closely.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Pt {age} {gender_short}. Indication: {indication}. Procedure: Flex & Rigid bronch, stent removal ({stent_name}), cryo ({cryo_count} apps), balloon dilation ({balloon_type}). Site: {loc_full}. Stent dislodged during suction, removed. Treated stenosis ({pre_patent}->{post_patent}). Plan: Stent vacation.",

    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} patient of Dr. {doctor}. Diagnosis {dx_code}. We performed a therapeutic bronchoscopy. The {stent_name} stent in the {loc_full} was removed after it migrated. We treated the granulation with {cryo_count} rounds of cryospray and dilated with a {balloon_size} balloon to {target_dilation}. Improved patency from {pre_patent} to {post_patent}.",

    # Style 3: Sloppy / Quick Note
    "{age}yo {gender_short} with {indication}. {loc_short} stent removal ({stent_dims}). Used rigid bronch. Cryo spray x{cryo_count}, balloon {target_dilation}. Stent came out during suction. Good hemostasis with {meds_short}. No new stent placed.",

    # Style 4: Billing Focus
    "Codes: 31645, 31630, 31635, 31641 (Mod 22). Dx: {dx_code}. Procedure involved complex stent removal from {loc_short} and stenosis mgmt. Used rigid scope, cryo ({cryo_count}x), and balloon dilation. {age}M/F. Stent vacation initiated.",

    # Style 5: Structured Request
    "Generate Procedure Note:\nPatient: {age} {gender_short}\nIndication: {indication}\nSite: {loc_full}\nInterventions: Stent removal ({stent_name}), Cryo ({cryo_count} applications), Balloon Dilation ({balloon_size})\nOutcome: {pre_patent} to {post_patent} patency."
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
        dx_code = random.choice(data_pool["diagnosis_code"])
        indication = random.choice(data_pool["indication"])
        
        # Location Logic
        loc_full = random.choice(data_pool["location"])
        loc_short, loc_context = data_pool["location_map"][loc_full]
        
        # Contextual text for lung exam based on location
        if "Right" in loc_full:
            lung_exam_text = f"The {loc_short} had a stent in place. Normal anatomic branching elsewhere."
        else:
            lung_exam_text = f"Right lung clear. The {loc_short} had a stent in place."

        stent_name = random.choice(data_pool["stent_type"])
        stent_dims = random.choice(data_pool["stent_dims"])
        
        pre_patent = random.choice(data_pool["pre_patent"])
        post_patent = random.choice(data_pool["post_patent"])
        
        cryo_count = random.choice(data_pool["cryo_apps"])
        
        balloon_type = random.choice(data_pool["balloon_type"])
        balloon_size = random.choice(data_pool["balloon_size"])
        target_dilation = random.choice(data_pool["target_dilation"])
        
        meds = random.choice(data_pool["meds_hemostasis"])
        meds_short = "Epi/TXA" if "tranexamic" in meds else "Cold Saline"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=indication,
            dx_code=dx_code,
            loc_full=loc_full,
            loc_short=loc_short,
            stent_name=stent_name,
            stent_dims=stent_dims,
            cryo_count=cryo_count,
            balloon_type=balloon_type,
            balloon_size=balloon_size,
            target_dilation=target_dilation,
            pre_patent=pre_patent,
            post_patent=post_patent,
            meds_short=meds_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            dx_code=dx_code,
            doctor=doctor,
            cryo_count=cryo_count,
            lung_exam_text=lung_exam_text,
            loc_short=loc_short,
            loc_long_desc=loc_full,
            loc_context=loc_context,
            stent_name=stent_name,
            stent_dims=stent_dims,
            meds=meds,
            balloon_size=balloon_size,
            balloon_type=balloon_type,
            target_dilation=target_dilation,
            pre_patent=pre_patent,
            post_patent=post_patent
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