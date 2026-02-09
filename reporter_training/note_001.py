import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_001" 
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
    "age": ["54", "59", "62", "65", "68", "71", "74", "77", "82"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Vasquez", "Dr. Al-Fayed"],
    "procedure_date": ["January 12", "February 24", "March 10", "April 05", "May 20", "June 15", "October 03"],
    
    # Clinical Variations
    "fistula_size": ["1.0 cm", "1.2 cm", "1.5 cm", "1.8 cm", "2.0 cm"],
    "fistula_loc": ["mid-left mainstem", "proximal left mainstem", "distal left mainstem"],
    "secretion_type": ["Purulent", "Thick mucoid", "Copious purulent", "Blood-tinged"],
    
    # Stent Hardware Variations (Aero Stents)
    # Stent 1 = The one that stays (originally pushed too far)
    # Stent 2 = The one removed (the second one placed)
    "stent_1_size": ["14x30 mm", "12x30 mm", "14x20 mm"],
    "stent_2_size": ["14x40 mm", "12x40 mm", "14x30 mm"], 
    
    # Post-op Plan Variations
    "neb_freq": ["TID", "Q4H", "Q6H", "BID"],
    "complication_desc": [
        "stent migration causing lobar obstruction",
        "distal displacement of the first stent",
        "obstruction of the UL/LL orifices by the migrated stent"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The Note Template (Reconstructs the detailed narrative)
note_template = """NOTE_ID: {note_id}
DATE OF PROCEDURE: {date}

INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with a broncho-esophageal (anastomosis) fistula s/p Ivor Lewis Esophagostomy. The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail. The patient wished to proceed and informed consent was obtained.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate. Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
Broncho-esophageal (anastomosis) fistula s/p Ivor Lewis Esophagostomy

POSTOPERATIVE DIAGNOSIS
Broncho-esophageal (anastomosis) fistula s/p Ivor Lewis Esophagostomy
Status post occlusive left mainstem stent placement

PROCEDURE
Flexible bronchoscopy via tracheostomy
Endobronchial biopsy (multiple sites)
Self-expandable airway stent placement (Aero)
Fluoroscopy guidance
Tracheostomy tube exchange (secondary to stent removal)

ATTENDING: {doctor}

ANESTHESIA: General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

PROCEDURE IN DETAIL
After induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality. Relevant procedural images were saved to the medical record.

Airway Inspection
The flexible bronchoscope was passed through the patient's tracheostomy tube and into the airways. The trachea was normal. {secretion_type} secretions were seen throughout the airways and were suctioned.

Right Lung: Inspection showed multiple small endobronchial nodular lesions concerning for airway metastasis.
Left Lung: A {fistula_size} fistula was identified at the medial aspect of the posterior wall of the {fistula_loc}. Distally, multiple small endobronchial lesions were noted with an appearance suggestive of malignancy.

Endobronchial Biopsy
Multiple nodules from the left and right side were biopsied with flexible forceps. Samples were placed in formalin.

Stent Placement
The length of the fistula was measured. A Jagwire was inserted through the flexible bronchoscope past the fistula within the left mainstem. Using fluoroscopy, the proximal and distal edges of the target area were marked with radiopaque markers (paper clips) taped to the patient’s chest wall. The flexible bronchoscope was removed.

An Aero {stent_1} stent was advanced over the guidewire and positioned based on the external markers under fluoroscopic observation. The stent was deployed slightly proximally, with the distal edge just covering the fistula.

A second {stent_2} Aero stent was placed into the previously placed stent to better cover the obstruction. Upon inspection, the originally placed stent ({stent_1}) was noted to have been pushed distally by the second stent, obstructing the orifice of the left upper and lower lobes.

Stent Revision and Tracheostomy Exchange
The {stent_2} stent was removed by grasping the proximal edge with forceps. The stent could not be retracted through the tracheostomy tube.

Tracheostomy Exchange: The tracheostomy tube was removed. The stent was pulled through the stoma. The tracheostomy tube was then re-inserted over a bronchoscope and re-attached to the ventilator.

Final Positioning
The remaining {stent_1} Aero fully covered self-expandable metallic stent was retracted into proper position (within the left mainstem covering the fistula) using forceps. Final inspection demonstrated satisfactory positioning. The bronchoscope was removed.

IMPRESSION / PLAN
Transfer back to ICU.
Await tissue diagnosis from biopsied endobronchial nodules.
Obtain post-procedure chest imaging.
{neb_freq} saline nebulizers along with ensuring oxygen is humidified to avoid mucous impaction and obstruction of stent."""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Pt: {age} {gender_short}. S/p Ivor Lewis with BPF ({fistula_size}, {fistula_loc}). Proc: Bronch, Biopsy, Stenting. Complication: {stent_1} pushed distal by {stent_2}. Action: Removed {stent_2} via stoma (trach exchange), retracted {stent_1}. Plan: ICU, nebs {neb_freq}.",
    
    # Style 2: Dictation / Narrative
    "Please generate a report for {doctor}. Patient is a {age}yo {gender_long} with a broncho-esophageal fistula. We found {secretion_type} secretions. We placed a {stent_1} Aero stent, then a {stent_2}. The second stent pushed the first one too deep, blocking lobes. We had to remove the {stent_2}, which required pulling the trach tube. We then pulled the {stent_1} back into position.",
    
    # Style 3: Sloppy / Quick Note
    "stent placement for fistula. {age} {gender_short}. used aero {stent_1} and {stent_2}. issue with migration. removed the {stent_2} (had to take out trach) and fixed the {stent_1}. biopsies taken. {doctor}.",
    
    # Style 4: Billing / Technical Focus
    "Procedures: Bronchoscopy, Stent Placement (Aero {stent_1}, {stent_2}), Trach Exchange. Diagnosis: BPF post-esophagectomy. Indication: {fistula_size} fistula in {fistula_loc}. Complication: Stent migration requiring revision. Disposition: ICU.",
    
    # Style 5: Structured Input
    "Patient: {age} | {gender_short}\nAttending: {doctor}\nDiagnosis: BPF s/p Ivor Lewis\nFindings: {fistula_size} fistula, {fistula_loc}, {secretion_type} secretions.\nIntervention: Placed {stent_1}. Placed {stent_2} which displaced first stent. Removed {stent_2} via stoma. Repositioned {stent_1}."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, he/she, his/her)
        doctor = random.choice(data_pool["doctor"])
        date = random.choice(data_pool["procedure_date"])
        
        fistula_size = random.choice(data_pool["fistula_size"])
        fistula_loc = random.choice(data_pool["fistula_loc"])
        secretion_type = random.choice(data_pool["secretion_type"])
        neb_freq = random.choice(data_pool["neb_freq"])
        
        # Stent logic
        stent_1 = random.choice(data_pool["stent_1_size"])
        stent_2 = random.choice(data_pool["stent_2_size"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            fistula_size=fistula_size,
            fistula_loc=fistula_loc,
            secretion_type=secretion_type,
            stent_1=stent_1,
            stent_2=stent_2,
            neb_freq=neb_freq
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            age=age,
            gender_long=gender_tup[0],
            doctor=doctor,
            secretion_type=secretion_type,
            fistula_size=fistula_size,
            fistula_loc=fistula_loc,
            stent_1=stent_1,
            stent_2=stent_2,
            neb_freq=neb_freq
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