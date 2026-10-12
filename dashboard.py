"""Interactive R-SPACE demonstration. Synthetic inputs only."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import streamlit as st
from rspace.engine import evaluate, verify_evidence, WEIGHTS
from rspace.evaluation import baseline_decision, compare
from rspace.scenarios import scenario_run, scenario_dataset, FAULTS
from rspace.audit import make_manifest, verify_manifest, append_record, verify_chain
from rspace.advanced import multi_seed, aggregate

st.set_page_config(page_title='R-SPACE Research Demo', page_icon='🛡️', layout='wide')
st.title('R-SPACE | Policy-Driven Compliance Research Demo')
st.warning('Synthetic research prototype only. Not a validated GxP system or regulatory certification.')
tab1, tab2 = st.tabs(['Policy decision', 'Synthetic comparison'])
with tab1:
    st.subheader('Configure synthetic controls')
    scenario = st.selectbox('Example fault scenario', ['none'] + list(FAULTS))
    run = scenario_run(1, None if scenario == 'none' else scenario)
    for key in WEIGHTS:
        run['controls'][key] = st.checkbox(key.replace('_', ' ').title(), value=run['controls'].get(key) is True)
    approved = st.checkbox('Approved policy version', value=run['policy_version'] == 'rspace-demo-v1')
    if not approved:
        run['policy_version'] = 'unapproved'
    else:
        run['policy_version'] = 'rspace-demo-v1'
    decision = evaluate(run)
    a, b, c = st.columns(3)
    a.metric('R-SPACE decision', decision.decision)
    b.metric('Illustrative risk score', f'{decision.risk_percent:.1f}%')
    c.metric('Limited baseline decision', baseline_decision(run))
    st.caption('Risk score is a weighted heuristic, not a calibrated probability. Baseline checks only authorization, encryption and integrity.')
    st.json(decision.as_dict())
    st.success(f'Evidence digest verifies: {verify_evidence(decision.evidence, decision.evidence_sha256)}')
    import json
    manifest = make_manifest(decision)
    st.download_button('Download verifiable evidence manifest (JSON)',
                       data=json.dumps(manifest, indent=2),
                       file_name='rspace_synthetic_manifest.json', mime='application/json')
    chain = []
    append_record(chain, manifest)
    st.caption(f'Local illustrative audit chain verifies: {verify_chain(chain)}; head SHA-256: {chain[-1]["record_sha256"][:16]}…')
    st.download_button('Download audit-chain example (JSON)',
                       data=json.dumps(chain, indent=2), file_name='rspace_synthetic_audit.json', mime='application/json')
with tab2:
    st.subheader('Controlled synthetic experiment')
    n = st.select_slider('Number of synthetic jobs', options=[100, 1000, 10000], value=1000)
    fault_rate = st.slider('Fault injection rate', 0.0, 1.0, 0.2, 0.05)
    seed = st.number_input('Random seed', value=42, step=1)
    if st.button('Run comparison'):
        runs = scenario_dataset(n, seed=int(seed), fault_rate=fault_rate)
        scores = compare(runs)
        st.dataframe([{'method': method, **values} for method, values in scores.items()], hide_index=True)
        st.caption('The synthetic oracle uses the same six-control release specification as R-SPACE. This is a limited ablation study, not independent real-world validation.')
        import csv, io
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=['method', *next(iter(scores.values())).keys()])
        writer.writeheader()
        writer.writerows([{'method': k, **v} for k, v in scores.items()])
        st.download_button('Download comparison CSV', stream.getvalue(),
                           file_name='rspace_comparison.csv', mime='text/csv')
    st.divider()
    st.subheader('Multi-seed ablation study')
    st.caption('Runs each method on the same generated jobs across seeds. Baselines and ablations deliberately omit checks.')
    num_seeds = st.slider('Number of seeds', 2, 30, 10)
    if st.button('Run multi-seed study'):
        with st.spinner('Evaluating synthetic workloads…'):
            detailed = multi_seed(sizes=(100, 1000), rates=(.1, .2, .5), seeds=range(num_seeds))
            summary = aggregate(detailed)
        st.dataframe(summary, hide_index=True)
        import csv, io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)
        st.download_button('Download multi-seed summary CSV', output.getvalue(),
                           file_name='rspace_multiseed_summary.csv', mime='text/csv')

with st.expander('Research reproducibility and limitations'):
    st.write('All inputs are synthetic. The limited baseline intentionally checks fewer controls. '
             'The synthetic oracle follows the R-SPACE release specification; this is not independent validation. '
             'Risk values are illustrative, not calibrated probabilities. Local SHA-256 hashes are tamper-evident '
             'only when the reference digest or chain head is retained in a trusted location.')
