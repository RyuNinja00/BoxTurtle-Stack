#!/usr/bin/env python3
"""Recreate the model stages in a clean workspace using pinned upstream CAD."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

TOOLS = Path(__file__).resolve().parent
STAGES = TOOLS / "rebuild-stages"
UPSTREAM = {
    "bte": ("https://github.com/ArmoredTurtle/BoxTurtle-Enclosure.git", "c2940c63be7a276a4c5c59f111fb72c9bd807601"),
    "lane-buffer": ("https://github.com/N3MI-DG/Lane-Buffer.git", "0a6b0cdb551db7cce285cbef08f7ae515c3962ac"),
}


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=Path("rebuild-work"))
    args = parser.parse_args()
    work = args.work_dir.resolve()
    if work.exists():
        parser.error("work directory must be new")
    shutil.copytree(STAGES, work)
    for directory, (url, sha) in UPSTREAM.items():
        repo = work / directory
        repo.mkdir()
        run("git", "init", "-q", cwd=repo)
        run("git", "fetch", "--depth=1", url, sha, cwd=repo)
        run("git", "checkout", "--detach", sha, cwd=repo)
    with ZipFile(work / "bte/CAD.zip") as archive:
        member = "CAD/BTE V1.0.step"
        target = work / "bte" / member
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(member) as source, target.open("wb") as out:
            shutil.copyfileobj(source, out)
    for subdir in ("revised", "audited", "dry-storage"):
        (work / subdir).mkdir()
    run(sys.executable, "build_alternate.py", cwd=work)
    (work / "stack_alternate.step").rename(work / "BoxTurtle-V1-Dual-Tier.step")
    run(sys.executable, "add_lane_buffers.py", cwd=work)
    run(sys.executable, "credit_lane.py", "revised/BoxTurtle-V1-Dual-Tier.step", cwd=work)
    run(sys.executable, "audit_revision.py", cwd=work)
    run(sys.executable, "set_service_pose.py", "audited/BoxTurtle-V1-Dual-Tier.step", cwd=work)
    run(sys.executable, "finalize_audit.py", cwd=work)
    run(sys.executable, "fix_dry_storage.py", cwd=work)
    run(sys.executable, "finalize_dry_storage.py", cwd=work)
    model = work / "dry-storage/BoxTurtle-V1-Dual-Tier.step"
    run(sys.executable, str(TOOLS / "verify_dry_storage.py"), str(model), cwd=work)
    print(model)


if __name__ == "__main__":
    main()
