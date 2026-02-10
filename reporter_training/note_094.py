import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_094"
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
    "age": ["45", "52", "56", "59", "63", "67", "71", "74"],
    "gender_tuple": [("female", "F", "she"), ("male", "M", "he")],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller"],
    "referring": ["Dr. Jones", "Dr. Doe", "Dr. White", "Dr. Lee"],
    
    # Clinical Context
    "indication_dx": [
        "anastomosis dehiscence, ischemic lung injury, and bronchial stenosis",
        "airway stenosis and recurrent granulation tissue",
        "post-transplant airway complications requiring maintenance",
        "recurrent microbial colonization and airway stenosis"
    ],
    
    # Stent Details
    "rml_stent_size": ["AeroMini 8mm x 15mm", "AeroMini 8mm x 10mm", "AeroMini 6mm x 15mm"],
    "lingula_stent_size": ["AeroMini 6mm x 10mm", "AeroMini 6mm x 15mm", "AeroMini 5mm x 10mm"],
    
    # Findings Variations
    "rml_findings": [
        "Small amount of tan exudative debris overlying RC2 carina minimally overlying edge of stent; minimal granulation tissue.",
        "Moderate mucous plugging at the proximal edge; mild granulation tissue visible.",
        "Clean stent edges with very minimal tissue overgrowth.",
        "Significant exudative debris requiring extensive debridement."
    ],
    "lingula_findings": [
        "Minimal non-obstructing mucus in stent.",
        "Mild granulation tissue at the distal end, non-obstructing.",
        "Clear stent with no significant secretions.",
        "Thick secretions adhering to the proximal rim."
    ],
    
    # BAL Details
    "bal_instilled": ["50", "60", "100", "120"],
    "bal_return": ["20", "25", "40", "55"],
    
    # Patency percentages
    "pre_patency": ["80%", "85%", "90%", "95%"],
    "post_patency": ["95%", "100%"],
    
    # Follow up
    "follow_up_weeks": ["2-3", "3-4", "4-6", "6-8"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring}

INDICATION FOR OPERATION {age}-year-old {gender_long} who presents with bilateral lung transplant and complication of {indication_dx} requiring endobronchial stents.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS) 
31646 Therapeutic aspiration subsequent episodes 
31622 Dx bronchoscope/cell washing 
31624 Dx bronchoscope/lavage (BAL) 
31640 Bronchoscopy with excision 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

NOTE: This patient required a bilateral procedure today when this procedure would typically be unilateral (Modifier 50).

ATTENDING {attending}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Disposable Bronchoscope; 1.7mm cryoprobe; bland alligator forceps.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL A timeout was performed (confirming the patient's name, procedure type, and procedure location).
Sedation was initiated, and mechanical ventilation was initiated via the patient's tracheostomy tube.
The Flexible Therapeutic Bronchoscope was advanced for airway examination. Endobronchial topical lidocaine was applied to the main carina, right carina 1, and left carina 2.

Initial Airway Examination Findings:

Trachea: Tracheostomy tube in good position; distal 1/3 normal.
Main Carina: Sharp.

Right Lung Proximal Airways: RMSB intact with visible sutures, greatly improved from prior with no evidence of dehiscence.
Moderate stenosis noted at RMSB anastomosis site due to circumferential fibrous tissue, but able to easily traverse with therapeutic bronchoscope without touching.

RUL: Bronchus in good repair; prior area of full-thickness erosion completely resolved. Small amount of fibrous scarring into RUL.
Bronchus Intermedius: Tan exudative debris and granulation tissue noted along the medial aspect.

RML: Stent ({rml_stent_size}) in good position and patent.
{rml_findings}
Mild non-obstructing mucus adhered to inside of stent.

RLL: RB6-10 widely patent and healthy.

Left Lung Proximal Airways: LMS anastomosis intact with visible sutures.
Mild stenosis at LMSB anastomosis site due to circumferential fibrous tissue, but able to easily traverse without touching.

LUL: Bronchus in good repair; prior area of full-thickness erosion completely resolved. Small amount of fibrous scarring in LUL.

Lingula: Stent ({lingula_stent_size}) in good position and patent. {lingula_findings}
Unable to traverse with therapeutic scope due to size, but fully patent LB4/LB5 visualized.

LLL: LB6-10 patent and healthy.

Interventions:

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the distal trachea, RMSB, RUL, BI, RML stent, RLL, LMSB, LUL, lingula stent, and LLL from mucus.
All secretions were suctioned to clear.

Excision/Debridement:
Endobronchial lesion of exudative debris at RC2 was excised with mechanical debridement using bland alligator forceps, improving patency of the RML stent.
Endobronchial lesion of exudative debris in bronchus intermedius was excised with mechanical debridement using bland alligator forceps.
Endobronchial lesion of exudative debris at LC1 was excised with mechanical debridement using bland alligator forceps, improving patency of the lingula stent.

Cryotherapy: Endobronchial lesion of granulation tissue at bronchus intermedius, RMSB anastomosis stricture, and left carina 1 was treated with a 1.7mm cryoprobe using numerous 30-second overlapping treatments.

Bronchoalveolar Lavage (BAL): Performed at RML bronchus. Instilled {bal_instilled} cc of NS, suction returned with {bal_return} cc of NS.

Results:
RML Bronchus/Stent: Prior to treatment {pre_patency} patent. After treatment 100% patent.
Bronchus Intermedius: Prior to treatment {pre_patency} patent. After treatment {post_patency} patent.
Lingula Bronchus/Stent: Prior to treatment {pre_patency} patent. After treatment 100% patent.

Completion: Therapeutic bronchoscope was removed.
A disposable bronchoscope with unused sterile channel was advanced for BAL. Residual secretions and saline were suctioned to clear.
The patient tolerated the procedure well with no immediate complications.
The patient was transported to the recovery room in stable condition.

SPECIMEN(S)
RML BAL: Cell count, cultures/micro 

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for airway evaluation and stent check.
All airways continue to greatly improve; areas of mild-to-moderate stenosis noted as described.
RML stent and lingula stent in good position and patent.
Mild tan exudative debris at edges of proximal stent causing minimal obstruction was excised, and areas of granulation tissue were treated with cryoprobe.

Plan: Repeat bronchoscopy in {follow_up_weeks} weeks.
If airways remain stable, will pursue RML stent holiday (placed [REDACTED]) at that time.
Lingula stent (placed [REDACTED]) may need to remain in place longer to allow durable remodeling."""

# 5 distinct prompt styles
prompt_styles = [
    # Style 1: Telegraphic
    "Operative note: {age} {gender_short}, bilat lung txp. Ind: {indication_dx}. Findings: RML stent ({rml_stent_size}) with {rml_findings_summary}. Lingula ({lingula_stent_size}) {lingula_findings_summary}. Interventions: Cryo, debridement, BAL ({bal_instilled}/{bal_return}cc). Plan repeat {follow_up_weeks} wks. Attending {attending}.",
    
    # Style 2: Dictation
    "Please generate a bronchoscopy report for a {age}-year-old {gender_long} patient of Dr. {referring}. History of bilateral transplant and {indication_dx}. We checked the RML stent which is a {rml_stent_size} and found {rml_findings_summary}. The Lingula stent is {lingula_stent_size}. Perform BAL returning {bal_return}cc from {bal_instilled}cc. Standard cryo and debridement performed. Follow up in {follow_up_weeks} weeks.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. stents check. RML {rml_stent_size} - {rml_findings_summary}. lingula {lingula_stent_size}. did bal {bal_return}cc return. used cryo and forceps for gran tissue. {attending} attending. plan 31640 31641 codes etc.",
    
    # Style 4: Billing Focus
    "Procedure Codes: 31899, 31646, 31622, 31624, 31640, 31641. Patient {age} {gender_short}. Indication: {indication_dx}. Findings: Stent maintenance required. RML ({rml_stent_size}) and Lingula ({lingula_stent_size}) patent post-debridement. BAL performed.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nHistory: Bilateral Lung Transplant\nIndication: {indication_dx}\nStents:\n- RML: {rml_stent_size}, {rml_findings_summary}\n- Lingula: {lingula_stent_size}\nInterventions: Cryotherapy, Debridement, BAL ({bal_instilled}cc)\nPlan: Repeat {follow_up_weeks} wks"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def summarize_findings(text):
    """Helper to make prompts less verbose than the full note"""
    if "debris" in text: return "debris/granulation"
    if "mucus" in text: return "mucus plugging"
    if "Clean" in text: return "clean/patent"
    if "Minimal" in text: return "minimal secretions"
    return "minor stenosis"

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        attending = random.choice(data_pool["attending"])
        referring = random.choice(data_pool["referring"])
        indication_dx = random.choice(data_pool["indication_dx"])
        
        rml_stent_size = random.choice(data_pool["rml_stent_size"])
        lingula_stent_size = random.choice(data_pool["lingula_stent_size"])
        
        rml_findings = random.choice(data_pool["rml_findings"])
        lingula_findings = random.choice(data_pool["lingula_findings"])
        
        bal_instilled = random.choice(data_pool["bal_instilled"])
        bal_return = random.choice(data_pool["bal_return"])
        
        pre_patency = random.choice(data_pool["pre_patency"])
        post_patency = random.choice(data_pool["post_patency"])
        follow_up_weeks = random.choice(data_pool["follow_up_weeks"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            referring=referring,
            attending=attending,
            indication_dx=indication_dx,
            rml_stent_size=rml_stent_size,
            lingula_stent_size=lingula_stent_size,
            rml_findings_summary=summarize_findings(rml_findings),
            lingula_findings_summary=summarize_findings(lingula_findings),
            bal_instilled=bal_instilled,
            bal_return=bal_return,
            follow_up_weeks=follow_up_weeks
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age,
            gender_long=gender_long,
            attending=attending,
            referring=referring,
            indication_dx=indication_dx,
            rml_stent_size=rml_stent_size,
            lingula_stent_size=lingula_stent_size,
            rml_findings=rml_findings,
            lingula_findings=lingula_findings,
            bal_instilled=bal_instilled,
            bal_return=bal_return,
            pre_patency=pre_patency,
            post_patency=post_patency,
            follow_up_weeks=follow_up_weeks
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