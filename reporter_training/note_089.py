import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_089" 
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
    "age": ["34", "45", "52", "57", "58", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "referring_doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Self-referral", "Dr. Jones", "Dr. Doe"],
    "attending": ["Dr. Anderson", "Dr. Roberts", "Dr. Kim", "Dr. Patel"],
    "fellow": ["Dr. Lee", "Dr. White", "Dr. Garcia", "Dr. Nguyen"],
    "rn": ["Sarah", "Mike", "Jessica", "David", "Emily"],
    "rt": ["Tom", "Lisa", "John", "Rachel"],
    
    # Anatomical Locations with Abbreviation
    "anatomy_tuple": [
        ("Right middle lobe", "RML"),
        ("Right upper lobe", "RUL"),
        ("Left lower lobe", "LLL"),
        ("Left mainstem", "LMS"),
        ("Bronchus intermedius", "BI"),
        ("Right lower lobe", "RLL")
    ],
    
    # Initial Stenosis Severity
    "initial_patency": ["10%", "5%", "pinpoint", "completely obstructed", "20%"],
    
    # Final Result
    "final_patency": ["100%", "95%", "90%", "widely patent"],
    
    # Balloon Details
    "balloon_type": ["Elation", "CRE", "Blue Rhino"],
    "balloon_size_tuple": [("6/7/8", "8 mm"), ("8/9/10", "10 mm"), ("10/11/12", "12 mm"), ("12/13/15", "13 mm")],
    "inflation_count": ["2", "3", "4"],
    "inflation_time": ["30 seconds", "45 seconds", "60 seconds"],
    
    # Modality (Tool / Action / CPT logic is usually same for destruction)
    "modality_tuple": [
        ("Electrocautery", "knife", "radial cuts", "endoI 4, 4, 1"),
        ("Argon Plasma Coagulation", "probe", "cauterization", "30W"),
        ("Laser", "fiber", "resection", "15W"),
        ("Cryotherapy", "probe", "freeze-thaw cycles", "n/a")
    ],
    
    "follow_up": ["2 weeks", "3 weeks", "1 month", "6 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Note Template
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring_doctor}

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with airway narrowing.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure. The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified
{anatomy_full} bronchial stenosis

PROCEDURE
Therapeutic aspiration (initial episode) (CPT 31645)
Destruction of tumor OR relief of stenosis by any method other than excision (e.g. laser therapy, cryotherapy) (CPT 31641)
Balloon dilation of {anatomy_full} orifice

ATTENDING {attending}
ASSISTANT {fellow}
SUPPORT STAFF RN: {rn} RT: {rt}

ANESTHESIA General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; {modality_tool} ({modality_subtool}); {balloon_type} balloon ({balloon_dims}).

ESTIMATED BLOOD LOSS None
COMPLICATIONS None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position [Supine]

Initial Airway Inspection
{anatomy_full} orifice was significantly narrowed. Prior to treatment, the affected airway was noted to be {initial_patency} patent.

Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out the proximal airways from mucus.

{anatomy_full} Intervention
Endobronchial obstruction at the {anatomy_abbr} orifice was treated with the following modalities:

{modality_name}: Using {modality_tool} {modality_subtool} (setting {modality_setting}), {modality_action} were made for a duration of 4 seconds.

Balloon Dilation: A {balloon_dims} {balloon_type} balloon was used to perform dilation to {balloon_target} at the {anatomy_full} orifice. Total of {inflation_count} inflations were performed with a dilation time of {inflation_time} each.

Results
After treatment, the airway was {final_patency} patent.

Conclusion
The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
None

IMPRESSION / PLAN
{age}-year-old {gender_long} who presented for bronchoscopy for airway narrowing.
Significant {anatomy_abbr} stenosis treated with {modality_name} {modality_action} and balloon dilation; airway patency improved from {initial_patency} to {final_patency}.

Next Step: {follow_up} follow-up bronchoscopy (order placed with level 2)."""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Ref {referring_doctor}. {age}yo {gender_short}. Dx J98.09 {anatomy_full} stenosis. Init patency {initial_patency}. Tx: {modality_name}, Balloon ({balloon_dims} to {balloon_target}, x{inflation_count}). Post-op {final_patency}. F/u {follow_up}.",
    
    # Style 2: Dictation
    "Write an IP op report for a {age} year old {gender_long} referred by {referring_doctor}. Patient had severe {anatomy_abbr} stenosis, about {initial_patency} open. We used {modality_name} ({modality_subtool}) and a {balloon_dims} {balloon_type} balloon to dilate to {balloon_target}. The airway ended up {final_patency}. Plan for f/u in {follow_up}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short}, {anatomy_abbr} stenosis. {initial_patency} -> {final_patency}. Used {modality_name} and {balloon_type} balloon ({balloon_dims} x {inflation_count}). {attending} / {fellow}. {follow_up} return.",
    
    # Style 4: Billing Focus
    "Codes 31645, 31641. Dx J98.09 ({anatomy_full} stenosis). {age}/{gender_short}. Procedures: Therapeutic aspiration, {modality_name}, Balloon dilation ({balloon_dims}). Patency improved {initial_patency} to {final_patency}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: Airway narrowing ({anatomy_abbr})\nFindings: {initial_patency} patency\nIntervention: {modality_name} + Balloon ({balloon_dims} -> {balloon_target})\nResult: {final_patency} patency\nPlan: {follow_up} bronch"
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
        attending = random.choice(data_pool["attending"])
        fellow = random.choice(data_pool["fellow"])
        rn = random.choice(data_pool["rn"])
        rt = random.choice(data_pool["rt"])
        
        # Anatomy logic
        anat_tup = random.choice(data_pool["anatomy_tuple"])
        anatomy_full = anat_tup[0]
        anatomy_abbr = anat_tup[1]
        
        initial_patency = random.choice(data_pool["initial_patency"])
        final_patency = random.choice(data_pool["final_patency"])
        
        # Balloon logic
        balloon_type = random.choice(data_pool["balloon_type"])
        balloon_size_tup = random.choice(data_pool["balloon_size_tuple"])
        balloon_dims = balloon_size_tup[0]
        balloon_target = balloon_size_tup[1]
        inflation_count = random.choice(data_pool["inflation_count"])
        inflation_time = random.choice(data_pool["inflation_time"])
        
        # Modality logic
        mod_tup = random.choice(data_pool["modality_tuple"])
        modality_name = mod_tup[0]
        modality_tool = mod_tup[0] if mod_tup[1] == "probe" else "Electrocautery" # slight adjustment for formatting
        modality_subtool = mod_tup[1]
        modality_action = mod_tup[2]
        modality_setting = mod_tup[3]
        
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            referring_doctor=referring_doctor, attending=attending, fellow=fellow,
            anatomy_full=anatomy_full, anatomy_abbr=anatomy_abbr,
            initial_patency=initial_patency, final_patency=final_patency,
            modality_name=modality_name, modality_subtool=modality_subtool, modality_action=modality_action,
            balloon_type=balloon_type, balloon_dims=balloon_dims, balloon_target=balloon_target,
            inflation_count=inflation_count, follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            referring_doctor=referring_doctor,
            anatomy_full=anatomy_full, anatomy_abbr=anatomy_abbr,
            attending=attending, fellow=fellow, rn=rn, rt=rt,
            modality_name=modality_name, modality_tool=modality_tool,
            modality_subtool=modality_subtool, modality_setting=modality_setting, modality_action=modality_action,
            balloon_type=balloon_type, balloon_dims=balloon_dims, balloon_target=balloon_target,
            inflation_count=inflation_count, inflation_time=inflation_time,
            initial_patency=initial_patency, final_patency=final_patency,
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