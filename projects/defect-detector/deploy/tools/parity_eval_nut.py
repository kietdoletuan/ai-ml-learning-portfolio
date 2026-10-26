"""Nut parity check: does the app give the same answers as the notebook?

Run from projects/defect-detector:
    python deploy/tools/parity_eval_nut.py --local
"""
import csv
import sys
from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPLOY))

from core.engine import Engine  # noqa: E402
from core.registry import load_registry  # noqa: E402

PROJECT = DEPLOY.parent
ROI_FOLDER = PROJECT / "data" / "nut_special" / "roi"
RUN_FOLDER = PROJECT / "results" / "nut_patchcore" / "20261017_153400"
VIEWS = ["A_above", "A_under", "B_above", "B_under"]
TOLERANCE = 0.0001

EXPECTED = {
    "val normal": [0, 12],
    "val defect": [12, 12],
    "test normal": [3, 12],
    "test defect": [12, 12],
}

ANCHORS = {
    "p055": 13.072965,
    "p095": 13.525324,
    "p101": 13.916843,
    "p074": 14.012569,
}

def read_notebook_answers():
    answers = {}

    with open(RUN_FOLDER / "val_scores.csv", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["experiment"] == "joint":
                part_id = row["part_id"]
                score = float(row["score"])
                if part_id not in answers:
                    answers[part_id] = {"split": "val", "label": row["label"], "score": score}
                elif score > answers[part_id]["score"]:
                    answers[part_id]["score"] = score

    with open(RUN_FOLDER / "test_parts.csv", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            answers[row["part_id"]] = {"split": "test", "label": row["label"], "score": float(row["score"])}

    return answers


def find_part_images(part_id):
    paths = []
    for view in VIEWS:
        file_name = part_id + "_" + view + ".png"
        for folder in ["heldout", "defects"]:
            path = ROI_FOLDER / view / folder / file_name
            if path.exists():
                paths.append(path)
    return paths


def main():
    use_local = "--local" in sys.argv
    registry = load_registry(DEPLOY / "parts")
    engine = Engine(registry, prefer_local=use_local)
    answers = read_notebook_answers()

    flagged = {"val normal": 0, "val defect": 0, "test normal": 0, "test defect": 0}
    total = {"val normal": 0, "val defect": 0, "test normal": 0, "test defect": 0}

    largest_anchor_difference = 0.0
    largest_difference = 0.0

    for part_id in sorted(answers):
        answer = answers[part_id]
        group = answer["split"] + " " + answer["label"]
        paths = find_part_images(part_id)

        try:
            prediction = engine.predict("nut_special", paths)
        except Exception as error:
            print(part_id, "SKIPPED:", error)
            continue

        result = prediction.result
        total[group] = total[group] + 1
        if result.flagged:
            flagged[group] = flagged[group] + 1
            verdict = "FLAGGED"
        else:
            verdict = "passed"

        difference = abs(result.part_score - answer["score"])
        if difference > largest_difference:
            largest_difference = difference

        if part_id in ANCHORS:
                    anchor_difference = abs(result.part_score - ANCHORS[part_id])
                    if anchor_difference > largest_anchor_difference:
                        largest_anchor_difference = anchor_difference

        print(group, part_id, "app:", round(result.part_score, 6),
              "notebook:", round(answer["score"], 6),
              "difference:", round(difference, 6), verdict)

    passed = True
    print("largest difference:", round(largest_difference, 6), "allowed:", TOLERANCE)
    print("largest difference from anchors:", round(largest_anchor_difference, 6), "allowed:", TOLERANCE)
    if largest_anchor_difference > TOLERANCE:
        passed = False

    for group in EXPECTED:
        want_flagged = EXPECTED[group][0]
        want_total = EXPECTED[group][1]
        print(group, "- flagged", flagged[group], "of", total[group],
              "- expected", want_flagged, "of", want_total)
        if flagged[group] != want_flagged or total[group] != want_total:
            passed = False

    if passed:
        print("Nut parity PASS")
        return 0
    else:
        print("Nut parity FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
