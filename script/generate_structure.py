#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

# ensure our parser helper is importable
sys.path.append(str(Path(__file__).resolve().parent.parent))
from get_repo_structure.get_repo_structure import create_structure

def copy_and_checkout(src_root: Path, dst_parent: Path, commit: str):
    """
    Copy entire src_root into dst_parent/<src_root.name>,
    then git-checkout <commit> inside it (warn if fails).
    """
    dst = dst_parent / src_root.name
    shutil.copytree(src_root, dst)
    try:
        subprocess.run(
            ["git", "-C", str(dst), "checkout", commit],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print(f"[!] warning: could not git checkout {commit} in {dst}", file=sys.stderr)
    return dst

def main():
    p = argparse.ArgumentParser(
        description="Generate per-benchmark structure JSONs from a JSONL bench_list"
    )
    p.add_argument("--bench_list", required=True,
                   help="path to a JSONL file, one bench obj per line")
    p.add_argument("--output_dir", required=True,
                   help="where to write <instance_id>.json")
    p.add_argument("--playground", required=True,
                   help="scratch area for copying repos")
    args = p.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(exist_ok=True)

    # load all bench entries
    benches = [json.loads(l) for l in open(args.bench_list)]

    for bench in benches:
        inst = bench["instance_id"]
        repo_name = bench["repo"]               # e.g. "validation-dataset"
        commit   = bench["base"]["sha"]         # e.g. "0000...1"
        org      = bench["org"]                 # e.g. "multi-swe-bench"

        # your local clone must live at project-root/repo/<repo_name>
        src_root = Path(__file__).parent.parent / "repo" / repo_name
        if not src_root.exists():
            raise FileNotFoundError(f"expected local clone at {src_root}")

        # make a clean per-instance playground
        pg = Path(args.playground) / inst
        if pg.exists():
            shutil.rmtree(pg)
        pg.mkdir(parents=True)

        # copy + checkout
        checked_out_root = copy_and_checkout(src_root, pg, commit)

        # parse entire structure under that root
        full_struct = create_structure(str(checked_out_root))
        # we only want the one benchmarks/<inst> subtree
        bench_struct = full_struct.get("benchmarks", {}).get(inst, {})

        result = {
            "repo": f"{org}/{repo_name}",
            "base_commit": commit,
            "instance_id": inst,
            "structure": {
                "benchmarks": {
                    inst: bench_struct
                }
            }
        }

        out_file = outdir / f"{inst}.json"
        with open(out_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"→ wrote {out_file}")

if __name__ == "__main__":
    main()
