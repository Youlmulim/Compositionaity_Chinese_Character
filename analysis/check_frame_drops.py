"""
check_frame_drops.py
--------------------
Post-hoc frame drop analysis across all subjects and phases.

Usage
-----
    python analysis/check_frame_drops.py
    python analysis/check_frame_drops.py --hz 120 --threshold 1.5
    python analysis/check_frame_drops.py --subject sub-002

Output (saved to analysis/results/)
-------------------------------------
    frame_drop_summary.csv  — one row per frame_log file
    frame_drop_detail.csv   — one row per dropped frame (only when drops exist)
"""

import argparse
from pathlib import Path

import pandas as pd

DATA_DIR    = Path(__file__).parent.parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"


def detect_drops(path: Path, expected_ifi: float, threshold: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["event_marker"] != "response"].copy()
    df["ifi"] = df["flip_time"].diff()
    df.loc[df["frame_idx"] == 0, "ifi"] = float("nan")  # event boundary, not a rendered frame
    drops = df[df["ifi"] > expected_ifi * threshold].copy()
    drops["source"] = str(path.relative_to(DATA_DIR))
    return drops[["source", "frame_idx", "flip_time", "ifi", "event_marker"]]


def collect_logs(subject: str | None) -> list[Path]:
    if subject:
        roots = [DATA_DIR / subject]
    else:
        roots = [p for p in DATA_DIR.iterdir() if p.is_dir()]
    return [p for root in roots for p in root.rglob("frame_log.csv")]


def main(hz: float, threshold: float, subject: str | None) -> None:
    expected_ifi = 1 / hz
    logs = collect_logs(subject)

    if not logs:
        print("No frame_log.csv files found.")
        return

    all_drops: list[pd.DataFrame] = []
    summary_rows: list[dict] = []

    for path in sorted(logs):
        drops = detect_drops(path, expected_ifi, threshold)
        n_frames = len(pd.read_csv(path)) - 1  # exclude response row
        drop_rate = len(drops) / n_frames * 100 if n_frames > 0 else 0.0
        summary_rows.append({
            "path":       str(path.relative_to(DATA_DIR)),
            "total_frames": n_frames,
            "drops":      len(drops),
            "drop_rate%": round(drop_rate, 2),
            "max_ifi_ms": round(drops["ifi"].max() * 1000, 2) if len(drops) else 0.0,
        })
        if len(drops):
            all_drops.append(drops)

    RESULTS_DIR.mkdir(exist_ok=True)

    tag = subject if subject else "all"
    summary = pd.DataFrame(summary_rows)
    summary_path = RESULTS_DIR / f"frame_drop_summary_{tag}.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Summary saved -> {summary_path}")

    if all_drops:
        detail = pd.concat(all_drops, ignore_index=True)
        detail_path = RESULTS_DIR / f"frame_drop_detail_{tag}.csv"
        detail.to_csv(detail_path, index=False)
        print(f"Detail  saved -> {detail_path}")
    else:
        print("No frame drops detected — detail file not created.")

    flagged = summary[summary["drops"] > 0]
    if len(flagged):
        print(f"\n[!] {len(flagged)} file(s) had drops:")
        for _, row in flagged.iterrows():
            print(f"    {row['path']}  —  {row['drops']} drop(s), max IFI {row['max_ifi_ms']} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hz",        type=float, default=60.0,  help="Monitor refresh rate (default 60)")
    parser.add_argument("--threshold", type=float, default=1.5,   help="IFI multiplier to flag as drop (default 1.5)")
    parser.add_argument("--subject",   type=str,   default=None,  help="Limit to one subject, e.g. sub-002")
    args = parser.parse_args()
    main(hz=args.hz, threshold=args.threshold, subject=args.subject)
