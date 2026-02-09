import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_017"
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
    "age": ["55", "62", "68", "71", "74", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Bowers", "Dr. Patel"],
    
    # Anatomy Tuples: (Side, Mainstem, Upper Lobe, Lower Lobe, Specific Segment/Carina, Secondary Carina)
    # This ensures anatomical consistency (e.g., Lingula is only on Left, Middle Lobe on Right)
    "anatomy_tuple": [
        ("Left", "Left Mainstem Bronchus (LMSB)", "LUL", "LLL", "Lingula", "LC2"),
        ("Right", "Right Mainstem Bronchus (RMSB)", "RUL", "RLL", "Middle Lobe", "RC2")
    ],
    
    "stent_brand": ["Microtech", "Boston Scientific", "Merit", "Novatech", "Silicone Y"],
    "stent_issue": [
        "migrated distally and appeared to be covering the mainstem",
        "migrated proximally causing subglottic obstruction",
        "fractured with granulation tissue ingrowth",
        "completely occluded by inspissated secretions"
    ],
    "mucus_desc": [
        "thick yellow-green mucus",
        "copious purulent secretions",
        "blood-tinged mucus plugs",
        "tenacious white frothy secretions",
        "thick brown fungal-like debris"
    ],
    "mucosa_condition": [
        "ragged and irregular, with dynamic collapse",
        "highly friable with contact bleeding",
        "edematous with cobble-stoning appearance",
        "necrotic with areas of char"
    ],
    "cryo_time": ["30", "45", "60", "20"],
    
    # Plan variations based on infectious suspicion
    "plan_tuple": [
        ("MSSA", "Prednisone 20 mg"),
        ("MRSA", "Vancomycin and Prednisone 40 mg"),
        ("Pseudomonas", "Cefepime and Solu-Medrol 40 mg"),
        ("polymicrobial infection", "Unasyn and Dexamethasone 4 mg")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Template replicates the structure of note_017.txt
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

PATIENT: [REDACTED] DATE OF PROCEDURE: [Date] ATTENDING: {attending}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with bronchial stenosis.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE

Therapeutic aspiration (initial episode) (CPT 31645)

Diagnostic bronchoscopy/lavage (BAL) (CPT 31624)

Endobronchial Biopsy (CPT 31625)

Radial EBUS for peripheral lesion (CPT 31654)

Destruction of tumor OR relief of stenosis (cryotherapy) (CPT 31641)

Foreign body removal (CPT 31635)

Modifier 22 (Unusual Procedural Services): This patient required extensive mechanical excision of endobronchial tissue to salvage the airway as well as stent management given aberrant anatomy.
This resulted in >80% increased work due to the technical difficulty of the procedure and the physical and mental effort required.
Specifically, the patient presented with a complex airway with significant stenosis of the {main_bronchus} and complete occlusion of the {lower_lobe} bronchus that required multiple attempts.
ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Disposable Bronchoscope

ESTIMATED BLOOD LOSS Minimal

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection and Therapeutic Aspiration An iGel was placed by anesthesia after adequate sedation.
Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), {main_short}, Carina, {upper_lobe} {segment} Carina, and {sec_carina} from mucus and mucus plugs.
The stent was noted to be partially occluded with {mucus_desc}.
Foreign Body (Stent) Removal and Debridement It appeared that the {main_short} stent had {stent_issue}.
Using forceps, the proximal end of the {stent_brand} stent was grasped and removed en bloc with the bronchoscope.
The foreign body removal was difficult due to significant inflammation.
After removal, the {main_short} mucosa was noted to be {mucosa_condition}.
The {upper_lobe} bronchus was approximately 3-4 mm. The {lower_lobe} bronchus could not be visualized, and the {sec_carina} was difficult to delineate along the inferior portion.
Endobronchial Tumor Destruction / Stenosis Relief Endobronchial tumor/tissue was noted and excised with mechanical debridement using alligator forceps.
A 1.7 mm cryoprobe was utilized with {cryo_time}-second freeze cycles to achieve vascular occlusion and for further debulking of the {upper_lobe} ostium.
Radial EBUS Survey Due to complex anatomy, a jag wire was placed in the {segment}.
Radial endobronchial ultrasound (EBUS) was utilized to identify vasculature and airways, but the {lower_lobe} was still unable to be identified.
Bronchoalveolar Lavage (BAL) Bronchoalveolar lavage was performed at the Superior Segment of the {segment}.
40 cc of normal saline was instilled, and suction returned 15 cc.

Conclusion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{upper_lobe} BAL: Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology

{main_short} Endobronchial Biopsy (EBBx): Pathology

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for bronchial stenosis.
Very odd presentation of cicatrization and benign stenosis of the {main_short} without evidence of residual malignancy.
Very challenging anatomy of the airway and stenosis.

The patient continues to have a robust inflammatory response;
no additional stents were placed.

Admit overnight.

Start antibiotics to treat {abx_target}; add {steroid_plan}.
Obtain CT chest with contrast.

NPO after midnight for repeat bronchoscopy [REDACTED]."""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report: {age}{gender_short}, {attending}. Dx: Bronchial stenosis. Proc: Stent removal, Cryo, BAL. Findings: {main_short} stent {stent_issue_short}. {mucus_desc}. Mucosa {mucosa_short}. Plan: Admit, treat {abx_target}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {attending}. Patient is {age} {gender_long}. We performed a complex stent removal and cryotherapy. The {stent_brand} stent in the {main_short} had {stent_issue}. We saw lots of {mucus_desc}. Used cryo for {cryo_time} seconds. Patient admitted for {abx_target} coverage.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} airway salvage. {main_short} stent removal ({stent_brand}). Stent was {stent_issue_short}. Suctioned {mucus_desc}. Cryo used. No comps. Plan: {abx_target}, CT chest.",
    
    # Style 4: Billing Focus
    "Procedures: 31645, 31624, 31625, 31654, 31641, 31635-22. {age} {gender_short}. Complex airway {main_short}. Removed {stent_brand} stent. Findings: {mucus_desc}, {mucosa_short}. Add modifier 22 for extensive debridement >80% extra work.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nSurgeon: {attending}\nProcedure: Bronchoscopy with Stent Removal & Cryo\nKey Findings:\n- {main_short} stent {stent_issue}\n- {mucus_desc}\n- {upper_lobe} BAL performed\nPlan: Admit, {abx_target}, {steroid_plan}."
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
        attending = random.choice(data_pool["attending"])
        
        # Anatomy logic unpacking
        anat = random.choice(data_pool["anatomy_tuple"])
        side = anat[0]
        main_bronchus = anat[1]
        upper_lobe = anat[2]
        lower_lobe = anat[3]
        segment = anat[4]
        sec_carina = anat[5]
        
        # Derived short forms for prompt/note consistency
        main_short = "LMSB" if side == "Left" else "RMSB"
        
        stent_brand = random.choice(data_pool["stent_brand"])
        stent_issue = random.choice(data_pool["stent_issue"])
        # Shorten stent issue for telegraphic prompts
        stent_issue_short = "migrated" if "migrated" in stent_issue else "occluded"
        
        mucus_desc = random.choice(data_pool["mucus_desc"])
        mucosa_condition = random.choice(data_pool["mucosa_condition"])
        # Shorten mucosa for telegraphic prompts
        mucosa_short = "ragged" if "ragged" in mucosa_condition else "friable"
        
        cryo_time = random.choice(data_pool["cryo_time"])
        
        plan_tup = random.choice(data_pool["plan_tuple"])
        abx_target = plan_tup[0]
        steroid_plan = plan_tup[1]
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            attending=attending,
            main_short=main_short,
            stent_issue=stent_issue,
            stent_issue_short=stent_issue_short,
            mucus_desc=mucus_desc,
            mucosa_short=mucosa_short,
            abx_target=abx_target,
            stent_brand=stent_brand,
            cryo_time=cryo_time,
            upper_lobe=upper_lobe,
            steroid_plan=steroid_plan
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            attending=attending,
            main_bronchus=main_bronchus,
            main_short=main_short,
            lower_lobe=lower_lobe,
            upper_lobe=upper_lobe,
            segment=segment,
            sec_carina=sec_carina,
            mucus_desc=mucus_desc,
            stent_issue=stent_issue,
            stent_brand=stent_brand,
            mucosa_condition=mucosa_condition,
            cryo_time=cryo_time,
            abx_target=abx_target,
            steroid_plan=steroid_plan
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