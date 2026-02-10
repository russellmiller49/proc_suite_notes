import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_095" 
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
    "patient_names": [
        "James Smith", "Robert Johnson", "Michael Williams", "David Brown", 
        "William Jones", "Richard Garcia", "Joseph Miller", "Thomas Davis"
    ],
    "ages": ["45", "52", "56", "61", "67", "72", "59", "64"],
    "gender_tuple": [("male", "M", "He", "his"), ("female", "F", "She", "her")],
    "attending_names": [
        "Dr. Anderson", "Dr. Chen", "Dr. Patel", "Dr. Roberts", "Dr. Kim", "Dr. Weiss"
    ],
    "fellow_names": ["Dr. Lee", "Dr. Smith", "Dr. Gomez", "Dr. Wright"],
    "ref_physicians": ["Dr. House", "Dr. Wilson", "Dr. Cuddy", "Dr. Foreman"],
    "staff_rn": ["Sarah RN", "Mike RN", "Jessica RN", "Emily RN"],
    "staff_rt": ["Tom RT", "Lisa RT", "David RT", "Karen RT"],
    "dates": [
        "January 12, 2024", "February 28, 2024", "March 15, 2024", 
        "April 04, 2024", "May 20, 2024"
    ],
    
    # Clinical Variations
    "diagnosis_code": ["J98.09", "J98.8", "J95.850"],
    
    # Anatomy Scenarios (Tuple: Severe Site, Mild Site, Specific Target for Stent)
    "anatomy_scenarios": [
        ("lingula orifice", "Right Mainstem (RMS) anastomosis and Bronchus Intermedius (BI)", "LUL Lingula Carina (Lc1)", "Right Mainstem"),
        ("RUL orifice", "Left Mainstem (LMS) and Carina", "RUL Carina (Rc1)", "Left Mainstem"),
        ("LUL orifice", "Right Mainstem (RMS)", "LUL Carina (Lc2)", "Right Mainstem"),
        ("RML orifice", "Bronchus Intermedius (BI)", "RML Carina (Rc2)", "Bronchus Intermedius"),
    ],
    
    # Intervention Details
    "stent_types": ["Aero mini 6x10", "Aero 10x15", "Ultraflex 12x10", "Silicone 10x10"],
    "balloon_severe": ["6/7/8", "8/9/10", "4/5/6"],
    "balloon_mild": ["10/11/12", "12/13/15", "11/12/13"],
    "severe_target_mm": ["8", "10", "6"],
    "mild_target_mm": ["12", "14", "13"],
    
    # Patency stats
    "pre_severe_patency": ["10%", "20%", "15%", "5%"],
    "pre_mild_patency": ["70%", "80%", "75%"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_doc}

INDICATION FOR OPERATION {patient_name} is a {age}-year-old {gender_long} who presents with airway stenosis.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 

31625 Endobronchial Biopsy(s) 

31636 Dilate and bronchial stent initial bronchus 

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

ATTENDING {attending}

ASSISTANT {fellow}

SUPPORT STAFF RN: {rn} RT: {rt}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pedatric) Bronchoscope.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Initial Airway Inspection There were significant stenosis noted at the {site_severe}.
Mild stenosis was noted at the {site_mild}.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the airways from mucus.
{site_mild_short} Interventions Endobronchial obstruction at the {site_mild} was treated with the following modalities:


Electrocautery: Needle knife, Effect 4, 40W, was used to make 2-3 second radial cuts.
Biopsy: Endobronchial biopsy was performed at the {site_mild_short}. The lesion was successfully removed and samples were sent for Pathology.
Balloon Dilation: A {balloon_m} Elation balloon was used to perform dilation to {target_m} mm at the {site_mild_short}.
Total 1 inflation with dilation time of 60 seconds.

Result: Prior to treatment, the affected airway was noted to be {pre_patency_m} patent.
After treatment, the airway was 100% patent.

{site_severe} Interventions Endobronchial obstruction at the {site_severe} was treated with the following modalities:


Electrocautery: Needle knife, Effect 4, 40W, was used to make 2-3 second radial cuts.
Balloon Dilation: A {balloon_s} Elation balloon was used to perform dilation to {target_s} mm at the {site_severe_specific}.
Total 1 inflation with dilation time of 60 seconds.


Stent Placement: The following stent ({stent}) was placed in the {site_severe}.
Result: Prior to treatment, the affected airway was noted to be {pre_patency_s} patent. After treatment, the airway was 100% patent.
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{site_mild_short} Biopsy - Pathology 

IMPRESSION/PLAN

{patient_name} is a {age}-year-old {gender_long} who presents for bronchoscopy for airway stenosis.
Follow up in 2 weeks for repeat bronchoscopy.

Await final pathology results.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Operative note for {patient_name}, {age}{gender_short}. Ref {ref_doc}. Found significant stenosis at {site_severe} and mild at {site_mild}. Interventions: Stented {site_severe} with {stent}, dilated/biopsied {site_mild_short}. No complications.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {attending}. Patient is {patient_name}, {age} year old {gender_long}. Diagnosis {dx_code}. We treated stenosis in the {site_severe} with a {stent} stent and balloon dilation. We also treated mild stenosis in the {site_mild} with dilation and biopsy. Pre-treatment patency was {pre_patency_s} at the severe site and {pre_patency_m} at the mild site. All post-treatment patency 100%.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} airway stenosis. {site_severe} tight ({pre_patency_s}), put in {stent}. {site_mild} mild ({pre_patency_m}), dilated to {target_m}mm and bx. Gen anesthesia. Stable.",
    
    # Style 4: Billing Focus
    "Codes: 31645, 31625, 31636, 31641. Dx {dx_code}. Procedure: Bronchoscopy with stent placement ({site_severe}) and dilation/biopsy ({site_mild}). Stent: {stent}. Balloon sizes: {balloon_s} and {balloon_m}. Attending: {attending}.",
    
    # Style 5: Structured Request
    "Patient: {patient_name}\nAge/Sex: {age}/{gender_short}\nIndication: Airway Stenosis\nFindings:\n1. {site_severe} (Severe, {pre_patency_s} patent) -> Stent ({stent})\n2. {site_mild} (Mild, {pre_patency_m} patent) -> Dilation/Biopsy\nPlan: Follow up 2 weeks."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        date = random.choice(data_pool["dates"])
        ref_doc = random.choice(data_pool["ref_physicians"])
        patient = random.choice(data_pool["patient_names"])
        age = random.choice(data_pool["ages"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, his/her)
        
        attending = random.choice(data_pool["attending_names"])
        fellow = random.choice(data_pool["fellow_names"])
        rn = random.choice(data_pool["staff_rn"])
        rt = random.choice(data_pool["staff_rt"])
        
        dx_code = random.choice(data_pool["diagnosis_code"])
        
        # Anatomy logic to ensure consistency
        # (Severe Site, Mild Site, Specific Target for Stent, Mild Short Name)
        anatomy = random.choice(data_pool["anatomy_scenarios"])
        site_severe = anatomy[0]
        site_mild = anatomy[1]
        site_severe_specific = anatomy[2]
        site_mild_short = anatomy[3]
        
        stent = random.choice(data_pool["stent_types"])
        
        balloon_s = random.choice(data_pool["balloon_severe"])
        target_s = random.choice(data_pool["severe_target_mm"])
        
        balloon_m = random.choice(data_pool["balloon_mild"])
        target_m = random.choice(data_pool["mild_target_mm"])
        
        pre_patency_s = random.choice(data_pool["pre_severe_patency"])
        pre_patency_m = random.choice(data_pool["pre_mild_patency"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            patient_name=patient,
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            ref_doc=ref_doc,
            attending=attending,
            dx_code=dx_code,
            site_severe=site_severe,
            site_mild=site_mild,
            site_mild_short=site_mild_short,
            stent=stent,
            balloon_s=balloon_s,
            balloon_m=balloon_m,
            target_m=target_m,
            pre_patency_s=pre_patency_s,
            pre_patency_m=pre_patency_m
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            ref_doc=ref_doc,
            patient_name=patient,
            age=age,
            gender_long=gender_tup[0],
            dx_code=dx_code,
            attending=attending,
            fellow=fellow,
            rn=rn,
            rt=rt,
            site_severe=site_severe,
            site_mild=site_mild,
            site_mild_short=site_mild_short,
            site_severe_specific=site_severe_specific,
            balloon_s=balloon_s,
            target_s=target_s,
            balloon_m=balloon_m,
            target_m=target_m,
            stent=stent,
            pre_patency_s=pre_patency_s,
            pre_patency_m=pre_patency_m
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