import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_049" 
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
    "age": ["19", "22", "27", "34", "41", "55", "62", "74"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "anesthesia_type": ["General Anesthesia", "General Anesthesia with LMA", "MAC / Deep Sedation"],
    "stenosis_size": ["~6mm", "~7mm", "~8mm", "~9mm", "~5mm"],
    "malacia_severity": ["<50%", "~50%", ">50%", "mild", "moderate"],
    "bal_fluids": [
        ("60 cc", "20 cc"), 
        ("100 cc", "40 cc"), 
        ("50 cc", "15 cc"), 
        ("120 cc", "50 cc")
    ],
    "follow_up_time": ["2 weeks", "4 weeks", "6 weeks", "3 months"],
    
    # Logic Scenarios to keep anatomy consistent
    # If stenosis is Left, findings must be Left, and Right must be normal.
    "pathology_scenarios": [
        {
            "side": "Left",
            "stenosis_site_full": "distal left mainstem bronchus",
            "stenosis_site_short": "LMSB",
            "stenosis_site_paren": "(distal left mainstem bronchus)",
            "malacia_site": "left mainstem bronchus",
            "right_lung_findings": "No evidence of mass, lesions, bleeding, or other endobronchial pathology.",
            "left_lung_findings_proximal": "The distal left mainstem bronchus (LMSB) was noted to be slightly stenotic ({size}).",
            "left_lung_malacia_desc": "On PEEP 0, the airways were noted to have slight malacia ({malacia}) at the proximal and distal left mainstem bronchus.",
            "left_lung_distal": "Normal anatomic branching to the segmental level in the LLL was observed, noting historic obliteration of the LUL.",
            "bal_location": "Anteromedial Segment of LLL (Lb7/8), Lateral-basal Segment of LLL (LB9), and Posterior-Basal Segment of LLL (LB10)",
            "bal_specimen_label": "LLL BAL",
            "aspiration_list": "Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2)",
            "impression_finding": "Distal left mainstem stenosis ({size}) and mild left mainstem malacia ({malacia}) identified. LUL obliteration noted."
        },
        {
            "side": "Right",
            "stenosis_site_full": "distal right mainstem bronchus",
            "stenosis_site_short": "RMSB",
            "stenosis_site_paren": "(distal right mainstem bronchus)",
            "malacia_site": "right mainstem bronchus",
            "right_lung_findings": "The distal right mainstem bronchus (RMSB) was noted to be slightly stenotic ({size}).",
            "left_lung_findings_proximal": "Normal anatomic branching to the segmental level.",
            "left_lung_malacia_desc": "No evidence of malacia.",
            "left_lung_distal": "No evidence of mass, lesions, bleeding, or other endobronchial pathology.",
            # For right side scenario, we inject malacia description into Right lung findings logic below
            "bal_location": "Lateral-basal Segment of RLL (RB9) and Posterior-Basal Segment of RLL (RB10)",
            "bal_specimen_label": "RLL BAL",
            "aspiration_list": "Trachea, Left Mainstem, Right Mainstem, RUL Carina, RML Carina, and Basal Segments",
            "impression_finding": "Distal right mainstem stenosis ({size}) and mild right mainstem malacia ({malacia}) identified. RUL obliteration noted."
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The note template carefully reconstructs the operative report structure.
# Logic regarding Right vs Left lung sections is handled in the generator function 
# to ensure "Normal" vs "Pathology" text appears in the correct section.

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with airway stenosis.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

Airway stenosis {stenosis_site_paren} 

Airway malacia ({malacia_site}) 

PROCEDURE

Therapeutic aspiration, subsequent episodes (CPT 31646) 

Diagnostic bronchoscopy with bronchoalveolar lavage (BAL) (CPT 31624) 

ANESTHESIA {anesthesia} 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Disposable Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Airway Inspection


Patient Position/Airway: The laryngeal mask airway (LMA) was noted to be in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.


Larynx: Normal.


Vocal Cords: Normal without mass or lesions.

Trachea: Mildly tortuous. Secretions were minimal, thin, and clear.


Carina: Sharp.

Right Lung


Proximal Airways: {right_lung_proximal_text}
Findings: {right_lung_findings_text}

Left Lung


Proximal Airways: {left_lung_proximal_text}
Malacia: {left_lung_malacia_text}
Distal Airways: {left_lung_distal_text}
Findings: {left_lung_findings_final_text}

Therapeutic Interventions


Therapeutic Aspiration: Successful therapeutic aspiration was performed to clear mucus from the {aspiration_list}.

Bronchoalveolar Lavage (BAL): BAL was performed at the {bal_location}.

Technique: Instilled {vol_in} of NS; suction returned with {vol_out} of NS.

Disposition: Samples were sent for Cell Count and Microbiology (Cultures/Viral/Fungal).

Termination The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)

{bal_specimen_label} (cell count, microbiology) 

IMPRESSION / PLAN

{age}-year-old {gender_long} presenting for evaluation of airway stenosis.

Findings: {impression_finding}

Plan:

Follow up on BAL results.

Repeat bronchoscopy in {follow_up_time} for possible dilation and stenting.
"""

# 5 Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Bronchoscopy note for {age}yo {gender_short}. Dx: Airway stenosis ({side}). Findings: {stenosis_size} stenosis {stenosis_short}, malacia {malacia}. BAL performed {bal_spec_short}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age}-year-old {gender_long}. Indication was airway stenosis. We found {stenosis_size} stenosis in the {stenosis_full} and {malacia} malacia. Plan is repeat in {follow_up_time}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} stenosis {stenosis_short} {stenosis_size}. malacia {malacia}. did BAL {bal_spec_short}. no comps. plan repeat {follow_up_time}.",
    
    # Style 4: Billing Focus
    "CPT 31646, 31624. Dx J98.09. {age} {gender_short}. Site: {stenosis_full}. Findings: Stenosis {stenosis_size}, Malacia {malacia}. Specimens: {bal_spec_short}.",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nINDICATION: Airway Stenosis\nSITE: {stenosis_full}\nFINDINGS: {stenosis_size} narrowing, {malacia} malacia\nPROCEDURE: BAL, Aspiration"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select basic variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        anesthesia = random.choice(data_pool["anesthesia_type"])
        stenosis_size = random.choice(data_pool["stenosis_size"])
        malacia_sev = random.choice(data_pool["malacia_severity"])
        vol_tup = random.choice(data_pool["bal_fluids"])
        follow_up = random.choice(data_pool["follow_up_time"])
        
        # B. Select Scenario (Left vs Right Logic)
        scenario = random.choice(data_pool["pathology_scenarios"])
        
        # C. Construct Lung Section Text based on Scenario
        # Note: The source text has specific paragraph structures we must mimic dynamically
        if scenario["side"] == "Left":
            # Right Lung is normal
            r_prox = "Normal anatomic branching to the segmental level."
            r_find = "No evidence of mass, lesions, bleeding, or other endobronchial pathology."
            
            # Left Lung has pathology
            l_prox = scenario["left_lung_findings_proximal"].format(size=stenosis_size)
            l_malacia = scenario["left_lung_malacia_desc"].format(malacia=malacia_sev)
            l_distal = scenario["left_lung_distal"]
            l_find = "No evidence of mass, lesions, bleeding, or other endobronchial pathology. Mucosa was normal." # Generic footer for that section
            
        else:
            # Right Lung has pathology
            r_prox = "Normal anatomic branching to the segmental level." # Keeping header, but adding findings below
            # We combine proximal desc + malacia for right side because original note structure split them only for the affected side
            r_find = f"{scenario['right_lung_findings'].format(size=stenosis_size)} On PEEP 0, {malacia_sev} malacia noted. Historic obliteration of RUL."
            
            # Left Lung is normal
            l_prox = "Normal anatomic branching to the segmental level."
            l_malacia = "None."
            l_distal = "Normal segmental anatomy."
            l_find = "No evidence of mass, lesions, bleeding, or other endobronchial pathology."

        # D. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            side=scenario["side"],
            stenosis_size=stenosis_size,
            stenosis_short=scenario["stenosis_site_short"],
            stenosis_full=scenario["stenosis_site_full"],
            malacia=malacia_sev,
            bal_spec_short=scenario["bal_specimen_label"],
            follow_up_time=follow_up
        )
        
        # E. Generate Completion
        impression_filled = scenario["impression_finding"].format(size=stenosis_size, malacia=malacia_sev)
        
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_long,
            stenosis_site_paren=scenario["stenosis_site_paren"],
            malacia_site=scenario["malacia_site"],
            anesthesia=anesthesia,
            right_lung_proximal_text=r_prox,
            right_lung_findings_text=r_find,
            left_lung_proximal_text=l_prox,
            left_lung_malacia_text=l_malacia,
            left_lung_distal_text=l_distal,
            left_lung_findings_final_text=l_find,
            aspiration_list=scenario["aspiration_list"],
            bal_location=scenario["bal_location"],
            vol_in=vol_tup[0],
            vol_out=vol_tup[1],
            bal_specimen_label=scenario["bal_specimen_label"],
            impression_finding=impression_filled,
            follow_up_time=follow_up
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