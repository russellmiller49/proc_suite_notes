import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_082" 
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
    "age": ["55", "62", "65", "68", "71", "74", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Rossi"],
    "indication": [
        "airway stenosis", 
        "obstructive airway disease", 
        "malignant airway obstruction",
        "post-intubation stenosis"
    ],
    # Logic: (Lobe Name, Mainstem Side, Bronchus Name)
    "location_tuple": [
        ("left lower lobe", "left mainstem", "left lower lobe orifice"),
        ("right lower lobe", "right mainstem", "right lower lobe orifice"),
        ("left upper lobe", "left mainstem", "left upper lobe orifice"),
    ],
    "lesion_size": ["0.8", "1.0", "1.2", "1.5", "2.0"],
    "balloon_1": [
        ("8/9/10", "10 mm"),
        ("6/7/8", "8 mm")
    ],
    "balloon_2": [
        ("10/11/12", "12 mm"),
        ("12/13.5/15", "15 mm")
    ],
    "ablation_params": [
        ("3.5KJ", "67 degrees", "1.3 KJ", "49 degrees"),
        ("4.0KJ", "75 degrees", "1.5 KJ", "55 degrees"),
        ("3.0KJ", "60 degrees", "1.0 KJ", "45 degrees")
    ],
    "anesthesia": ["General Anesthesia", "General with LMA", "General ETT"],
    "blood_loss": ["Minimal", "Moderate", "Less than 10ml", "Less than 50ml"],
    "complications": ["None", "None immediate", "None. Patient stable."],
    "follow_up": ["1 week", "2 weeks", "5 days", "10 days"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Derived from note_082.txt
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]
CC Referred Physician: {doctor}

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified.

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified.

PROCEDURE
Therapeutic aspiration
Bronchial washing and Bronchoalveolar lavage (BAL)
Transbronchial biopsy (TBBX) single and additional lobes
Navigational Bronchoscopy (computer assisted)
Radiologic guidance for CT guided needle placement (CIOS)
3D rendering with interpretation (ION Planning Station)
Radial EBUS for peripheral lesion
Balloon dilation
Destruction of tumor OR relief of stenosis (Microwave Ablation)
Foreign body removal

ANESTHESIA {anesthesia}.

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope.

ESTIMATED BLOOD LOSS {blood_loss}.
COMPLICATIONS {complications}.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection
The airway was inspected; the trachea and contralateral lung were intact and appropriate to the segmental level.
The {mainstem_side} was inflamed and the upper lobe was visualized.
The {target_lobe} was not visualized.

Robotic Navigational Bronchoscopy (Ion)
A CT Chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target. The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform. Robotic navigation bronchoscopy was performed with the Ion platform using partial registration.
The Ion robotic catheter was used to engage the presumed {target_lobe} orifice.
The target lesion was approximately {lesion_size} cm in diameter; under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.

Localization and Imaging (rEBUS & Cone Beam CT)
Radial EBUS was performed; the target location was not well visualized, noting soft tissue features.
Cone Beam CT (Cios Spin) was used for evaluation of target location, performing a low dose spin to acquire CT imaging. I personally interpreted the cone beam CT and 3-D reconstruction.
3D reconstructions were performed on an independent workstation and passed to the Ion platform for nodule location.
Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.
The target airway was visualized and targets were placed to ensure optimal trajectory of the tools to open the obstructed airway.

Target Sampling
TBNA: Transbronchial needle aspiration was performed with a 19G needle through the extended working channel catheter; total 2 samples were collected and sent for Microbiology and Cytology.
Biopsy: Transbronchial biopsy was performed with the precisor through the extended working channel catheter; total 2 samples were collected and sent for Microbiology and Pathology.
The robotic bronchoscope was advanced until the airway lumen was visualized, then the catheter was withdrawn and the robotic bronchoscope disconnected.

Therapeutic Interventions
The therapeutic bronchoscope was used to clear the airway and the lung was irrigated with saline.
Excision/Debulking: Granulation tissue and inflamed tissue were excised with the precisor, pulmonary, and large forceps.

Balloon Dilation:
Performed at the {target_bronchus} using an {b1_type} Elation balloon dilated to {b1_size} (1 inflation, 60 seconds).
Performed again at the {target_bronchus} using a {b2_type} Elation balloon dilated to {b2_size} (3 inflations, 60 seconds each).

Irrigation/Removal: Serial irrigation with iced saline was performed with excision of granulation tissue and blood clot/foreign body.

Ablation:
The 2.5 cm microwave catheter was used to ablate the inflamed tissue for three minutes ({abl_kj1} and {abl_temp1} Celsius reached), followed by a pause for further extensive excision, and then one minute ({abl_kj2} and {abl_temp2} Celsius reached).

Procedural Complexity Note
This patient required extensive ablation and debulking with excision along the {mainstem_side} and {target_lobe} with multiple dilations and multiple episodes of excision between other therapeutic modalities.
This resulted in >90% increased work due to increased intensity, time, technical difficulty, and physical/mental effort required.

Final Inspection
The upper lobe and the {target_lobe} were better visualized. The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)
{target_lobe} transbronchial needle aspiration, transbronchial forceps biopsies
{mainstem_side} and {target_lobe} biopsies
{target_lobe} bronchoalveolar lavage

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for {indication}.
Follow up CXR.
Follow up bronchoscopic lab work.
Plan for follow up bronchoscopy in ~{follow_up}.
"""

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================

prompt_styles = [
    # Style 1: Telegraphic
    "Gen Anesthesia IP Bronchoscopy. Pt {age}{gender_short}, ref {doctor}. Dx: {indication}, {target_lobe} obstruction. Performed Ion Nav, rEBUS, Cone Beam. Balloon dilation ({b1_type}, {b2_type}) + Microwave ablation ({abl_kj1}/{abl_kj2}). Complex debulking >90% extra work. Plan f/u {follow_up}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} referred by {doctor}. Procedure: Robotic bronchoscopy with Ion, CIOS spin, EBUS. Indication is {indication} with stenosis in the {target_lobe}. Interventions: Balloon dilation to {b2_size}, microwave ablation, and extensive debulking. Complexity statement required.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {indication}. Did robotic bronch w/ EBUS and cone beam CT. Found {lesion_size}cm lesion. {target_lobe} blocked. Used balloons {b1_type} and {b2_type} and microwave ablation to open it up. Big mess, lots of debulking >90% effort. No complications.",
    
    # Style 4: Billing Focus
    "Post-op diagnosis J98.09. Procedures: Therapeutic aspiration, BAL, TBBX, Navigational Bronch (Ion), 3D rendering, CT guidance, EBUS, Balloon Dilation, Microwave Ablation. Pt {age} {gender_short}. Target: {target_lobe}. Complexity modifier >90%.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nReferring: {doctor}\nDiagnosis: {indication}\nTarget: {target_lobe} ({lesion_size} cm)\nTools: Ion Robot, Cios Spin, rEBUS, Elation Balloons ({b2_size}), Microwave Ablation\nNotes: Extensive debulking required."
]

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        doctor = random.choice(data_pool["doctor"])
        indication = random.choice(data_pool["indication"])
        
        # Location logic
        loc_tup = random.choice(data_pool["location_tuple"])
        target_lobe = loc_tup[0]
        mainstem_side = loc_tup[1]
        target_bronchus = loc_tup[2]
        
        lesion_size = random.choice(data_pool["lesion_size"])
        
        # Equipment logic
        b1 = random.choice(data_pool["balloon_1"])
        b2 = random.choice(data_pool["balloon_2"])
        abl = random.choice(data_pool["ablation_params"])
        
        anesthesia = random.choice(data_pool["anesthesia"])
        blood_loss = random.choice(data_pool["blood_loss"])
        complications = random.choice(data_pool["complications"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            indication=indication,
            target_lobe=target_lobe,
            lesion_size=lesion_size,
            b1_type=b1[0], b1_size=b1[1],
            b2_type=b2[0], b2_size=b2[1],
            abl_kj1=abl[0], abl_kj2=abl[2],
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            indication=indication,
            mainstem_side=mainstem_side,
            target_lobe=target_lobe,
            target_bronchus=target_bronchus,
            lesion_size=lesion_size,
            b1_type=b1[0], b1_size=b1[1],
            b2_type=b2[0], b2_size=b2[1],
            abl_kj1=abl[0], abl_temp1=abl[1],
            abl_kj2=abl[2], abl_temp2=abl[3],
            anesthesia=anesthesia,
            blood_loss=blood_loss,
            complications=complications,
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