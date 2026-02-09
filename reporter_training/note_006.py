import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_006"
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
    "age": ["45", "52", "64", "68", "71", "74", "79", "84", "88", "91"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "respiratory failure",
        "acute on chronic respiratory failure",
        "ventilator dependence",
        "inability to wean from mechanical ventilation",
        "prolonged intubation"
    ],
    "diagnosis_code": ["J96.90", "J96.00", "J96.20", "J96.10"],
    "lidocaine_vol": ["2 mL", "3 mL", "4 mL", "5 mL"],
    "incision_size": ["1 cm", "1.5 cm", "small vertical"],
    "tube_size": ["6.0", "7.0", "8.0"],
    "tube_type": ["Portex", "Shiley"],
    "airway_segments": [
        "Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina",
        "RUL, RML, and RLL bronchi",
        "bilateral mainstems and lower lobes",
        "LUL, Lingula, and Left Lower Lobe",
        "trachea, carina, and mainstem bronchi",
        "Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2)"
    ],
    "secretions": ["mucus and blood", "thick purulent secretions", "copious secretions", "blood-tinged mucus", "moderate white secretions"],
    "ultrasound_finding": [
        "There were no significant vessels or masses noted overlying the tracheostomy site",
        "No abnormal vasculature was identified in the surgical field",
        "Anatomy was normal with no intervening vessels identified"
    ],
    "drain_type": ["Lyofoam drain sponge", "split gauze drain sponge", "Allevyn foam"],
    "hemostatic_agent": ["Surgicel", "Gelfoam", "Silver Nitrate"],
    "follow_up_days": ["5", "7", "10", "14"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [REDACTED] 
INDICATION FOR OPERATION: [REDACTED] is an {age}-year-old {gender_long} who presents with {indication}. The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail. The patient indicated a wish to proceed with the procedure and informed consent was signed.

CONSENT: Obtained before the procedure. Its indications, potential complications, and alternatives were discussed with the patient or surrogate. The patient or surrogate read and signed the provided consent form or provided consent over the phone. The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
{diagnosis_code} Respiratory Failure

POSTOPERATIVE DIAGNOSIS
{diagnosis_code} Respiratory Failure

PROCEDURE
Therapeutic aspiration (CPT 31645)
Percutaneous Tracheostomy (CPT 31600)
Tracheobronchoscopy via Tracheostomy (CPT 31615)
Ultrasound of Neck (CPT 76536)

ANESTHESIA: General Anesthesia

MONITORING: Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION: Disposable Bronchoscope; Percutaneous Tracheostomy Kit; Ultrasound.

ESTIMATED BLOOD LOSS: None

COMPLICATIONS: None

PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and procedure location.

Neck Ultrasound:
Neck Ultrasound was performed to evaluate for any abnormal vessels, masses, or structures at the site of the percutaneous tracheostomy. {ultrasound_finding} on examination from the laryngeal prominence to the sternal notch.

Therapeutic Aspiration:
Successful therapeutic aspiration was performed to clean out the {airway_segments} from {secretions}.

Percutaneous Tracheostomy:
The bronchoscope was retracted into the ETT tube and the ET tube retracted into the subglottic space under direct visualization. The inferior border of the cricoid along with the proximal tracheal rings were visualized. Next, the anterior neck was prepped and draped in the usual sterile fashion.

Lidocaine 1% ({lidocaine_vol}) was injected into the anterior neck. A {incision_size} incision was made vertically with a #10 blade down through the subcutaneous tissue, just inferior to the cricoid cartilage. The introducer needle was passed between the 1st and 2nd tracheal rings and into the trachea under direct visualization. This needle was removed, and the introducer catheter over needle was advanced.

Next, a J-wire was passed through the catheter, also visualized with the bronchoscope. The site was then dilated using the 14 Fr introducing dilator passed over the wire. The 14 Fr dilator was then removed from the guide wire and an 8 Fr guiding catheter placed over the guide wire until the safety ridge on the guiding catheter was at skin level. A Portex dilator was placed over the guiding catheter until the positioning mark was visualized via the bronchoscope. The Portex dilator was then removed leaving the guiding catheter and guide wire assembly in place, all under direct visualization bronchoscopically.

Finally, a {tube_type} {tube_size} tracheostomy tube with appropriate dilator was introduced over the guiding catheter into the trachea under direct visualization. The dilator, guiding catheter, and J-wire were then removed and the tracheostomy tube left in place.

Tracheobronchoscopy via Tracheostomy:
Tracheobronchoscopy was performed with insertion of bronchoscope through the tracheostomy to perform airway clearance and confirm tracheostomy position.

Conclusion:
The Endotracheal tube was then removed and the ventilator connected to the tracheostomy tube. {hemostatic_agent} was placed preemptively around the tracheostomy site to reduce bleeding. A {drain_type} was placed under the tracheostomy tube prior to suturing into place.

The patient tolerated the procedure well. There were no immediate complications. The staff physician was present throughout the entire procedure. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS: None

IMPRESSION / PLAN
{age}-year-old {gender_long} presented for bronchoscopy for tracheostomy.
Follow-up in {follow_up_days} days for tracheostomy change.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen Anesth. {age}yo {gender_short}. Indication: {indication}. Proc: Perc Trach ({tube_size} {tube_type}), Tx Aspiration ({airway_segments}), Neck US. Lidocaine {lidocaine_vol}. No complications. F/u {follow_up_days} days.",

    # Style 2: Dictation
    "Write an op report for a {age}-year-old {gender_long} presenting with {indication}. We did a perc trach using a {tube_size} {tube_type} tube and therapeutic aspiration of the {airway_segments}. US neck showed {ultrasound_finding_short}. Used {lidocaine_vol} lido. Placed {hemostatic_agent} and {drain_type}.",

    # Style 3: Sloppy / Quick
    "{age} {gender_short} trach and bronch. dx {diagnosis_code}. cleaned out {secretions} from {airway_segments}. trach size {tube_size} {tube_type}. no vessels on US. {incision_size} incision. stable to RR.",

    # Style 4: Billing Focus
    "CPT 31600, 31645, 31615, 76536. Dx: {diagnosis_code} ({indication}). Patient: {age} {gender_short}. Trach size: {tube_size}. Aspiration: {airway_segments}. No complications.",

    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedures: Percutaneous Tracheostomy, Therapeutic Aspiration, Neck US\nTube: {tube_size} {tube_type}\nFindings: {secretions} in {airway_segments}\nUS: {ultrasound_finding_short}"
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
        indication = random.choice(data_pool["indication"])
        diagnosis_code = random.choice(data_pool["diagnosis_code"])
        lidocaine_vol = random.choice(data_pool["lidocaine_vol"])
        incision_size = random.choice(data_pool["incision_size"])
        tube_size = random.choice(data_pool["tube_size"])
        tube_type = random.choice(data_pool["tube_type"])
        airway_segments = random.choice(data_pool["airway_segments"])
        secretions = random.choice(data_pool["secretions"])
        ultrasound_finding = random.choice(data_pool["ultrasound_finding"])
        drain_type = random.choice(data_pool["drain_type"])
        hemostatic_agent = random.choice(data_pool["hemostatic_agent"])
        follow_up_days = random.choice(data_pool["follow_up_days"])

        # Shorten US finding for prompts
        ultrasound_finding_short = "no abnormal vessels" if "no" in ultrasound_finding.lower() else "normal anatomy"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            tube_size=tube_size,
            tube_type=tube_type,
            airway_segments=airway_segments,
            lidocaine_vol=lidocaine_vol,
            follow_up_days=follow_up_days,
            secretions=secretions,
            ultrasound_finding_short=ultrasound_finding_short,
            incision_size=incision_size,
            hemostatic_agent=hemostatic_agent,
            drain_type=drain_type
        )

        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            lidocaine_vol=lidocaine_vol,
            incision_size=incision_size,
            tube_size=tube_size,
            tube_type=tube_type,
            airway_segments=airway_segments,
            secretions=secretions,
            ultrasound_finding=ultrasound_finding,
            drain_type=drain_type,
            hemostatic_agent=hemostatic_agent,
            follow_up_days=follow_up_days
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