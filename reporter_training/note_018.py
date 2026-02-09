import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_018"
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
    "age": ["45", "52", "58", "60", "64", "68", "71", "75", "82"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": [
        "Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", 
        "Dr. Miller", "Dr. Jones", "Dr. Patel", "Dr. Weiss"
    ],
    "indication": [
        "airway stenosis", "subglottic stenosis", "tracheal stenosis", 
        "malignant airway obstruction", "benign tracheal narrowing"
    ],
    "diagnosis_code": ["J98.09", "J95.5", "J38.6", "C34.90"],
    "diagnosis_text": [
        "Other diseases of bronchus, not elsewhere classified",
        "Postprocedural subglottic stenosis",
        "Stenosis of larynx",
        "Malignant neoplasm of unspecified part of bronchus or lung"
    ],
    "narrowing_location": [
        "at the cord level", "in the subglottic space", 
        "in the proximal trachea", "in the mid-trachea"
    ],
    "cricoid_relation": ["At cricoid", "1 cm below cricoid", "2 cm below cricoid", "Just above cricoid"],
    
    # Measurements logic (Pre-calculated sets to ensure physical consistency)
    "measurements": [
        {
            "dist_vocal": "0 mm", "top_to_bot": "105 mm", "bot_to_carina": "90 mm", "narrow": "6 mm"
        },
        {
            "dist_vocal": "10 mm", "top_to_bot": "95 mm", "bot_to_carina": "80 mm", "narrow": "5 mm"
        },
        {
            "dist_vocal": "15 mm", "top_to_bot": "80 mm", "bot_to_carina": "100 mm", "narrow": "4 mm"
        },
        {
            "dist_vocal": "5 mm", "top_to_bot": "110 mm", "bot_to_carina": "85 mm", "narrow": "7 mm"
        }
    ],
    
    # Intervention Details
    "cautery_setting": ["Endo cut I 2 2 1", "Endo cut Q 3 1 1", "Coagulation Soft 40W", "Spray Coag 30W"],
    "cautery_technique": ["Radial cut (4-second burst)", "Linear incision (3-second burst)", "Circumferential ablation"],
    
    # Patency (Pre -> Post)
    "patency": [
        ("50%", "80%"), ("20%", "90%"), ("30%", "85%"), ("40%", "100%"), ("10%", "70%")
    ],
    
    # Balloon
    "balloon_loc": ["Trachea (Proximal 1/3)", "Trachea (Mid 1/3)", "Subglottic Space"],
    "balloon_device": ["8/9/10 Elation balloon", "10/11/12 CRE balloon", "12/13/15 Hercules balloon"],
    "balloon_size_final": ["10 mm", "11 mm", "12 mm", "14 mm"],
    "balloon_inflation_time": ["60 seconds", "45 seconds", "90 seconds"],
    "balloon_cycles": ["3 inflations", "2 inflations", "4 inflations"],
    
    # Excision
    "excision_method": ["forceps in a circular fashion", "cryoprobe extraction", "rigid coring"],
    
    # BAL
    "bal_location": [
        "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)",
        "RUL Apical Segment",
        "LLL Basilar Segments",
        "LUL Lingula"
    ],
    "bal_volume": [("60 cc", "20 cc"), ("100 cc", "40 cc"), ("120 cc", "50 cc"), ("50 cc", "15 cc")],
    
    # Therapeutic Aspiration
    "aspiration_locs": [
        "Trachea (Proximal 1/3, Middle 1/3, Distal 1/3), Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Bilateral mainstems and distal trachea",
        "Right lower lobe and bronchus intermedius",
        "Left mainstem and upper lobe"
    ],
    
    "follow_up": ["4-6 weeks", "2-3 months", "1 week", "6-8 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT
Obtained before the procedure.
Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field

POSTOPERATIVE DIAGNOSIS
{post_op_code} {post_op_dx}

PROCEDURE
Therapeutic aspiration initial episode (CPT 31645)
Diagnostic bronchoscopy/lavage (BAL) (CPT 31624)
Dilate and tracheal stent placement (CPT 31631)
Bronchoscopy with excision (CPT 31640)
Destruction of tumor OR relief of stenosis by any method other than excision (e.g., laser therapy, cryotherapy) (CPT 31641)

ANESTHESIA
General Anesthesia.

MONITORING
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS
None.

COMPLICATIONS
None.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Patient Position: Supine
Initial Airway Inspection: Significant narrowing was noted {narrowing_loc}; the therapeutic scope was not able to be passed.

Surgical Planning Measurements:
Distance from vocal folds to stenosis: {m_dist_vocal}
Location of stenosis relative to cricoid: {m_cricoid}
Distance from top of stenosis to bottom: {m_top_bot}
Distance of bottom of stenosis to carina: {m_bot_carina}
Approximation of most narrow portion: {m_narrow}

Interventions:

Endobronchial Tumor Destruction / Incision (Electrocautery)
Endobronchial obstruction at the subglottic level was treated with electrocautery.
Tool: Knife (needle)
Settings: {cautery_setting}
Technique: {cautery_technique}
Results: Prior to treatment, the affected airway was noted to be {patency_pre} patent.
After treatment, the airway was {patency_post} patent.

Balloon Dilation
Bronchial stenosis was dilated with a balloon catheter.
Location: {balloon_loc}
Device: {balloon_device}
Technique: Dilated to {balloon_final}.
Total {balloon_cycles} with dilation time of {balloon_time} each.

Endobronchial Excision / Debridement
Endobronchial excision of tissue was performed at the {balloon_loc}. The lesion was successfully removed.
A sheet of tissue was completely peeled off with {excision_method}.
Samples were sent for Microbiology (Cultures/Viral/Fungal) and Cytology.

Bronchoalveolar Lavage (BAL)
BAL was performed in the {bal_loc} with saline instilled and returned.
Volume: Instilled {bal_in} of NS; suction returned with {bal_out} of NS.
Analysis: Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out the airways from mucus and blood.
Locations: {aspiration_locs}.

Termination:
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
Endobronchial Biopsy (EBBX) — Cytology/Microbiology
BAL — Cell Count, Microbiology, Cytology

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for {indication}.
Repeat bronchoscopy in {follow_up}.
Follow-up in clinic.
"""

prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate IP report. {age}{gender_short}, ref {doctor}. Dx: {indication}. Found narrowing {narrowing_loc}. Cautery ({cautery_setting}), Balloon ({balloon_device} to {balloon_final}), Excision via {excision_method_short}. BAL {bal_loc_short}. Pre {patency_pre} -> Post {patency_post}. Plan: scope in {follow_up}.",
    
    # Style 2: Dictation
    "Please write a procedure note for a {age} year old {gender_long} referred by {doctor} for {indication}. Under general anesthesia, we found significant narrowing {narrowing_loc}. We used electrocautery ({cautery_setting}), then balloon dilation with a {balloon_device} up to {balloon_final}. We also excised tissue using {excision_method_short}. BAL was done in the {bal_loc_short}. Patency improved from {patency_pre} to {patency_post}. Repeat scope in {follow_up}.",
    
    # Style 3: Sloppy / Handoff
    "{age}yo {gender_short} {indication}. {doctor} pt. Cautery used {cautery_setting}, balloon {balloon_final} x {balloon_cycles}. Excision done. BAL {bal_loc_short} ({bal_in}/{bal_out}). Stenosis {m_cricoid}. Improved {patency_pre} to {patency_post}. No comps.",
    
    # Style 4: Billing Focus
    "Procedure: Bronchoscopy with lysis of stenosis (31641), dilation (31631), excision (31640), BAL (31624). Pt {age} {gender_short}. Indication: {indication}. Findings: Stenosis {narrowing_loc}, dilated to {balloon_final}. Cautery used. BAL return {bal_out}. F/U {follow_up}.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nReferring: {doctor}\nIndication: {indication}\nInterventions:\n- Cautery: {cautery_setting}\n- Dilation: {balloon_device} to {balloon_final}\n- Excision: {excision_method_short}\n- BAL: {bal_loc_short}\nPatency Change: {patency_pre} to {patency_post}"
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
        doctor = random.choice(data_pool["doctor"])
        indication = random.choice(data_pool["indication"])
        
        # Diagnosis
        post_op_code = random.choice(data_pool["diagnosis_code"])
        post_op_dx = random.choice(data_pool["diagnosis_text"])
        
        # Narrowing & Measurements
        narrowing_loc = random.choice(data_pool["narrowing_location"])
        cricoid_rel = random.choice(data_pool["cricoid_relation"])
        meas = random.choice(data_pool["measurements"])
        
        # Interventions
        cautery_set = random.choice(data_pool["cautery_setting"])
        cautery_tech = random.choice(data_pool["cautery_technique"])
        
        patency = random.choice(data_pool["patency"]) # Tuple (Pre, Post)
        
        balloon_loc = random.choice(data_pool["balloon_loc"])
        balloon_dev = random.choice(data_pool["balloon_device"])
        balloon_final = random.choice(data_pool["balloon_size_final"])
        balloon_time = random.choice(data_pool["balloon_inflation_time"])
        balloon_cycles = random.choice(data_pool["balloon_cycles"])
        
        excision_meth = random.choice(data_pool["excision_method"])
        
        bal_loc = random.choice(data_pool["bal_location"])
        bal_vol = random.choice(data_pool["bal_volume"]) # Tuple (Instilled, Returned)
        
        aspiration_locs = random.choice(data_pool["aspiration_locs"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # Helper strings for prompts
        excision_method_short = "forceps" if "forceps" in excision_meth else "cryo" if "cryo" in excision_meth else "coring"
        bal_loc_short = "RML" if "RML" in bal_loc else "RUL" if "RUL" in bal_loc else "LLL" if "LLL" in bal_loc else "LUL"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            doctor=doctor, indication=indication,
            narrowing_loc=narrowing_loc,
            cautery_setting=cautery_set,
            balloon_device=balloon_dev, balloon_final=balloon_final, balloon_cycles=balloon_cycles,
            excision_method_short=excision_method_short,
            bal_loc_short=bal_loc_short,
            bal_in=bal_vol[0], bal_out=bal_vol[1],
            patency_pre=patency[0], patency_post=patency[1],
            m_cricoid=cricoid_rel,
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0], 
            doctor=doctor, indication=indication,
            post_op_code=post_op_code, post_op_dx=post_op_dx,
            narrowing_loc=narrowing_loc,
            
            # Measurements
            m_dist_vocal=meas["dist_vocal"],
            m_cricoid=cricoid_rel,
            m_top_bot=meas["top_to_bot"],
            m_bot_carina=meas["bot_to_carina"],
            m_narrow=meas["narrow"],
            
            # Procedures
            cautery_setting=cautery_set,
            cautery_technique=cautery_tech,
            patency_pre=patency[0], patency_post=patency[1],
            
            balloon_loc=balloon_loc,
            balloon_device=balloon_dev,
            balloon_final=balloon_final,
            balloon_cycles=balloon_cycles,
            balloon_time=balloon_time,
            
            excision_method=excision_meth,
            
            bal_loc=bal_loc,
            bal_in=bal_vol[0], bal_out=bal_vol[1],
            
            aspiration_locs=aspiration_locs,
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