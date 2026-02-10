import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_086" 
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
    "age": ["49", "52", "55", "57", "61", "64", "68", "72", "75"],
    "gender_tuple": [("female", "F", "she", "her"), ("male", "M", "he", "his")],
    "doctor": ["Dr. Smith", "Dr. Chen", "Dr. Al-Fayed", "Dr. Rodriguez", "Dr. Bowers", "Dr. Patel"],
    "diagnosis_code": ["J98.09", "J95.850", "J44.9"],
    "indication_text": [
        "bronchial stenosis", 
        "airway obstruction evaluation", 
        "dyspnea and history of airway stenosis", 
        "surveillance of bronchial anastomoses"
    ],
    "trachea_desc": [
        "Mildly tortuous, otherwise normal",
        "Normal caliber and configuration",
        "Slight saber-sheath deformity",
        "Mildly dilated"
    ],
    "anastomosis_sutures": [
        "visible intact blue sutures",
        "visible suture material",
        "well-healed suture lines",
        "intact surgical staples"
    ],
    # Right/Left Anastomosis Severity
    "anastomosis_severity": [
        "mild stenosis",
        "moderate stenosis",
        "widely patent",
        "mild narrowing"
    ],
    # RML Specific Findings (Tuple: Severity, Size, Traversal Status, Mucosa)
    "rml_findings": [
        ("moderate stenosis", "~5mm patent", "unable to be traversed", "appeared anthracotic"),
        ("severe stenosis", "~3mm patent", "unable to be traversed", "appeared erythematous"),
        ("mild stenosis", "~6mm patent", "difficult but able to traverse", "appeared normal"),
        ("moderate narrowing", "~4mm patent", "unable to be traversed", "showed mild edema")
    ],
    # Secretions/Aspiration
    "secretions": [
        ("moderate, thin, and clear", "clear mucus"),
        ("scant, white, and mucoid", "white mucus"),
        ("copious, thick, and white", "thick secretions"),
        ("moderate, mucoid", "mucoid secretions")
    ],
    # BAL Volumes (Instilled, Returned)
    "bal_volumes": [
        ("40", "15"),
        ("50", "20"),
        ("30", "10"),
        ("60", "25")
    ],
    "plan_timing": ["2-3 weeks", "4 weeks", "1 month", "6 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}. {gender_pronoun_cap} presents for bronchoscopy for airway evaluation and BAL.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient. The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{dx_code} Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
{dx_code} Other diseases of bronchus, not elsewhere classified
Bronchial stenosis (Right and Left anastomosis)
RML bronchial stenosis

PROCEDURE
Flexible Therapeutic Bronchoscopy
Therapeutic aspiration (initial episode)
Bronchoalveolar lavage (BAL) of Right Middle Lobe

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope

ESTIMATED BLOOD LOSS
None

COMPLICATIONS
None

SPECIMENS
RML BAL - cell count, cultures/micro, cytology

PROCEDURE IN DETAIL
A timeout was performed (confirming the patient's name, procedure type, and procedure location). Sedation was initiated and an LMA was placed. The Flexible Therapeutic Bronchoscope was advanced for airway examination.

Initial Airway Inspection
Larynx: Not fully assessed due to bronchoscopy introduction through LMA.
Vocal Cords: Normal without mass/lesions.
Trachea: {trachea_desc}. Endobronchial topical lidocaine was applied to the vocal cords, main carina, right carina 1, and left carina 2.
Main Carina: Sharp.

Right Lung Findings
Anastomosis: The right anastomosis site was intact with {sutures} at the site. There was {right_anastomosis_status} of the right anastomosis without dehiscence.
Proximal Airways: The RUL and RB1-3 were normal to the segmental level. The bronchus intermedius and more distal lobes/airways were mildly rotated clockwise.
Right Middle Lobe (RML): The RML bronchus presented with {rml_severity}, estimated at {rml_size}; it was {rml_traversal} with the therapeutic bronchoscope. The mucosa {rml_mucosa}. However, there was no associated granulation tissue and this was overall the best the RML has appeared prior to intervention. Patent RB5/RB5 was visualized.
Right Lower Lobe: RLL and RB6-10 had normal anatomic branching to the segmental level.

Left Lung Findings
Anastomosis: The left anastomosis site was intact with {sutures} at the site. There was {left_anastomosis_status} of the left anastomosis.
Proximal Airways: The LUL bronchus and LB1-3 were normal to the first subsegmental level.
Lingula: Patent and LB4-5 were normal to the first subsegmental level; able to traverse the lingular bronchus with the therapeutic bronchoscope.

Interventions
Therapeutic Aspiration: Secretions were {secretion_desc}. Successful therapeutic aspiration was performed to clear {secretion_short} from the trachea, right mainstem bronchus, right upper lobe, bronchus intermedius, right middle lobe, right lower lobe, left mainstem bronchus, left upper lobe, and left lower lobe. All secretions were suctioned to clear.

Bronchoalveolar Lavage (BAL): Performed at the Right Middle Lobe (Lateral Segment RB4 and Medial Segment RB5). {bal_in} cc of NS was instilled, and suction returned {bal_out} cc of NS. Samples were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Conclusion
Residual secretions and saline were suctioned to clear. No bleeding was observed. The bronchoscope was removed. At the conclusion of the operation, the patient's LMA was removed in the operating room and the patient was transported to the recovery room in stable condition. The patient tolerated the procedure well with no immediate complications.

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for airway evaluation and BAL.
RML bronchus appears overall the best seen at the beginning of bronchoscopy, with no granulation tissue or signs of irritation.
Although {rml_traversal_impression}, the RB4 and RB5 subsegments are grossly patent.
To avoid undue inflammation, no dilation or other intervention was performed today.
Repeat bronchoscopy in {plan_timing} to confirm stability of the RML bronchus.
Consideration of interventions depending on the appearance of the airway at that time.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Write an IP op note. Pt: {age}{gender_short}, Ref: {doctor}. Indication: {indication}. Findings: Trachea {trachea_desc_short}. Bilateral anastomoses intact with {right_anastomosis_status}. RML has {rml_severity} ({rml_size}), {rml_mucosa}. BAL RML done ({bal_in}cc in/{bal_out}cc out). Plan: surveillance {plan_timing}.",
    
    # Style 2: Dictation Style
    "Please generate a bronchoscopy report for a {age}-year-old {gender_long} referred by {doctor}. The patient came in for {indication}. We found the right and left anastomoses had {right_anastomosis_status} but were intact. The RML had {rml_severity}, roughly {rml_size}, and we were {rml_traversal} it. Secretions were {secretion_desc}. We did a BAL on the RML. Follow up in {plan_timing}.",
    
    # Style 3: Sloppy / Quick Note
    "{age}yo {gender_short} bronch for {indication}. RML stenosis {rml_size} {rml_mucosa}, no dilation today. Bilateral anastomosis {right_anastomosis_status}. BAL performed RML. {doctor} is referring MD.",
    
    # Style 4: Structured Input
    "Patient Age: {age}\nGender: {gender_long}\nIndication: {indication}\nFindings:\n- Trachea: {trachea_desc}\n- Anastomoses: {right_anastomosis_status}\n- RML: {rml_severity}, {rml_size}\nProcedure: Bronchoscopy + BAL ({bal_in}cc)\nPlan: Repeat {plan_timing}",
    
    # Style 5: Medical Context Focused
    "Generate operative report: Diagnosis {dx_code}. Procedure: Therapeutic Bronchoscopy/BAL. Findings: {rml_severity} at RML, {right_anastomosis_status} at main anastomoses. Secretions {secretion_desc}. {bal_out}cc return on lavage. Patient tolerated well.",
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pro, poss)
        doctor = random.choice(data_pool["doctor"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        indication = random.choice(data_pool["indication_text"])
        trachea_desc = random.choice(data_pool["trachea_desc"])
        sutures = random.choice(data_pool["anastomosis_sutures"])
        
        # Anastomosis status (sync R and L slightly or keep same for consistency)
        right_anastomosis_status = random.choice(data_pool["anastomosis_severity"])
        left_anastomosis_status = random.choice(data_pool["anastomosis_severity"])
        
        # RML Complex logic
        rml_tup = random.choice(data_pool["rml_findings"])
        rml_severity = rml_tup[0]
        rml_size = rml_tup[1]
        rml_traversal = rml_tup[2]
        rml_mucosa = rml_tup[3]
        
        # Secretions
        sec_tup = random.choice(data_pool["secretions"])
        secretion_desc = sec_tup[0]
        secretion_short = sec_tup[1]
        
        # BAL
        bal_tup = random.choice(data_pool["bal_volumes"])
        bal_in = bal_tup[0]
        bal_out = bal_tup[1]
        
        plan_timing = random.choice(data_pool["plan_timing"])

        # Derived logic for Impression
        # If traversal is "unable", impression usually says "unable to traverse"
        # We clean the phrase for the impression section
        rml_traversal_impression = "unable to traverse with the therapeutic bronchoscope"
        if "able" in rml_traversal and "unable" not in rml_traversal:
            rml_traversal_impression = "able to traverse with difficulty"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=indication,
            trachea_desc=trachea_desc,
            trachea_desc_short=trachea_desc.split(",")[0],
            right_anastomosis_status=right_anastomosis_status,
            rml_severity=rml_severity,
            rml_size=rml_size,
            rml_mucosa=rml_mucosa,
            rml_traversal=rml_traversal,
            secretion_desc=secretion_desc,
            bal_in=bal_in,
            bal_out=bal_out,
            plan_timing=plan_timing,
            dx_code=dx_code
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            gender_pronoun=gender_tup[2],      # he/she
            gender_pronoun_cap=gender_tup[2].capitalize(),
            doctor=doctor,
            indication=indication,
            dx_code=dx_code,
            trachea_desc=trachea_desc,
            sutures=sutures,
            right_anastomosis_status=right_anastomosis_status,
            left_anastomosis_status=left_anastomosis_status,
            rml_severity=rml_severity,
            rml_size=rml_size,
            rml_traversal=rml_traversal,
            rml_mucosa=rml_mucosa,
            secretion_desc=secretion_desc,
            secretion_short=secretion_short,
            bal_in=bal_in,
            bal_out=bal_out,
            rml_traversal_impression=rml_traversal_impression,
            plan_timing=plan_timing
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