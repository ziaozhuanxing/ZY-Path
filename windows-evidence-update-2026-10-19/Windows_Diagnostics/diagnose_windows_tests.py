"""Collect separate failure/crash logs without changing application or test files."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

BATCHES=[
 ('history-selection',['tests/test_history_panel.py::test_selection_and_double_click_emit_record_ids']),
 ('minimum-layout',['tests/test_inference_panel.py::test_minimum_window_fits_panel_content_and_elides_filenames']),
 ('rerun-module',['tests/test_main_window_rerun.py']),
 ('full-suite',[]),
]


def git_record(project, directory, prefix=''):
    for name,args in [('commit.txt',['rev-parse','HEAD']),('git-status.txt',['status','--porcelain=v1','--untracked-files=all'])]:
        result=subprocess.run(['git','--no-optional-locks','-C',str(project),*args],capture_output=True,check=True)
        (directory/(prefix+name)).write_bytes(result.stdout)


def run_batch(project, directory, selectors, executable=None):
    directory.mkdir(parents=True,exist_ok=False)
    command=[str(executable or sys.executable),'-X','faulthandler','-u','-m','pytest','-p','zy_path_pytest_probe',
             '-vv','-ra','--tb=long','--color=no','--capture=tee-sys','-o','faulthandler_timeout=60',
             '--junitxml='+str(directory/'pytest.xml'),*selectors]
    env=os.environ.copy()
    env['PYTHONPATH']=str(Path(__file__).resolve().parent)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['PYTHONIOENCODING']='utf-8'
    (directory/'command.json').write_text(json.dumps(command,indent=2),encoding='utf-8')
    with (directory/'pytest-live.log').open('wb') as log:
        process=subprocess.Popen(command,cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        assert process.stdout is not None
        for line in iter(process.stdout.readline,b''):
            log.write(line);log.flush()
            print(line.decode('utf-8',errors='replace'),end='',flush=True)
        code=process.wait()
    result={'exit_code':code,'exit_code_hex':hex(code & 0xffffffff),'xml_generated':(directory/'pytest.xml').is_file(),
            'scope':'Complete unselected suite' if not selectors else 'Diagnostic subset; not a full-suite result'}
    (directory/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path(r'E:\ZY-PATH'))
    parser.add_argument('--evidence-root',type=Path)
    args=parser.parse_args()
    if os.name!='nt':raise ValueError('Run this launcher on Windows. Linux tool checks do not verify Windows behaviour.')
    project=args.project_root.resolve()
    if not (project/'main.py').is_file():raise ValueError('Project main.py not found')
    if Path(sys.executable).resolve()!=(project/'.venv/Scripts/python.exe').resolve():raise ValueError('Use the project virtual-environment Python.')
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(errors='replace')
    stamp=datetime.now().astimezone()
    root=(args.evidence_root or project.parent/'ZY-PATH-evidence')/('diagnose-'+stamp.strftime('%Y%m%d-%H%M%S'))
    root.mkdir(parents=True,exist_ok=False)
    (root/'test-date.txt').write_text(stamp.isoformat(),encoding='utf-8')
    git_record(project,root)
    results={}
    for label,selectors in BATCHES:
        print('\nRunning '+label+'; each batch has its own process and result.\n',flush=True)
        results[label]=run_batch(project,root/label,selectors)
        print('\n'+label+': '+json.dumps(results[label]),flush=True)
    git_record(project,root,'post-')
    (root/'summary.json').write_text(json.dumps({'batches':results,'scope':'Separate diagnostic subsets plus one full-suite invocation. Do not add subset counts to the full-suite result. Qt platform is observed by the probe, not forced by this launcher.'},indent=2),encoding='utf-8')
    print('\nUpload this evidence directory: '+str(root),flush=True)
    return 0 if all(r['exit_code']==0 for r in results.values()) else 1


if __name__=='__main__':sys.exit(main())
