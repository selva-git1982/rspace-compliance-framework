"""Reproducible synthetic ablations and multi-seed experiments."""
from __future__ import annotations
import csv
import math
import statistics
from pathlib import Path
from .engine import WEIGHTS, POLICY_VERSION, evaluate
from .evaluation import baseline_decision, ground_truth, confusion
from .scenarios import scenario_dataset

ALL_CHECKS = tuple(WEIGHTS) + ('policy_version',)

def ablated_decision(run, checks):
    """Evaluate only selected checks; disabled checks are deliberately ignored."""
    if not isinstance(run.get('run_id'), str) or not run['run_id'].strip():
        return 'BLOCK'
    controls = run.get('controls')
    if not isinstance(controls, dict):
        return 'BLOCK'
    return ('RELEASE' if all((run.get('policy_version') == POLICY_VERSION if k == 'policy_version'
                             else controls.get(k) is True) for k in checks) else 'BLOCK')

def evaluate_dataset(runs):
    truth = [ground_truth(run) for run in runs]
    methods = {'rspace': [evaluate(r).decision for r in runs],
               'limited_baseline': [baseline_decision(r) for r in runs]}
    for removed in ALL_CHECKS:
        methods['without_' + removed] = [ablated_decision(r, [k for k in ALL_CHECKS if k != removed]) for r in runs]
    return {name: confusion(truth, pred) for name, pred in methods.items()}

def multi_seed(*, sizes=(100, 1000, 10000), rates=(0.1, 0.2, 0.5), seeds=range(10)):
    rows = []
    for n in sizes:
        for rate in rates:
            for seed in seeds:
                runs = scenario_dataset(n, seed=seed, fault_rate=rate)
                for name, metrics in evaluate_dataset(runs).items():
                    rows.append({'jobs': n, 'fault_rate': rate, 'seed': seed, 'method': name, **metrics})
    return rows

def aggregate(rows):
    groups = {}
    for row in rows:
        groups.setdefault((row['jobs'], row['fault_rate'], row['method']), []).append(row)
    out = []
    for (n, rate, method), members in sorted(groups.items()):
        result = {'jobs': n, 'fault_rate': rate, 'method': method, 'seeds': len(members)}
        for metric in ('recall', 'precision', 'specificity', 'accuracy'):
            values = [float(r[metric]) for r in members if r[metric] is not None]
            mean = statistics.mean(values) if values else None
            sd = statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)
            result[f'{metric}_mean'] = mean
            result[f'{metric}_sd'] = sd
            # Descriptive normal-approximation CI across seeds; not a clinical/production CI.
            result[f'{metric}_ci95_low'] = max(0, mean - 1.96 * sd / math.sqrt(len(values))) if values else None
            result[f'{metric}_ci95_high'] = min(1, mean + 1.96 * sd / math.sqrt(len(values))) if values else None
        out.append(result)
    return out

def write_csv(path, rows):
    if not rows:
        raise ValueError('No results')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
