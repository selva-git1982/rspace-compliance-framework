# R-SPACE — Synthetic Reference Implementation

**Research prototype only. Not a validated GxP system, clinical product, or regulatory certification.**

A small, dependency-free Python implementation of the six-control release gate described in *R-SPACE: A Policy-Driven Framework for Continuous Compliance Assurance and Secure Data Pipeline Orchestration in Regulated Life Sciences*.

## Scope

Checks explicit `True` for authorization, encryption, integrity, lineage, validation approval, and audit trail. Missing, false, or malformed observations fail closed. An unapproved policy version blocks release. A canonical SHA-256 digest binds an exported evidence payload; this is **not** a tamper-proof store or digital signature. No real patient, clinical, or employer data are used.

## Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Run benchmark

```bash
python experiments/run_benchmark.py --sizes 100 1000 10000 --repeats 5 --seed 42
```

Results are written to `results/benchmark.csv`. The benchmark measures only in-process Python policy evaluation. It does **not** compare a baseline pipeline, test external services, measure audit preparation time, or demonstrate regulatory compliance. All fault labels are generated synthetically; detection metrics describe agreement with those generated labels, not independent field validation. Report hardware and environment when citing measured times.

## Data model

`{"run_id":"synthetic-0000001","policy_version":"rspace-demo-v1","controls":{"authorization":true,"encryption":true,"integrity":true,"lineage":true,"validation_approval":true,"audit_trail":true},"synthetic":true}`

## Research and publication notes

Do not imply that all six architecture layers or orchestration adapters are implemented. This prototype demonstrates the control evaluation, release decision, and evidence-digest components only. Review source and outputs before making a public GitHub release. Cite the repository only after publishing it and obtaining its canonical URL.

## Extended evaluation (v0.2)

The optional Streamlit interface is a **synthetic research demonstration**, not a
production compliance system. The six-control engine and existing tests are
unchanged.

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m pytest -v
python experiments/compare_baseline.py --sizes 100 1000 10000 --fault-rates 0.1 0.2 0.5 --seed 42 --repeats 5
python -m streamlit run dashboard.py
```

The comparison uses an explicitly **limited three-control baseline** that checks
authorization, encryption, and integrity only. R-SPACE checks six controls plus
policy version. Higher fault detection is therefore expected by construction,
not evidence that R-SPACE outperforms a complete competitor. The synthetic
oracle uses the same six-control specification as the engine, so perfect
agreement is not independent validation. Timings are in-process and do not
include distributed orchestration, network calls, or evidence storage.

Scenario injection covers six single-control failures, missing lineage,
unapproved policy, multiple failures, and missing controls. Metrics and timings
are written to `results/comparison.csv` when the comparison is run. Benchmark
numbers vary with hardware, Python version and machine load. Do not present
these numbers as clinical, regulatory, or production results.

For stronger future research: compare equal-information implementations,
include independent policy specifications, external services and workload
traces, and report confidence intervals over multiple seeds and machines.

## v0.3 research enhancements

This version adds independently verifiable JSON evidence manifests (`rspace.audit`),
a SHA-256 linked *illustrative local* audit chain, multi-seed synthetic evaluation,
seven single-control ablations, latency comparison, CSV export, dashboard downloads,
and GitHub Actions tests on Python 3.11–3.13.

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m pytest -v
PYTHONPATH=src python experiments/advanced_evaluation.py --seeds 10
PYTHONPATH=src python experiments/performance_compare.py --repeats 15
python -m streamlit run dashboard.py
```

`results/advanced_runs.csv` contains individual seed metrics; `results/advanced_summary.csv`
contains mean, sample standard deviation and approximate normal 95% confidence intervals
across seeds. Undefined metrics are blank, not artificially assigned 100%.
`results/performance_comparison.csv` reports median *per-job repeat-average* latency;
its p95 is **across repeat averages**, not a distribution of individual request latencies.
These are descriptive local microbenchmarks, not production performance claims.

**Scientific limitations:** The ground-truth oracle implements the same mandatory
release specification as the framework. The intentionally restricted three-control
baseline and single-control ablations demonstrate coverage tradeoffs, not superiority
over industry systems. Synthetic fault generation is not a representative sample of
real regulated workflows. A SHA-256 linked local audit chain cannot prevent an attacker
from rewriting the entire chain; the final chain head must be anchored externally.
Evidence manifests are not digitally signed and do not independently establish
provenance, regulatory validation, GxP qualification or deployment readiness.
