import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_050"
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
    "age": ["19", "22", "26", "31", "35", "42", "48", "55", "63"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones"],
    "attending": ["Dr. Rossi", "Dr. Patel", "Dr. O'Malley", "Dr. Henderson", "Dr. Wu"],
    "assistant": ["Dr. Registrar", "Dr. Fellow", "Dr. Resident", "Dr. Lee", "Dr. Gomez"],
    
    # Clinical Variables - Left Mainstem (LMS)
    "lms_findings": [
        "noted to be slightly stenotic (~8mm)",
        "found to be moderately stenotic (~6mm)",
        "appeared narrowed with circumferential webbing (~7mm)",
        "showed significant concentric stenosis (~5mm)"
    ],
    "balloon_type": ["Elation", "CRE", "Hercules"],
    "balloon_dims": ["10/11/12 mm", "8/9/10 mm", "12/13.5/15 mm"],
    "target_dilation": ["10 mm", "9 mm", "12 mm", "8 mm"],
    "inflation_time": ["60 seconds", "45 seconds", "90 seconds", "30 seconds"],
    
    # Clinical Variables - Left Upper Lobe (LUL)
    "lul_condition": [
        "completely fused with historic obliteration",
        "totally obstructed by dense scar tissue",
        "showing complete stenosis/fusion",
        "completely effaced and unrecognizable"
    ],
    "needle_sequence": [
        "25G, 22G, and 19G",
        "22G and 19G",
        "21G and 18G",
        "serial TBNA needles"
    ],
    "lul_balloon": ["Mustang", "Renal", "Coronary", "Small diameter"],
    "fail_reason": [
        "was only able to pass 1/4 of the way in",
        "could not traverse the stricture",
        "met significant resistance and could not advance",
        "created a false track and was withdrawn"
    ],
    
    # Plan
    "follow_up": ["4 weeks", "6 weeks", "8 weeks", "12 weeks", "3 months"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with airway stenosis.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 
Left mainstem stenosis
Left Upper Lobe (LUL) complete fusion

PROCEDURE
31646 Therapeutic aspiration subsequent episodes 
31899NFN Bronchoscopy with Endobronchial Ultrasound (EBUS) 
31630 Balloon dilation 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (e.g. laser therapy, cryotherapy) 

ATTENDING {attending}
ASSISTANT {assistant}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope, Linear EBUS.

ESTIMATED BLOOD LOSS None 
COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine 

Initial Airway Inspection: The laryngeal mask airway (LMA) was in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.

Larynx: Normal.
Vocal Cords: Normal without mass/lesions.
Trachea: Mildly tortuous.
Main Carina: Sharp.

Right Lung:
Proximal Airways: Normal anatomic branching to the segmental level.
Mucosa/Findings: No evidence of mass, lesions, bleeding, or other endobronchial pathology.
Intervention: Successful therapeutic aspiration was performed to clear mucus from the Right Mainstem and Bronchus Intermedius.

Left Lung:
Proximal Airways: The distal left mainstem (LMS) bronchus was {lms_findings}.
LUL: Noted to be {lul_condition}.
LLL: Normal anatomic branching to the segmental level.
Mucosa/Secretions: Mucosa was normal; secretions were minimal, thin, and clear. No mass or lesions identified.

Interventions:
Therapeutic Aspiration: Performed to clear the Left Mainstem of mucus.
LMS Balloon Dilation: A {balloon_dims} {balloon_type} balloon was used to dilate the Left Mainstem stenosis to {target_dilation}.
A total of 1 inflation was performed with a dilation time of {inflation_time}.

LUL Recanalization Attempt:
Linear EBUS was used to identify the area of the prior airway.
A needle knife was used to cut into the airway.
The pathway was reinforced using serial needle dilation ({needle_sequence}).
A {lul_balloon} balloon was used to engage the airway but {fail_reason};
it was unable to dilate open the airway.

The attempt was stopped given the inability to completely engage the LUL passage.
Conclusion: The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S) None 

IMPRESSION / PLAN
{age}-year-old {gender_long} presenting for evaluation of airway stenosis.
LMS stenosis successfully dilated to {target_dilation}.
LUL complete fusion; recanalization attempted with needle knife and serial dilation but aborted due to inability to pass the balloon.
The patient tolerated the procedure well with no immediate complications.

Plan: Repeat bronchoscopy in {follow_up}.
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Generate Op Report. {age}{gender_short}, {ref_physician}. Dx: Airway stenosis. Findings: LMS stenosis ({lms_findings_short}), LUL fused. Actions: LMS balloon dilation ({target_dilation}). LUL recan attempted w/ needle knife/balloon but failed/aborted. Plan: rpt {follow_up}.",
    
    # Style 2: Dictation style
    "Please draft a bronchoscopy note for Dr. {attending}. Patient is a {age} year old {gender_long}. We found the LMS {lms_findings} and the LUL {lul_condition}. We dilated the LMS to {target_dilation} using a {balloon_dims} balloon. We tried to open the LUL with EBUS and needles ({needle_sequence}) but the balloon couldn't pass. Procedure aborted for LUL.",
    
    # Style 3: Sloppy / Quick Handoff
    "{age}yo {gender_short} airway stenosis. Right side clear. Left LMS narrow, dilated to {target_dilation}. LUL was fused shut. Tried to recan w/ needle knife + dilation but unsuccessful. Pt stable. follow up {follow_up}.",
    
    # Style 4: Billing / Technical Focus
    "Codes: 31630, 31641, 31899NFN. Diagnosis J98.09. {age}/{gender_short}. Procedures: LMS dilation (to {target_dilation}), LUL recanalization attempt (failed). Instruments: {balloon_type} balloon, EBUS, Needle knife. No complications.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nAttending: {attending}\nFindings: LMS stenosis, LUL complete fusion.\nInterventions: LMS dilated to {target_dilation}. LUL recanalization attempted (aborted).\nOutcome: Stable."
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
        assistant = random.choice(data_pool["assistant"])
        
        # Clinical vars
        lms_findings = random.choice(data_pool["lms_findings"])
        # Create a short version of lms findings for the prompt
        lms_findings_short = "stenotic" if "stenotic" in lms_findings else "narrowed"
        
        balloon_type = random.choice(data_pool["balloon_type"])
        balloon_dims = random.choice(data_pool["balloon_dims"])
        target_dilation = random.choice(data_pool["target_dilation"])
        inflation_time = random.choice(data_pool["inflation_time"])
        
        lul_condition = random.choice(data_pool["lul_condition"])
        needle_sequence = random.choice(data_pool["needle_sequence"])
        lul_balloon = random.choice(data_pool["lul_balloon"])
        fail_reason = random.choice(data_pool["fail_reason"])
        
        follow_up = random.choice(data_pool["follow_up"])
        
        # Date generation
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
        date_str = date_obj.strftime("%m/%d/%Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            ref_physician=ref_physician,
            attending=attending,
            lms_findings=lms_findings,
            lms_findings_short=lms_findings_short,
            lul_condition=lul_condition,
            target_dilation=target_dilation,
            balloon_dims=balloon_dims,
            balloon_type=balloon_type,
            needle_sequence=needle_sequence,
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_str=date_str,
            ref_physician=ref_physician,
            age=age,
            gender_long=gender_long,
            attending=attending,
            assistant=assistant,
            lms_findings=lms_findings,
            lul_condition=lul_condition,
            balloon_dims=balloon_dims,
            balloon_type=balloon_type,
            target_dilation=target_dilation,
            inflation_time=inflation_time,
            needle_sequence=needle_sequence,
            lul_balloon=lul_balloon,
            fail_reason=fail_reason,
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