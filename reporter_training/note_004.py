import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_004"
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
    "age": ["62", "65", "68", "71", "74", "79", "82", "55", "59"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "physician": ["Dr. Smith", "Dr. Johnson", "Dr. Chen", "Dr. Patel", "Dr. Weiss", "Self"],
    "assistant": ["Dr. Lee (Fellow)", "Dr. Gomez (Fellow)", "Dr. Abdi (Fellow)"],
    "indication_detail": [
        "abnormal CT chest findings and neutropenic fever",
        "persistent RUL infiltrate and fevers of unknown origin",
        "cavitary lesion on CT and concern for fungal infection",
        "dense consolidation RLL and failure of outpatient antibiotics",
        "bilateral ground glass opacities and hypoxia"
    ],
    "sedation_meds": [
        {"versed": "2 mg", "fentanyl": "75 mcg"},
        {"versed": "3 mg", "fentanyl": "100 mcg"},
        {"versed": "1 mg", "fentanyl": "50 mcg"},
        {"versed": "4 mg", "fentanyl": "125 mcg"}
    ],
    "duration": [15, 20, 24, 30, 35, 40],
    "airway_finding": [
        'RML was noted to be "fishmouthed"',
        'RML appeared stenotic with concentric narrowing',
        'RML showed mild erythema but was patent',
        'LUL lingula segment appeared edematous',
        'RLL superior segment showed extrinsic compression'
    ],
    "mucus_segments": [
        "RB1, RB2, LB1/2, LB3",
        "RB4, RB5, LB4, LB5",
        "RLL basilar segments and LLL basilar segments",
        "RUL apical segment and LUL apical-posterior segment",
        "diffuse bilateral lower lobes"
    ],
    "bal_right": [
        {"code": "RB2", "desc": "Posterior Segment RUL"},
        {"code": "RB1", "desc": "Apical Segment RUL"},
        {"code": "RB3", "desc": "Anterior Segment RUL"},
        {"code": "RML", "desc": "Right Middle Lobe"},
        {"code": "RB6", "desc": "Superior Segment RLL"}
    ],
    "bal_left": [
        {"code": "LB1/2", "desc": "Apical-Posterior Segment LUL"},
        {"code": "LB3", "desc": "Anterior Segment LUL"},
        {"code": "LB4", "desc": "Superior Lingular Segment"},
        {"code": "LB6", "desc": "Superior Segment LLL"},
        {"code": "LB10", "desc": "Posterior Basal Segment LLL"}
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] CC REFERRED PHYSICIAN: {physician}

INDICATION FOR OPERATION
{patient_name} is a {age}-year-old {gender_long} who presents with {indication_detail}.
The procedure is indicated to obtain specimens for cultures to identify the source of fever and to evaluate for infectious etiology or synchronous processes.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed and informed consent was obtained.

CONSENT
Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field 

Neutropenic fever, concern for infectious etiology 

POSTOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field 

Bilateral mucus plugging 

{airway_finding_short} 

PROCEDURE
Flexible bronchoscopy with diagnostic bronchial alveolar lavage (BAL) 

Bilateral BAL ({bal_r_code} and {bal_l_code}) for infectious workup 

Therapeutic aspiration of mucus plugs ({mucus_segments}) 

Thoracentesis (deferred/not started - CPT 73) 

ATTENDING: [Attending Name] ASSISTANT: {assistant}

SUPPORT STAFF

RN: [RN Name]

RT: [RT Name]

ANESTHESIA
Moderate sedation (99152).
Total sedation time: {duration} minutes (Start {start_time}, Stop {stop_time}).

Versed: {versed_dose}

Fentanyl: {fent_dose} 

MONITORING
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION
Disposable flexible bronchoscope.

ESTIMATED BLOOD LOSS
None.

COMPLICATIONS
None.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Patient Position: Supine 

Initial Airway Inspection: The bronchoscope was introduced via the oral route.
6 mL of 2% lidocaine was applied to the vocal cords for topical anesthesia.
The airways were examined to the subsegmental level bilaterally. {airway_finding_full}. Mucosa appeared normal throughout.
Therapeutic Aspiration: Successful therapeutic aspiration was performed to clear mucus plugging from the following segments:

{mucus_segments_formatted}

Bronchoalveolar Lavage (BAL):


{bal_r_code} ({bal_r_desc}): {bal_vol_in} cc of NS instilled with {bal_vol_out} cc return.
{bal_l_code} ({bal_l_desc}): {bal_vol_in_2} cc of NS instilled with {bal_vol_out_2} cc return.
Samples were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

The patient tolerated the procedure well without immediate complications.
The bronchoscope was removed.

SPECIMENS
BAL {bal_r_code} – Cell count, microbiology, cytology

BAL {bal_l_code} – Cell count, microbiology, cytology 

IMPRESSION / PLAN
Bilateral BAL and therapeutic aspiration successfully performed to address mucus plugging and workup for neutropenic fever.
Await final pathology and cultures.

Post-procedure monitoring per protocol."""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Bronchoscopy note. Pt {age} {gender_short}. Indication: {indication_short}. Findings: Mucus plugs cleared {mucus_segments}. {airway_finding_keyword}. BAL performed {bal_r_code} and {bal_l_code}. Sedation: Versed {versed_dose}, Fent {fent_dose}.",
    
    # Style 2: Dictation Style
    "Generate an op report for a {age} year old {gender_long} referred by {physician}. We did a flex bronch with BAL for {indication_short}. I found {airway_finding_keyword} and mucus plugging in {mucus_segments}. We lavaged the {bal_r_code} and {bal_l_code}.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} neutropenic fever. bronch done. {mucus_segments} mucus plugs suctioned. {bal_r_code}/{bal_l_code} BAL sent for cx. {airway_finding_keyword} noted. used {versed_dose} versed {fent_dose} fent.",
    
    # Style 4: Structured Request
    "Procedure: Bronchoscopy/BAL\nPatient: {age} {gender_short}\nIndication: {indication_detail}\nSegments Lavaged: {bal_r_code}, {bal_l_code}\nFindings: Mucus plugging, {airway_finding_keyword}",
    
    # Style 5: Billing/Coding Focused
    "Please write procedure note for CPT 31624, 31645. Dx R91.8. Patient {age} {gender_short}. Sedation {duration} mins. Findings: {airway_finding_full}. Bilateral BAL performed."
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        physician = random.choice(data_pool["physician"])
        assistant = random.choice(data_pool["assistant"])
        
        indication_detail = random.choice(data_pool["indication_detail"])
        # Derive short indication for prompts
        indication_short = "neutropenic fever" if "neutropenic" in indication_detail else "abnormal CT"
        
        sedation = random.choice(data_pool["sedation_meds"])
        duration = random.choice(data_pool["duration"])
        
        # Calculate time (Mock logic for realism)
        start_hour = random.randint(8, 15)
        start_min = random.choice([0, 15, 30, 45])
        start_time_obj = datetime.datetime(2023, 1, 1, start_hour, start_min)
        end_time_obj = start_time_obj + datetime.timedelta(minutes=duration)
        start_str = start_time_obj.strftime("%H:%M")
        stop_str = end_time_obj.strftime("%H:%M")

        # Findings
        airway_full = random.choice(data_pool["airway_finding"])
        # Extract keyword for prompt
        if "fishmouthed" in airway_full:
            airway_keyword = "fishmouthed RML"
            airway_short = 'RML "fishmouthed" airway'
        elif "stenotic" in airway_full:
            airway_keyword = "stenosis"
            airway_short = "Bronchial stenosis"
        elif "edematous" in airway_full:
            airway_keyword = "edema"
            airway_short = "Airway edema"
        elif "compression" in airway_full:
            airway_keyword = "compression"
            airway_short = "Extrinsic airway compression"
        else:
            airway_keyword = "erythema"
            airway_short = "Mucosal erythema"

        mucus_segs = random.choice(data_pool["mucus_segments"])
        
        # BAL details
        bal_r = random.choice(data_pool["bal_right"])
        bal_l = random.choice(data_pool["bal_left"])
        
        vol_in = random.choice(["60", "80", "100", "120"])
        vol_out = str(int(int(vol_in) * random.uniform(0.2, 0.5)))
        vol_in_2 = random.choice(["60", "80", "100"])
        vol_out_2 = str(int(int(vol_in_2) * random.uniform(0.2, 0.5)))

        # Format Mucus Segments for "Procedure in Detail" (splitting for visual list)
        if "," in mucus_segs:
            # If comma separated, just list them clearly
            mucus_formatted = f"Targeted segments: {mucus_segs}"
        else:
            mucus_formatted = mucus_segs

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            physician=physician,
            indication_short=indication_short,
            indication_detail=indication_detail,
            mucus_segments=mucus_segs,
            airway_finding_keyword=airway_keyword,
            airway_finding_full=airway_full,
            bal_r_code=bal_r["code"],
            bal_l_code=bal_l["code"],
            versed_dose=sedation["versed"],
            fent_dose=sedation["fentanyl"],
            duration=duration
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            patient_name="[Patient Name]", # Kept generic as per request, or could randomize
            age=age,
            gender_long=gender_long,
            physician=physician,
            assistant=assistant,
            indication_detail=indication_detail,
            airway_finding_short=airway_short,
            airway_finding_full=airway_full,
            bal_r_code=bal_r["code"],
            bal_r_desc=bal_r["desc"],
            bal_l_code=bal_l["code"],
            bal_l_desc=bal_l["desc"],
            mucus_segments=mucus_segs,
            mucus_segments_formatted=mucus_formatted,
            duration=duration,
            start_time=start_str,
            stop_time=stop_str,
            versed_dose=sedation["versed"],
            fent_dose=sedation["fentanyl"],
            bal_vol_in=vol_in,
            bal_vol_out=vol_out,
            bal_vol_in_2=vol_in_2,
            bal_vol_out_2=vol_out_2
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