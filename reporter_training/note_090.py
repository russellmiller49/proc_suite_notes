import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_090"
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
    "age": ["45", "52", "57", "61", "64", "68", "73", "59", "55"],
    # Tuple: (Gender Full, Gender Short, Pronoun Subj, Pronoun Poss)
    "gender_tuple": [
        ("female", "F", "she", "her"), 
        ("male", "M", "he", "his")
    ],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Bowers", "Dr. Gupta"],
    "fellow": ["Dr. Lee", "Dr. Jacobs", "Dr. Miller", "Dr. X. Zhang"],
    "ref_physician": ["Dr. P. Jones", "Dr. L. White", "Dr. K. O'Malley"],
    
    # Clinical Variables specific to Airway Stenosis/Transplant
    "stenosis_severity": ["Severe", "Critical", "Moderate-to-severe", "High-grade"],
    "stenosis_mm_patent": ["2mm", "3mm", "4mm", "pinpoint"],
    "secretion_type": ["moderate, thin, and clear", "thick white", "copious mucoid", "scant serous"],
    "mucostasis_loc": ["RB4/RB5", "the medial segment", "the lateral segment", "distal airways"],
    
    # Procedure Variables
    "balloon_size_combo": ["6/7/8", "5/6/7", "8/9/10"],
    "balloon_max_mm": ["8", "7", "10"],
    "cryo_probe_size": ["1.7", "2.4", "1.1"],
    "cryo_duration": ["30", "45", "60"],
    
    # Outcome Variables
    "pre_patency": ["20%", "30%", "15%", "10%"],
    "post_patency": ["75%", "80%", "85%", "90%"],
    "stent_plan": ["8x20mm", "10x30mm", "10x40mm", "12x20mm"],
    "stent_type": ["custom silicone", "hybrid Y", "covered metal"],
    
    # Dates/Times (Generic placeholders)
    "follow_up_time": ["2 weeks", "3 weeks", "1 month", "10 days"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_md}

INDICATION FOR OPERATION {gender_subj} is a {age}-year-old {gender_long} who presents with bronchial stenosis.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy, balloon dilation, and cryotherapy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 
{severity} RML bronchial stenosis 

PROCEDURE
Therapeutic aspiration (initial episode) 
Diagnostic bronchoscopy with cell washing 
Bronchoalveolar lavage (BAL) 
Endobronchial Biopsy(s) 
Balloon dilation 
Bronchoscopy with excision of tumor 
Destruction of tumor or relief of stenosis (Cryotherapy) 

ATTENDING {attending}
ASSISTANT {fellow}
SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope; {balloon_combo} mm Elation balloon; {cryo_size} mm Cryoprobe; Alligator forceps.

ESTIMATED BLOOD LOSS Trivial 
COMPLICATIONS None 

PROCEDURE IN DETAIL A timeout was performed (confirming the patient's name, procedure type, and procedure location).
Sedation was initiated and an LMA was placed.

Initial Airway Inspection The Flexible Therapeutic Bronchoscope was advanced for airway examination.
Vocal Cords: Normal without mass/lesions; appropriate abduction (adduction not assessed due to paralysis).
Trachea: Mildly tortuous, otherwise normal.
Main Carina: Sharp.

Right Lung Proximal Airways: The right anastomosis site was intact with visible intact blue sutures; mild stenosis noted without dehiscence. The RUL and RB1-3 were normal to the segmental level.
The bronchus intermedius and distal airways were mildly rotated clockwise.
Right Middle Lobe (RML): The proximal take-off appeared normal, but {severity_lower} stenosis (~{patent_mm} patent) was noted starting halfway into the bronchus.
A second area of moderate stenosis (~5mm) was noted just before the take-off of RB4 and RB5.
The stenosis appeared circumferential due to fibrotic and granulation tissue, with a small patch of white debris overlying the area.
Right Lower Lobe (RLL): Able to enter truncus basalis with mild pressure; RB7 was compressed and fish-mouthed.
RB6 and RB8-10 showed normal anatomic branching.

Left Lung Proximal Airways: Left anastomosis intact with visible blue sutures and mild stenosis.
LUL, Lingula, and LLL showed normal branching to the segmental/subsegmental level.

Secretions: Moderate, thin, and clear secretions noted generally; {secretions} secretions (likely mucostasis) suctioned from {mucostasis_loc} after relief of stenosis.

Interventions

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clear mucus from the trachea, bilateral mainstems, RUL, bronchus intermedius, RML, RLL, LUL, and LLL.
Endobronchial Biopsy: A biopsy was performed at the white patch of tissue in the RML bronchus; the lesion was successfully removed and sent for tissue culture.
Cryotherapy & Debridement (RML): Endobronchial obstruction at the RML bronchus was treated to relieve stenosis.
Cryotherapy: Overlapping treatments ({cryo_time} seconds each) were performed using a {cryo_size}mm cryoprobe on the circumferential stenosis in the middle and distal RML bronchus, leading to softening of fibrotic and granulation tissue.
Excision: Tissue debris causing obstruction was excised via mechanical debridement using bland alligator forceps.
Balloon Dilation (RML): Balloon dilation was performed using a {balloon_combo} Elation balloon with the following sequence:

RML Bronchus: Dilated to {balloon_max} mm (60 seconds).
RML Bronchus: Dilated to {balloon_max} mm (60 seconds).
RML Bronchus: Dilated to {balloon_max} mm (60 seconds).
RML Medial Segment: Dilated to 6 mm (60 seconds).
RML Lateral Segment: Dilated to 6 mm (60 seconds).

Final Assessment & Lavage Despite multiple dilations, the RML bronchus continued to mildly narrow, particularly at the distal end.
The therapeutic bronchoscope could not traverse the entire length of the RML bronchus.
A hybrid bronchoscope was advanced, confirming patency of RB4 and RB5 to their respective subsegments.
Patency: Improved from {pre_pat}% pre-treatment to {post_pat}% post-treatment.

Hemostasis: Trivial bleeding was controlled with suction and saline.
BAL: Performed at the Lateral (RB4) and Medial (RB5) segments of the RML.
Instilled 60 cc NS, returned 20 cc NS.

Conclusion The patient tolerated the procedure well with no immediate complications.
The LMA was removed in the OR and the patient was transported to recovery in stable condition.

SPECIMENS
RML Endobronchial Biopsy (EBBx): Culture 
RML BAL: Cell count, Microbiology (Cultures/Viral/Fungal), Cytology 

IMPRESSION / PLAN [REDACTED] is a {age}-year-old {gender_long} with bronchial stenosis who underwent bronchoscopy for balloon dilation, cryotherapy, and airway clearance.
Follow-up: Repeat bronchoscopy in {fup_time} for airway evaluation, dilation, and possible stent placement.
Stent Consideration: Will review with IP providers regarding {stent_plan} stent vs. {stent_type} stent placement.
Results: Will request lung transplant team follow-up on EBBx culture and BAL results.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "IP report. {age}{gender_short}, ref {ref_md}. {severity} RML stenosis ({patent_mm}). Tx: Balloon {balloon_combo}, Cryo {cryo_size}mm. Patency {pre_pat}->{post_pat}. Plan: {stent_plan} stent check in {fup_time}.",
    
    # Style 2: Dictation
    "Please generate an operative note for Dr. {attending}. Patient is a {age} year old {gender_long} with {severity_lower} RML stenosis seen on bronchoscopy. We used a {balloon_combo} CRE balloon and cryotherapy. Secretions were {secretions}. Resulting patency improved from {pre_pat} to {post_pat}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch /w {attending}. RML stenosis {patent_mm} patent. dilated w/ {balloon_max}mm balloon x3. cryo debridement. secretions: {secretions}. plan f/u {fup_time} for possible {stent_plan} stent.",
    
    # Style 4: Billing Focus
    "Procedure: Bronchoscopy, BAL, EBBx, Balloon Dilation, Cryotherapy. Dx: J98.09. Pt: {age} {gender_short}. Findings: {severity} RML stenosis. Balloon sizes: {balloon_combo}. Cryo used. Imprv to {post_pat}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nAttending: {attending}\nDiagnosis: {severity} RML Stenosis\nInterventions: \n- Cryo ({cryo_size}mm probe)\n- Balloon ({balloon_combo})\n- BAL/Biopsy\nOutcome: Patency {post_pat} (from {pre_pat})."
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
        fellow = random.choice(data_pool["fellow"])
        ref_md = random.choice(data_pool["ref_physician"])
        
        severity = random.choice(data_pool["stenosis_severity"])
        patent_mm = random.choice(data_pool["stenosis_mm_patent"])
        secretions = random.choice(data_pool["secretion_type"])
        mucostasis_loc = random.choice(data_pool["mucostasis_loc"])
        
        balloon_combo = random.choice(data_pool["balloon_size_combo"])
        balloon_max = random.choice(data_pool["balloon_max_mm"])
        cryo_size = random.choice(data_pool["cryo_probe_size"])
        cryo_time = random.choice(data_pool["cryo_duration"])
        
        pre_pat = random.choice(data_pool["pre_patency"])
        post_pat = random.choice(data_pool["post_patency"])
        stent_plan = random.choice(data_pool["stent_plan"])
        stent_type = random.choice(data_pool["stent_type"])
        fup_time = random.choice(data_pool["follow_up_time"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            attending=attending,
            ref_md=ref_md,
            severity=severity,
            severity_lower=severity.lower(),
            patent_mm=patent_mm,
            balloon_combo=balloon_combo,
            balloon_max=balloon_max,
            cryo_size=cryo_size,
            pre_pat=pre_pat,
            post_pat=post_pat,
            stent_plan=stent_plan,
            secretions=secretions,
            fup_time=fup_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_subj=gender_tup[2].capitalize(), # He/She
            gender_long=gender_tup[0],
            ref_md=ref_md,
            severity=severity,
            severity_lower=severity.lower(),
            attending=attending,
            fellow=fellow,
            balloon_combo=balloon_combo,
            balloon_max=balloon_max,
            cryo_size=cryo_size,
            cryo_time=cryo_time,
            patent_mm=patent_mm,
            secretions=secretions,
            mucostasis_loc=mucostasis_loc,
            pre_pat=pre_pat,
            post_pat=post_pat,
            fup_time=fup_time,
            stent_plan=stent_plan,
            stent_type=stent_type
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