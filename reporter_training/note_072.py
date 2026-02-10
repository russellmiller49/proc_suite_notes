import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_072"
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
    "age": ["34", "39", "45", "49", "52", "58", "61", "64", "70"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Sarkissian"],
    
    # Diagnosis and Locations
    "diagnosis_full": ["Recurrent Respiratory Papillomatosis (RPP)", "Tracheal Papillomatosis", "Laryngeal Papillomatosis"],
    "papilloma_location": [
        "anterior commissure of the larynx and right vocal cord",
        "posterior commissure and left true vocal cord",
        "subglottic space extending to the proximal trachea",
        "bilateral vocal cords and anterior commissure",
        "right vocal cord and subglottic shelf"
    ],
    
    # Trachea Findings
    "trachea_appearance": [
        "spiraling tissue creating a focal area of mild stenosis",
        "circumferential tissue causing moderate narrowing",
        "exophytic growth causing focal obstruction",
        "irregular sessile tissue narrowing the lumen"
    ],
    "stenosis_mild_pct": ["20%", "25%", "30%", "15%"],
    
    # Treatment Modalities
    "tools_used": [
        "cryospray, electro-cautery (PreciSect/softcoag), and mechanical debulking",
        "argon plasma coagulation (APC), cryotherapy, and forceps debridement",
        "laser ablation, balloon dilation, and mechanical coring"
    ],
    
    # Rigid Dilation Details
    "dilation_size": ["10 mm", "11 mm", "12 mm", "13 mm", "14 mm"],
    "dilation_location": ["Trachea (Proximal 1/3)", "Subglottic Airway", "Mid-Trachea"],
    "dilation_duration": ["300", "180", "240", "120"],
    "num_inflations": ["2", "3", "1"],
    
    # Patency Stats
    "pre_patency": ["40%", "30%", "50%", "35%"],
    "post_patency": ["90%", "95%", "85%", "100%"],
    
    # Plan
    "follow_up": ["4-6 weeks", "6-8 weeks", "2-3 months", "3-4 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_072.txt
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old adult who presents with {diagnosis_full}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

1899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS) 

31645 Therapeutic aspiration initial episode 

31625 Endobronchial Biopsy(s) 

31630 Balloon dilation 

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

CODE MODIFIERS Unusual Procedure (22 MODIFIER): This patient required multiple forms of ablative therapy (soft coag and cryotherapy) to multiple different structures, including glottis, infraglottis, subglottis, and tracheal structures.
This resulted in >50% increased work due to Time, Technical difficulty of procedure, Severity of patient's condition, and Physical and mental effort required.
Apply to: 31641 Destruction of tumor OR relief of stenosis by any method other than excision.
ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Rigid Tracheoscope; Flexible Therapeutic Bronchoscope.

ESTIMATED BLOOD LOSS Trivial 

COMPLICATIONS None 

PROCEDURE IN DETAIL A timeout was performed (confirming the patient's name, procedure type, and procedure location).
Sedation was initiated and an LMA was placed.

Flexible Bronchoscopy & Airway Inspection The Flexible Therapeutic Bronchoscope was advanced for airway examination.
Endobronchial topical lidocaine was applied to the vocal cords and larynx.


Larynx/Vocal Cords: Vocal cords demonstrated appropriate adduction/abduction.
A large patch of papillomas was noted at the {papilloma_location}.
Trachea: The proximal trachea showed a focal area of {trachea_appearance} (about {stenosis_mild_pct} stenosis prior to treatment).
The therapeutic bronchoscope was able to easily traverse the area of mild stenosis without issue.
Right Lung: Assessment of right airways revealed normal anatomic branching to the first subsegmental level.
There was no evidence of mass, lesions, bleeding, or other endobronchial pathology.
Left Lung: Assessment of left airways revealed normal anatomic branching to the first subsegmental level.
There was no evidence of mass, lesions, bleeding, or other endobronchial pathology.
Intervention: Tumor Destruction and Debridement Endobronchial papillomatous tumors at the proximal trachea, subglottic region, infraglottic region, left vocal fold, and anterior commissure were treated.
Modalities: VC papilloma were treated with a combination of {tools_used}.
Cryotherapy: The base of all patch sites was treated with cryotherapy.


Tool: 2.3 mm catheter.
Settings: Normal flow, Freeze, 5-second burst.


Result: Tumor frozen, 5 sites treated with 3-5 treatments each.
Mechanical Debridement: Endobronchial tumor and coagulated debris were noted and excised with mechanical debridement using alligator forceps.
Specimens were sent to pathology and microbiology.

Intervention: Rigid Tracheoscopy & Dilation A rigid tracheoscope was used to dilate the proximal tracheal obstruction, mechanically coring through the tumor.
Dilation: A black non-ventilating scope was used to perform dilation to {dilation_size} at the {dilation_location}.
Duration: Total of {num_inflations} inflations with dilation time of {dilation_duration} seconds each.
Additional Ablation: Cryospray was performed at the tumor site in the proximal trachea for 2 different sites.
A total of 3-5 treatments with 5 seconds of freeze at Normal flow was completed for both sides.
Results & Conclusion Prior to treatment, the proximal trachea airway was noted to be {pre_patency} patent.
After treatment, the airway was {post_patency} patent. Throughout the procedure, careful attention was paid to suction any secretions and blood to prevent them from falling into the distal trachea or more distal airways.
Residual secretions and blood were suctioned to clear. Video imaging was obtained and saved, and the bronchoscope was removed.
The patient tolerated the procedure well with no immediate complications.
At the conclusion of the operation, the patient had the airway device removed in the operating room and was transported to the recovery room in stable condition.
SPECIMEN(S) Trachea biopsy: Pathology.

IMPRESSION/PLAN [REDACTED] is a {age}-year-old adult who presents for bronchoscopy for ablation of papillomatous tumors in the context of recurrent respiratory papillomatosis.
Recommend repeat bronchoscopy in {follow_up} to reassess recurrence of papillomas and consideration of additional treatment.
"""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Operative note for {age}yo {gender_short}. RRP. Treated with {tools_used}. Findings: {papilloma_location}. Trachea dilated to {dilation_size} ({dilation_location}). Pre-patency {pre_patency}, post {post_patency}. Modifier 22 applied.",
    
    # Style 2: Dictation
    "Please generate a procedure note. The patient is a {age} year old {gender_long} with {diagnosis_full}. We performed a flexible and rigid bronchoscopy. Papillomas found at the {papilloma_location} and trachea. We used {tools_used}. Rigid dilation done to {dilation_size}. Improvement from {pre_patency} to {post_patency} patency. No complications.",
    
    # Style 3: Sloppy / Quick
    "post op dx J98.09 RRP. {age}y {gender_short}. complex ablation (mod 22). lesions at {papilloma_location}. rigid dilation {dilation_size} x{num_inflations}. airway {post_patency} open now. f/u {follow_up}.",
    
    # Style 4: Billing Focus
    "Code 31645, 31625, 31630, 31641-22. {age} {gender_short}. Indication: {diagnosis_full}. Document extensive ablation using {tools_used}. Dilation of {dilation_location} to {dilation_size}. Patency improved {pre_patency} -> {post_patency}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {diagnosis_full}\nFindings: Papillomas at {papilloma_location}, {trachea_appearance}.\nInterventions: {tools_used}, Dilation to {dilation_size}.\nOutcome: {post_patency} patency."
]

# ==========================================
# 5. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        doctor = random.choice(data_pool["doctor"])
        
        diagnosis_full = random.choice(data_pool["diagnosis_full"])
        papilloma_location = random.choice(data_pool["papilloma_location"])
        trachea_appearance = random.choice(data_pool["trachea_appearance"])
        stenosis_mild_pct = random.choice(data_pool["stenosis_mild_pct"])
        
        tools_used = random.choice(data_pool["tools_used"])
        
        dilation_size = random.choice(data_pool["dilation_size"])
        dilation_location = random.choice(data_pool["dilation_location"])
        dilation_duration = random.choice(data_pool["dilation_duration"])
        num_inflations = random.choice(data_pool["num_inflations"])
        
        pre_patency = random.choice(data_pool["pre_patency"])
        post_patency = random.choice(data_pool["post_patency"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diagnosis_full=diagnosis_full,
            papilloma_location=papilloma_location,
            trachea_appearance=trachea_appearance,
            tools_used=tools_used,
            dilation_size=dilation_size,
            dilation_location=dilation_location,
            num_inflations=num_inflations,
            pre_patency=pre_patency,
            post_patency=post_patency,
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            diagnosis_full=diagnosis_full,
            papilloma_location=papilloma_location,
            trachea_appearance=trachea_appearance,
            stenosis_mild_pct=stenosis_mild_pct,
            tools_used=tools_used,
            dilation_size=dilation_size,
            dilation_location=dilation_location,
            num_inflations=num_inflations,
            dilation_duration=dilation_duration,
            pre_patency=pre_patency,
            post_patency=post_patency,
            follow_up=follow_up
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