import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_042"
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
    "indication_tuple": [
        ("Respiratory Failure", "J96.90"),
        ("Acute Hypoxic Respiratory Failure", "J96.01"),
        ("Acute Hypercapnic Respiratory Failure", "J96.02"),
        ("Chronic Respiratory Failure", "J96.10")
    ],
    "medications": [
        "Versed 4 mg, Fentanyl 100 mcg, Etomidate 20 mg, Rocuronium 43 mg",
        "Versed 2 mg, Fentanyl 50 mcg, Propofol 100 mg, Rocuronium 50 mg",
        "Midazolam 3 mg, Fentanyl 100 mcg, Etomidate 18 mg, Succinylcholine 100 mg",
        "Propofol infusion, Fentanyl 150 mcg bolus, Rocuronium 40 mg"
    ],
    "procedure_time": ["90", "107", "115", "120", "95", "130"],
    "trach_size": ["6.0mm", "7.0mm", "8.0mm"],
    "trach_brand": ["Portex", "Shiley"],
    "trach_ring_location": ["1st and 2nd", "2nd and 3rd"],
    # Tuple: (Lobe Name for Prompt, Specific Segments for Note)
    "bal_location_tuple": [
        ("RML", "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)"),
        ("RUL", "Apical Segment (RB1) and Posterior Segment (RB2)"),
        ("LUL", "Lingula Superior (LB4) and Inferior (LB5) Segments"),
        ("LLL", "Superior Segment (LB6) and Posterior Basal Segment (LB10)")
    ],
    "secretions_desc": [
        "Copious thick and thin light-yellow mucus/secretions",
        "Moderate amount of thick white mucoid secretions",
        "Copious purulent green secretions",
        "Thin, blood-tinged secretions",
        "Thick tan tenacious secretions"
    ],
    "peg_size": ["18Fr", "20Fr", "22Fr", "24Fr"],
    "peg_bumper_depth": ["1.5 cm", "2.0 cm", "2.5 cm", "3.0 cm", "3.5 cm"],
    "peg_incision_adjustment": [
        "a new more lateral insertion site was chosen where no hepatic tissue was identified",
        "the standard insertion site was utilized as no hepatic tissue was identified",
        "a slightly more medial approach was taken to avoid colonic interposition"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} with {indication_text}.
The nature, purpose, risks, benefits, and alternatives to the procedures were discussed.

PREOPERATIVE DIAGNOSIS
{indication_code} {indication_text}

POSTOPERATIVE DIAGNOSIS
{indication_code} {indication_text}

PROCEDURE
Therapeutic aspiration, initial episode (31645)
Bronchoscopy with bronchoalveolar lavage (BAL) (31624)
Percutaneous tracheostomy (incision of windpipe) (31600)
Esophagogastroduodenoscopy, flexible, transoral with directed placement of percutaneous gastrostomy tube (43246)
Ultrasound of Neck (76536)

ANESTHESIA
Moderate sedation
Medications: {medications}
Start time: 1513 | Stop time: 1700 | Total time: {total_time} minutes
Administered by ICU RN

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer present throughout the entire procedure. The patient was monitored continuously one-to-one by the attending physician while anesthesia was administered.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope.

ESTIMATED BLOOD LOSS
Minimum

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Supine

Bronchoscopy and Airway Inspection
The endotracheal tube was in good position. The pharynx, larynx, and vocal cords were not assessed due to bronchoscopy introduction through the ETT.
Trachea: Distal 1/3 normal.
Main Carina: Sharp.
Right Lung Proximal Airways: Normal anatomic branching to segmental level; no evidence of mass, lesions, bleeding, or other endobronchial pathology.
Left Lung Proximal Airways: Normal anatomic branching to segmental level; no evidence of mass, lesions, bleeding, or other endobronchial pathology.
Mucosa: Normal.
Secretions: {secretions}.

Therapeutic Aspiration and BAL
Successful therapeutic aspiration was performed to clean mucus from the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2).
Bronchoalveolar lavage (BAL) was performed at the {bal_segments}.
Instilled: 40 cc NS
Returned: 25 cc NS
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Percutaneous Tracheostomy
Neck ultrasound was performed at the proposed insertion site. The bronchoscope was retracted into the ETT and the ETT retracted into the subglottic space under direct visualization. The inferior border of the cricoid and proximal tracheal rings were visualized.
The anterior neck was prepped and draped in sterile fashion.
Anesthesia: Lidocaine 1% (3 ml) was injected into the anterior neck.
Incision: A 1 cm horizontal incision was made with a #10 blade down through the subcutaneous tissue, just inferior to the cricoid cartilage.
Access: The introducer needle passed between the {trach_rings} tracheal rings into the trachea under direct visualization.
A J-wire was passed through the catheter, visualized with the bronchoscope.
Dilation: The site was dilated using the 14Fr introducing dilator passed over the wire. The 14Fr dilator was removed, and an 8Fr guiding catheter was placed over the wire until the safety ridge was at skin level. The tissue dilator was placed over the guiding catheter until the positioning mark was visualized via the bronchoscope. The tissue dilator was removed, leaving the guiding catheter and wire assembly in place.
Placement: A {trach_brand} {trach_size} cuffed tracheostomy tube with appropriate dilator was introduced over the guiding catheter into the trachea under direct visualization. The dilator, guiding catheter, and J-wire were removed, leaving the tracheostomy tube in place.

Confirmation: Good position was confirmed bronchoscopically. The ETT was removed and the ventilator connected to the tracheostomy tube.
Hemostasis/Dressing: Surgicel was placed preemptively around the site to reduce bleeding. A Lyofoam drain sponge was placed under the tracheostomy tube prior to suturing into place.

Percutaneous Endoscopic Gastrostomy (PEG)
Under sterile prep and draping, the abdomen was evaluated. Ultrasound identified hepatic tissue just under the standard/traditional PEG insertion site (2 cm below costal margin on the left). As such, {peg_site_adj}.
Access: The scope was introduced through the mouth; the stomach was reached within 10 seconds with continuous insufflation. The point of digital pressure was identified and transillumination was accomplished successfully.
Placement: A 1 cm incision was made and a 14ga angiocath introduced. Using modified Seldinger technique, a wire was introduced and pulled through the mouth using pull-through technique. The wire was linked to the {peg_size} PEG catheter.

Positioning: The wire was pulled through the abdominal wall and the PEG tube positioned correctly with the bumper at {peg_bumper}. Remaining air was suctioned out and complete apposition of the stomach and esophagus was seen.
Total procedural time for PEG was 20 minutes.

The patient tolerated the procedure well with no immediate complications. At the conclusion, the patient was in stable condition.

SPECIMENS
{bal_lobe_short} BAL (Cell Count, Cytology, Microbiology)

IMPRESSION / PLAN
{age}-year-old {gender_long} who presented for tracheostomy and PEG tube placement.
Post-procedure CXR.
Anticipate suture removal in 7 days.
Anticipate trach change in 10 days.

PEG Instructions:
PEG can be used for medications 6 hrs post procedure (@2200).
PEG (or NG tube) can be used for feeds 6 hrs post procedure (@2200).
No enteral feeding prior.
OK to restart systemic anticoagulation @2200, if needed.
If required to place gauze underneath the skin bumper, please use only 1 thin layer and change as needed to avoid tension on the gastric cuff.
Please call the Interventional Pulmonary fellow on call should there be any issues with the PEG.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Generate op note: {age}yo {gender_short}, {indication_text}. Procedures: Trach ({trach_brand} {trach_size}), PEG ({peg_size}), BAL ({bal_lobe_short}). {secretions_short} secretions seen. PEG bumper at {peg_bumper}.",

    # Style 2: Dictation
    "Please write an operative report for a {age}-year-old {gender_long} with {indication_text}. We performed a Percutaneous Tracheostomy placing a {trach_size} {trach_brand} tube at the {trach_rings} rings. We also did a PEG placement using a {peg_size} tube and a BAL of the {bal_lobe_short}. Note that {secretions_short} secretions were aspirated.",

    # Style 3: Sloppy / Quick Input
    "{age} {gender_short} {indication_text}. Trach {trach_size} {trach_brand}, PEG {peg_size}, BAL {bal_lobe_short}. secretions: {secretions_short}. no complications.",

    # Style 4: Billing Focused
    "Procedure Codes: 31645, 31624, 31600, 43246, 76536. Patient: {age} {gender_short}. Dx: {indication_code}. Details: Trach ({trach_size} {trach_brand}), PEG ({peg_size}), BAL ({bal_lobe_short}). Findings: {secretions_short}.",

    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nINDICATION: {indication_text}\nPROCEDURES: Trach ({trach_brand} {trach_size}), PEG ({peg_size}), BAL\nBAL SITE: {bal_lobe_short}\nFINDINGS: {secretions_short} secretions."
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
        indication_tup = random.choice(data_pool["indication_tuple"])
        meds = random.choice(data_pool["medications"])
        total_time = random.choice(data_pool["procedure_time"])
        
        trach_size = random.choice(data_pool["trach_size"])
        trach_brand = random.choice(data_pool["trach_brand"])
        trach_rings = random.choice(data_pool["trach_ring_location"])
        
        bal_tup = random.choice(data_pool["bal_location_tuple"])
        
        secretions = random.choice(data_pool["secretions_desc"])
        # Extract a short summary of secretions for the prompt (e.g., "Copious thick" from "Copious thick and thin...")
        secretions_short = " ".join(secretions.split()[:3]) 
        
        peg_size = random.choice(data_pool["peg_size"])
        peg_bumper = random.choice(data_pool["peg_bumper_depth"])
        peg_adj = random.choice(data_pool["peg_incision_adjustment"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            indication_text=indication_tup[0],
            indication_code=indication_tup[1],
            trach_brand=trach_brand,
            trach_size=trach_size,
            trach_rings=trach_rings,
            peg_size=peg_size,
            peg_bumper=peg_bumper,
            bal_lobe_short=bal_tup[0],
            secretions_short=secretions_short
        )

        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            indication_text=indication_tup[0],
            indication_code=indication_tup[1],
            medications=meds,
            total_time=total_time,
            secretions=secretions,
            bal_segments=bal_tup[1],
            trach_rings=trach_rings,
            trach_brand=trach_brand,
            trach_size=trach_size,
            peg_site_adj=peg_adj,
            peg_size=peg_size,
            peg_bumper=peg_bumper,
            bal_lobe_short=bal_tup[0]
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