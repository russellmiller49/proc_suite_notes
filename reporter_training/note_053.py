import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_053"
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
    "attending": [
        "Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Patel", "Dr. Ingraham", "Dr. Weiss"
    ],
    "age": ["35", "42", "49", "55", "61", "68", "72", "50", "39"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    
    # Variations on the complex medical history (Indication)
    "indication_scenario": [
        "polycythemia vera (JAK2 mutation) and a history of thrombogenic events. {pronoun} presented with shortness of breath and chest pain and was found to have group 4 CTEPH with massive PEs and RV strain",
        "severe COVID-19 ARDS with fibrotic lung disease. {pronoun} presented with acute hypoxic respiratory failure and required prolonged sedation",
        "interstitial lung disease exacerbation with pulmonary hypertension. {pronoun} suffered a cardiac arrest requiring prolonged resuscitation and subsequent RV failure",
        "multifocal pneumonia complicated by septic shock. {pronoun} developed critical illness myopathy and failed multiple extubation attempts"
    ],
    
    # Variations on the ECMO/Stroke course
    "clinical_course": [
        "course was complicated by a left CVA following failed thrombectomy and subsequent RV failure requiring VA ECMO, which was converted to VV ECMO on 12/10",
        "course was complicated by severe barotrauma requiring high PEEP strategies and initiation of VV ECMO for refractory hypoxemia",
        "course was complicated by heparin-induced thrombocytopenia and a right-sided stroke, necessitating a transition to argatroban while on VV ECMO",
        "hospital stay was prolonged by acute renal failure requiring CRRT and dependence on VV ECMO for oxygenation support"
    ],
    
    # Ultrasound Anatomy Findings
    "us_findings": [
        "A slightly high-riding innominate artery and a large bridging neck vein were identified",
        "A prominent thyroid isthmus and a traversing anterior jugular vein were identified",
        "Standard vascular anatomy was observed, though a small crossing vessel was noted at the level of the 3rd ring",
        "A high-riding innominate artery was identified crossing at the suprasternal notch"
    ],
    
    # Variations on the specific vessels managed during dissection
    "vessel_management": [
        "Two vertical engorged veins were identified with a bridging vein between them. The bridging vein was dissected, suture ligated, and divided",
        "A large anterior jugular vein was identified crossing the midline. It was dissected, clamped, and ligated with silk sutures",
        "Several small superficial veins were encountered in the subcutaneous tissue and coagulated with Bovie cautery",
        "An engorged thyroid imus vein was identified, doubly ligated, and divided to clear the pre-tracheal space"
    ],
    
    # Tracheal Ring Entry
    "tracheal_entry": [
        "between the 2nd and 3rd cartilaginous rings",
        "between the 1st and 2nd cartilaginous rings",
        "through the 2nd tracheal interspace"
    ],
    
    # Tube specifics
    "tube_details": [
        ("#7", "Shiley"),
        ("#8", "Shiley"),
        ("#6", "Shiley"),
        ("#8", "Portex"),
        ("#7", "Portex")
    ],
    
    # Anticoagulation Plan
    "anticoag_plan": [
        ("bivalirudin", "1 hour"),
        ("heparin", "4 hours"),
        ("anticoagulation", "6 hours"),
        ("bivalirudin", "2 hours")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Current Date] ATTENDING PHYSICIAN: {attending}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} with {indication}.
{clinical_course}.
The patient requires a tracheostomy to assist with ventilator weaning, secretion management, and rehabilitation.

CONSENT The primary team, ICU team, and family were in agreement with the procedure.
The nature, purpose, risks, and benefits were discussed. Consent was signed.

PREOPERATIVE DIAGNOSIS
Respiratory failure on VV ECMO 
CTEPH, Acute PE, RV Failure (or primary etiology)
Status post complications as noted

POSTOPERATIVE DIAGNOSIS
Same 

PROCEDURE
Modified open/percutaneous tracheostomy 
Bronchoscopic guidance 

ANESTHESIA Local anesthesia with sedation/analgesia as per ICU protocol.
ESTIMATED BLOOD LOSS 1 mL 
COMPLICATIONS None immediately apparent 
DISPOSITION Stable, ventilated, remained in ICU, on VV ECMO 

PROCEDURE IN DETAIL
Preparation and Exposure The patient remained in the ICU on VV ECMO support.
{pronoun} was positioned supine with a padded shoulder roll, head elevated, and neck moderately extended. A surgical timeout was performed.
The anterior neck was prepped and draped in the standard sterile fashion.

Neck ultrasound was performed to confirm vascular anatomy.
{us_findings}.
5 mL of 1% lidocaine was injected 2-3 cm above the sternal notch;
the injection site was adjusted higher due to the anatomical findings.

Incision and Dissection A 3 cm horizontal skin incision was made with a #15 blade in a relaxed skin tension line midway between the cricoid cartilage and the sternal notch.
Bovie cautery was used to dissect through the platysma down to the strap muscles, avoiding the anterior jugular veins.
{vessel_management}.
to allow visualization of the midline raphe.
The strap muscles were separated vertically at the midline with Bovie cautery and retracted laterally.
Using blunt and careful cautery dissection, the anterior tracheal wall was freed of soft tissue.
The innominate artery was identified and protected; the soft tissue between the artery and trachea was left undisturbed.

Tracheostomy Placement The trachea was palpated to identify the tracheal rings, ensuring adequate distance from the innominate artery.
Under bronchoscopic guidance, the endotracheal tube cuff was deflated and withdrawn to a level below the vocal cords.
A finder needle was placed through the anterior trachea {tracheal_entry}.
Once position was confirmed by bronchoscopy, a Seldinger technique was used to serially dilate the tract over a wire.
A {tube_size} cuffed {tube_type} tracheostomy tube was placed.

Confirmation and Closure The tracheostomy cuff was inflated.
Cross-table ventilation was performed, and placement was confirmed by both bronchoscopic visualization through the tracheostomy and CO2 return on the monitor.
The inner cannula was inserted.

Surgicel was placed in the wound bed for hemostasis, anticipating the resumption of anticoagulation.
The tracheostomy was secured with loose 2-0 prolene sutures to the skin and tracheostomy straps.
The endotracheal tube was withdrawn completely.

IMPRESSION / PLAN
Successful placement of {tube_size} {tube_type} tracheostomy via modified open/percutaneous technique.
Okay to resume {anticoag_drug} (anticoagulation) in {anticoag_time}.
Trach ties to remain for 7-10 days.
No routine trach exchange within the first 14 days unless issues arise.
Avoid over-inflation of the cuff.
Family notified of successful procedure.
"""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Patient {age} {gender_short}. On VV ECMO. Needs modified open trach. {us_desc_short} on US. Placed {tube_size} {tube_type}. Restart {anticoag_drug} in {anticoag_time}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {attending}. Patient is a {age}-year-old {gender_long} on VV ECMO. Indication is {indication_snippet}. We did a modified open tech due to {us_desc_short}. Used a {tube_size} {tube_type}. Ligation of bridging veins required. Plan to restart {anticoag_drug} in {anticoag_time}.",
    
    # Style 3: Sloppy / Quick Input
    "IP op note. {age}yo {gender_short}. dx: resp failure, ecmo. procedure: modified perc trach. findings: {us_desc_short}, ligated veins. tube: {tube_size} {tube_type}. no comps. resume {anticoag_drug} + {anticoag_time}.",
    
    # Style 4: Billing / Coding Focus
    "Procedure: Modified Percutaneous Tracheostomy (31600). Attending: {attending}. Patient: {age} {gender_short}. Complex anatomy: {us_desc_short}. Implant: {tube_size} {tube_type}. Post-op: Resume {anticoag_drug} {anticoag_time}.",
    
    # Style 5: Structured Request
    "ACTION: Write Operative Report\nPATIENT: {age}/{gender_short}\nSTATUS: VV ECMO\nANATOMY: {us_desc_short}\nPROCEDURE: Modified open approach, ligation of veins\nTUBE: {tube_size} {tube_type}\nPLAN: {anticoag_drug} in {anticoag_time}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        attending = random.choice(data_pool["attending"])
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, CapPronoun, Possessive)
        
        # Clinical variables
        # Note: Capitalize the first letter of the pronoun for the start of the sentence in indication
        raw_indication = random.choice(data_pool["indication_scenario"])
        indication = raw_indication.format(pronoun=gender_tup[2]) 
        # Create a short snippet for prompts
        indication_snippet = raw_indication.split('.')[0]
        
        clinical_course = random.choice(data_pool["clinical_course"])
        
        us_findings = random.choice(data_pool["us_findings"])
        # Create short US desc for prompts
        if "high-riding" in us_findings:
            us_desc_short = "high-riding innominate"
        elif "thyroid" in us_findings:
            us_desc_short = "large thyroid isthmus"
        else:
            us_desc_short = "complex neck veins"
            
        vessel_management = random.choice(data_pool["vessel_management"])
        tracheal_entry = random.choice(data_pool["tracheal_entry"])
        
        tube_tup = random.choice(data_pool["tube_details"])
        anticoag_tup = random.choice(data_pool["anticoag_plan"])

        # B. Generate Completion (The Note)
        completion = note_template.format(
            attending=attending,
            age=age,
            gender_long=gender_tup[0],
            pronoun=gender_tup[2], # He/She
            indication=indication,
            clinical_course=clinical_course,
            us_findings=us_findings,
            vessel_management=vessel_management,
            tracheal_entry=tracheal_entry,
            tube_size=tube_tup[0],
            tube_type=tube_tup[1],
            anticoag_drug=anticoag_tup[0],
            anticoag_time=anticoag_tup[1]
        )

        # C. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            attending=attending,
            us_desc_short=us_desc_short,
            tube_size=tube_tup[0],
            tube_type=tube_tup[1],
            anticoag_drug=anticoag_tup[0],
            anticoag_time=anticoag_tup[1],
            indication_snippet=indication_snippet
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