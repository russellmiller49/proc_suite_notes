import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_099" 
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
    "age": ["48", "52", "56", "59", "63", "67", "71", "74"],
    "gender_tuple": [("female", "F", "she", "her"), ("male", "M", "he", "his")],
    "doctor": ["Dr. Harrison", "Dr. Chen", "Dr. Gupta", "Dr. Rossi", "Dr. Smith", "Dr. Banerji"],
    
    # Clinical Indications
    "indication_desc": [
        "bilateral lung transplant complications including anastomosis dehiscence, ischemic lung injury, and bronchial stenosis",
        "post-transplant airway complications characterized by extensive granulation tissue and dehiscence",
        "complex airway disease following bilateral lung transplantation with dehiscence and severe stenosis",
    ],
    
    # Variable Procedure Metrics
    "bal_instilled": ["30", "40", "50", "60"],
    "stent_type": ["iCast fully covered", "Atrium Advanta V12 covered"],
    "stent_size_rml": ["7mm x 22mm", "6mm x 22mm", "7mm x 19mm"],
    "stent_size_lingula": ["7mm x 16mm", "6mm x 16mm", "7mm x 12mm"], # The one that fails
    
    # Balloon Dilation Details
    "balloon_type": ["Elation", "CRE", "Hercules"],
    "balloon_size_rml": ["8mm", "9mm", "7mm"],
    "balloon_size_lingula": ["6mm", "7mm", "8mm"],
    
    # Debridement Tools (Variation in technology used)
    "debridement_tool_tuple": [
        ("Erbe HybridKnife electrocautery", "Effect 2, 40 Watts, 1-5 second bursts"),
        ("APC (Argon Plasma Coagulation)", "40 Watts, pulsed mode"),
        ("Cryotherapy probe", "3 freeze-thaw cycles of 30 seconds"),
        ("Nd:YAG Laser", "20 Watts, 0.5 sec pulse duration")
    ],
    
    # Complication Variation (Bleeding vs No Bleeding)
    "bleeding_event_tuple": [
        (
            "Hemostasis: During debridement, a very small laceration to RC1 occurred. Bleeding was easily controlled and stopped with direct bronchoscopic pressure and 0.2mg epinephrine.",
            "minor bleeding at RC1 controlled with epi"
        ),
        (
            "Hemostasis: No significant bleeding occurred during debridement. Minimal oozing was controlled with saline lavage.",
            "no active bleeding, minimal oozing"
        ),
        (
            "Hemostasis: A small amount of bleeding was noted at the debridement site, controlled immediately with cold saline and wedge technique.",
            "minor bleeding controlled with cold saline"
        )
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION
{patient_name_redacted} is a {age}-year-old {gender_long} who presents with {indication}.
The patient required bronchoscopy for airway dilation, stent placement, and airway debridement.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT
Obtained before the procedure.
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
31625 Endobronchial Biopsy(s) 
31630 Balloon dilation 
31636 Dilate and bronchial stent initial bronchus 
31637 Dilate and bronchial stent additional bronchus 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 
31635 Foreign body removal 
22 Substantially greater work than normal (Unusual Procedure) 

Note on Unusual Procedure: This patient required an unusual amount of clinical expertise and use of simultaneous bronchoscopes due to the severity of the patient's profound airway injury.
This resulted in >50% increased work due to increased intensity, time, technical difficulty, and severity of the patient's condition.

ANESTHESIA
General Anesthesia 

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; Disposable Bronchoscope (Slim scope); Disposable Bronchoscope (Regular scope).

ESTIMATED BLOOD LOSS
Minimum 

COMPLICATIONS
None 

PROCEDURE IN DETAIL
A timeout was performed (confirming the patient's name, procedure type, and procedure location).
Sedation was initiated.

Initial Airway Inspection The Flexible Therapeutic Bronchoscope was advanced for airway examination.
Endobronchial topical lidocaine was applied to the main carina, right carina 1, and left carina 2.

Tracheostomy/Trachea: Tracheostomy tube in good position.
Distal trachea and main carina normal.

RMS (Right Main Stem): Dehiscence continues to be healed and remains closed.
Prior metallic hemoclip is no longer visible. Fibrinous exudate/granulation tissue noted in the donor RMS, proximal RUL bronchus, BI, overlying RML take-off, and overlying RB6 take-off.
This tissue has become bulky and partially obstructing these airways.

RUL (Right Upper Lobe): Previously seen area of full thickness erosion/ulceration along anterior wall remains fully covered by fibrinous exudate/granulation tissue.
RB1-2 normal. RB3 mildly stenotic with swirling granulation tissue/scar forming around the segmental airway take-off.

RML (Right Middle Lobe): The RML take-off is completely sealed and obstructed by fibrinous exudate/granulation tissue. RB4-5 not visible.

RLL (Right Lower Lobe): RB6 mildly stenotic due to surrounding granulation tissue. Basilar segments appear healthy.

LMS (Left Main Stem): Anastomosis intact with visible sutures, showing increasing amounts of overlying granulation tissue causing mild to moderate stenosis.

LUL (Left Upper Lobe): Evidence of continued healing with fibrin exudates/granulation tissue.
Underlying mediastinum/pulmonary artery no longer visible along medial aspect. Area looks improved from prior, but heaped granulation tissue is forming around the lingula take-off, causing moderate stenosis.

LLL (Left Lower Lobe): LB1-5 are patent. LLL bronchus and segments appear healthy. LB6-10 are patent.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the RMS, BI, RLL, LMS, and LLL from thin mucus.

RML Intervention: Dilation, Stenting, and Lavage Attention turned to the completely obstructed RML bronchus.
Dilation: Therapeutic bronchoscope was used to perform blunt dilation to 6.2 mm at the RML bronchus.
A patent airway was achieved, and copious tan-white secretions immediately poured out.
Successful therapeutic aspiration cleared the secretions, revealing patent RB4-5 segmental airways.

BAL: Bronchial alveolar lavage was performed at the RML.
Instilled {bal_instilled} cc of NS, suction returned with {bal_return} cc of NS. Samples sent for Cell Count and Microbiology.

Stent Placement: A second slim disposable bronchoscope was advanced via oral approach to assist with dual-scope visualization.
An {stent_type} {stent_size_rml} stent was successfully deployed in the RML bronchus.

Balloon Dilation: An 8/9/10 {balloon_type} balloon was used to perform dilation to {balloon_size_rml} within the full RML bronchus stent (1 inflation, 10 seconds), achieving 100% patency.
The proximal portion of the stent was flared using blunt dilation with the bronchoscope tip, blunt forceps, and serial balloon dilations.
The 8/9/10 {balloon_type} balloon was used for serial dilations to 8 mm, 9 mm, and 10 mm at the proximal stent (5 inflations, 5-10 seconds each).

Lingula Intervention: Attempted Stenting and Dilation Attention turned to the stenotic lingula airway.
Stent Attempt: An {stent_type} {stent_size_lingula} stent was deployed.
However, the stent migrated proximally and the distal edge became caught on LC1.
It could not be advanced back into the lingula despite multiple attempts.

Foreign Body Removal: The {stent_type} stent overlying the lingula take-off was extracted using blunt forceps.

Balloon Dilation: An 8/9/10 {balloon_type} balloon was used to perform dilation to {balloon_size_lingula} within the lingular bronchus (2 inflations, 30 seconds each).
This resulted in improved patency.

RMS Debridement and Biopsy Attention turned to the bulky partially obstructing fibrinous exudate within the RMS and BI.
The slim bronchoscope was withdrawn and a regular disposable bronchoscope was advanced.
Biopsy: Endobronchial biopsy was performed at the RMS bronchus fibrinous exudate/debris.
Portions of the lesion were successfully removed and sent for tissue culture and pathology.

Debridement Modalities:
With the first bronchoscope, fibrinous exudate was stretched away from the RMS wall.
With the second bronchoscope, {debride_tool} ({debride_settings}) was used to cut/debride the debris.
Large portions of debris were excised. Airway patency improved from 60% to 70%.

{hemostasis_text}

Conclusion Final airway exam performed showed no active bleeding. Residual secretions were suctioned to clear.
The patient tolerated the procedure well with no immediate complications and was returned to the ICU in stable condition.

SPECIMENS
RML bronchus BAL - cell count, cultures 
RMS bronchus exudate/debris - tissue culture, pathology 

IMPRESSION/PLAN
Successful dilation of RML bronchus achieved patency; copious secretions behind blockage were suctioned clear.
RML BAL performed.
{stent_type} stent ({stent_size_rml}) successfully placed within RML bronchus, achieving full patency.
Attempted stenting of lingula bronchus resulted in stent malposition; stent was removed.
Balloon dilation of lingula bronchus performed as additional stents were not available.
Debridement of bulky partially obstructing fibrinous exudate/debris in the RMS bronchus completed.
Plan for repeat bronchoscopy with airway evaluation and likely lingula stent placement early next week (likely Tues) when desired stents arrive.
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Bronchoscopy for {age}yo {gender_short}. Indication: {indication_summary}. RML obstructed -> dilated, BAL ({bal_instilled}cc), placed {stent_size_rml} {stent_type}. Lingula: tried {stent_size_lingula} stent but migrated/failed -> removed -> balloon dilation only. RMS debridement using {debride_tool_short}. {bleed_summary}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} referred by {doctor}. Patient has bilateral transplant complications. We did a BAL, RML stenting with a {stent_size_rml} {stent_type}, and attempted Lingula stenting which failed and required removal. We used the {debride_tool_short} for RMS debridement. Note the complex dual scope work.",
    
    # Style 3: Sloppy / Quick Handoff
    "{doctor} ref. {age} {gender_short} post-transplant. RML closed off. Opened it, drained pus, placed {stent_size_rml} stent. Tried to stent lingula ({stent_size_lingula}) but it slipped, had to pull it out. Debrided RMS with {debride_tool_short}. {bleed_summary}.",
    
    # Style 4: Billing Focus
    "Documentation for codes 31636, 31637, 31635 (FB removal), 31641. Patient {age} {gender_short}. Complex airway w/ dehiscence. RML stent ({stent_size_rml}) successful. Lingula stent failed/removed. RMS debridement via {debride_tool_short}. 22 modifier for dual scopes.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nIndication: {indication_summary}\nRML Procedure: Dilation, BAL, {stent_size_rml} stent.\nLingula Procedure: Attempted {stent_size_lingula} stent (failed/removed), balloon dilation.\nDebridement: RMS using {debride_tool_short}.\nComplications: {bleed_summary}"
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
        indication = random.choice(data_pool["indication_desc"])
        
        # Procedure Variables
        bal_in = int(random.choice(data_pool["bal_instilled"]))
        bal_out = bal_in - random.randint(5, 15) # Ensure return is less than instilled
        
        stent_type = random.choice(data_pool["stent_type"])
        stent_rml = random.choice(data_pool["stent_size_rml"])
        stent_ling = random.choice(data_pool["stent_size_lingula"])
        
        balloon_type = random.choice(data_pool["balloon_type"])
        balloon_rml = random.choice(data_pool["balloon_size_rml"])
        balloon_ling = random.choice(data_pool["balloon_size_lingula"])
        
        debride_tup = random.choice(data_pool["debridement_tool_tuple"])
        bleed_tup = random.choice(data_pool["bleeding_event_tuple"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication_summary="transplant complications/stenosis",
            bal_instilled=bal_in,
            stent_size_rml=stent_rml,
            stent_type=stent_type,
            stent_size_lingula=stent_ling,
            debride_tool_short=debride_tup[0].split()[0], # e.g., "Erbe" or "APC"
            bleed_summary=bleed_tup[1]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            doctor=doctor,
            patient_name_redacted="[REDACTED]",
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            bal_instilled=bal_in,
            bal_return=bal_out,
            stent_type=stent_type,
            stent_size_rml=stent_rml,
            balloon_type=balloon_type,
            balloon_size_rml=balloon_rml,
            stent_size_lingula=stent_ling,
            balloon_size_lingula=balloon_ling,
            debride_tool=debride_tup[0],
            debride_settings=debride_tup[1],
            hemostasis_text=bleed_tup[0]
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