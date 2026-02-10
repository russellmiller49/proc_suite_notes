import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_063"
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
    "date_offset": range(-10, 10), # Days relative to today
    
    # Clinical Variables
    "indication": [
        "airway stenosis", 
        "worsening dyspnea and stridor", 
        "known tracheal stenosis with stent obstruction",
        "obstructing airway lesion"
    ],
    
    # Anatomy Scenarios (Linked data to ensure consistency between findings and procedure)
    "anatomy_scenarios": [
        {
            "site_full": "Left Mainstem Bronchus",
            "site_abbr": "LMSB",
            "secondary_sites": "RMSB, LUL, LLL",
            "bal_site": "Anteromedial Segment of LLL (Lb7/8)",
            "migration_desc": "migrated distally",
            "stent_issue": "highly malacic ~1cm section proximal to the stent"
        },
        {
            "site_full": "Right Mainstem Bronchus",
            "site_abbr": "RMSB",
            "secondary_sites": "LMSB, RUL, RLL",
            "bal_site": "Lateral Segment of RML (Rb4)",
            "migration_desc": "migrated proximally touching the carina",
            "stent_issue": "granulation tissue overgrowth at proximal edge"
        },
        {
            "site_full": "Trachea",
            "site_abbr": "Distal Trachea",
            "secondary_sites": "LMSB, RMSB",
            "bal_site": "Superior Segment of LLL (Lb6)",
            "migration_desc": "migrated towards the vocal cords",
            "stent_issue": "mucous plugging and malacia distal to the stent"
        }
    ],

    # Device Details
    "old_stent_brand": ["MicroTech", "Boston Scientific", "Merit"],
    "old_stent_size": ["10mm x 40mm", "12mm x 40mm", "14mm x 40mm"],
    "new_stent_brand": ["Bonastent", "Aero", "Ultraflex"],
    "new_stent_size": ["10mm x 50mm", "12mm x 60mm", "14mm x 50mm"],
    
    # Tools
    "balloon_brand": ["Elation", "CRE", "Hercules"],
    "balloon_sizes": ["8/9/10", "10/11/12", "12/13.5/15"],
    "apc_probe": ["Straightfire probe", "FiAPC probe", "Circumferential probe"],
    
    # Findings
    "mucus_desc": ["Thick tenacious mucus", "Copious purulent secretions", "Moderate mucoid secretions"],
    "granulation_loc": ["proximal LMSB", "distal trachea", "right mainstem anastomosis", "suture line"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """DATE OF PROCEDURE: {date_str} INDICATION FOR OPERATION {patient_name_redacted} is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

Airway stenosis ({site_abbr}, {secondary_sites}) 

Stent migration 

PROCEDURE

Therapeutic aspiration, initial episode (31645) 

Bronchoalveolar lavage (BAL) (31624) 

Endobronchial Biopsy(s) (31625) 

Balloon dilation (31630) – Bilateral/Multiple sites ({site_abbr}, {secondary_sites}) 

Bronchial stent placement, initial bronchus (31636) 

Bronchoscopy with excision (31640) 

Destruction of tumor or relief of stenosis by any method other than excision (APC) (31641) 

Foreign body removal (Stent removal) (31635) 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout 
the entire procedure.

INSTRUMENTATION Rigid Bronchoscope; Flexible Therapeutic Bronchoscope; APC ({apc_probe}); Pulmonary forceps; {balloon_brand} balloons ({balloon_sizes} and {balloon_sizes_2}).
ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection (via LMA) The laryngeal mask airway was in good position.

Larynx/Trachea: Normal. Vocal cords normal without mass/lesions.
Trachea normal.


Main Carina: Somewhat splayed with granulation tissue noted.
Right Lung: Stenosis noted at the anastomosis/suture line with granulation tissue.
Left Lung: Stenosis noted at the {site_full} ({site_abbr}).
The existing metallic stent in the {site_abbr} had {migration_desc}, leaving a stenotic and {stent_issue}.
{mucus_desc} was noted within the stent.

Therapeutic Interventions


Therapeutic Aspiration: Performed to clear mucus from the Trachea, Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina.
Biopsy & Tissue Removal: Endobronchial biopsy was performed at the {site_abbr}; the lesion was successfully removed.
Stenosis/Granulation Treatment: Granulation tissue causing stenosis at the {granulation_loc} was treated.
Mechanical destruction was performed using pulmonary forceps, followed by APC ablation ({apc_probe}, Forced coag, Effect 2) for destruction and hemostasis.
Bronchoalveolar Lavage (BAL): Performed at the {bal_site} with 60 cc NS instilled and 20 cc return.
Rigid Bronchoscopy & Stent Exchange The LMA was removed, and a rigid bronchoscope was introduced.
The vocal cords were identified, and the scope was advanced to the distal trachea; jet ventilation was initiated.
Stent Removal: The patient's existing {old_stent_brand} {old_stent_size} stent was grasped with pulmonary forceps and removed en bloc.
Balloon Dilation ({site_abbr}): A {balloon_sizes_2} {balloon_brand} balloon was used to dilate the {site_abbr} to 12 mm (1 inflation, 60 seconds).
Stent Placement: A new {new_stent_brand} ({new_stent_size}) was placed in the {site_full}.
Post-Deployment Dilation: The stent was dilated using a {balloon_sizes_2} {balloon_brand} balloon to expand and seat the stent (4 inflations, 30 seconds each).
Additional Balloon Dilations


Secondary sites ({secondary_sites}): Dilated using {balloon_sizes} {balloon_brand} balloon.
The rigid bronchoscope was extubated, the LMA replaced, and lidocaine applied to the vocal cords.
The patient was extubated in the operating room and transported to recovery in stable condition.
SPECIMENS

BAL (cell count, micro, cyto) 

{site_abbr} endobronchial forceps biopsies (pathology) 

{site_full} stent (pathology) 

IMPRESSION/PLAN

{age}-year-old {gender_long} with airway stenosis and {migration_desc} of existing stent.
Existing stent removed; {new_stent_brand} {new_stent_size} re-placed in the {site_abbr}.
Multilevel balloon dilation performed and granulation tissue ablated.

Follow-up BAL and pathology results.
Continue stent hydration therapy regimen.

Repeat bronchoscopy in approximately 4 weeks for re-evaluation.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report: {age}{gender_short}, {indication}. Stent exchange {site_abbr}. Old: {old_stent_brand} {old_stent_size}, New: {new_stent_brand} {new_stent_size}. Dilation {secondary_sites}. APC used.",
    
    # Style 2: Dictation
    "Please generate an op note for a {age} year old {gender_long} presenting with {indication}. We found the existing stent in the {site_abbr} had {migration_desc}. We performed a stent exchange removing the {old_stent_brand} and placing a {new_stent_brand} sized {new_stent_size}. Also did APC and BAL at {bal_site}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. stent migration in {site_abbr}. removed old {old_stent_brand}, put in {new_stent_size} {new_stent_brand}. balloon dilated {secondary_sites} and {site_abbr}. biopsy taken.",
    
    # Style 4: Billing Focus
    "Procedure Codes: 31645, 31624, 31636, 31630, 31635. Patient {age} {gender_short}. Indication: {indication}. Site: {site_abbr}. Intervention: Removal of {old_stent_brand} stent, placement of {new_stent_brand} {new_stent_size}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: J98.09 Airway Stenosis\nKey Finding: Stent migration {site_abbr}\nAction: Exchange {old_stent_brand} -> {new_stent_brand} ({new_stent_size})\nAdd'l Procedures: APC, BAL ({bal_site}), Dilation ({secondary_sites})"
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
        date_offset = random.choice(data_pool["date_offset"])
        date_str = (datetime.date.today() + datetime.timedelta(days=date_offset)).strftime("%B %d, %Y")
        
        indication = random.choice(data_pool["indication"])
        
        # Select cohesive anatomy scenario
        scenario = random.choice(data_pool["anatomy_scenarios"])
        
        # Select device/tool details
        old_stent_brand = random.choice(data_pool["old_stent_brand"])
        old_stent_size = random.choice(data_pool["old_stent_size"])
        new_stent_brand = random.choice(data_pool["new_stent_brand"])
        new_stent_size = random.choice(data_pool["new_stent_size"])
        
        balloon_brand = random.choice(data_pool["balloon_brand"])
        balloon_sizes = random.choice(data_pool["balloon_sizes"])
        balloon_sizes_2 = random.choice(data_pool["balloon_sizes"]) # Size for main stent
        apc_probe = random.choice(data_pool["apc_probe"])
        
        mucus_desc = random.choice(data_pool["mucus_desc"])
        granulation_loc = random.choice(data_pool["granulation_loc"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            site_abbr=scenario["site_abbr"],
            old_stent_brand=old_stent_brand,
            old_stent_size=old_stent_size,
            new_stent_brand=new_stent_brand,
            new_stent_size=new_stent_size,
            secondary_sites=scenario["secondary_sites"],
            bal_site=scenario["bal_site"],
            migration_desc=scenario["migration_desc"]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_str=date_str,
            patient_name_redacted="[REDACTED]",
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            site_full=scenario["site_full"],
            site_abbr=scenario["site_abbr"],
            secondary_sites=scenario["secondary_sites"],
            migration_desc=scenario["migration_desc"],
            stent_issue=scenario["stent_issue"],
            mucus_desc=mucus_desc,
            bal_site=scenario["bal_site"],
            granulation_loc=granulation_loc,
            apc_probe=apc_probe,
            old_stent_brand=old_stent_brand,
            old_stent_size=old_stent_size,
            balloon_brand=balloon_brand,
            balloon_sizes=balloon_sizes,
            balloon_sizes_2=balloon_sizes_2,
            new_stent_brand=new_stent_brand,
            new_stent_size=new_stent_size
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