import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_056"
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
    "age": ["78", "82", "85", "88", "91", "93", "95", "96"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "airway obstruction",
        "worsening dyspnea and stridor",
        "critical central airway stenosis",
        "mucus impaction and respiratory distress"
    ],
    "mucus_desc": [
        "Copious thick and thin, clear to tan secretions/mucus throughout with left > right",
        "Moderate amount of thick, tenacious secretions bilaterally",
        "Significant purulent secretions plugging the distal airways",
        "Copious mucoid secretions requiring extensive suctioning"
    ],
    "tear_location": [
        "subglottic posterior trachea",
        "distal tracheal posterior membrane",
        "mid-tracheal posterior wall",
        "posterior membrane just proximal to the carina"
    ],
    "defect_dims": [
        {"vocal_dist": "8 cm", "length": "2.5 cm", "carina_dist": "3 cm"},
        {"vocal_dist": "7 cm", "length": "3.0 cm", "carina_dist": "2.5 cm"},
        {"vocal_dist": "9 cm", "length": "2.0 cm", "carina_dist": "4 cm"},
        {"vocal_dist": "6 cm", "length": "3.5 cm", "carina_dist": "2 cm"}
    ],
    "failed_stent": [
        "silicone Y-stent (16mm x 13mm x 13mm)",
        "silicone Y-stent (15mm x 12mm x 12mm)",
        "Montgomery T-tube",
        "studded silicone stent"
    ],
    "failure_reason": [
        "significant difficulty was encountered advancing the stent into the deployer, eventually causing a mild tear of a bronchial limb",
        "the stent could not be seated properly due to the angulation of the defect",
        "migration occurred immediately upon deployment requiring removal",
        "the stent limbs were too long for the patient's anatomy causing carina obstruction"
    ],
    "final_stent": [
        "tubular tracheal stent measuring 16mm x 45mm",
        "tubular silicone stent measuring 14mm x 40mm",
        "straight silicone stent measuring 18mm x 50mm",
        "modified tubular stent measuring 15mm x 40mm"
    ],
    "balloon_size": ["12/13.5/15", "10/11/12", "15/16.5/18", "13.5/15/16.5"],
    "final_dilation_mm": ["15 mm", "12 mm", "18 mm", "16.5 mm"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]
INDICATION FOR OPERATION: [REDACTED] is a {age} year-old {gender_long} who presents with {indication}.

This patient required a complex tracheal stent placement. This resulted in >100% increased work due to Increased intensity, Time, Technical difficulty of procedure, and Physical and mental effort required.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified
Posterior membrane defect

PROCEDURE
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)
31899NFN Bronchoscopy with Endobronchial Ultrasound (EBUS) of mediastinal and/or hilar lymph nodes without biopsy
31630 Balloon dilation
31631 Dilate and tracheal stent placement
43200 Esophagoscopy, flexible, transoral; diagnostic

ANESTHESIA: General Anesthesia
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer.

INSTRUMENTATION: Rigid Bronchoscope, Flexible Therapeutic Bronchoscope, Linear EBUS.
ESTIMATED BLOOD LOSS: Minimum
COMPLICATIONS: Injury to {tear_location}.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed.
Patient Position: Supine.

Initial Airway Inspection: The laryngeal mask airway is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.
Larynx: Mild edema and erythema.
Vocal Cords: Normal without mass/lesions.
Trachea: Normal.
Main Carina: Sharp.
Right Lung Proximal Airways: Normal anatomic branching to segmental level. No evidence of mass, lesions, bleeding or other endobronchial pathology.
Left Lung Proximal Airways: Normal anatomic branching to segmental level. No evidence of mass, lesions, bleeding or other endobronchial pathology.
Mucosa: Friable.
Secretions: {mucus_desc}.
Supraglottic Space: Erythematous and edematous.

Therapeutic Aspiration & BAL
Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina, RML Carina, LUL Lingula Carina, and Left Carina from mucus.
Bronchial alveolar lavage was performed at Anterior Segment of LUL. Instilled 40 cc of NS, suction returned with 20 cc of NS. Samples sent for Cell Count, Microbiology, and Cytology.

EBUS Inspection & Complication Management
After initial airway inspection and BAL the therapeutic bronchoscope was removed and the linear EBUS scope introduced via the LMA. The patient's trachea was inspected and particular attention was paid to the {tear_location} where suspicious tissue was identified on cross-sectional imaging. No suspicious lesion was identified and no samples were taken.

The linear EBUS was removed and repeat inspection with the therapeutic scope revealed a full thickness tear in the airway, presumably from the EBUS scope. Advanced Gastroenterology service was consulted intraoperatively and came to the OR for consultation. The defect was observed from within the trachea and the bronchoscope was introduced into the defect where no esophageal lumen was identified, only soft tissue c/w mediastinum. The scope was subsequently introduced into the esophagus to evaluate for esophageal injury. With Gastroenterology present, the length of the esophagus was examined and no esophageal defect/injury was identified. Decision was then made to place a tracheal stent across the defect and forgo esophageal stenting.

Rigid Bronchoscopy & Stent Placement
After induction of muscle relaxants, tooth or gum protector was placed. The black long rigid barrel was introduced through the mouth and advanced in the midline. The vocal cords were identified and the rigid bronchoscope was advanced carefully. Once the rigid bronchoscope was positioned at the mid-trachea, jet ventilation (14 DP, 80 F, 100% FiO2) was initiated and chest wall movement was confirmed. Intubation was easy.

Measurements were taken of the posterior membrane defect as follows:
Distance from vocal folds to membrane defect: {dist_vocal}
Distance from top of defect to bottom: {dist_length}
Distance of bottom of defect to main carina: {dist_carina}

The black rigid bronchoscope was removed and the patient was reintubated with the yellow rigid bronchoscope in the standard fashion. A {failed_stent} was initially selected. However, {failure_reason}.
Thus, the stent was modified to a {final_stent}.
The modified tracheal stent was loaded on to the rigid stent loader and placed in the trachea. The rigid forceps were then used to grasp the silicone stent and position it squarely across the tracheal defect.

Balloon dilation was performed at Trachea (Distal 1/3) within the silicone stent to seat it in place. {balloon_size} Elation balloon was used to perform dilation to {final_dilation_mm} at the Trachea (Distal 1/3) (within the silicone stent). Total 1 inflations with dilation time of 30 seconds each.

Conclusion
The patient tolerated the procedure well. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS: LUL BAL (cell count, micro, cyto)

IMPRESSION / PLAN
[REDACTED] is a {age} year-old {gender_long} who presents for bronchoscopy for evaluation of airway occlusion.
No occlusion was identified on bronchoscopic evaluation. Copious mucus/secretions were suctioned. The patient was examined with endobronchial ultrasound but no suspicious lesions were identified. On re-inspection the patient had a posterior membrane defect at the distal trachea.
A silicone tracheal stent was placed via rigid bronchoscopy to span the defect.
Stent Hydration Regimen (TID): 1) Albuterol nebs, 2) Hypertonic saline (3%) nebs, 3) Flutter valve.
Guaifenesin 1200mg PO BID.
Case management engaged to obtain nebulizer and medications prior to discharge.
Anticipate bronchoscopic re-evaluation of stent in appx 2 weeks.
"""

prompt_styles = [
    # Style 1: Narrative/Complex
    "Prepare an operative report for a {age} year old {gender_long} undergoing bronchoscopy for {indication}. Note a complication: EBUS caused a tear in the {tear_location}. GI consult ruled out esophageal injury. Initial {failed_stent} failed because {failure_reason}. Successful placement of {final_stent} and dilation to {final_dilation_mm}.",

    # Style 2: Telegraphic/Quick
    "Op note: {age}{gender_short}, {indication}. EBUS neg but caused tracheal tear. No esophageal perf (GI confirmed). Failed {failed_stent}, switched to {final_stent}. Dilation with {balloon_size} balloon. Plan: nebs and re-eval 2 weeks.",

    # Style 3: Structured Input
    "Patient: {age} {gender_long}\nIndication: {indication}\nProcedure: Bronch + EBUS + Stent\nComplication: Tear of {tear_location} (No esophageal injury)\nIntervention: Cleaned {mucus_desc_short}, placed {final_stent} after failed first attempt.",

    # Style 4: Dictation Style
    "Dictate a procedure note. {age} year old {gender_long} with {indication}. We did a therapeutic aspiration, BAL, and EBUS. Complication was a tracheal tear. We consulted GI, no esophageal leak. We placed a stent, specifically a {final_stent}, after an initial struggle with a {failed_stent}. Dilation performed.",

    # Style 5: Billing/Coding Focus
    "Generate report for CPT 31631, 31630, 31645, 31899. Diagnosis J98.09. {age}yo {gender_short}. Complex airway case involving repair of iatrogenic {tear_location} injury using {final_stent}. Include GI consult details and balloon dilation."
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
        mucus_desc = random.choice(data_pool["mucus_desc"])
        tear_loc = random.choice(data_pool["tear_location"])
        
        # Dimensions logic
        dims = random.choice(data_pool["defect_dims"])
        
        # Stent logic
        failed_stent = random.choice(data_pool["failed_stent"])
        failure_reason = random.choice(data_pool["failure_reason"])
        final_stent = random.choice(data_pool["final_stent"])
        
        # Balloon logic
        balloon_size = random.choice(data_pool["balloon_size"])
        final_dilation_mm = random.choice(data_pool["final_dilation_mm"])

        # Helper for prompt
        mucus_desc_short = "secretions" if "secretions" in mucus_desc else "mucus"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            tear_location=tear_loc,
            failed_stent=failed_stent,
            failure_reason=failure_reason,
            final_stent=final_stent,
            final_dilation_mm=final_dilation_mm,
            balloon_size=balloon_size,
            mucus_desc_short=mucus_desc_short
        )

        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            tear_location=tear_loc,
            mucus_desc=mucus_desc,
            # Dimensions
            dist_vocal=dims["vocal_dist"],
            dist_length=dims["length"],
            dist_carina=dims["carina_dist"],
            # Stent/Procedure
            failed_stent=failed_stent,
            failure_reason=failure_reason,
            final_stent=final_stent,
            balloon_size=balloon_size,
            final_dilation_mm=final_dilation_mm
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