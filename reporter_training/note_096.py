import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_096"
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
    "age": ["42", "49", "56", "59", "63", "67", "71", "75", "82", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Harken", "Dr. Weiss"],
    "attending": ["Dr. K. Lee", "Dr. R. Patel", "Dr. S. Johnson", "Dr. M. Gonzales", "Dr. A. Wright"],
    "assistant": ["Dr. T. Nguyen", "Dr. B. Clark", "Dr. L. Davis", "PA-C J. Doe", "PA-C S. Ray"],
    "support_staff_rn": ["Sarah J.", "Mike T.", "Emily R.", "Jessica L.", "David K."],
    "support_staff_rt": ["Tom B.", "Lisa M.", "Chris P.", "Amanda G.", "Robert H."],
    
    # Clinical Variations
    "indication_desc": [
        "presents with respiratory failure",
        "presents with worsening hypoxia",
        "presents with difficulty clearing secretions",
        "admitted for acute respiratory distress",
        "presents with tracheostomy obstruction"
    ],
    "tissue_appearance": [
        "improvement of the yellow necrotic tissue. It remains present, but less prominent",
        "significant granulation tissue at the distal tip",
        "mild inflammation with white fibrinous debris",
        "stable airway anatomy with minimal necrotic debris",
        "moderate amount of thick, tenacious secretions adhering to the walls"
    ],
    "stent_location": [
        "right middle lobe", 
        "left mainstem", 
        "tracheal", 
        "bronchus intermedius", 
        "left upper lobe"
    ],
    "stent_status": [
        "partially occluded with mucus; this was rinsed with saline and cleaned",
        "completely patent with minor secretions; rinsed with saline",
        "showing signs of minor granulation at edges; cleaned and debrided",
        "heavily encrusted with secretions; extensive lavage required",
        "in good position with no significant obstruction"
    ],
    "follow_up": ["2-3 weeks", "1 month", "1 week", "2 weeks", "4-6 weeks"],
    
    # Anatomical segments for aspiration list
    "segments_pool": [
        "Trachea (Proximal 1/3)", "Trachea (Middle 1/3)", "Trachea (Distal 1/3)",
        "Right Mainstem", "Left Mainstem", "Bronchus Intermedius",
        "Carina", "RUL Carina (RC1)", "RML Carina (RC2)", "RLL Basal Segments",
        "LUL Lingula Carina (Lc1)", "Left Carina (LC2)", "LLL Basal Segments"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who {indication_desc}.

The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure.

PREOPERATIVE DIAGNOSIS

J96.90 Respiratory Failure 

POSTOPERATIVE DIAGNOSIS

J96.90 Respiratory Failure 

PROCEDURE

31615 Visualization of windpipe (Tracheobronchoscopy through established tracheostomy incision) 

31646 Therapeutic aspiration subsequent episodes 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: {rn_name} RT: {rt_name}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection The airway was inspected via the tracheostomy tube. Lidocaine was applied to the airway.

The airway anatomy demonstrated {tissue_appearance}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the following segments from mucus and mucus plug: 

{segments_block}

Secretions were cleared.

Stent Maintenance The {stent_location} stent was {stent_status}.

Conclusion The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS

None 

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for respiratory failure.

Follow up bronchoscopy in {follow_up}.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen Anesth bronch via trach on {age}{gender_short}. Ref {ref_physician}. Ind: {indication_short}. Found {tissue_short}. Suctioned {segments_short}. {stent_location} stent {stent_status_short}. Plan fu {follow_up}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} referred by {ref_physician}. We did a trach bronch for respiratory failure. Airway showed {tissue_short}. We aspirated mucus from {segments_short}. Also checked the {stent_location} stent, it was {stent_status_short}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} trach bronch. {ref_physician}. J96.90. suctioned mucus {segments_count} segments. {stent_location} stent cleaned. airway had {tissue_short}. no comps.",
    
    # Style 4: Billing Focus
    "Codes 31615, 31646. Dx J96.90 Respiratory Failure. Pt {age} {gender_short}. Attending {attending}. Procedure: Tracheobronchoscopy, aspiration of secretions ({segments_short}), {stent_location} stent maintenance.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: Resp Failure\nVia: Tracheostomy\nFindings: {tissue_short}\nAction: Aspiration of {segments_short}, {stent_location} stent maintenance ({stent_status_short})\nPlan: F/u {follow_up}"
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
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        rn_name = random.choice(data_pool["support_staff_rn"])
        rt_name = random.choice(data_pool["support_staff_rt"])
        
        indication_desc = random.choice(data_pool["indication_desc"])
        tissue_appearance = random.choice(data_pool["tissue_appearance"])
        stent_location = random.choice(data_pool["stent_location"])
        stent_status = random.choice(data_pool["stent_status"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Dynamic Segments List
        # Select 5-8 random segments
        num_segments = random.randint(5, 8)
        selected_segments = random.sample(data_pool["segments_pool"], num_segments)
        
        # Format for Note (Vertical list with newlines)
        segments_block = "\n\n".join(selected_segments)
        
        # Format for Prompt (Comma separated, abbreviated)
        segments_short = ", ".join(selected_segments[:3]) + " etc"
        segments_count = str(num_segments)
        
        # Shorten descriptions for prompts
        indication_short = "resp failure"
        tissue_short = "necrotic tissue" if "necrotic" in tissue_appearance else "granulation/secretions"
        stent_status_short = "cleaned" if "cleaned" in stent_status else "lavaged"

        # C. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            indication_short=indication_short,
            tissue_short=tissue_short,
            segments_short=segments_short,
            segments_count=segments_count,
            stent_location=stent_location,
            stent_status_short=stent_status_short,
            follow_up=follow_up
        )
        
        # D. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            assistant=assistant,
            rn_name=rn_name,
            rt_name=rt_name,
            indication_desc=indication_desc,
            tissue_appearance=tissue_appearance,
            segments_block=segments_block,
            stent_location=stent_location,
            stent_status=stent_status,
            follow_up=follow_up
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