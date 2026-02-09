import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_019"
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
    "age": ["62", "67", "71", "74", "79", "82", "85", "87", "91", "94"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Patel", "Dr. O'Connor"],
    "date_offset": range(-10, 10), # Days relative to today
    "indication": [
        "complicated effusion", "loculated pleural effusion", "complex parapneumonic effusion", 
        "non-draining pleural effusion", "fibrinous effusion"
    ],
    "target_side_tuple": [("Right", "Left"), ("Left", "Right")], # (Target/Bad Side, Contralateral/Good Side)
    
    # Ultrasound Findings for the TARGET (Pathologic) side
    "target_effusion_desc": [
        "Large volume, anechoic echogenicity, thick loculations",
        "Moderate volume, complex septated fluid",
        "Large volume, swirling debris, multiple loculations",
        "Significant volume, hyperechoic strands, loculated"
    ],
    "target_diaphragm": ["Diminished motion", "Paradoxical motion", "Elevated hemidiaphragm with poor excursion"],
    "target_pleura": ["Pleura appears thick", "Nodular pleural thickening", "Diffusely thickened pleura"],
    
    # Ultrasound Findings for the CONTRALATERAL (Normal/Minor) side
    "other_effusion_desc": [
        "Minimal volume, anechoic echogenicity, no loculations",
        "Trace pleural fluid, simple appearance",
        "No significant effusion identified",
        "Small simple effusion, free flowing"
    ],
    
    # Intervention details
    "agent_dose": [
        "10 mg tPA / 5 mg DNase", "5 mg tPA / 5 mg DNase", "10 mg tPA / 10 mg DNase"
    ],
    "dwell_time": ["1 hour", "45 minutes", "2 hours", "90 minutes"],
    "drainage_method": ["vacutainer", "wall suction", "gravity drainage", "syringe aspiration"],
    "drainage_vol": ["250", "300", "400", "450", "550", "600", "850"],
    "drainage_color": ["bloody", "serosanguinous", "dark yellow", "turbid", "amber", "hemorrhagic"],
    "disposition": ["Discharge home", "Return to ward", "Remain in observation unit"],
    "follow_up": ["10-14 days", "1 week", "7-10 days", "2 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 

DATE OF PROCEDURE: {date_str}


INDICATION FOR OPERATION: The patient is a {age}-year-old {gender_long} who presents with a {indication}.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient wished to proceed and informed consent was obtained.
PREOPERATIVE DIAGNOSIS

{indication_title} 

POSTOPERATIVE DIAGNOSIS

{indication_title} 

PROCEDURE

Ultrasound, chest (includes mediastinum), real time with image documentation (CPT 76604)

Instillation(s), via chest tube/catheter, agent for fibrinolysis;
initial day (CPT 32561)

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
PROCEDURE IN DETAIL After induction of anesthesia (local), a timeout was performed confirming patient identity, planned procedures, and laterality.
Focused Thoracic Ultrasound Focused thoracic ultrasound was performed and relevant procedural images were saved to the medical record.
{first_side_header} Hemithorax:

Pleural Effusion: {first_effusion_desc}.

Diaphragm: {first_diaphragm}.

Lung/Pleura: Lung sliding present pre- and post-procedure.
No consolidation/atelectasis. {first_pleura}.

{second_side_header} Hemithorax:

Pleural Effusion: {second_effusion_desc}.

Diaphragm: {second_diaphragm}.
Lung/Pleura: {second_pleura}.

Intrapleural Fibrinolysis ({target_side}) The existing {target_side_lower}-sided chest tube (inserted {date_str}) was identified.
Agent Instilled: {agent_dose} (Dose #1).
Dwell Time: The agents were allowed to dwell for {dwell_time}.
Drainage: Following the dwell time, drainage was performed using a {drainage_method}.

Output: {drainage_vol} cc of {drainage_color} fluid was drained.
COMPLICATIONS No immediate complications occurred. 

IMPRESSION / PLAN

Successful chest ultrasound and instillation of fibrinolytic agents for {indication}.
Patient tolerated the procedure well. 

Disposition: {disposition}.


Follow-up: Return to pleural clinic in {follow_up} for repeat lytics.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Generate procedure note. Pt: {age}{gender_short}. Indication: {indication}. US Findings: {target_side} {target_effusion_snippet}, {other_side} benign. Intervention: {agent_dose} instilled {target_side}. Output: {drainage_vol}cc {drainage_color}.",
    
    # Style 2: Dictation
    "Please write an IP op report for a {age} year old {gender_long} with a {indication}. We performed a thoracic ultrasound and fibrinolytic instillation. The ultrasound showed a {target_effusion_snippet} on the {target_side} and minimal findings on the {other_side}. We instilled {agent_dose} into the {target_side} tube. After {dwell_time}, we drained {drainage_vol} cc of {drainage_color} fluid.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {indication}. US: {target_side} loculated/thick, {other_side} clear. Instilled {agent_dose} to {target_side}. Drained {drainage_vol}ml {drainage_color}. {disposition}.",
    
    # Style 4: Billing Focus
    "CPT 76604, 32561. Dx: {indication_title}. {age} {gender_short}. US findings: {target_side} complex, {other_side} simple. Rx: {agent_dose} to {target_side}. Outcome: {drainage_vol}cc drainage.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nProcedure: US Chest + Lytics Instillation\nFindings: {target_side} ({target_effusion_snippet}), {other_side} (Normal)\nAction: {agent_dose} via {target_side} tube\nOutput: {drainage_vol}cc {drainage_color}"
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
        
        # Date Logic
        today = datetime.date.today()
        offset = random.choice(data_pool["date_offset"])
        proc_date = today + datetime.timedelta(days=offset)
        date_str = proc_date.strftime("%-m/%-d/%y")
        
        # Side Logic (Crucial for US findings consistency)
        # target_side_tup[0] is the BAD side (Target), [1] is the GOOD side (Other)
        target_side_tup = random.choice(data_pool["target_side_tuple"])
        target_side = target_side_tup[0]
        other_side = target_side_tup[1]
        
        # Select Findings
        target_effusion_desc = random.choice(data_pool["target_effusion_desc"])
        target_diaphragm = random.choice(data_pool["target_diaphragm"])
        target_pleura = random.choice(data_pool["target_pleura"])
        
        other_effusion_desc = random.choice(data_pool["other_effusion_desc"])
        other_diaphragm = "Normal motion"
        other_pleura = "Pleura appears normal"
        
        # Assign findings to Left/Right headers based on which is target
        # The template has {first_side_header} and {second_side_header}
        # We will fix the template order to Left then Right to match original structure,
        # but populate content dynamically.
        
        first_side_header = "Left"
        second_side_header = "Right"
        
        if target_side == "Left":
            # Left is Bad, Right is Good
            first_effusion_desc = target_effusion_desc
            first_diaphragm = target_diaphragm
            first_pleura = target_pleura
            
            second_effusion_desc = other_effusion_desc
            second_diaphragm = other_diaphragm
            second_pleura = other_pleura
        else:
            # Right is Bad, Left is Good
            first_effusion_desc = other_effusion_desc
            first_diaphragm = other_diaphragm
            first_pleura = other_pleura
            
            second_effusion_desc = target_effusion_desc
            second_diaphragm = target_diaphragm
            second_pleura = target_pleura

        # Rest of variables
        agent_dose = random.choice(data_pool["agent_dose"])
        dwell_time = random.choice(data_pool["dwell_time"])
        drainage_method = random.choice(data_pool["drainage_method"])
        drainage_vol = random.choice(data_pool["drainage_vol"])
        drainage_color = random.choice(data_pool["drainage_color"])
        disposition = random.choice(data_pool["disposition"])
        follow_up = random.choice(data_pool["follow_up"])

        # Snippet for prompts (shortened finding)
        target_effusion_snippet = "complex fluid" if "complex" in target_effusion_desc else "loculated effusion"
        indication_title = indication.title()

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            indication=indication, indication_title=indication_title,
            target_side=target_side, other_side=other_side,
            target_effusion_snippet=target_effusion_snippet,
            agent_dose=agent_dose, dwell_time=dwell_time,
            drainage_vol=drainage_vol, drainage_color=drainage_color,
            disposition=disposition
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            age=age, gender_long=gender_tup[0],
            indication=indication, indication_title=indication_title,
            
            # Dynamic Side Headers and Content
            first_side_header=first_side_header,
            first_effusion_desc=first_effusion_desc,
            first_diaphragm=first_diaphragm,
            first_pleura=first_pleura,
            
            second_side_header=second_side_header,
            second_effusion_desc=second_effusion_desc,
            second_diaphragm=second_diaphragm,
            second_pleura=second_pleura,
            
            # Intervention Details
            target_side=target_side,
            target_side_lower=target_side.lower(),
            agent_dose=agent_dose,
            dwell_time=dwell_time,
            drainage_method=drainage_method,
            drainage_vol=drainage_vol,
            drainage_color=drainage_color,
            disposition=disposition,
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