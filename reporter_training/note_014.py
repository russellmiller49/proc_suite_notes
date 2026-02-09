import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_014"
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
    "age": ["28", "33", "39", "45", "51", "56", "62"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Patel"],
    "diagnosis_primary": ["hemoptysis", "complex aspergilloma", "fungal ball with hemoptysis"],
    "comorbidity": ["airway obstruction", "endobronchial clot", "mucous plugging"],
    "sedation_time": ["95", "110", "124", "135", "140"],
    "cryo_probe_size": ["1.1mm", "1.9mm", "2.4mm"],
    "cryo_duration": ["5-10 second", "3-5 second", "10-15 second"],
    "ampho_dose": ["10mg", "20mg", "50mg"],
    "txa_dose": ["250mg", "400mg", "500mg"],
    "uniblocker_size": ["5 Fr", "7 Fr", "9 Fr"],
    "blocker_inflation": ["2.5cc", "3.0cc", "4.0cc"],
    "blocker_duration": ["2 hours", "4 hours", "6 hours"],
    "removal_time": ["1400", "1600", "1800", "1200"],
    
    # Anatomy Scenarios to ensure logic consistency (Side vs Anatomy)
    "anatomy_scenarios": [
        {
            "side": "Left",
            "opp_side": "Right",
            "affected_lobe": "LUL",
            "affected_segments": "Lingula, LUL, and LB6",
            "carina_target": "Left Carina (LC2)",
            "opp_carina": "Right Carina (RC2)",
            "anatomy_desc_norm": "Right Lung: Proximal airways demonstrated normal anatomic branching to the segmental level.",
            "anatomy_desc_path": "Left Lung: Endobronchial balloon noted at Lingula, LUL, and LB6 with organized clot obscuring evaluation.",
            "blocker_depth": "27.5cm"
        },
        {
            "side": "Right",
            "opp_side": "Left",
            "affected_lobe": "RUL",
            "affected_segments": "RUL, RML, and RB6",
            "carina_target": "RUL Carina (RC1) and RML Carina (RC2)",
            "opp_carina": "Left Carina (LC2)",
            "anatomy_desc_norm": "Left Lung: Proximal airways demonstrated normal anatomic branching to the segmental level.",
            "anatomy_desc_path": "Right Lung: Endobronchial balloon noted at RUL and RML with organized clot obscuring evaluation.",
            "blocker_depth": "25.0cm"
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# Note template captures the IP Bronchoscopy structure
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 

DATE OF PROCEDURE: {date_proc}

INDICATION FOR OPERATION: {age}-year-old {gender_long} who presents with {diagnosis}, {comorbidity}, and aspergilloma.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT: Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS: {diagnosis}, {comorbidity}, aspergilloma
POSTOPERATIVE DIAGNOSIS: {diagnosis}, {comorbidity}, aspergilloma

PROCEDURE: 
Therapeutic aspiration, subsequent episodes (31646)
Therapeutic injection (Amphotericin) (31573)
Destruction of tumor or relief of stenosis by cryotherapy (31641)
Note: Substantially greater work than normal (>100% increased work) due to time, technical difficulty, and physical/mental effort required for removal of organized clot.
Bronchoscopy with application of Tranexamic Acid (31899NFD)
Balloon occlusion / placement of occlusive substance (31634)

ANESTHESIA: Moderate sedation (Total time: {sed_time} minutes).
Medications: Versed, Fentanyl, Propofol, Dexmedetomidine, Cisatracurium.

MONITORING: Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION: Disposable Bronchoscope; {cryo_size} Cryoprobe; {blocker_size} Uniblocker.

ESTIMATED BLOOD LOSS: Minimal 

COMPLICATIONS: None 

PROCEDURE IN DETAIL: 
After induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Relevant procedural images were saved to the medical record.

Patient position: Supine 
Airway Inspection: The tracheostomy tube was found to be in good position.
Pharynx, Larynx, Vocal Cords: Not assessed due to bronchoscopy introduction through tracheostomy tube.
Trachea: Distal 1/3 normal. Main Carina: Sharp.

{anatomy_normal}
No evidence of mass, lesions, bleeding, or other endobronchial pathology.

{anatomy_pathology}
Otherwise, normal anatomic branching to segmental level.

Mucosa/Secretions: Mucosa normal. Secretions were minimal, thin, and clear.

Therapeutic Aspiration & Clot Removal: 
Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), {opp_side} Mainstem, Bronchus Intermedius, {side} Mainstem, Carina, {opp_carina}, and {carina_target} from mucus, blood, and blood clots.
Organized endobronchial clot at the {affected_segments} was treated using a {cryo_size} cryoprobe ({cryo_dur} freezes), resulting in excellent clot removal.

Instillation & Occlusion: 
After organized clot was removed from the {affected_lobe}, Amphotericin ({ampho_dose} in 10cc sterile water) was instilled into the {affected_lobe} proper.
The bronchoscope was wedged into the {affected_lobe} to prevent backflow for 5 minutes.
Tranexamic Acid (TXA) {txa_dose} was applied directly into the {affected_lobe}.
Balloon occlusion was performed at the {carina_target} with a {blocker_size} Uniblocker.
The blocker was secured at {depth} (dark blue securement device), and inflation with {infl_vol} of air was confirmed to fully occlude the {affected_lobe}.

IMPRESSION / PLAN: 
{age}-year-old {gender_long} evaluated for {diagnosis} and aspergilloma.
{affected_lobe} and {affected_segments} airways successfully evacuated of organized clot using a combination of cold saline and cryotherapy.
Amphotericin instilled into {affected_lobe}; {blocker_size} Uniblocker placed and left inflated at the {affected_lobe}.

Post-procedure Plan:
Obtain post-procedure Chest X-Ray.
Leave Uniblocker in place for {blocker_dur} post-procedure (deflate at {removal_time} on {date_removal}).
Plan for repeat bronchoscopy and likely repeat instillation of Amphotericin on {date_repeat}.

No immediate complications occurred.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "IP Bronchoscopy note. Pt {age} {gender_short}. Indication: {diagnosis} / Aspergilloma {side} lung. Findings: Clot in {affected_lobe}. Procedures: Cryo clot removal ({cryo_size}), Ampho {ampho_dose} instilled, TXA {txa_dose}, {blocker_size} Uniblocker placed at {depth}. No complications.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} patient of {doctor}. Diagnosis is {diagnosis} and {comorbidity} due to Aspergilloma in the {side} lung. We performed therapeutic aspiration, cryotherapy clot destruction, and placed a {blocker_size} balloon blocker after instilling Amphotericin and TXA.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with aspergilloma {side} side. Bronch done. Removed clot from {affected_lobe} using cryo. Injected {ampho_dose} ampho and {txa_dose} TXA. Left a {blocker_size} uniblocker in place. Plan to deflate at {removal_time}.",
    
    # Style 4: Billing Focus
    "Procedure codes: 31646, 31573, 31641, 31634. Patient {age} {gender_short}. Indication: {diagnosis}. Site: {side} Lung ({affected_lobe}). Complex clot removal via cryotherapy. Meds: Amphotericin {ampho_dose}, TXA {txa_dose}. Device: {blocker_size} Uniblocker.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {diagnosis}, Aspergilloma ({side} Lung)\nProcedures:\n- Cryotherapy extraction of clot ({affected_lobe})\n- Instillation of Amphotericin ({ampho_dose})\n- Application of TXA ({txa_dose})\n- Placement of {blocker_size} Uniblocker at {depth}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    today = datetime.date.today()
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        doctor = random.choice(data_pool["doctor"])
        diagnosis = random.choice(data_pool["diagnosis_primary"])
        comorbidity = random.choice(data_pool["comorbidity"])
        sed_time = random.choice(data_pool["sedation_time"])
        
        # Treatment Details
        cryo_size = random.choice(data_pool["cryo_probe_size"])
        cryo_dur = random.choice(data_pool["cryo_duration"])
        ampho_dose = random.choice(data_pool["ampho_dose"])
        txa_dose = random.choice(data_pool["txa_dose"])
        blocker_size = random.choice(data_pool["uniblocker_size"])
        infl_vol = random.choice(data_pool["blocker_inflation"])
        blocker_dur = random.choice(data_pool["blocker_duration"])
        removal_time = random.choice(data_pool["removal_time"])
        
        # Anatomy Logic (Ensure side consistency)
        scenario = random.choice(data_pool["anatomy_scenarios"])
        
        # Dates
        date_proc_obj = today - datetime.timedelta(days=random.randint(0, 30))
        date_proc = date_proc_obj.strftime("%Y-%m-%d")
        # Removal is usually same day or next day
        date_removal = date_proc 
        date_repeat = (date_proc_obj + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            diagnosis=diagnosis,
            comorbidity=comorbidity,
            side=scenario["side"],
            affected_lobe=scenario["affected_lobe"],
            cryo_size=cryo_size,
            ampho_dose=ampho_dose,
            txa_dose=txa_dose,
            blocker_size=blocker_size,
            depth=scenario["blocker_depth"],
            removal_time=removal_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_proc=date_proc,
            age=age, 
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            comorbidity=comorbidity,
            sed_time=sed_time,
            cryo_size=cryo_size,
            blocker_size=blocker_size,
            
            # Anatomy Variables from Scenario
            anatomy_normal=scenario["anatomy_desc_norm"],
            anatomy_pathology=scenario["anatomy_desc_path"],
            opp_side=scenario["opp_side"],
            side=scenario["side"],
            opp_carina=scenario["opp_carina"],
            carina_target=scenario["carina_target"],
            affected_segments=scenario["affected_segments"],
            cryo_dur=cryo_dur,
            affected_lobe=scenario["affected_lobe"],
            
            # Meds and Devices
            ampho_dose=ampho_dose,
            txa_dose=txa_dose,
            depth=scenario["blocker_depth"],
            infl_vol=infl_vol,
            blocker_dur=blocker_dur,
            removal_time=removal_time,
            date_removal=date_removal,
            date_repeat=date_repeat
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