"""Reproduce the bolt held-out evaluation through the deploy path (gate G1).

Run from projects/defect-detector:
    python deploy/tools/parity_eval.py            # pinned model from the Hub
    python deploy/tools/parity_eval.py --local    # checkpoint on disk
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPLOY))

from core.engine import Engine  # noqa: E402
from core.registry import load_registry  # noqa: E402

PART_ID = re.compile(r"_p(\d+)_r\d+_")

# name -> (folder under the data root, parts flagged, parts total), from 04_patchcore_bolt.ipynb
EXPECTED = {
    "heldout normal": ("heldout", 1, 24),
    "surface defect": ("defects/surface", 14, 14),
    "thread defect": ("defects/thread", 12, 13),
}


def group_by_part(folder: Path) -> dict[str, list[Path]]:
    parts = defaultdict(list)
    for path in sorted(folder.glob("*.png")):
        match = PART_ID.search(path.name)
        if match:
            parts[match.group(1)].append(path)
    return parts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="use the checkpoint on disk, not the Hub")
    ap.add_argument("--data", type=Path, default=DEPLOY.parent / "data" / "bolt_roi")
    args = ap.parse_args()

    engine = Engine(load_registry(DEPLOY / "parts"), prefer_local=args.local)
    ok = True
    for label, (folder, want_flagged, want_total) in EXPECTED.items():
        parts = group_by_part(args.data / folder)
        flagged = 0
        print(f"\n{label}: {len(parts)} parts")
        for part_no, paths in sorted(parts.items()):
            result = engine.predict("bolt", paths).result
            flagged += result.flagged
            views = ", ".join(f"{s:.6f}" for s in result.view_scores)
            print(f"  p{part_no}  {len(paths)} views  [{views}]  part {result.part_score:.6f}  "
                  f"margin {result.part_score - result.threshold:+.6f}  "
                  f"{'FLAGGED' if result.flagged else 'passed'}")
        match = (flagged, len(parts)) == (want_flagged, want_total)
        ok &= match
        print(f"  -> flagged {flagged}/{len(parts)}, expected {want_flagged}/{want_total}: "
              f"{'OK' if match else 'MISMATCH'}")

    print("\nG1", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
