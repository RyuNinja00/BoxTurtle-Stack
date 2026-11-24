#!/usr/bin/env python3
"""Reassemble and verify the STEP delivery from a checkout or source ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile

CAD_ROOT = Path(__file__).resolve().parents[1] / "cad"


def check(path, record):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if path.stat().st_size != record["bytes"] or digest != record["sha256"]:
        raise ValueError(f"Size or SHA-256 mismatch for {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path.cwd(), help="Directory for the files")
    args = parser.parse_args()
    meta = json.loads((CAD_ROOT / "manifest.json").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for record in (meta["archive"], meta["step"]):
        candidate = args.output / record["name"]
        if candidate.exists():
            check(candidate, record)
    with tempfile.TemporaryDirectory(dir=args.output) as staging:
        staging = Path(staging)
        archive = staging / meta["archive"]["name"]
        with archive.open("wb") as combined:
            for record in meta["parts"]:
                part = CAD_ROOT / "parts" / record["name"]
                check(part, record)
                with part.open("rb") as stream:
                    shutil.copyfileobj(stream, combined)
        check(archive, meta["archive"])
        member = meta["step"]["name"]
        model = staging / member
        with ZipFile(archive) as package:
            if package.namelist() != [member]:
                raise ValueError("Unexpected members in STEP archive")
            with package.open(member) as source, model.open("wb") as target:
                shutil.copyfileobj(source, target)
        check(model, meta["step"])
        for path in (archive, model):
            target = args.output / path.name
            if not target.exists():
                path.rename(target)
        print(f"Verified STEP: {args.output / member}")


if __name__ == "__main__":
    main()
