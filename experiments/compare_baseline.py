"""Synthetic ablation comparison; NOT a comparison with commercial products."""
import argparse
import csv
import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rspace.engine import evaluate
from rspace.evaluation import baseline_decision, compare
from rspace.scenarios import scenario_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', nargs='+', type=int, default=[100, 1000, 10000])
    parser.add_argument('--fault-rates', nargs='+', type=float, default=[0.1, 0.2, 0.5])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--output', default=str(ROOT / 'results' / 'comparison.csv'))
    args = parser.parse_args()
    if args.repeats < 1 or any(n < 1 for n in args.sizes) or any(not 0 <= f <= 1 for f in args.fault_rates):
        parser.error('invalid sizes, repeats or fault rates')
    records = []
    for n in args.sizes:
        for fault_rate in args.fault_rates:
            runs = scenario_dataset(n, seed=args.seed, fault_rate=fault_rate)
            scores = compare(runs)
            for name, func in [('rspace', lambda r: evaluate(r).decision), ('baseline', baseline_decision)]:
                times = []
                for _ in range(args.repeats):
                    start = time.perf_counter()
                    decisions = [func(run) for run in runs]
                    times.append(time.perf_counter() - start)
                median = statistics.median(times)
                records.append(dict(jobs=n, seed=args.seed, fault_rate=fault_rate, repeats=args.repeats,
                                    method=name, **scores[name], median_seconds=median,
                                    microseconds_per_job=median * 1e6 / n,
                                    jobs_per_second=n / median if median > 0 else None,
                                    python_version=platform.python_version(), platform=platform.platform()))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps(records, indent=2))
    print(f'Saved {path}')


if __name__ == '__main__':
    main()
