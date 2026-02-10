import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_048"
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
    "age": ["55", "62", "65", "68", "71", "74", "79", "83", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones", "Dr. Patel"],
    "attending": ["Dr. Al-Fayed", "Dr. Stevens", "Dr. Wong", "Dr. Gathers", "Dr. House", "Dr. Wilson"],
    "indication": ["Respiratory Failure", "Hypoxia due to secretion retention", "Mucus plugging", "Acute Respiratory Failure with Hypoxia"],
    "icd_code": ["J96.90", "J96.00", "J96.01", "J96.21"],
    
    "secretion_type": [
        "thick, foul-smelling secretions", 
        "copious, tenacious purulent secretions", 
        "moderate amount of thick white mucus", 
        "large volume of blood-tinged mucoid secretions", 
        "inspissated mucus plugs"
    ],
    "edema_status": [
        "Moderate edema", 
        "Severe edema", 
        "Mild edema", 
        "No significant edema"
    ],
    "trach_finding": [
        "A small shelf of tissue", 
        "A rim of granulation tissue", 
        "Mild anterior trachealomalacia", 
        "Healthy tracheal mucosa with no obstruction"
    ],
    "trach_brand": [
        "Portex cuffed Trach ISO/ID", 
        "Shiley cuffed Tracheostomy Tube", 
        "Bivona Fome-Cuf"
    ],
    "trach_size": ["6.0mm", "7.0mm", "7.5mm", "8.0mm", "9.0mm"],
    
    # Variations of segments cleaned
    "segments_list": [
        # Variation A (Full Tree)
        "Supraglottic, Vocal Cord, Subglottic\n\nTrachea (Proximal, Middle, and Distal 1/3)\n\nRight Mainstem, Bronchus Intermedius, RUL Carina (RC1), RML Carina (RC2)\n\nLeft Mainstem, Carina, LUL Lingula Carina (Lc1), and Left Carina (LC2).",
        # Variation B (Right Dominant)
        "Supraglottic and Trachea\n\nRight Mainstem, RUL, RML, and RLL basilar segments (specifically RB8, RB9).\n\nLeft system clear.",
        # Variation C (Bilateral Mains)
        "Trachea and bilateral mainstem bronchi only.\n\nDistal airways appeared patent.",
        # Variation D (Plugging focus)
        "Heavy plugging removed from the Left Lower Lobe (LB10) and Right Middle Lobe."
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication_lower}.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed. The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail. The patient wished to proceed and informed consent was signed.

PREOPERATIVE DIAGNOSIS

{icd_code} {indication}

POSTOPERATIVE DIAGNOSIS

{icd_code} {indication}

PROCEDURE

Therapeutic aspiration, initial episode (CPT 31645) 

Tracheostomy tube change (CPT 31899 Unlisted Procedure) 

ATTENDING {attending}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection After adequate sedation, an iGel airway was placed by anesthesia and ventilation continued via the tracheostomy tube.
Glottic Findings: There was a large amount of {secretion_type} at the level of the glottis, which were therapeutically aspirated.
{edema_status} was noted, and the true vocal cords were unable to be visualized.
Tracheal Findings: {trach_finding} was noted along the 12 o'clock to 2 o'clock position where the tracheostomy tube enters.
This did not cause significant obstruction. With the cuff of the tracheostomy tube deflated, the bronchoscope easily passed the tracheostomy tube.
Therapeutic Aspiration The bronchoscope was removed and introduced into the existing tracheostomy tube.
Successful therapeutic aspiration was performed to clean out mucus and mucus plugs from the following segments:

{segments_list}

Tracheostomy Tube Change Under direct visualization from the glottis, the cuff was deflated and the tracheostomy tube was easily removed.
The stoma appeared widely patent and some granulation tissue was immediately visualized.
The new tracheostomy tube was placed with the obturator in place.
The obturator was removed, the inner cannula was placed, and the cuff was inflated under direct visualization, confirming occlusion of the entire trachea.
Device Exchange Details: Percutaneous tracheostomy was changed from:

{trach_brand} size {trach_size} suctionaid


To: {trach_brand} size {trach_size} suctionaid.
The exchange was performed without issue.

Conclusion Pictures and videos were taken from the tracheostomy tube and from the mouth.
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS None 

IMPRESSION / PLAN

{age}-year-old {gender_long} presented for bronchoscopy for {indication_lower}.
Successful therapeutic aspiration of {secretion_type} and mucus plugs throughout the tracheobronchial tree.
Tracheostomy tube exchanged successfully from {trach_brand} {trach_size} to {trach_brand} {trach_size}.


Follow-up: Tracheostomy change in ~3 months.
Orders: DME order for {trach_brand} {trach_size} inner cannulas.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen report: {age}{gender_short}, {indication_lower}. Bronch aspiration + trach change. Found {secretion_type_short}. Trach {trach_size} exchanged.",
    
    # Style 2: Dictation
    "Please generate an operative note for a {age} year old {gender_long} patient referred by {ref_physician}. The indication is {indication_lower}. We performed therapeutic aspiration and a trach change. Findings included {secretion_type} and {trach_finding_lower}. Swapped {trach_size} tube for same.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {indication_lower}. bronch done by {attending}. cleaned out {secretion_type_short}. changed the {trach_size} trach. no comps.",
    
    # Style 4: Billing Focus
    "Codes 31645, 31899. Dx {icd_code}. {age} {gender_short}. Procedure: Aspiration of {secretion_type_short} and exchange of {trach_size} tracheostomy tube.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedure: Therapeutic Aspiration & Trach Change\nFindings: {secretion_type}, {trach_finding}\nPlan: Exchange {trach_size} tube."
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
        
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        indication = random.choice(data_pool["indication"])
        icd_code = random.choice(data_pool["icd_code"])
        
        secretion_type = random.choice(data_pool["secretion_type"])
        edema_status = random.choice(data_pool["edema_status"])
        trach_finding = random.choice(data_pool["trach_finding"])
        trach_brand = random.choice(data_pool["trach_brand"])
        trach_size = random.choice(data_pool["trach_size"])
        segments_list = random.choice(data_pool["segments_list"])
        
        # Generate random date
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
        date_str = date_obj.strftime("%m/%d/%Y")

        # Helpers for prompts
        secretion_type_short = secretion_type.split(" ")[0] + " secretions" # e.g., "thick secretions"
        trach_finding_lower = trach_finding.lower()
        indication_lower = indication.lower()

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            indication=indication,
            indication_lower=indication_lower,
            ref_physician=ref_physician,
            attending=attending,
            secretion_type=secretion_type,
            secretion_type_short=secretion_type_short,
            trach_finding=trach_finding,
            trach_finding_lower=trach_finding_lower,
            trach_size=trach_size,
            icd_code=icd_code
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            ref_physician=ref_physician,
            age=age,
            gender_long=gender_long,
            indication=indication,
            indication_lower=indication_lower,
            icd_code=icd_code,
            attending=attending,
            secretion_type=secretion_type,
            edema_status=edema_status,
            trach_finding=trach_finding,
            segments_list=segments_list,
            trach_brand=trach_brand,
            trach_size=trach_size
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