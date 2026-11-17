"""Reproduce Lab09 evidence (run from src: python -m lab9.report).

Reports are generated from live trials, never patched. This does not publish or
approve a release. Human tone-audit confirmation is recorded in docs separately.
"""
from __future__ import annotations

import contextlib
import io
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

from lab8.shapes import SHAPES
from lab9 import gate, mutation, variants
from lab9.eval import load_spec, load_world, make_task, run_eval
from lab9.graders import GRADERS
from lab9.judge import calibrate
from lab9.traps import main as traps_main
from lab9.variant_agent import make_shape

OUT = Path('reports/lab9')


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    variants.register()
    summary = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               'working_tree_changes': subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines(),
               'versions': {}, 'judges': {}, 'traces': {}}
    source_paths = sorted([*Path('lab9').glob('*.py'), *Path('tests').glob('test_lab9*.py'),
                           Path('config/metric_spec.yaml'), Path('config/metric_spec_v2.yaml'),
                           Path('config/fm_map.yaml'), Path('requirements.txt'), Path('requirements-lab9.txt')])
    summary['source_files_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    summary['source_sha256'] = hashlib.sha256(json.dumps(summary['source_files_sha256'], sort_keys=True).encode()).hexdigest()
    messages = []
    for version in ('v1', 'v2'):
        spec = load_spec(Path('config/metric_spec' + ('_v2' if version == 'v2' else '') + '.yaml'))
        base = run_eval('swarm', spec)
        write(Path(f'reports/baseline_{version}.json'), base)
        alternate = run_eval('swarm', spec, [66, 77, 88, 99, 110])
        write(OUT / f'aa_{version}.json', alternate)
        results = {}
        for shape, expected in mutation.EXPECTED.items():
            rep = run_eval(shape, spec)
            write(OUT / f'{shape}_{version}.json', rep)
            blocked, lines = gate.check(rep, base, spec, spec)
            (OUT / f'gate_{shape}_{version}.log').write_text('\n'.join(lines) + '\nblocked: ' + ', '.join(blocked) + '\n', encoding='utf-8')
            results[shape] = {'expected': expected, 'actual': 'block' if blocked else 'merge', 'blocked': blocked}
        det, fa = mutation.detect(spec)
        summary['versions'][version] = {'baseline_run': base['run_id'], 'baseline': base['metrics'],
            'aa': alternate['metrics'], 'scorecard': results, 'detection': det, 'false_alarm': fa}
        message = f'{version} {results} detection {det} false_alarm {fa}'
        messages.append(message)
        print(message, flush=True)
    for criterion in ('tone', 'helpful'):
        summary['judges'][criterion] = calibrate(Path(f'data/eval/judge_{criterion}_public.csv'))
    spec = load_spec(Path('config/metric_spec_v2.yaml'))
    world, claims = load_world(spec)
    labels = json.loads(Path(spec['labels']).read_text())
    cases = [('FM-01', 'leaky_trace', 'C-010'), ('FM-02', 'ignore_denied', 'C-007'),
             ('FM-03', 'ticket_trust', 'C-002'), ('FM-04', 'sum_parts', 'C-105'),
             ('FM-05', 'pre_deducted', 'C-014'), ('FM-06', 'stale_clause', 'C-006'),
             ('FM-07', 'sibling_refund', 'C-001'), ('FM-08', 'misreport', 'C-008'),
             ('FM-09', None, 'C-110')]
    for fm, bug, claim in cases:
        shape = f'evidence_{fm}' if bug else 'fixed'
        if bug:
            SHAPES[shape] = make_shape(shape, {'no_override', bug})
        evidence = {'claim_id': claim, 'seed': 11, 'bug': bug, 'label': labels[claim]}
        for key, selected in [('observed', shape), ('control', 'fixed')]:
            with tempfile.TemporaryDirectory() as tmp:
                trial = make_task(selected, world, claims, labels, Path(tmp))({'claim_id': claim, 'seed': 11})
            ctx = SimpleNamespace(output=trial, expected_output=labels[claim])
            evidence[key] = {'trial': trial, 'graders': {
                mid: {'value': bool(res.value), 'reason': res.reason}
                for mid, grader in GRADERS.items() for res in [grader().evaluate(ctx)]}}
        write(OUT / f'trace_{fm}.json', evidence)
        summary['traces'][fm] = {'claim': claim, 'bug': bug,
            'observed': evidence['observed']['graders'], 'control': evidence['control']['graders']}
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        result = traps_main(['--pr', str(OUT / 'slice_regression_v2.json'), '--baseline', 'reports/baseline_v2.json',
                             '--spec', 'config/metric_spec_v2.yaml', '--out', str(OUT / 'traps')])
    (OUT / 'traps.log').write_text(capture.getvalue(), encoding='utf-8')
    summary['traps_exit'] = result
    write(OUT / 'summary.json', summary)
    # v1 has no slice/pass^k contract; advanced mutants are scored on v2 only.
    ok = result == 0 and all(v['detection'] >= .8 and v['false_alarm'] <= .1
                            for v in summary['versions'].values()) and all(
        r['actual'] == r['expected'] for r in summary['versions']['v2']['scorecard'].values()) and all(
        summary['versions']['v1']['scorecard'][name]['actual'] == mutation.EXPECTED[name]
        for name in ('fixed', 'honest_refactor', 'seeded_regression'))
    message = f"Evidence generated: {OUT / 'summary.json'} {'PASS' if ok else 'FAIL'}"
    messages.append(message)
    (OUT / 'reproduce.log').write_text('\n'.join(messages) + '\n', encoding='utf-8')
    print(message, flush=True)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
