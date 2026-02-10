import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_069"
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
    "age": ["54", "59", "61", "64", "67", "72", "75", "81"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Weiss", "Dr. Patel"],
    "anesthesiologist": ["Dr. O'Malley", "Dr. Lee", "Dr. Corazon", "Dr. Metric"],
    
    # Diagnosis Variations
    "indication_desc": [
        "bronchial stenosis related to endobronchial tumor",
        "malignant airway obstruction and shortness of breath",
        "extrinsic compression and endobronchial tumor invasion",
        "respiratory failure secondary to central airway obstruction"
    ],

    # Anatomical Logic: Target Lobe for Stenting and associated segments
    "target_lobe_data": [
        {
            "lobe": "Right Middle Lobe", 
            "abbr": "RML", 
            "segments": "RB4 and RB5", 
            "seg_1": "RB4 (lateral)", 
            "seg_2": "RB5 (medial)",
            "other_lobe": "Right Lower Lobe"
        },
        {
            "lobe": "Right Upper Lobe", 
            "abbr": "RUL", 
            "segments": "RB1, RB2, and RB3", 
            "seg_1": "RB1 (apical)", 
            "seg_2": "RB2 (posterior)",
            "other_lobe": "Right Lower Lobe"
        },
        {
            "lobe": "Left Upper Lobe", 
            "abbr": "LUL", 
            "segments": "LB3, LB4, and LB5", 
            "seg_1": "LB3 (apical-posterior)", 
            "seg_2": "LB4 (lingular)",
            "other_lobe": "Left Lower Lobe"
        }
    ],

    # Stent Devices
    "stent_device": [
        "AEROMini 6x15mm stent",
        "AEROMini 6x10mm stent",
        "Boston Scientific Ultraflex 10x40mm cover stent",
        "Merit Endotek 8x20mm stent"
    ],

    # Patency percentages (Pre -> Post)
    "patency_improvement": [
        ("1%", "80%"),
        ("5%", "90%"),
        ("0%", "75%"),
        ("10%", "85%")
    ],
    
    # Tumor descriptions
    "tumor_desc": [
        "Extensive partially obstructing vascular endobronchial tumor",
        "Fleshy, polypoid endobronchial mass",
        "Friable, necrotic tumor with white debris",
        "Infiltrating submucosal tumor with exophytic component"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]

INDICATION FOR OPERATION: The patient is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT: Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient. Informed consent was obtained.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing
31624 Dx bronchoscope/lavage (BAL)
31625 Endobronchial Biopsy(s)
31630 Balloon dilation - {other_lobe} bronchus (no stent placed)
31636 Dilate and bronchial stent initial bronchus - {lobe_abbr} bronchus (dilation and stent placement)
31640 Bronchoscopy with excision
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)

ANESTHESIA: General Anesthesia

MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION: Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS: Minimal

COMPLICATIONS: None

PROCEDURE IN DETAIL:
A timeout was performed (confirming the patient's name, procedure type, and procedure location). Sedation was initiated and an LMA was placed.

Initial Airway Inspection: The Flexible Therapeutic Bronchoscope was advanced for airway examination. Endobronchial topical lidocaine was applied to the vocal cords, main carina, right carina 1, and left carina 2.

Larynx/Vocal Cords: No lesions; normal movement without mass.

Trachea/Bronchi: {tumor_desc} and overlying white necrotic debris were noted involving the mid-trachea, distal trachea, main carina, and lobar bronchi.

Severity: Obstruction was most severe at the distal trachea and {lobe_abbr} orifice.
{lobe_abbr}: Highly stenotic and completely obstructed by tumor, debris, and mucus; unable to traverse initially.
{other_lobe}: Moderate stenosis due to tumor and extrinsic compression.

Therapeutic Interventions

Therapeutic Aspiration: Secretions were moderate, thin, and clear. Successful therapeutic aspiration was performed to clear mucus and overlying necrotic debris from the trachea and mainstem bronchi.

Endobronchial Biopsy: Biopsies were performed at tumor sites in the trachea, main carina, and {lobe_abbr}. These were combined into a single sample labeled "trachea".

Tumor Excision: The obstructing tumor at the trachea, main carina, and {lobe_abbr} was excised with mechanical debridement using bland alligator forceps.

Tumor Ablation (APC): Tumor destruction was performed using a 1.5mm Pulmonary axial 'straight-fire' probe (forcedAPC, 0.5 LPM, Max Watts 30-40) in 1-5 second bursts. Extensive tumor ablation and hemostasis were achieved.

{lobe_name} Management:
After tumor excision and ablation, the {lobe_abbr} bronchus was traversed with a Hybrid bronchoscope and saline hydrodissection. Patency of {seg_1} was confirmed; {seg_2} appeared viable but filled with debris.

Balloon Dilation: A 6/7/8 mm Elation balloon was used to dilate the {lobe_abbr} stenosis to 7 mm (2 inflations, 60 and 30 seconds). The therapeutic scope could then traverse with moderate pressure.

Bronchoalveolar Lavage (BAL): Performed at the {lobe_abbr} ({segments}) with 60 cc instilled and 15 cc returned.

Stent Placement: An {stent_device} was placed in the {lobe_abbr} bronchus. It seated very well and maintained patency of both {segments} segments.

{other_lobe} Management:
Balloon Dilation: A 6/7/8 mm Elation balloon was used to dilate the {other_lobe} bronchus take-off to 8 mm (1 inflation, 60 seconds).

Results and Patency
Trachea: Improved from 80% patent to 95% patent.
Right-sided airways (excl. {lobe_abbr}): Improved from 60% patent to 90% patent.
{lobe_abbr} Bronchus: Improved from {pre_patent} patent to {post_patent} patent.
Left Mainstem: Improved from 80% patent to 95% patent.

Residual secretions, saline, and blood were suctioned to clear. The patient tolerated the procedure well. The LMA was removed in the operating room.

SPECIMENS
Endobronchial biopsy (combined samples): Pathology
{lobe_abbr} BAL: Cell count, micro/cultures, cytology

IMPRESSION/PLAN
The patient is a {age}-year-old {gender_long} who underwent bronchoscopy for endobronchial tumor excision/ablation, airway dilation, and {lobe_abbr} stent placement.

Intervention: Extensive endobronchial tumor excision and ablation in the trachea and {lobe_abbr}.
Stent: Placement of {stent_device} in {lobe_abbr} bronchus.

Post-Procedure Care:
Follow-up post-op CXR.
Await EBBx and BAL results.
Stent hydration/hygiene protocol: QID albuterol nebulizer, hypertonic saline (3%, 4mL) nebulizer, and flutter valve regimen; Mucinex 1200mg BID for mucolysis.
Engage case management to obtain devices/meds prior to discharge.

Follow-up: Repeat bronchoscopy with airway evaluation, stent check, and likely additional tumor excision/ablation in ~3-4 weeks. Consideration of rigid bronchoscopy with micro-debrider given extensive involvement.
"""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic
    "Pt {age} {gender_short}, {indication}. Procedure: APC, Balloon, Stent {lobe_abbr}. Device: {stent_device}. {lobe_abbr} patency {pre_patent} -> {post_patent}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long}. We performed a therapeutic bronchoscopy with tumor debulking and placed a {stent_device} in the {lobe_name}. The {other_lobe} was also dilated.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} tumor stenosis. rigid bronchsopy consideration. interventions: apc, balloon {other_lobe}, stent {lobe_abbr} ({stent_device}). bal sent.",
    
    # Style 4: Billing Focus
    "Codes: 31645, 31636 ({lobe_abbr} stent), 31640, 31641. Dx J98.09. Pt {age}/{gender_short}. Stent used: {stent_device}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedure: Tumor excision, APC, Stenting\nTarget: {lobe_name}\nStent: {stent_device}\nOutcome: {lobe_abbr} opened from {pre_patent} to {post_patent}"
]

# ==========================================
# 5. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        indication = random.choice(data_pool["indication_desc"])
        
        # Select Lobe/Anatomy logic to ensure consistency
        lobe_data = random.choice(data_pool["target_lobe_data"])
        
        stent_device = random.choice(data_pool["stent_device"])
        patency = random.choice(data_pool["patency_improvement"])
        tumor_desc = random.choice(data_pool["tumor_desc"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            lobe_abbr=lobe_data["abbr"],
            lobe_name=lobe_data["lobe"],
            other_lobe=lobe_data["other_lobe"],
            stent_device=stent_device,
            pre_patent=patency[0],
            post_patent=patency[1]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            tumor_desc=tumor_desc,
            lobe_name=lobe_data["lobe"],
            lobe_abbr=lobe_data["abbr"],
            segments=lobe_data["segments"],
            seg_1=lobe_data["seg_1"],
            seg_2=lobe_data["seg_2"],
            other_lobe=lobe_data["other_lobe"],
            stent_device=stent_device,
            pre_patent=patency[0],
            post_patent=patency[1]
        )
        
        dataset.append({"prompt": prompt, "completion": completion})
    
    return dataset

# ==========================================
# 6. EXECUTION & SAVING
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