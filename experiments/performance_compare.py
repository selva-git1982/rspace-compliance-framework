"""Descriptive single-process microbenchmark, not production throughput."""
import argparse
import csv
import platform
import statistics
import sys
from pathlib import Path
from time import perf_counter_ns
from rspace.engine import evaluate
from rspace.evaluation import baseline_decision
from rspace.scenarios import scenario_dataset

def measure(runs, method, repeats):
    durations = []
    for _ in range(repeats):
        start = perf_counter_ns()
        for run in runs:
            method(run)
        durations.append((perf_counter_ns() - start) / len(runs) / 1000)
    sorted_values = sorted(durations)
    return {'median_microseconds_per_job': statistics.median(durations),
            'p95_repeat_microseconds_per_job': sorted_values[max(0, int(.95 * (len(sorted_values)-1)))],
            'min_microseconds_per_job': min(durations)}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repeats', type=int, default=15)
    p.add_argument('--output', default='results/performance_comparison.csv')
    args = p.parse_args()
    if args.repeats < 2:
        p.error('At least 2 repeats required')
    rows = []
    for n in (100, 1000, 10000):
        runs = scenario_dataset(n, seed=42, fault_rate=.2)
        for label, fn in (('limited_baseline', baseline_decision), ('rspace', evaluate)):
            fn(runs[0])  # warm-up
            rows.append({'jobs': n, 'method': label, 'repeats': args.repeats,
                         'python': sys.version.split()[0], 'platform': platform.platform(),
                         **measure(runs, fn, args.repeats)})
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f'Saved {dest}. Note: p95 is across repeat-average times, not per-job p95.')
