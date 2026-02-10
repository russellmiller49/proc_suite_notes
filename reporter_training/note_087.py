import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_087"
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
    "age": ["34", "45", "52", "57", "58", "61", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones"],
    "attending": ["Dr. P. Pulmonologist", "Dr. L. Airway", "Dr. S. Bronch"],
    "assistant": ["Dr. Fellow", "Dr. Resident", "PA Smith"],
    "date": ["January 12, 2025", "February 28, 2025", "March 15, 2025", "April 10, 2025"],
    
    # Clinical Variables
    "diagnosis_context": [
        "transplant recipient", 
        "granulomatosis with polyangiitis patient", 
        "patient with history of prolonged intubation", 
        "lung cancer survivor"
    ],
    "stenosis_location": [
        "RML", "RUL", "Bronchus Intermedius", "LUL", "LLL", "Left Mainstem", "Right Mainstem"
    ],
    "stenosis_cause": ["stenosis", "stricture", "scarring", "webbing"],
    
    # Quantifiable Metrics
    "initial_patency": ["75%", "60%", "50%", "40%", "80%"],
    "initial_diameter": ["5-6 mm", "4 mm", "3-4 mm", "6 mm"],
    "target_diameter": ["8 mm", "9 mm", "10 mm", "12 mm"],
    "final_patency": ["100%", "95%", "90%"],
    
    # Procedure Specifics (Modifier 22 Justification)
    "balloon_name": ["6/7/8 Elation", "8/9/10 CRE", "10/11/12 CRE", "12/13.5/15 Hercules"],
    "balloon_inflations_total": ["2", "3", "4"], # Total inflations in procedure detail
    "mod22_balloon_count": ["4", "5", "6"], # Complexity count (inflations across session)
    "dilation_time": ["60 seconds", "45 seconds", "90 seconds"],
    
    "cryo_probe_size": ["1.7mm", "1.9mm", "2.4mm"],
    "cryo_cycles": ["30-second", "45-second", "60-second"],
    "cryo_app_count": ["6", "5", "8", "4"], # Complexity count
    
    "secretions_desc": [
        "Moderate clear secretions bilaterally, white thicker mucus emanating from {loc}",
        "Copious mucoid secretions bilaterally, thick plug at {loc}",
        "Scant clear secretions, purulent discharge at {loc}",
        "Thick white secretions throughout, plugging at {loc}"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION
{patient_name} is a {age}-year-old {gender_long} who presents with bronchial {stenosis_cause}. This patient is a {diagnosis_context} with {stenosis_cause} that required increased complexity, specifically {mod22_balloon_count} balloon dilations and {cryo_app_count} applications of cryotherapy. This resulted in >50% increased work due to time, technical difficulty, and physical/mental effort required.

CONSENT
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail. The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing
31624 Dx bronchoscope/lavage (BAL)
31630 Balloon dilation
31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)
22 Substantially greater work than normal (increased intensity, time, technical difficulty)

ATTENDING
{attending}

ASSISTANT
{assistant}

SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; {cryo_probe_size} Cryoprobe; {balloon_name} balloon.

ESTIMATED BLOOD LOSS
Minimum

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position: Supine

Initial Airway Inspection: The laryngeal mask airway is in good position. The vocal cords appear normal. The subglottic space is normal. The trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level.

Airway Exam:
Stenosis: Notable for {stenosis_cause} of the {stenosis_location} ({initial_patency} patent). Diameter was {initial_diameter}.

Secretions: {secretions_filled}

Therapeutic Aspiration & Lavage: Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, and {stenosis_location} Carina from mucus and mucus plug.

Endobronchial Stenosis Treatment: Endobronchial obstruction at {stenosis_location} was treated with the following modalities:

Cryotherapy: Using a {cryo_probe_size} probe, ablation was performed with {cryo_cycles} freeze-thaw cycles for a total of {cryo_app_count} applications.

Balloon Dilation: Performed at {stenosis_location} using a {balloon_name} balloon to dilate to {target_diameter}. Total {balloon_inflations_total} inflations with dilation time of {dilation_time} each were performed during this specific sequence.

Results: Prior to treatment, affected airway was noted to be {initial_patency} patent. After treatment, the airway was {final_patency} patent.

Conclusion: The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was successfully extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
BAL - {stenosis_location}

IMPRESSION / PLAN
{age}-year-old {gender_long} treated for bronchial {stenosis_cause}.
Successful restoration of {stenosis_location} patency from {initial_patency} to {final_patency} using balloon dilation and cryotherapy.
Follow-up results.
Follow-up CXR.
Repeat bronchoscopy on [Date].
"""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate op note. {age}yo {gender_short}, {diagnosis_context}. Stenosis at {stenosis_location} ({initial_patency}). Did Balloon ({balloon_name}) and Cryo x{cryo_app_count}. Complex case (mod 22). Outcome {final_patency}.",
    
    # Style 2: Dictation style
    "Please dictate an operative report for Dr. {attending}. Patient is a {age} year old {gender_long} {diagnosis_context} with {stenosis_location} stenosis. We performed therapeutic bronchoscopy with balloon dilation and cryotherapy. Note the increased complexity requiring {mod22_balloon_count} dilations and {cryo_app_count} cryo apps.",
    
    # Style 3: Billing/Coding Focus
    "Procedure codes: 31645, 31630, 31641-22. Patient: {age} {gender_short}. Indication: {stenosis_location} stenosis ({initial_patency} -> {final_patency}). Instruments: {balloon_name}, {cryo_probe_size} cryo.",
    
    # Style 4: Sloppy / Rapid input
    "{age}M {stenosis_location} stenosis. fixed with balloon and cryo. used {balloon_name} and {cryo_probe_size} probe. lots of secretions. complex case required extra work/time. patency improved {initial_patency} to {final_patency}.",
    
    # Style 5: Structured
    "PATIENT: {age}/{gender_short}\nDIAGNOSIS: Bronchial {stenosis_cause} ({stenosis_location})\nPROCEDURE: Bronchoscopy, Balloon Dilation, Cryotherapy\nDETAILS: {mod22_balloon_count} dilations, {cryo_app_count} cryo applications. Mod 22 applied.\nRESULT: {final_patency} patent."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for i in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        date = random.choice(data_pool["date"])
        
        diagnosis_context = random.choice(data_pool["diagnosis_context"])
        stenosis_location = random.choice(data_pool["stenosis_location"])
        stenosis_cause = random.choice(data_pool["stenosis_cause"])
        
        initial_patency = random.choice(data_pool["initial_patency"])
        initial_diameter = random.choice(data_pool["initial_diameter"])
        target_diameter = random.choice(data_pool["target_diameter"])
        final_patency = random.choice(data_pool["final_patency"])
        
        balloon_name = random.choice(data_pool["balloon_name"])
        balloon_inflations_total = random.choice(data_pool["balloon_inflations_total"])
        mod22_balloon_count = random.choice(data_pool["mod22_balloon_count"])
        dilation_time = random.choice(data_pool["dilation_time"])
        
        cryo_probe_size = random.choice(data_pool["cryo_probe_size"])
        cryo_cycles = random.choice(data_pool["cryo_cycles"])
        cryo_app_count = random.choice(data_pool["cryo_app_count"])
        
        # Handle logic for secretions description (inserting location)
        secretions_raw = random.choice(data_pool["secretions_desc"])
        secretions_filled = secretions_raw.replace("{loc}", stenosis_location)
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diagnosis_context=diagnosis_context,
            stenosis_location=stenosis_location,
            stenosis_cause=stenosis_cause,
            initial_patency=initial_patency,
            final_patency=final_patency,
            balloon_name=balloon_name,
            cryo_app_count=cryo_app_count,
            mod22_balloon_count=mod22_balloon_count,
            attending=attending,
            cryo_probe_size=cryo_probe_size
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            ref_physician=ref_physician,
            patient_name="[REDACTED]",
            age=age,
            gender_long=gender_tup[0],
            diagnosis_context=diagnosis_context,
            stenosis_cause=stenosis_cause,
            mod22_balloon_count=mod22_balloon_count,
            cryo_app_count=cryo_app_count,
            attending=attending,
            assistant=assistant,
            cryo_probe_size=cryo_probe_size,
            balloon_name=balloon_name,
            stenosis_location=stenosis_location,
            initial_patency=initial_patency,
            initial_diameter=initial_diameter,
            secretions_filled=secretions_filled,
            cryo_cycles=cryo_cycles,
            target_diameter=target_diameter,
            balloon_inflations_total=balloon_inflations_total,
            dilation_time=dilation_time,
            final_patency=final_patency
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