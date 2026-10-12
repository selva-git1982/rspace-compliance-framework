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
