import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_057"
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
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "indication": [
        "airway stenosis", 
        "malignant airway obstruction", 
        "granulation tissue obstruction", 
        "benign bronchial stenosis",
        "post-transplant airway complications"
    ],
    # Anatomy logic to ensure consistency between mainstem, lobes, and laterality
    "anatomy_config": [
        {
            "side_adj": "left",
            "side_cap": "Left",
            "mainstem": "left mainstem",
            "target_lobe": "left lower lobe",
            "target_abbr": "LLL",
            "other_lobe": "left upper lobe",
            "target_orifice": "left lower lobe orifice"
        },
        {
            "side_adj": "right",
            "side_cap": "Right",
            "mainstem": "bronchus intermedius",
            "target_lobe": "right lower lobe",
            "target_abbr": "RLL",
            "other_lobe": "right upper lobe",
            "target_orifice": "right lower lobe orifice"
        }
    ],
    "balloon_sets": [
        {
            "b1": "8/9/10", "b1_size": "10 mm", 
            "b2": "10/11/12", "b2_size": "12 mm"
        },
        {
            "b1": "10/11/12", "b1_size": "12 mm", 
            "b2": "12/13/15", "b2_size": "13.5 mm"
        },
        {
            "b1": "6/7/8", "b1_size": "8 mm", 
            "b2": "8/9/10", "b2_size": "10 mm"
        }
    ],
    "ablation_params": [
        {"time1": "three minutes", "kj1": "3.5", "temp1": "67", "time2": "one-minute", "kj2": "1.3", "temp2": "49"},
        {"time1": "two minutes", "kj1": "2.8", "temp1": "60", "time2": "30 seconds", "kj2": "0.9", "temp2": "42"},
        {"time1": "four minutes", "kj1": "4.2", "temp1": "75", "time2": "90 seconds", "kj2": "1.8", "temp2": "55"}
    ],
    "work_increase": [">90%", ">75%", ">50%", "double the standard"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE
Therapeutic aspiration (31646) 
Bronchoscopy with bronchial washing (31622) and BAL (31624) 
Transbronchial biopsy (TBBX), single lobe (31628) and additional lobes (31632) 
Navigational Bronchoscopy (computer assisted) (31627) 
Radiologic guidance for CT guided needle placement (CIOS) (77012) 
3D rendering with interpretation and reporting (ION Planning Station) (76377) 
Radial EBUS for peripheral lesion (31654) 
Balloon dilation (31630) 
Destruction of tumor OR relief of stenosis by any method other than excision (e.g., laser, cryotherapy, microwave) (31641) 
Foreign body removal (31635) 

Modifier 22 (Increased Procedural Services): This patient required extensive ablation and debulking with excision along the {mainstem} and {target_lobe}. This included multiple dilations and multiple episodes of excision between other therapeutic modalities. This resulted in {work_increase} increased work due to increased intensity, time, technical difficulty, and physical/mental effort required.

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Radial EBUS; Ion Robotic Bronchoscope; Disposable Bronchoscope; Microwave Ablation Catheter; Cios Spin System.

ESTIMATED BLOOD LOSS Moderate 
COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and location.

Initial Airway Inspection The airway was inspected. The trachea and right lung were intact and appropriate to the segmental level. The {mainstem} was inflamed and the {other_lobe} was visualized; however, the {target_lobe} was not visualized initially.

Robotic Navigational Bronchoscopy (Ion) — {target_lobe_cap} Target A CT chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target. The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform.

Navigation: Robotic navigation was performed with the Ion platform using partial registration. The Ion robotic catheter was used to engage the presumed orifice of the {target_lobe}. The target lesion was approximately 1 cm in diameter, and the catheter was advanced to 1.0 cm away from the planned target under navigational guidance.

Radial EBUS: Radial EBUS was performed to confirm lesion location; it was noted that the target was not well visualized, with soft tissue features noted.

Cone-Beam CT (Cios Spin): The Cios Spin system was used for evaluation of the target location. A low-dose spin was performed to acquire CT imaging. These images were passed to the Ion platform for reconstruction and nodule location. The 3D images were interpreted on an independent workstation.

Adjustment: Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location. The target airway was visualized, and targets were placed to ensure optimal trajectory of the tools to open the obstructed airway. I personally interpreted the cone beam CT and 3D reconstruction.

Specimen Collection
TBNA: Transbronchial needle aspiration was performed with a 19G needle through the extended working channel. Total 2 samples were collected and sent for Microbiology and Cytology.
Biopsy: Transbronchial biopsy was performed with the semiconductor precisor through the extended working channel. Total 2 samples were collected and sent for Microbiology and Pathology.
The robotic bronchoscope was advanced until the airway lumen was visualized with the vision probe. The catheter was then withdrawn, and the robotic bronchoscope was disconnected.

Therapeutic Bronchoscopy and Airway Recanalization The therapeutic bronchoscope was then used to clear the airway, and the {side_adj} lung was irrigated with saline.

Mechanical Debridement: Granulation tissue and inflamed tissue were excised using the precisor, pulmonary, and large forceps.

Balloon Dilation:
An {balloon1} Elation balloon was used to perform dilation to {balloon1_size} at the {target_orifice} (1 inflation, 60 seconds).
A {balloon2} Elation balloon was used to perform dilation to {balloon2_size} at the {target_orifice} (3 inflations, 60 seconds each).

Microwave Ablation: A 2.5 cm microwave catheter was used to ablate the inflamed tissue. Ablation was performed for {time1} ({kj1} KJ and {temp1}°C reached), followed by a pause for further extensive excision, and then a subsequent one-minute ablation ({kj2} KJ and {temp2}°C reached).

Airway Clearance: Serial irrigation with iced saline was performed alongside excision of granulation tissue and blood clot/foreign body.

Final Inspection Following these interventions, the {other_lobe} and the {target_lobe} were better visualized. The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
{target_lobe_cap} transbronchial needle aspiration, transbronchial forceps biopsies 
{mainstem_cap} and {target_lobe} biopsies 
{target_lobe_cap} bronchoalveolar lavage 

IMPRESSION / PLAN
{age}-year-old {gender_long} with {indication}, successfully treated with extensive debulking, dilation, and ablation.
Follow up CXR.
Follow up bronchoscopic lab work.
Plan for follow up bronchoscopy in ~1 week.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Op report: {age}{gender_short}, {indication}. Robotic bronch, EBUS, Cios used. Target {target_abbr}. Extensive debulking, ablation, balloon dilation ({balloon1_size}/{balloon2_size}). Mod 22 applies.",
    
    # Style 2: Dictation
    "Please write a procedure note for Dr. {doctor}. Patient is {age} yo {gender_long} with {indication}. We performed navigational bronchoscopy with Ion and Cios spin. The {target_lobe} was obstructed. We did extensive ablation and balloon dilation. No complications.",
    
    # Style 3: Sloppy / Quick
    "{age}F {indication} {target_abbr}. Ion robot, ablation {time1}, dilation. Mod 22 for complex debulking. specimen to path. ref {doctor}.",
    
    # Style 4: Billing Focus
    "Codes: 31627, 31628, 31630, 31641, 31646. Add modifier 22 for significant increased work ({work_increase}). Pt {age} {gender_short}. Procedure: Robotic bronch with ablation and dilation of {target_lobe}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedure: Ion Navigational Bronchoscopy + Therapeutic Debulking\nLocation: {target_lobe_cap}\nDetails: Microwave ablation, balloon dilation ({balloon1_size}, {balloon2_size}), extensive excision."
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
        indication = random.choice(data_pool["indication"])
        
        # Anatomy Logic
        anat = random.choice(data_pool["anatomy_config"])
        
        # Procedure Configs
        balloons = random.choice(data_pool["balloon_sets"])
        ablation = random.choice(data_pool["ablation_params"])
        work = random.choice(data_pool["work_increase"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=indication,
            target_abbr=anat["target_abbr"],
            target_lobe=anat["target_lobe"],
            target_lobe_cap=anat["target_lobe"].title(),
            balloon1_size=balloons["b1_size"],
            balloon2_size=balloons["b2_size"],
            time1=ablation["time1"],
            work_increase=work
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=indication,
            
            # Anatomy
            side_adj=anat["side_adj"],
            mainstem=anat["mainstem"],
            mainstem_cap=anat["mainstem"].title(),
            target_lobe=anat["target_lobe"],
            target_lobe_cap=anat["target_lobe"].title(),
            other_lobe=anat["other_lobe"],
            target_orifice=anat["target_orifice"],
            
            # Procedure Details
            balloon1=balloons["b1"],
            balloon1_size=balloons["b1_size"],
            balloon2=balloons["b2"],
            balloon2_size=balloons["b2_size"],
            
            # Ablation Details
            time1=ablation["time1"],
            kj1=ablation["kj1"],
            temp1=ablation["temp1"],
            time2=ablation["time2"], # Not used in prompt but needed for note
            kj2=ablation["kj2"],
            temp2=ablation["temp2"],
            
            work_increase=work
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