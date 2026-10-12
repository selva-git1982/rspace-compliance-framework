"""Microbenchmark of policy engine only; not production throughput or GxP validation."""
import argparse
import csv
import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rspace.engine import evaluate, WEIGHTS
from rspace.synthetic import generate


def benchmark(n, seed, repeats, fault_rate):
    rows = list(generate(n, seed=seed, fault_rate=fault_rate))
    measurements = []
    last = None
    for _ in range(repeats):
        started = time.perf_counter()
        decisions = [evaluate(run) for run, _ in rows]
        elapsed = time.perf_counter() - started
        measurements.append(elapsed)
        last = decisions
    expected_block = [fault is not None for _, fault in rows]
    observed_block = [d.decision == "BLOCK" for d in last]
    tp = sum(e and o for e, o in zip(expected_block, observed_block))
    tn = sum(not e and not o for e, o in zip(expected_block, observed_block))
    fp = sum(not e and o for e, o in zip(expected_block, observed_block))
    fn = sum(e and not o for e, o in zip(expected_block, observed_block))
    return {"jobs": n, "seed": seed, "repeats": repeats, "fault_rate": fault_rate,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "recall": tp/(tp+fn) if tp+fn else None,
            "false_positive_rate": fp/(fp+tn) if fp+tn else None,
            "median_seconds": statistics.median(measurements),
            "median_microseconds_per_job": statistics.median(measurements)*1e6/n,
            "jobs_per_second": n/statistics.median(measurements),
            "python_version": platform.python_version(),
            "platform": platform.platform()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", nargs="+", type=int, default=[100, 1000, 10000])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--fault-rate", type=float, default=0.2)
    p.add_argument("--output", default=str(ROOT / "results" / "benchmark.csv"))
    args = p.parse_args()
    if args.repeats < 1 or any(n < 1 for n in args.sizes): p.error("sizes and repeats must be positive")
    data = [benchmark(n, args.seed, args.repeats, args.fault_rate) for n in args.sizes]
    dest = Path(args.output); dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys()); w.writeheader(); w.writerows(data)
    print(json.dumps(data, indent=2))
    print(f"Saved {dest}")

if __name__ == "__main__": main()
