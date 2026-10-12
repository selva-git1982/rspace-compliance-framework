"""Run controlled multi-seed experiments. Invoke: PYTHONPATH=src python experiments/advanced_evaluation.py"""
import argparse
from rspace.advanced import multi_seed, aggregate, write_csv

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--seeds', type=int, default=10)
    p.add_argument('--output', default='results')
    args = p.parse_args()
    if not 1 <= args.seeds <= 1000:
        p.error('--seeds must be between 1 and 1000')
    rows = multi_seed(seeds=range(args.seeds))
    write_csv(f'{args.output}/advanced_runs.csv', rows)
    write_csv(f'{args.output}/advanced_summary.csv', aggregate(rows))
    print(f'Completed {args.seeds} seeds x 3 workloads x 3 fault rates; {len(rows)} method-level rows.')
    print(f'Saved {args.output}/advanced_runs.csv and {args.output}/advanced_summary.csv')
