import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_064"
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
    "age": ["55", "62", "64", "68", "71", "73", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "date_var": ["January 12", "February 28", "March 15", "April 10", "May 22", "June 05", "October 18"],
    
    # Anatomical Logic Configuration: 
    # Maps the target stenosis site to the contralateral (normal) side and specific segmental anatomy for BAL
    "anatomy_config": [
        {
            "target_site_long": "Left Mainstem Bronchus",
            "target_site_short": "LMSB",
            "contralateral_lung": "Right Lung",
            "ipsilateral_lung": "Left Lung",
            "contralateral_segments": "Right Mainstem, Bronchus Intermedius",
            "bal_segment_name": "Superior Segment of Lingula (LB4) and Inferior Segment of Lingula (LB5)",
            "bal_short": "Lingula",
            "anatomy_normal_desc": "Right Lung: Proximal airways showed normal anatomic branching to the segmental level.",
            "anatomy_abnormal_desc": "Left Lung: The Left Mainstem Bronchus (LMSB) was noted to have stenosis"
        },
        {
            "target_site_long": "Right Mainstem Bronchus",
            "target_site_short": "RMSB",
            "contralateral_lung": "Left Lung",
            "ipsilateral_lung": "Right Lung",
            "contralateral_segments": "Left Mainstem, Upper Lobe",
            "bal_segment_name": "Medial Segment of RML (RB5) and Lateral Segment of RML (RB4)",
            "bal_short": "RML",
            "anatomy_normal_desc": "Left Lung: Proximal airways showed normal anatomic branching to the segmental level.",
            "anatomy_abnormal_desc": "Right Lung: The Right Mainstem Bronchus (RMSB) was noted to have stenosis"
        }
    ],

    "indication": [
        "bronchial stenosis",
        "malignant airway obstruction",
        "extrinsic airway compression",
        "post-transplant anastomotic stenosis"
    ],
    
    "stent_brand": ["MicroTech", "Aero", "Ultraflex", "Bonastent"],
    "stent_size": ["10 x 40", "12 x 40", "14 x 40", "10 x 60"],
    
    "dilation_balloon_pre": ["8/9/10", "6/7/8", "9/10/11"],
    "dilation_size_pre": ["10", "8", "11"],
    
    "dilation_balloon_post": ["10/11/12", "12/13.5/15", "11/12/13"],
    "dilation_size_post": ["12", "13.5", "13"],
    
    "destruction_method": [
        "electrocautery with a Needle Knife (EndoCut, Effect 3) making radial cuts",
        "Argon Plasma Coagulation (APC) at 40 watts",
        "Nd:YAG Laser therapy"
    ],
    
    "mucosa_finding": ["cobblestoning", "erythema", "nodularity", "inflammation"],
    "patency_pre": ["75%", "60%", "80%", "50%"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 

31624 Dx bronchoscope/lavage (BAL) 

31625 Endobronchial Biopsy(s) 

31630 Balloon dilation 

31636 Dilate and bronchial stent initial bronchus 

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENT Flexible Therapeutic Bronchoscope 

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings The laryngeal mask airway (LMA) was in good position.

Pharynx/Larynx: Not fully assessed due to bronchoscopy introduction through LMA.


Vocal Cords: Normal without mass/lesions.


Trachea: Normal.


Main Carina: Sharp.

{anatomy_normal_desc}

There was no evidence of mass, lesions, bleeding, or other endobronchial pathology. The anastomosis site was noted to be normal.

{anatomy_abnormal_desc} (both static at the anastomosis and dynamic at the proximal {target_site_short}).

Otherwise, normal anatomic branching to the segmental level was observed with no evidence of mass, lesions, or bleeding.

Mucosa: Some {mucosa_finding} was noted at the main carina and proximal {target_site_short}; otherwise normal.


Secretions: Minimal, thin, and clear.

Therapeutic Interventions


Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean mucus from the Trachea (Distal 1/3), {contralateral_segments}, {target_site_long}, Carina.

Bronchoalveolar Lavage (BAL): BAL was performed at the {bal_segment_name}.

40 cc of NS was instilled, and suction returned 15 cc of NS.

Samples were sent for Cell Count and Microbiology (Cultures/Viral/Fungal).


Endobronchial Biopsy: Biopsy of {mucosa_finding} mucosa was performed at the {target_site_long} and Carina using 2.0mm pulmonary forceps.

Samples were sent for Pathology.


Stenosis Destruction: Endobronchial obstruction at the {target_site_short} anastomosis stenosis was treated using {destruction_method}.

Prior to treatment, the affected airway was noted to be {patency_pre} patent.

Balloon Dilation (Pre-Stent): Balloon dilation was performed at the {target_site_long}.

An {dilation_balloon_pre} Elation balloon was used to perform dilation to {dilation_size_pre} mm.

Total 1 inflation was performed with a dilation time of 60 seconds.

Stent Placement: A {stent_brand} {stent_size}mm stent was placed in the {target_site_long}.

Balloon Dilation (Post-Stent):

An {dilation_balloon_pre} Elation balloon was used to perform dilation to {dilation_size_pre} mm at the {target_site_long} to fully extend and seat the stent (3 inflations, 30 seconds each).

A {dilation_balloon_post} Elation balloon was used to perform dilation to {dilation_size_post} mm at the {target_site_long} (3 inflations, 30 seconds each).

Result: After treatment, the airway was 100% patent.

The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)

{target_site_short} endobronchial forceps biopsies 

{bal_short} BAL (cell count, micro) 

IMPRESSION / PLAN [REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for evaluation of {indication}.

{stent_brand} {stent_size} mm stent was successfully deployed to the {target_site_short}.

Patient tolerated the procedure well and there were no immediate complications.

Stent Hydration Regimen TID in the following order: 

Albuterol nebs

Hypertonic saline (3%) nebs

Flutter valve

Guaifenesin 1200mg PO BID.

Follow-up endobronchial biopsy and BAL results.

Outpatient follow-up in IP clinic as scheduled on [REDACTED].

Repeat bronchoscopy for stent check in 2-3 weeks.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "{age}{gender_short} with {indication}. {target_site_short} stent placement ({stent_brand} {stent_size}mm). BAL {bal_short}, Bx {target_site_short}.",
    
    # Style 2: Dictation
    "Please generate an IP op report for a {age} year old {gender_long}. Indication is {indication}. We found stenosis in the {target_site_long}. Performed destruction with {destruction_method_short}, balloon dilation, and placed a {stent_brand} {stent_size} stent.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. {target_site_short} stenosis. placed {stent_brand} stent. bal {bal_short}. biopsy taken.",
    
    # Style 4: Billing Focus
    "Procedure codes 31636, 31630, 31624, 31625. {age} {gender_short}. Dx J98.09. Site: {target_site_short}. Device: {stent_brand} {stent_size}mm.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nTarget: {target_site_long}\nIntervention: Stent ({stent_brand}), Balloon Dilation, BAL, Biopsy."
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
        indication = random.choice(data_pool["indication"])
        
        # Anatomy Logic
        anatomy = random.choice(data_pool["anatomy_config"])
        
        # Procedure details
        stent_brand = random.choice(data_pool["stent_brand"])
        stent_size = random.choice(data_pool["stent_size"])
        
        dilation_balloon_pre = random.choice(data_pool["dilation_balloon_pre"])
        dilation_size_pre = random.choice(data_pool["dilation_size_pre"])
        
        dilation_balloon_post = random.choice(data_pool["dilation_balloon_post"])
        dilation_size_post = random.choice(data_pool["dilation_size_post"])
        
        destruction_method = random.choice(data_pool["destruction_method"])
        if "Needle Knife" in destruction_method:
            destruction_method_short = "Needle Knife"
        elif "APC" in destruction_method:
            destruction_method_short = "APC"
        else:
            destruction_method_short = "Laser"
            
        mucosa_finding = random.choice(data_pool["mucosa_finding"])
        patency_pre = random.choice(data_pool["patency_pre"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            target_site_short=anatomy["target_site_short"],
            target_site_long=anatomy["target_site_long"],
            stent_brand=stent_brand,
            stent_size=stent_size,
            bal_short=anatomy["bal_short"],
            destruction_method_short=destruction_method_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            # Anatomy Variables
            anatomy_normal_desc=anatomy["anatomy_normal_desc"],
            anatomy_abnormal_desc=anatomy["anatomy_abnormal_desc"],
            target_site_long=anatomy["target_site_long"],
            target_site_short=anatomy["target_site_short"],
            contralateral_segments=anatomy["contralateral_segments"],
            bal_segment_name=anatomy["bal_segment_name"],
            bal_short=anatomy["bal_short"],
            # Procedure Variables
            mucosa_finding=mucosa_finding,
            destruction_method=destruction_method,
            patency_pre=patency_pre,
            dilation_balloon_pre=dilation_balloon_pre,
            dilation_size_pre=dilation_size_pre,
            stent_brand=stent_brand,
            stent_size=stent_size,
            dilation_balloon_post=dilation_balloon_post,
            dilation_size_post=dilation_size_post
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