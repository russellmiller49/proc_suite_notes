import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_054"
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
    "age": ["38", "45", "49", "52", "58", "64", "69", "72", "77"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Hudson", "Dr. Weiss", "Dr. Chen", "Dr. Patel", "Dr. Smith"],
    "diagnosis": [
        ("J96.90", "Respiratory Failure"),
        ("J96.00", "Acute Respiratory Failure"),
        ("J96.21", "Acute on Chronic Respiratory Failure with hypoxia")
    ],
    "medications": [
        "Versed 5 mg, Fentanyl 150 mcg, Propofol gtt 60 mcg/kg/min",
        "Versed 2 mg, Fentanyl 100 mcg, Propofol gtt 40 mcg/kg/min",
        "Midazolam 4 mg, Fentanyl 200 mcg, Dexmedetomidine infusion",
        "Propofol gtt 80 mcg/kg/min only"
    ],
    "tube_sizes": ["6.0", "7.0", "7.5", "8.0"],
    "tube_brands": [("Shiley", "Portex"), ("Portex", "Shiley"), ("Bivona", "Shiley")],
    
    # BAL Locations and corresponding segments
    "bal_targets": [
        {"loc": "RML", "segs": "lateral (RB4) and medial (RB5)"},
        {"loc": "RLL", "segs": "superior (RB6) and posterior basal (RB10)"},
        {"loc": "LUL", "segs": "apicoposterior (LB1+2) and anterior (LB3)"},
        {"loc": "Lingula", "segs": "superior (LB4) and inferior (LB5)"}
    ],
    
    "fluids": [
        {"in": "40", "out": "15"},
        {"in": "60", "out": "25"},
        {"in": "100", "out": "40"},
        {"in": "30", "out": "10"}
    ]
}

# COMPLEX SCENARIOS: Stoma findings affect the Procedure Code (Mod 22), The Consult, and The Plan.
stoma_scenarios = [
    # Scenario 1: Original (Erosion + Packing + Mod 22)
    {
        "condition": "erosion",
        "visual": "an erosion was visualized at the {clock} o'clock ({pos}) position",
        "findings_header": "Stoma erosion noted at the {clock} o'clock position",
        "intervention": "Cardiothoracic Surgery was consulted. Under their guidance, the erosion was packed with iodoform gauze.",
        "modifier_text": "31502-22 Tracheotomy tube change prior to establishment of fistula tract\n\n\nModifier 22 Note: Substantially greater work than normal (>50% increased work) due to the requirement of wound packing at the tracheostomy stoma.",
        "plan_text": "Stoma erosion identified and packed with iodoform gauze.\nPlan: Recommend Wound Care evaluation for stoma erosion; follow up BAL results; continue care per primary team.",
        "work_level": "complex",
        "positions": [("4", "inferolateral"), ("8", "inferolateral"), ("6", "inferior")]
    },
    # Scenario 2: Granulation Tissue (Cautery, No Mod 22 usually, or different management)
    {
        "condition": "granulation",
        "visual": "hypertrophic granulation tissue was visualized at the {clock} o'clock position",
        "findings_header": "Granulation tissue noted at stoma site",
        "intervention": "Silver nitrate cautery was applied to the granulation tissue to achieve hemostasis.",
        "modifier_text": "31502 Tracheotomy tube change prior to establishment of fistula tract",
        "plan_text": "Granulation tissue cauterized with silver nitrate.\nPlan: Routine tracheostomy care; follow up BAL results; continue care per primary team.",
        "work_level": "standard",
        "positions": [("12", "superior"), ("3", "lateral"), ("9", "lateral")]
    },
    # Scenario 3: Healthy/Patent (Routine)
    {
        "condition": "healthy",
        "visual": "the stoma appeared widely patent, clean, and without signs of infection or breakdown",
        "findings_header": "Stoma patent and healthy",
        "intervention": "Routine cleaning was performed.",
        "modifier_text": "31502 Tracheotomy tube change prior to establishment of fistula tract",
        "plan_text": "Routine tube exchange completed.\nPlan: Routine tracheostomy care; follow up BAL results; continue care per primary team.",
        "work_level": "standard",
        "positions": [("", "")] # Dummy position
    }
]

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} INDICATION FOR OPERATION: The patient is a {age}-year-old {gender_long} who presents with {diag_name}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery, and informed consent was signed.

CONSENT: Obtained before the procedure.
Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS: * {diag_code} {diag_name}


POSTOPERATIVE DIAGNOSIS: * {diag_code} {diag_name}

{findings_header}


PROCEDURE: * 31645 Therapeutic aspiration initial episode 

31624 Bronchoalveolar lavage (BAL) 

{modifier_text}


ATTENDING: {attending} ANESTHESIA: Moderate sedation (99152, 99153) administered by ICU RN.
Medications: {meds}.


Total Sedation Time: {sedation_time} minutes.
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer throughout the entire procedure.
The patient was monitored one-to-one by the attending physician during anesthesia.
INSTRUMENT: Flexible Diagnostic Bronchoscope 


ESTIMATED BLOOD LOSS: None 


COMPLICATIONS: None 

PROCEDURE IN DETAIL: After successful induction of anesthesia, a timeout was performed to confirm patient identity and procedure.
Patient Position: Supine 

Initial Airway Inspection:


Tracheostomy tube: In good position.


Pharynx/Larynx/Trachea: Normal.


Vocal Cords: Normal without mass or lesions.
Main Carina: Sharp.


Bronchial Tree: Normal anatomic branching to the segmental level bilaterally;
no evidence of mass, lesions, bleeding, or endobronchial pathology.


Mucosa/Secretions: Normal mucosa; minimal, thin, clear secretions.
Therapeutic Aspiration and Lavage: Successful therapeutic aspiration was performed to clear mucus from the subglottic area, trachea, bilaterally mainstems, and segmental carinas.
Bronchoalveolar lavage (BAL) was performed at the {bal_segs} of the {bal_loc}.
{fluid_in} cc of NS was instilled with a return of {fluid_out} cc.
Tracheostomy Tube Change: The upper airway and endotracheal space were suctioned.
The cuff was deflated and the existing {old_brand} cuffed size {tube_size} mm tube was removed. The stoma appeared widely patent;
however, {visual_finding}.

{intervention_text}
A new {new_brand} cuffed size {tube_size} mm tracheostomy tube was placed with an obturator, which was then replaced with an inner cannula and the cuff inflated.
The patient tolerated the procedure well and was in stable condition at the conclusion.
SPECIMENS: * {bal_loc} BAL (Cell count, microbiology, cytology) 


IMPRESSION / PLAN: * Successful tracheostomy tube exchange ({old_brand} to {new_brand} {tube_size} mm) and diagnostic bronchoscopy.
{bal_loc} BAL performed; results pending.

{plan_text}
"""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Operative note for {age}{gender_short}. Dx: {diag_name}. Proc: BAL ({bal_loc}) and Trach Change ({old_brand} -> {new_brand}, size {tube_size}). Finding: {stoma_summary}. Plan: {plan_summary}.",
    
    # Style 2: Dictation
    "Write a pulmonology op report for a {age} year old {gender_long} with {diag_name}. We did a therapeutic aspiration and BAL of the {bal_loc}. Then we exchanged the {tube_size} {old_brand} for a {new_brand}. {dictation_context} Sedation used: {meds_short}.",
    
    # Style 3: Sloppy / Handover
    "{age}yo {gender_short} trach change & BAL. {bal_loc} lavage {fluid_in}cc. Swapped size {tube_size} tube. {stoma_summary} on inspection. No other comps. Attending {attending}.",
    
    # Style 4: Billing Focus
    "Generate procedure note. Codes: 31645, 31624, {code_31502}. Pt: {age} {gender_short}. Diagnosis {diag_code}. Note specific findings: {stoma_summary}. Intervention: {intervention_summary}.",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nDIAGNOSIS: {diag_name}\nPROCEDURE: Trach Change (Size {tube_size}) + BAL ({bal_loc})\nFINDINGS: {stoma_summary}\nACTION: {intervention_summary}"
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
        diag_tup = random.choice(data_pool["diagnosis"])
        meds = random.choice(data_pool["medications"])
        tube_size = random.choice(data_pool["tube_sizes"])
        brands = random.choice(data_pool["tube_brands"]) # (Old, New)
        bal_data = random.choice(data_pool["bal_targets"])
        fluids = random.choice(data_pool["fluids"])
        
        # Sedation time randomization
        sedation_time = str(random.randint(45, 120))
        
        # Select Stoma Scenario
        scenario = random.choice(stoma_scenarios)
        
        # Handle specific scenario logic
        clock = ""
        pos_desc = ""
        stoma_summary = ""
        intervention_summary = ""
        dictation_context = ""
        code_31502 = "31502"
        
        if scenario["condition"] == "erosion":
            pos_data = random.choice(scenario["positions"])
            clock = pos_data[0]
            pos_desc = pos_data[1]
            visual_finding = scenario["visual"].format(clock=clock, pos=pos_desc)
            stoma_summary = f"Stoma erosion at {clock} o'clock"
            intervention_summary = "Packed with iodoform"
            dictation_context = f"Noted erosion at {clock} o'clock so we consulted CT surgery and packed it."
            code_31502 = "31502-22"
        elif scenario["condition"] == "granulation":
            pos_data = random.choice(scenario["positions"])
            clock = pos_data[0]
            visual_finding = scenario["visual"].format(clock=clock)
            stoma_summary = "Granulation tissue found"
            intervention_summary = "Silver nitrate cautery"
            dictation_context = "Found some granulation tissue, cauterized with silver nitrate."
            code_31502 = "31502"
        else: # Healthy
            visual_finding = scenario["visual"]
            stoma_summary = "Stoma healthy/patent"
            intervention_summary = "Routine cleaning"
            dictation_context = "Stoma looked clean, simple change."
            code_31502 = "31502"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diag_name=diag_tup[1],
            diag_code=diag_tup[0],
            bal_loc=bal_data["loc"],
            old_brand=brands[0],
            new_brand=brands[1],
            tube_size=tube_size,
            stoma_summary=stoma_summary,
            plan_summary=scenario["plan_text"].split("\n")[0], # First line of plan
            dictation_context=dictation_context,
            meds_short=meds.split(",")[0] + " etc",
            attending=attending,
            fluid_in=fluids["in"],
            code_31502=code_31502,
            intervention_summary=intervention_summary
        )
        
        # C. Generate Completion (Structured Note)
        # Date logic
        date_str = (datetime.date.today() + datetime.timedelta(days=random.randint(-30, 0))).strftime("%B %d, %Y")
        
        completion = note_template.format(
            date_str=date_str,
            age=age,
            gender_long=gender_tup[0],
            diag_name=diag_tup[1],
            diag_code=diag_tup[0],
            findings_header=scenario["findings_header"].format(clock=clock),
            modifier_text=scenario["modifier_text"],
            attending=attending,
            meds=meds,
            sedation_time=sedation_time,
            bal_segs=bal_data["segs"],
            bal_loc=bal_data["loc"],
            fluid_in=fluids["in"],
            fluid_out=fluids["out"],
            old_brand=brands[0],
            new_brand=brands[1],
            tube_size=tube_size,
            visual_finding=visual_finding,
            intervention_text=scenario["intervention"],
            plan_text=scenario["plan_text"]
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