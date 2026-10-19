#!/usr/bin/env python3
"""
Nyyo Automation — Custom script demo
Does ONE job well: bulk-rename files by a pattern and write a PDF-style text report.

Example:
  invoices/INV_2025_1.pdf  →  invoices/2025-01-15_acme_inv-001.pdf
  (using a mapping CSV)

Paid jobs use the same pattern: you describe the rule, I deliver a commented script + README + a dry-run mode.
"""
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


def load_map(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plan_renames(folder: Path, mapping: list[dict]) -> list[tuple[Path, Path]]:
    plans = []
    for row in mapping:
        src = folder / row["current_name"]
        dst = folder / row["new_name"]
        plans.append((src, dst))
    return plans


def apply(plans: list[tuple[Path, Path]], dry_run: bool) -> list[str]:
    log = []
    for src, dst in plans:
        if not src.exists():
            log.append(f"SKIP missing: {src.name}")
            continue
        if dst.exists():
            log.append(f"SKIP exists:  {dst.name}")
            continue
        if dry_run:
            log.append(f"DRY  {src.name}  →  {dst.name}")
        else:
            src.rename(dst)
            log.append(f"OK   {src.name}  →  {dst.name}")
    return log


def write_report(log: list[str], out: Path) -> None:
    lines = [
        "Nyyo Automation — bulk rename report",
        f"entries: {len(log)}",
        "-" * 40,
        *log,
        "-" * 40,
        "dry-run first, then re-run without --dry-run to apply.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def seed_demo(folder: Path, map_path: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    samples = [
        ("INV_2025_1.pdf", "dummy invoice 1"),
        ("INV_2025_2.pdf", "dummy invoice 2"),
        ("scan_photo.JPG", "dummy scan"),
        ("notes.txt", "keep me"),
    ]
    for name, body in samples:
        (folder / name).write_text(body, encoding="utf-8")
    map_path.write_text(
        "current_name,new_name\n"
        "INV_2025_1.pdf,2025-01-15_acme_inv-001.pdf\n"
        "INV_2025_2.pdf,2025-01-22_beta_inv-002.pdf\n"
        "scan_photo.JPG,2025-01-22_receipt_scan.jpg\n",
        encoding="utf-8",
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Bulk rename from a CSV mapping + report")
    p.add_argument("--folder", default="demo_files", help="Folder with files to rename")
    p.add_argument("--map", default="rename_map.csv", help="CSV with current_name,new_name")
    p.add_argument("--report", default="rename_report.txt", help="Report path")
    p.add_argument("--seed", action="store_true", help="Create demo files + mapping")
    p.add_argument("--dry-run", action="store_true", help="Show plan without renaming")
    args = p.parse_args()

    folder = Path(args.folder)
    map_path = Path(args.map)
    if args.seed:
        seed_demo(folder, map_path)
        print(f"Seeded {folder}/ and {map_path}")
        return

    mapping = load_map(map_path)
    plans = plan_renames(folder, mapping)
    log = apply(plans, dry_run=args.dry_run)
    write_report(log, Path(args.report))
    for line in log:
        print(line)
    print(f"Report → {Path(args.report).resolve()}")


if __name__ == "__main__":
    main()
