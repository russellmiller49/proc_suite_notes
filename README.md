# proc_suite_notes

This repo is intended to store **large note corpora, training fixtures, and evaluation datasets**
that are useful for developing Procedure Suite, without bloating the main `proc_suite` repo.

## How `proc_suite` finds this repo

Set an environment variable before running scripts/Make targets:

```bash
export PROCSUITE_NOTES_ROOT="/home/rjm/projects/proc_suite_notes"
```

If `PROCSUITE_NOTES_ROOT` is not set, many scripts will also try a sibling repo at
`../proc_suite_notes` automatically.

## Recommended layout

Mirror the main repo’s data layout so paths stay consistent:

```
proc_suite_notes/
  data/
    knowledge/
      golden_extractions/
      golden_extractions_scrubbed/
      golden_extractions_final/
      golden_registry_v3/
      patient_note_texts/
    granular annotations/
      notes_text/
      phase0_excels/
      Python_update_scripts/
    registry_granular/
      notes/
      csvs/
  Training_data/
```

## PHI / safety note

Use only de-identified / scrubbed data where required, and treat this repo as sensitive.
Keep it private and access-controlled if it can contain real patient text.

