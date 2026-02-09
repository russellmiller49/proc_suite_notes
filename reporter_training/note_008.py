import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_008"
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
    "age": ["24", "29", "33", "41", "48", "55", "62", "70"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "doctor": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Al-Fayed", "Dr. Ivanov", "Dr. Bowers"],
    "referred_by": ["Primary Care", "Dr. Jones (ENT)", "Oncology", "Emergency Dept", "Dr. Miller"],
    
    "indication": [
        "subglottic stenosis and tracheal stenosis",
        "complex post-intubation tracheal stenosis",
        "recurrent malignant airway obstruction",
        "tracheomalacia and subglottic narrowing",
        "granulation tissue formation with tracheal stenosis"
    ],
    
    "larynx_finding": [
        "Raised nodules noted on the medial aspects of the arytenoids, likely consistent with irritation",
        "Mild erythema of the posterior commissure",
        "Normal appearance of the arytenoids and vocal cords",
        "Slight edema of the false vocal cords"
    ],
    
    "subglottic_finding": [
        "Granulation tissue noted along the left and right portions; soft but causing approximately 15% obstruction",
        "Circumferential scarring causing 30% luminal narrowing",
        "Firm granulation tissue along the anterior wall causing 20% obstruction",
        "Mild narrowing with soft tissue proliferation causing 10% obstruction"
    ],
    
    "trachea_condition": [
        "Evidence of skin graft from the 9 o'clock to 3 o'clock position; hair follicles and longer hair stubbles seen within the airway",
        "Complex scarring with web-like formation in the mid-trachea",
        "Tortuous airway with significant malacia in the distal trachea",
        "Focal fibrotic stenosis in the proximal trachea with preserved distal patency"
    ],
    
    "stent_model": [
        "Bona stent", "AERO stent", "Ultraflex stent", "Dumon silicone stent"
    ],
    
    "stent_dims": [
        "14 x 60 mm", "16 x 40 mm", "12 x 50 mm", "14 x 40 mm", "18 x 60 mm"
    ],
    
    "balloon_sequence": [
        "12 mm, 13.5 mm, and 15 mm",
        "10 mm, 12 mm, and 13.5 mm",
        "14 mm, 15 mm, and 16 mm",
        "8 mm, 10 mm, and 12 mm"
    ],
    
    # Logic pair: (Issue found, Correction performed)
    "revision_scenario": [
        ("approximately 0.5 cm more distal than desired", "retract the stent 0.5 cm proximally"),
        ("approximately 1 cm too proximal", "advance the stent 1 cm distally"),
        ("slightly rotated to the right", "rotate the stent to align with the airway axis"),
        ("inadequate apposition to the tracheal wall", "dilate further to seat the stent")
    ],
    
    "suture_type": ["2.0 polyene", "0-Silk", "2.0 Prolene", "3.0 Ethibond"],
    
    "hygiene_meds": [
        "Albuterol 2.5 mg nebs and 3% hypertonic saline",
        "Duoneb and 7% hypertonic saline",
        "Saline nebulizers and Acetycysteine",
        "Levalbuterol and normal saline"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referred_by}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.
Modifier 22 Declaration: Patient with tracheal reconstruction and subglottic stenosis required an emergent procedure for stent revision due to narrowing of the upper airway.
This involved increased technical skill for placing a suture through the stent and trachea due to the tracheal flap.
This required increased effort and skill (100% increased effort) due to intensity and mental effort.

CONSENT Obtained before the procedure.
The nature, indications, purpose, benefits, risks, potential complications, and alternatives to the procedure were discussed with the patient or surrogate decision-maker in detail.
The patient or surrogate decision-maker agreed to proceed with the procedure.
The patient or surrogate decision-maker read and signed the provided consent form or provided consent over the phone.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE
31645 Therapeutic aspiration initial episode
31630 Balloon dilation
31631 Dilate and tracheal stent placement
31638 Revision of tracheal/bronchial stent
31612 Tracheal puncture

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope.

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Airway Inspection The Flexible Therapeutic Bronchoscope was advanced for airway examination.
Endobronchial topical lidocaine was applied to the vocal cords, main carina, right carina 1, and left carina 2. A total of 4 mL of 2% lidocaine was instilled onto the vocal cords.

Larynx: {larynx_finding}.
Vocal Cords: Widely abducted and moving bilaterally.

Subglottis: {subglottic_finding}.

Trachea: The proximal and mid-trachea are abnormal.
{trachea_condition}.
Numerous sutures visualized with areas of pedunculated tissue around suture sites. No evidence of dehiscence or necrosis seen.
Main Carina: Sharp.

Right Lung Proximal Airways: Mild webbing of tissue at the RUL take-off.
Left Lung Proximal Airways: Normal anatomic branching to first subsegmental level.

Mucosa: Trachea as described above; more distal airways are normal.

Secretions: Moderate, thin, and clear.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the trachea, right mainstem bronchus, right upper lobe, bronchus intermedius, right middle lobe, right lower lobe, left mainstem bronchus, left upper lobe, and left lower lobe from mucus.
All secretions were suctioned to clear.

Airway Stent Placement A jag wire was introduced into the iGel and advanced to the LLL.
The bronchoscope was removed and the jag wire left in place.
A {stent_model} ({stent_dims}) was deployed under direct visualization into the trachea.

Stent Revision Following deployment, the stent was noted to be {rev_issue}.
Stent revision was performed using forceps to {rev_fix}.
Following revision, the stent was confirmed to be in the appropriate position.

Balloon Dilation Balloon dilation was performed to expand the stent distally, mid-portion, and proximally.
Balloons sized {balloon_seq} were used sequentially.

Tracheal Fixation (Tracheal Puncture) A 14-gauge angiocath was used to puncture the anterior tracheal wall more superiorly.
With the stent in appropriate position, the bronchoscope was used to guide a {suture_type} suture through the anterior trachea via the angiocath.
Using forceps, the suture was grasped and pulled through the trachea and into the stent.
A second 14-gauge angiocath was used to puncture the anterior tracheal wall laterally.
A snare was introduced through this angiocatheter into the trachea.
The snare was used to retrieve the first suture through the angiocatheter.
Both sutures were pulled through the skin and then tied together at the skin.
The stent was secured across 3 struts in the trachea.

Conclusion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the airway device was removed.

SPECIMENS
None

IMPRESSION / PLAN The patient is a {age}-year-old {gender_long} who presents for bronchoscopy for airway evaluation of tracheal stenosis.
Follow-up CXR.

Restart stent hygiene with {hygiene_meds}.
Add 1% lidocaine neb to assist with irritation of stent in subglottis.

If able to tolerate the above, consider ambulation.
Note: The proximal end of the stent is <0.5 cm below the true vocal cords.
Intubation Precautions: Should the patient need to be intubated, use a 6.0 ETT and keep the cuff just below the cords to avoid dragging the stent distally with the ETT.
The stent is covered and could occlude the airway.

If there is concern for additional migration, will consider the addition of a second suture."""

prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Pt {age} {gender_short}, refer {referred_by}. {indication}. Placed {stent_model} {stent_dims}. Req revision ({rev_issue}). Dilated {balloon_seq}. Fixated w/ {suture_type}. Plan: {hygiene_meds}.",
    
    # Style 2: Dictation / Narrative
    "Please generate an IP op report for a {age} year old {gender_long} sent by {referred_by}. Indication: {indication}. We performed therapeutic aspiration and balloon dilation using {balloon_seq}. We deployed a {stent_model} size {stent_dims}. Note that we had to revise the stent because it was {rev_issue}; we used forceps to {rev_fix}. We then performed tracheal fixation using {suture_type} via angiocath. Hygiene: {hygiene_meds}.",
    
    # Style 3: Sloppy / Quick Inputs
    "{age}yo {gender_short} {indication}. {stent_model} {stent_dims} placed. initial pos {rev_issue}, fixed by {rev_fix}. balloons {balloon_seq}. sutured to trachea. {hygiene_meds} for hygiene.",
    
    # Style 4: Billing / CPT Focus
    "Codes 31645, 31630, 31631, 31638, 31612. Dx J98.09. {age}/{gender_short}. Complex airway w/ {trachea_condition}. {stent_model} ({stent_dims}) placed and sutured. Modifier 22 for complex revision ({rev_fix}) and suture fixation.",
    
    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nREFERRAL: {referred_by}\nINDICATION: {indication}\nSTENT: {stent_model} {stent_dims}\nISSUE: {rev_issue}\nACTION: {rev_fix}\nDILATION: {balloon_seq}\nFIXATION: {suture_type}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        referred_by = random.choice(data_pool["referred_by"])
        indication = random.choice(data_pool["indication"])
        larynx_finding = random.choice(data_pool["larynx_finding"])
        subglottic_finding = random.choice(data_pool["subglottic_finding"])
        trachea_condition = random.choice(data_pool["trachea_condition"])
        stent_model = random.choice(data_pool["stent_model"])
        stent_dims = random.choice(data_pool["stent_dims"])
        balloon_seq = random.choice(data_pool["balloon_sequence"])
        
        # Revision Logic Pair
        rev_pair = random.choice(data_pool["revision_scenario"])
        rev_issue = rev_pair[0]
        rev_fix = rev_pair[1]
        
        suture_type = random.choice(data_pool["suture_type"])
        hygiene_meds = random.choice(data_pool["hygiene_meds"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            referred_by=referred_by,
            indication=indication,
            stent_model=stent_model,
            stent_dims=stent_dims,
            rev_issue=rev_issue,
            rev_fix=rev_fix,
            balloon_seq=balloon_seq,
            suture_type=suture_type,
            hygiene_meds=hygiene_meds,
            trachea_condition=trachea_condition
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age,
            gender_long=gender_tup[0],
            referred_by=referred_by,
            indication=indication,
            larynx_finding=larynx_finding,
            subglottic_finding=subglottic_finding,
            trachea_condition=trachea_condition,
            stent_model=stent_model,
            stent_dims=stent_dims,
            rev_issue=rev_issue,
            rev_fix=rev_fix,
            balloon_seq=balloon_seq,
            suture_type=suture_type,
            hygiene_meds=hygiene_meds
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