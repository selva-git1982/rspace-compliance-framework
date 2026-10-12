"""Tamper-evident synthetic audit records (not a secure external audit service)."""
from __future__ import annotations
from .engine import digest, verify_evidence

GENESIS = '0' * 64

def make_manifest(decision):
    """Self-contained evidence manifest with a verifiable SHA-256 digest."""
    return {'schema': 'rspace-manifest-v1', 'decision': decision.as_dict(),
            'manifest_sha256': digest({'schema': 'rspace-manifest-v1', 'decision': decision.as_dict()})}

def verify_manifest(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get('decision'), dict):
        return False
    body = {'schema': manifest.get('schema'), 'decision': manifest['decision']}
    d = manifest['decision']
    try:
        return (manifest['schema'] == 'rspace-manifest-v1' and
                digest(body) == manifest['manifest_sha256'] and
                verify_evidence(d['evidence'], d['evidence_sha256']) and
                d['evidence']['decision'] == d['decision'] and
                d['evidence']['run_id'] == d['run_id'])
    except (KeyError, TypeError, ValueError):
        return False

def append_record(chain, manifest):
    if not verify_manifest(manifest):
        raise ValueError('Invalid evidence manifest')
    previous = chain[-1]['record_sha256'] if chain else GENESIS
    payload = {'sequence': len(chain), 'previous_sha256': previous, 'manifest': manifest}
    record = {**payload, 'record_sha256': digest(payload)}
    chain.append(record)
    return record

def verify_chain(chain, *, expected_head=None):
    previous = GENESIS
    for index, record in enumerate(chain):
        if not isinstance(record, dict):
            return False
        try:
            payload = {k: record[k] for k in ('sequence', 'previous_sha256', 'manifest')}
            if (record['sequence'] != index or record['previous_sha256'] != previous or
                not verify_manifest(record['manifest']) or
                record['record_sha256'] != digest(payload)):
                return False
            previous = record['record_sha256']
        except (KeyError, TypeError, ValueError):
            return False
    return expected_head is None or previous == expected_head
