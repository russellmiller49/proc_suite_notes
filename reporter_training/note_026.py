import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_026"
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
    "dates": [
        "January 12, 2024", "February 28, 2024", "March 15, 2024", 
        "April 04, 2024", "May 22, 2024", "June 10, 2024", 
        "July 19, 2024", "August 30, 2024", "September 05, 2024", 
        "October 11, 2024", "November 24, 2024", "December 02, 2024"
    ],
    "age": ["24", "29", "30", "35", "42", "48", "55", "61", "67", "72", "81"],
    "gender_tuple": [("female", "F", "Female"), ("male", "M", "Male")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones", "Dr. Patel"],
    "mrn_prefix": ["442", "991", "102", "339", "882", "551"],
    "dob_year": ["1999", "1993", "1985", "1978", "1965", "1950", "1942"],
    
    # Clinical Variables
    "indication": [
        "complicated effusion", 
        "persistent pleural effusion", 
        "suspected empyema", 
        "loculated pleural collection",
        "hydropneumothorax"
    ],
    "preop_dx": [
        "Complicated Effusion", 
        "Pleural Effusion", 
        "Empyema", 
        "Loculated Effusion"
    ],
    "side_tuple": [("Left", "Right"), ("Right", "Left")],
    
    # Consistency Tuples: (Volume, Character, Lung Status, Drainability, Plan, Plan Logic for Prompt)
    "findings_scenarios": [
        (
            "minimal volume", 
            "anechoic with thin loculations noted", 
            "Atelectasis has improved compared to the previous day", 
            "no significantly drainable fluid identified",
            "Discontinue chest tube",
            "improvement, remove tube"
        ),
        (
            "trace", 
            "simple and anechoic", 
            "Lung re-expansion is noted with minimal residual atelectasis", 
            "no drainable pocket identified",
            "Discontinue chest tube",
            "resolved, pull tube"
        ),
        (
            "small to moderate volume", 
            "complex septated fluid", 
            "Persistent compressive atelectasis is noted", 
            "a loculated pocket amenable to tPA",
            "Continue chest tube; consider intrapleural fibrinonlytics",
            "persistent loculation, keep tube"
        ),
        (
            "moderate volume", 
            "highly echogenic with fibrin stranding", 
            "Lower lobe atelectasis remains unchanged", 
            "fluid is accessible but loculated",
            "Maintain chest tube suction; monitor output",
            "no change, continue suction"
        ),
        (
            "trace residual", 
            "mostly resolved with pleural thickening", 
            "Significant improvement in aeration", 
            "no drainable fluid",
            "Discontinue chest tube and follow up CXR",
            "looks good, stop tube"
        )
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY PROCEDURAL REPORT

DATE OF PROCEDURE: {date}
PATIENT: [REDACTED]
MRN: {mrn}
DOB: [REDACTED] (Age: {age})
SEX: {gender_full}

INDICATION FOR PROCEDURE
The patient is a {age}-year-old {gender_lower} who presents with a {indication}.
The nature, purpose, risks, benefits, and alternatives to the chest ultrasound were discussed with the patient in detail.
The patient indicated a wish to proceed, and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{preop_dx}

POSTOPERATIVE DIAGNOSIS
{preop_dx}; {lung_status_short}.

PROCEDURE
Focused Thoracic Ultrasound (Pleura & Lung) (CPT 76604)

ANESTHESIA/MONITORING
No sedation required.
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
COMPLICATIONS
None.

PROCEDURE IN DETAIL
Focused Thoracic Ultrasound (Pleura & Lung)
Focused thoracic ultrasound was performed and archived.
The patient was positioned in the sitting position. The following findings were documented:

{side_primary} Hemithorax:

Pleural Effusion: A {volume} effusion was identified.
Character: The fluid was {character}.

Lung: Lung sliding was present before the procedure.
{lung_status_long}.

Diaphragm: Normal diaphragmatic motion was observed.

Pleura: The pleura appeared normal.

{side_secondary} Hemithorax:

Not assessed during this focused exam.

Summary of Findings:
Imaging revealed a {volume} posterior collection. {drainability}.

IMPRESSION / PLAN

Focused chest ultrasound of the {side_primary_lower} hemithorax demonstrates a {volume}, {character_short} effusion.
{lung_status_short_summary} with {drainability_summary} amenable to further intervention at this time.

Plan: {plan_action}.
The patient tolerating the procedure well with no immediate complications.
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "{age}yo {gender_short}, {side_primary_lower} chest US. Indication: {indication}. Findings: {volume}, {character_short}. Plan: {plan_action}.",
    
    # Style 2: Dictation Request
    "Please generate a focused thoracic ultrasound report for a {age}-year-old {gender_lower}. We checked the {side_primary_lower} side due to {indication}. We found {volume} fluid that was {character}. {drainability}. Plan is to {plan_action_lower}.",
    
    # Style 3: Sloppy / Quick Note
    "US chest {side_primary_lower}. {age}{gender_short}. {indication}. saw {volume} fluid, {character_short}. {lung_status_short}. {plan_action}.",
    
    # Style 4: Billing & Coding Focus
    "CPT 76604 Thoracic Ultrasound. Dx: {preop_dx}. Side: {side_primary}. Patient {age} {gender_short}. Findings: {volume} effusion. Outcome: {plan_action}.",
    
    # Style 5: Structured Data Input
    "Patient: {age} {gender_short}\nProcedure: Focused Thoracic US\nSide: {side_primary}\nFindings: {volume}, {character}\nPlan: {plan_action}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        date = random.choice(data_pool["dates"])
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (lower, short, Full)
        mrn = f"{random.choice(data_pool['mrn_prefix'])}-{random.randint(1000,9999)}"
        doctor = random.choice(data_pool["doctor"])
        indication = random.choice(data_pool["indication"])
        preop_dx = random.choice(data_pool["preop_dx"])
        
        # Side Logic
        side_tup = random.choice(data_pool["side_tuple"])
        side_primary = side_tup[0]
        side_secondary = side_tup[1]
        
        # Clinical Consistency Logic
        scen = random.choice(data_pool["findings_scenarios"])
        volume = scen[0]
        character = scen[1]
        lung_status_long = scen[2]
        drainability = scen[3]
        plan_action = scen[4]
        prompt_hint = scen[5]
        
        # Derived variables for flow
        character_short = character.split(" ")[0] + " " + character.split(" ")[1] if len(character.split(" ")) > 1 else character
        lung_status_short = "atelectasis improved" if "improved" in lung_status_long.lower() else "atelectasis persistent"
        drainability_summary = "no drainable fluid" if "no" in drainability.lower() else "loculated fluid"
        lung_status_short_summary = "Atelectasis is improved" if "improved" in lung_status_long.lower() else "Atelectasis is unchanged"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_lower=gender_tup[0],
            side_primary_lower=side_primary.lower(),
            side_primary=side_primary,
            indication=indication,
            volume=volume,
            character=character,
            character_short=character_short,
            drainability=drainability,
            plan_action=plan_action,
            plan_action_lower=plan_action.lower(),
            lung_status_short=lung_status_short,
            preop_dx=preop_dx
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            mrn=mrn,
            age=age,
            gender_full=gender_tup[2],
            gender_lower=gender_tup[0],
            indication=indication,
            preop_dx=preop_dx,
            lung_status_short=lung_status_short,
            side_primary=side_primary,
            side_primary_lower=side_primary.lower(),
            volume=volume,
            character=character,
            character_short=character_short,
            lung_status_long=lung_status_long,
            side_secondary=side_secondary,
            drainability=drainability,
            drainability_summary=drainability_summary,
            lung_status_short_summary=lung_status_short_summary,
            plan_action=plan_action
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