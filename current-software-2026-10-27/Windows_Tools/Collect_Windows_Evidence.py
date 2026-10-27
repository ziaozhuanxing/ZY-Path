"""Collect real source/test records locally; do not install or replace resources."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def git(project, *args):
    result = subprocess.run(['git', *args], cwd=project, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Git command failed')
    return result.stdout


def source_hashes(project):
    files = git(project, 'ls-files').splitlines()
    return {name: hashlib.sha256((project / name).read_bytes()).hexdigest()
            for name in files if (project / name).is_file()
            and (name.endswith('.py') or name in ['requirements.txt', 'requirements-windows-build.txt'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--output-root', type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    if not (project / 'main.py').is_file() or not (project / 'tests').is_dir():
        parser.error('The project must contain main.py and tests/.')
    root = args.output_root or project.parent / 'ZY-PATH-evidence'
    out = root / ('thesis-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    out.mkdir(parents=True, exist_ok=False)
    before = {'head': git(project, 'rev-parse', 'HEAD').strip(),
              'branch': git(project, 'branch', '--show-current').strip(),
              'status': git(project, 'status', '--porcelain=v1', '--untracked-files=all'),
              'source_hashes': source_hashes(project)}
    (out / 'source-before.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
    (out / 'commit.txt').write_text(before['head'] + '\n', encoding='utf-8')
    (out / 'git-status.txt').write_text(before['status'], encoding='utf-8')
    environment = {'date': datetime.now().astimezone().isoformat(), 'python': sys.version,
                   'executable': sys.executable, 'platform': platform.platform(),
                   'machine': platform.machine(), 'processor': platform.processor(),
                   'QT_QPA_PLATFORM_environment': os.environ.get('QT_QPA_PLATFORM'),
                   'QT_SCALE_FACTOR_environment': os.environ.get('QT_SCALE_FACTOR')}
    (out / 'environment.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
    dependencies = subprocess.run([sys.executable, '-m', 'pip', 'freeze'],
                                  cwd=project, capture_output=True, text=True)
    (out / 'dependencies-command.txt').write_text(dependencies.stdout + dependencies.stderr,
                                                 encoding='utf-8')
    # pip can be absent in a uv-managed venv; preserve the actual probe outcome.
    probe = """import json,torch,pytest
from PyQt5.QtCore import PYQT_VERSION_STR,QT_VERSION_STR,qVersion
from PyQt5.QtWidgets import QApplication
app=QApplication([])
print(json.dumps({'torch':torch.__version__,'cuda_available':torch.cuda.is_available(),
'torch_threads':torch.get_num_threads(),'pytest':pytest.__version__,'PyQt5':PYQT_VERSION_STR,
'Qt_compiled':QT_VERSION_STR,'Qt_runtime':qVersion(),'Qt_platform':app.platformName(),
'probe_scope':'independent minimal QApplication; not a manual acceptance result'}))
"""
    p = subprocess.run([sys.executable, '-c', probe], cwd=project, capture_output=True, text=True)
    (out / 'runtime-probe.log').write_text(p.stdout + p.stderr, encoding='utf-8')
    command = [sys.executable, '-m', 'pytest', '-ra', '--tb=long', '--color=no',
               '--junitxml=' + str(out / 'pytest.xml')]
    (out / 'command.json').write_text(json.dumps(command, indent=2), encoding='utf-8')
    print('Running complete pytest; no tests are selected, skipped or modified by this collector.', flush=True)
    started = time.perf_counter()
    with (out / 'pytest-full.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(command, cwd=project, stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - started
    (out / 'pytest-exit-code.txt').write_text(str(result.returncode) + '\n', encoding='utf-8')
    after = {'head': git(project, 'rev-parse', 'HEAD').strip(),
             'status': git(project, 'status', '--porcelain=v1', '--untracked-files=all'),
             'source_hashes': source_hashes(project)}
    summary = {'exit_code': result.returncode, 'collector_elapsed_seconds': elapsed,
               'source_before': before['head'], 'source_after': after['head'],
               'source_changed_during_test': before['source_hashes'] != after['source_hashes'],
               'qt_probe_exit_code': p.returncode, 'pip_probe_exit_code': dependencies.returncode,
               'results': None}
    xml = out / 'pytest.xml'
    if xml.is_file():
        suites = ET.parse(xml).getroot().findall('testsuite')
        counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites)
                  for key in ['tests', 'failures', 'errors', 'skipped']}
        counts['passed'] = counts['tests'] - counts['failures'] - counts['errors'] - counts['skipped']
        summary['results'] = counts
    (out / 'source-after.json').write_text(json.dumps(after, indent=2), encoding='utf-8')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print('Evidence directory:', out)
    print('Review paths and private data before sharing the evidence directory.')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
