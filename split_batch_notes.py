#!/usr/bin/env python3
"""Split synthetic batch note files into one file per note.

Example:
  python split_batch_notes.py \
    --input-dir "/home/rjm/projects/proc_suite_notes/new_synthetic_notes_3_5_26"
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


START_RE = re.compile(r"^<<<NOTE\s+(\d+)>>>$")
END_RE = re.compile(r"^<<<END NOTE\s+(\d+)>>>$")


@dataclass
class ParsedNote:
    note_id: int
    text: str


def parse_batch_text(batch_text: str) -> list[ParsedNote]:
    notes: list[ParsedNote] = []
    lines = batch_text.splitlines()

    active_note_id: int | None = None
    buffer: list[str] = []

    for line in lines:
        start_match = START_RE.match(line.strip())
        if start_match:
            # If a note was open and no end marker appeared, close it anyway.
            if active_note_id is not None:
                notes.append(ParsedNote(note_id=active_note_id, text="\n".join(buffer).strip() + "\n"))
            active_note_id = int(start_match.group(1))
            buffer = []
            continue

        end_match = END_RE.match(line.strip())
        if end_match and active_note_id is not None:
            notes.append(ParsedNote(note_id=active_note_id, text="\n".join(buffer).strip() + "\n"))
            active_note_id = None
            buffer = []
            continue

        if active_note_id is not None:
            buffer.append(line)

    if active_note_id is not None:
        notes.append(ParsedNote(note_id=active_note_id, text="\n".join(buffer).strip() + "\n"))

    return notes


def write_notes_for_batch(
    batch_file: Path,
    destination_root: Path,
    *,
    overwrite: bool,
    dry_run: bool,
) -> tuple[int, int]:
    batch_name = batch_file.stem
    out_dir = destination_root / batch_name
    raw_text = batch_file.read_text(encoding="utf-8")
    notes = parse_batch_text(raw_text)

    if not notes:
        print(f"[WARN] {batch_file.name}: no notes found")
        return 0, 0

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    seen: set[int] = set()

    for note in notes:
        suffix = ""
        if note.note_id in seen:
            # Keep duplicates deterministic if they exist.
            count = 2
            while (out_dir / f"note_{note.note_id:03d}_{count}.txt").exists():
                count += 1
            suffix = f"_{count}"
        seen.add(note.note_id)

        file_name = f"note_{note.note_id:03d}{suffix}.txt"
        out_path = out_dir / file_name

        if out_path.exists() and not overwrite:
            skipped += 1
            print(f"[SKIP] {out_path} (exists; use --overwrite)")
            continue

        if dry_run:
            print(f"[DRY-RUN] {batch_file.name} -> {out_path}")
            written += 1
            continue

        out_path.write_text(note.text, encoding="utf-8")
        written += 1

    print(f"[OK] {batch_file.name}: parsed={len(notes)} written={written} skipped={skipped} -> {out_dir}")
    return written, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split each batch_*.txt file into a subfolder with one .txt per note."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing batch_*.txt files",
    )
    parser.add_argument(
        "--glob",
        default="batch_*.txt",
        help="Glob pattern for batch files (default: batch_*.txt)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Where subfolders are created (default: input-dir)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing per-note files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing files",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"[ERROR] Input directory not found: {input_dir}")
        return 1

    output_root = args.output_root or input_dir
    batch_files = sorted(input_dir.glob(args.glob))
    if not batch_files:
        print(f"[ERROR] No files matched '{args.glob}' in {input_dir}")
        return 1

    total_written = 0
    total_skipped = 0
    for batch_file in batch_files:
        written, skipped = write_notes_for_batch(
            batch_file,
            output_root,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        total_written += written
        total_skipped += skipped

    print(
        f"[DONE] batches={len(batch_files)} written={total_written} skipped={total_skipped} "
        f"output_root={output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
