import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_079"
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
    "age": ["55", "59", "60", "62", "67", "71", "74", "80"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "intubation_duration": ["~2 weeks", "~10 days", "~3 weeks", "~12 days"],
    "indication_mass": ["neck mass", "mediastinal mass", "large thyroid mass", "paratracheal mass"],
    
    # Tube/Airway Findings
    "tube_condition": [
        "flaking/peeling plastic along its length", 
        "significant biofilm accumulation", 
        "kinking at the proximal end", 
        "mucus plugging at the tip"
    ],
    "secretion_type": [
        "large burden, thick, and clear", 
        "moderate burden, purulent", 
        "copious, mucoid, and white", 
        "tenacious and blood-tinged"
    ],
    
    # Anatomy / BAL
    "bal_location_tuple": [
        ("Right Middle Lobe (RML)", "Lateral Segment (RB4) and Medial Segment (RB5)"),
        ("Right Lower Lobe (RLL)", "Superior Segment (RB6) and Basal Segments"),
        ("Left Upper Lobe (LUL)", "Lingula Segments (LB4, LB5)")
    ],
    
    # Rigid Bronch Details
    "rigid_barrel_color": ["black", "red", "metallic", "blue"],
    "stenosis_location": ["proximal trachea (subglottic space)", "mid-trachea", "distal trachea"],
    "stenosis_length": ["3.5 cm", "4.0 cm", "5.5 cm", "6.0 cm"],
    "vocal_cord_side": ["Left", "Right"],
    
    # EBUS Logic (Bundled for consistency)
    "ebus_scenarios": [
        {
            "stations": "11Rs, 4R, 7, 4L, 11L",
            "rose_result": "suggestive of malignancy",
            "pattern_desc": "Type 3 elastographic pattern (predominantly stiff/blue)",
            "dx_impres": "Malignancy"
        },
        {
            "stations": "4R, 4L, 7",
            "rose_result": "suggestive of Small Cell Carcinoma",
            "pattern_desc": "Type 3 elastographic pattern (predominantly stiff/blue)",
            "dx_impres": "Small Cell Carcinoma"
        },
        {
            "stations": "11L, 7, 4L",
            "rose_result": "suggestive of Squamous Cell Carcinoma",
            "pattern_desc": "Type 2 elastographic pattern (mixed soft/stiff)",
            "dx_impres": "Squamous Cell Carcinoma"
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] 
INDICATION FOR OPERATION: Patient is a {age}-year-old {gender_long} who presents with respiratory failure and {indication_mass}.
The patient required bronchoscopy for evaluation of the neck mass with extrinsic compression.
The patient had a history of prolonged intubation at an outside hospital ({intubation_duration}).

CONSENT: The nature, purpose, risks, benefits, and alternatives to the procedure were discussed. The patient/surrogate understood and agreed to proceed.

PREOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure 

POSTOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure 
Tracheal stenosis / Extrinsic compression 
{dx_impres} (Preliminary ROSE positive) 

PROCEDURE
Therapeutic aspiration, initial episode (31645) 
Bronchoscopy with Bronchoalveolar Lavage (BAL) (31624) 
EBUS sampling 3 or more nodes (31653) 
Ultrasound Elastography (Parenchyma, First Target, Additional Targets) (76981, 76982, 76983) 
Balloon dilation (31630) 
Destruction of tumor or relief of stenosis by any method other than excision (31641) 
Intra-operative ENT consultation for tracheostomy 

ANESTHESIA: General Anesthesia 
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION: Rigid Tracheoscope, Flexible Therapeutic Bronchoscope, Flexible Hybrid (Pediatric) Bronchoscope, Linear EBUS.

ESTIMATED BLOOD LOSS: Minimum 
COMPLICATIONS: Injury to {vocal_cord_side} vocal cord.

PROCEDURE IN DETAIL
Initial Assessment and Airway Management: After the successful induction of anesthesia, a timeout was performed.
The patient was positioned supine. Initial inspection revealed the endotracheal tube (ETT) in good position, though the tube itself had {tube_condition}.
The pharynx, larynx, and vocal cords were not initially assessed due to bronchoscopy introduction through the ETT.

Therapeutic Aspiration and Lavage: Secretions were noted to be a {secretion_type} bilaterally.
Successful therapeutic aspiration was performed to clear mucus from the Distal 1/3 Trachea, Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, and segmental carinas.
Bronchoalveolar lavage (BAL) was performed at the {bal_location_full} of the {bal_location_lobe}.
40 cc of normal saline was instilled with 15 cc returned. Samples were sent for Cell Count, Microbiology, and Cytology.

Rigid Bronchoscopy and Difficult Intubation: A {rigid_barrel_color} rigid barrel tracheoscope was introduced side-by-side with the ETT.
Upon removal of the ETT, moderate blood was noted in the oropharynx, and there was anterior and {vocal_cord_side} displacement of the airway.
The glottic inlet could not be fully appreciated, and the patient began to desaturate; intubation was aborted and the patient was re-recruited with bag-mask ventilation.
For the second attempt, a short barrel was used.
The vocal cords were only partially identified, but the rigid bronchoscope was successfully advanced into the trachea.
Once positioned at the mid-trachea, jet ventilation was initiated. This process constituted a very challenging rigid bronchoscopy intubation due to deviated upper airway anatomy and stenosis.

Findings: Severe extrinsic compression from the posterior membrane was noted at the {stenosis_location}, displacing the trachea anteriorly.
Stenosis Measurements: Distance from vocal folds to stenosis: 5 mm; Length of stenosis: {stenosis_length};
Distance from bottom of stenosis to carina: 5.7 cm.

Vocal Cords: {vocal_cord_side} vocal cord erythema/injury was noted.

EBUS Staging and Elastography: Endobronchial ultrasound (EBUS) was performed for diagnostic staging.
All lymph node stations were assessed, and those >=5 mm were sampled.
Elastography was used to assess tissue stiffness (Type 1–3) to guide biopsy selection.
Stations sampled included: {ebus_stations}.
Patterns noted included {ebus_pattern}, raising concern for malignancy.
Tracheal Mass (>=10mm): 8 EBUS-guided TBNA biopsies and 5 transbronchial cryobiopsies were obtained.

ROSE Results: Preliminary ROSE cytology was reported as adequate and {rose_result}.

Tracheostomy (ENT Consult): Given the prolonged intubation, distorted anatomy, tracheal stenosis, and possible vocal cord injury, an intraoperative ENT consultation was requested.
The ENT team reviewed the case and proceeded with surgical tracheostomy placement under the same anesthesia.
The rigid tracheoscope was removed, and the patient underwent fiberoptic intubation with a 7.0 ETT to facilitate the ENT procedure.

Conclusion: The patient tolerated the procedure well with no immediate complications. Care was turned over to the anesthesia and ENT teams for tracheostomy.

SPECIMENS
{bal_location_lobe} BAL (Cell count, Micro, Cyto) 
TBNA: Stations {ebus_stations}, and Tracheal Mass 
Cryobiopsy: Tracheal Mass 

IMPRESSION / PLAN
Bronchoscopy performed for {indication_mass} with extrinsic compression; severe compression and tracheal stenosis identified.
Malignancy: Preliminary ROSE cytology {rose_result} (final pathology pending).
Airway: Difficult airway requiring rigid bronchoscopy; patient transitioned to ENT for tracheostomy placement.

Plan:
Post-procedure CXR.
Follow up BAL, TBNA, and cryobiopsy results.
Continued care per primary team.
"""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Note: {age}yo {gender_short}, {indication_mass}. Hx {intubation_duration} intubation. Rigid bronch + EBUS performed. Findings: {stenosis_location} compression, len {stenosis_length}. {vocal_cord_side} VC injury. ROSE: {dx_impres}. ENT consult for trach done.",
    
    # Style 2: Dictation
    "Please draft a procedure note for a {age}-year-old {gender_long} presenting with {indication_mass} and respiratory failure after {intubation_duration} of intubation. We did a rigid bronchoscopy, EBUS, and lavage of the {bal_location_lobe}. There was severe stenosis at the {stenosis_location}. ROSE showed {dx_impres}. We handed off to ENT for a tracheostomy.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} with {indication_mass}. complicated airway, had to use rigid scope. {stenosis_length} stenosis found. EBUS stations {ebus_stations} sampled. {vocal_cord_side} cord looks injured. ENT came in for trach.",
    
    # Style 4: Billing Focus
    "Generate report for codes 31645, 31624, 31653, 31630, 31641. Dx J96.90. Pt: {age} {gender_short}. Findings: {stenosis_location} stenosis, {dx_impres} on ROSE. Complication: {vocal_cord_side} VC trauma. Disposition: ENT Tracheostomy.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication_mass} / {intubation_duration} intubation\nProcedure: Rigid Bronch, EBUS, BAL ({bal_location_lobe})\nFindings: Stenosis length {stenosis_length}, {vocal_cord_side} VC erythema\nOutcome: Tracheostomy by ENT"
]

# ==========================================
# 5. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, possessive)
        intubation_duration = random.choice(data_pool["intubation_duration"])
        indication_mass = random.choice(data_pool["indication_mass"])
        tube_condition = random.choice(data_pool["tube_condition"])
        secretion_type = random.choice(data_pool["secretion_type"])
        
        # BAL Logic
        bal_tup = random.choice(data_pool["bal_location_tuple"])
        bal_lobe = bal_tup[0]
        bal_segs = bal_tup[1]
        
        # Rigid Bronch Logic
        rigid_barrel_color = random.choice(data_pool["rigid_barrel_color"])
        stenosis_location = random.choice(data_pool["stenosis_location"])
        stenosis_length = random.choice(data_pool["stenosis_length"])
        vocal_cord_side = random.choice(data_pool["vocal_cord_side"])
        
        # EBUS Logic
        ebus_scenario = random.choice(data_pool["ebus_scenarios"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication_mass=indication_mass,
            intubation_duration=intubation_duration,
            stenosis_location=stenosis_location,
            stenosis_length=stenosis_length,
            vocal_cord_side=vocal_cord_side,
            dx_impres=ebus_scenario["dx_impres"],
            bal_location_lobe=bal_lobe,
            ebus_stations=ebus_scenario["stations"]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication_mass=indication_mass,
            intubation_duration=intubation_duration,
            tube_condition=tube_condition,
            secretion_type=secretion_type,
            bal_location_lobe=bal_lobe,
            bal_location_full=bal_segs,
            rigid_barrel_color=rigid_barrel_color,
            vocal_cord_side=vocal_cord_side,
            stenosis_location=stenosis_location,
            stenosis_length=stenosis_length,
            ebus_stations=ebus_scenario["stations"],
            ebus_pattern=ebus_scenario["pattern_desc"],
            rose_result=ebus_scenario["rose_result"],
            dx_impres=ebus_scenario["dx_impres"]
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