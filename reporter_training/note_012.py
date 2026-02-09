import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_012"
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
    "age": [str(x) for x in range(25, 85)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "patient_name_initials": ["A.B.", "J.S.", "M.K.", "L.R.", "T.W.", "C.D."],
    "diagnosis": [
        "aspergilloma", "mycetoma", "pulmonary fungal ball", "invasive aspergillosis", "cavitary lung lesion"
    ],
    "symptom": [
        "hemoptysis", "recurrent hemoptysis", "blood-streaked sputum", "productive cough with blood", "chronic cough"
    ],
    "drug_name": ["Amphotericin", "Amphotericin B", "Voriconazole", "Ambisome"],
    "hemostatic_agent": ["Tranexamic Acid (TXA)", "Epinephrine", "Cold Saline", "Thrombin"],
    
    # Anatomy scenarios to ensure segments match the lobes
    "anatomy_scenarios": [
        {
            "side": "Left",
            "lobe": "Left Upper Lobe (LUL)",
            "seg1": "apico-posterior subsegment (LB1/2)",
            "seg2": "anterior subsegment (LB3)",
            "blocker_loc": "Left Mainstem Bronchus (LMSB)",
            "carina_obstruction": "LUL Lingula Carina (Lc1) and Left Carina (LC2)",
            "secretion_side": "left greater than right"
        },
        {
            "side": "Right",
            "lobe": "Right Upper Lobe (RUL)",
            "seg1": "apical subsegment (RB1)",
            "seg2": "posterior subsegment (RB2)",
            "blocker_loc": "Right Mainstem Bronchus (RMSB)",
            "carina_obstruction": "RUL Carina (RC1) and Bronchus Intermedius",
            "secretion_side": "right greater than left"
        },
        {
            "side": "Right",
            "lobe": "Right Lower Lobe (RLL)",
            "seg1": "superior subsegment (RB6)",
            "seg2": "posterior basal subsegment (RB10)",
            "blocker_loc": "Bronchus Intermedius",
            "carina_obstruction": "RLL Basal Carina and RML orifice",
            "secretion_side": "right greater than left"
        }
    ],
    
    "anesthesia_plan": [
        "Etomidate 20 mg, Rocuronium 26 mg, Propofol 40 mcg/kg/min, Fentanyl 150 mcg/hr",
        "Propofol 120 mcg/kg/min, Fentanyl 50 mcg boluses",
        "Midazolam 4 mg, Fentanyl 100 mcg, Propofol infusion",
        "Ketamine 50 mg, Propofol 100 mcg/kg/min"
    ],
    
    "follow_up_date": [
        "1/5/2026", "2/10/2026", "next Monday", "in two weeks", "pending clinical status"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_012.txt
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] INDICATION FOR OPERATION {patient_initials} is a {age}-year-old {gender_long} who presents with {diagnosis} and {symptom}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient wished to proceed, and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field
{diagnosis_title}
{symptom_title}

POSTOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field
{diagnosis_title}
{symptom_title}

PROCEDURE
Therapeutic aspiration of tracheobronchial tree (CPT 31645)
Therapeutic injection via endoscope channel ({drug_name}) (CPT 31573)
Destruction of tumor/relief of stenosis by cryotherapy (CPT 31641)
Bronchoscopy with application of {hemostatic_agent} (CPT 31899)

ANESTHESIA Moderate sedation was administered.
The patient was monitored continuously by the attending physician while anesthesia was administered.
Medications: {anesthesia_meds}.

Duration: 50 minutes.
MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Disposable Bronchoscope; 1.1mm Cryoprobe.

ESTIMATED BLOOD LOSS Minimal

COMPLICATIONS None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and procedure location.
Airway Inspection The bronchoscope was introduced through the tracheostomy tube. The tracheostomy tube was found to be in good position.
A Uniblocker was noted in place (deflated) at the {blocker_loc}.

Trachea: Distal 1/3 normal. Main carina sharp.
Right Lung: Proximal airways demonstrated normal anatomic branching to the segmental level. No evidence of mass or lesions.
Left Lung: Proximal airways demonstrated normal anatomic branching to the segmental level. No evidence of mass or lesions.
Secretions: Mild bloody secretions were noted, with {secretion_side}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the airway segments from mucus, blood, and blood clots.
Segments Cleared: Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2).

Therapeutic Injection ({drug_name}) {drug_name} (50 mg in 20 cc sterile water) was instilled into the {target_lobe} as follows:
10 cc into the {seg1}.
10 cc into the {seg2}.

Endobronchial Hemostasis Post-instillation, the patient had a mild ooze of fresh blood.
Hemostasis was achieved by applying {hemostatic_agent} directly into the {target_lobe_short} through the bronchoscope (Total dose: 1000 mg).

Cryo-Extraction of Clot A formalized clot was identified causing obstruction at the {carina_obstruction}.
A 1.1 mm cryoprobe was applied to the clot with freeze times of 5–10 seconds.
Excellent clot removal was achieved, and the airway obstruction was relieved.

Conclusion The patient tolerated the procedure well.
There were no immediate complications.

IMPRESSION / PLAN
{age}-year-old {gender_long} with {diagnosis} and {symptom}.
Successful therapeutic aspiration and clearance of bloody secretions.
Successful instillation of {drug_name} into {target_lobe_short}.
Effective clot extraction via cryoprobe and hemostasis achieved with {hemostatic_agent}.

Plan:
Continued care per primary team.
May consider repeat instillation of {drug_name} on {follow_up_date} and possible clot extraction.
"""

# 5 Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Gen report: {age}{gender_short}, {diagnosis} w/ {symptom}. Bronch done. Asp secretions. Inj {drug_name} into {target_lobe_short}. Cryo clot removal @ {carina_obstruction}. {hemostatic_agent} for bleed. No comps.",
    
    # Style 2: Dictation
    "Please generate an op note for patient {patient_initials}, {age} {gender_long}. Pre-op dx {diagnosis} and {symptom}. We performed therapeutic aspiration, injection of {drug_name} into the {target_lobe_short}, and cryotherapy. A uniblocker was in the {blocker_loc}. We cleared a clot from the {carina_obstruction}. Hemostasis with {hemostatic_agent}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {diagnosis}. Proc: Bronch, asp, inj {drug_name} ({seg1}/{seg2}), cryo for clot. Used {hemostatic_agent}. Uniblocker was at {blocker_loc}.",
    
    # Style 4: Billing Focus
    "Procedures: 31645, 31573, 31641, 31899. Pt {age} {gender_short}. Dx: {diagnosis}, {symptom}. Interventions: {drug_name} injection ({target_lobe_short}), Cryo extraction of clot, {hemostatic_agent} application.",
    
    # Style 5: Structured
    "Patient Demographics: {age} {gender_short}\nIndication: {diagnosis}, {symptom}\nProcedure Details:\n- Aspiration\n- Injection: {drug_name} to {target_lobe_short}\n- Cryo: Clot extraction at {carina_obstruction}\n- Hemostasis: {hemostatic_agent}\nFindings: Uniblocker at {blocker_loc}."
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
        patient_initials = random.choice(data_pool["patient_name_initials"])
        diagnosis = random.choice(data_pool["diagnosis"])
        symptom = random.choice(data_pool["symptom"])
        drug_name = random.choice(data_pool["drug_name"])
        hemostatic_agent = random.choice(data_pool["hemostatic_agent"])
        anesthesia_meds = random.choice(data_pool["anesthesia_plan"])
        follow_up_date = random.choice(data_pool["follow_up_date"])
        
        # Select cohesive anatomy scenario
        anatomy = random.choice(data_pool["anatomy_scenarios"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            patient_initials=patient_initials,
            diagnosis=diagnosis,
            symptom=symptom,
            drug_name=drug_name,
            target_lobe_short=anatomy["lobe"].split(" (")[1].replace(")", ""), # Extract LUL/RUL
            carina_obstruction=anatomy["carina_obstruction"],
            hemostatic_agent=hemostatic_agent,
            blocker_loc=anatomy["blocker_loc"],
            seg1=anatomy["seg1"],
            seg2=anatomy["seg2"]
        )
        
        # C. Generate Completion (Structured Note)
        # Helper for titles
        diagnosis_title = diagnosis.capitalize()
        symptom_title = symptom.capitalize()
        target_lobe_short = anatomy["lobe"].split(" (")[1].replace(")", "")
        
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_initials=patient_initials,
            age=age,
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            diagnosis_title=diagnosis_title,
            symptom=symptom,
            symptom_title=symptom_title,
            drug_name=drug_name,
            hemostatic_agent=hemostatic_agent,
            anesthesia_meds=anesthesia_meds,
            blocker_loc=anatomy["blocker_loc"],
            secretion_side=anatomy["secretion_side"],
            target_lobe=anatomy["lobe"],
            target_lobe_short=target_lobe_short,
            seg1=anatomy["seg1"],
            seg2=anatomy["seg2"],
            carina_obstruction=anatomy["carina_obstruction"],
            follow_up_date=follow_up_date
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