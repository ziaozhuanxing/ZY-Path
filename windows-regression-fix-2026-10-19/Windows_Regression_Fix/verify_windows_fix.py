"""Run related regressions, then the entire unfiltered suite on native Windows Qt."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

RELATED=[
 'tests/test_worker_lifetime.py','tests/test_history_panel.py','tests/test_main_window_rerun.py',
 'tests/test_cancellation_and_model_defaults.py','tests/test_inference_panel.py',
 'tests/test_linked_image_comparison.py','tests/test_classification_results_layout.py',
 'tests/test_segmentation_results_layout.py','tests/test_screen_fit_and_tile_grid.py',
 'tests/test_window_lifecycle_and_theme.py',
]


def git_record(project,output,prefix=''):
    for name,args in [('commit.txt',['rev-parse','HEAD']),('git-status.txt',['status','--porcelain=v1','--untracked-files=all']),('working-diff.patch',['diff','--binary'])]:
        p=subprocess.run(['git','--no-optional-locks','-C',str(project),*args],capture_output=True,check=True)
        (output/(prefix+name)).write_bytes(p.stdout)
    manifest=json.loads((Path(__file__).parent/'manifest.json').read_text(encoding='utf-8'))
    hashes={n:hashlib.sha256((project/n).read_bytes()).hexdigest() for n in manifest['files']}
    (output/(prefix+'source-hashes.json')).write_text(json.dumps(hashes,indent=2),encoding='utf-8')


def run_batch(project,directory,selectors):
    directory.mkdir()
    command=[sys.executable,'-X','faulthandler','-u','-m','pytest',*selectors,'-ra','--tb=long','--color=no','--capture=tee-sys','--junitxml='+str(directory/'pytest.xml')]
    env=dict(os.environ,QT_QPA_PLATFORM='windows',PYTHONIOENCODING='utf-8')
    # No trace/probe plugin, test exclusions, collection-error continuation or assertion changes.
    (directory/'command.json').write_text(json.dumps({'command':command,'cwd':str(project),'QT_QPA_PLATFORM':env['QT_QPA_PLATFORM']},indent=2),encoding='utf-8')
    start=datetime.now(timezone.utc)
    with (directory/'pytest-full.log').open('wb') as f:
        process=subprocess.Popen(command,cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,b''):
            f.write(line);f.flush();print(line.decode('utf-8',errors='replace'),end='',flush=True)
        code=process.wait()
    record={'exit_code':code,'exit_code_hex':hex(code & 0xffffffff),'start_utc':start.isoformat(),'end_utc':datetime.now(timezone.utc).isoformat(),'final_counts':None,'scope':'Complete suite' if not selectors else 'Related regressions (not added to full-suite totals)'}
    if (directory/'pytest.xml').exists():
        try:
            suites=list(ET.parse(directory/'pytest.xml').getroot().iter('testsuite'))
            counts={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
            counts['passed']=counts['tests']-counts['failures']-counts['errors']-counts['skipped']
            record['final_counts']=counts
        except (ET.ParseError,ValueError) as error:record['xml_read_error']=str(error)
    (directory/'result.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    (directory/'pytest-exit-code.txt').write_text(str(code),encoding='utf-8')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path(r'E:\ZY-PATH'))
    args=parser.parse_args();project=args.project_root.resolve()
    if os.name!='nt':raise ValueError('Use Windows for the native verification.')
    if Path(sys.executable).resolve()!=(project/'.venv/Scripts/python.exe').resolve():raise ValueError('Use the project virtual-environment Python.')
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(errors='replace')
    manifest=json.loads((Path(__file__).parent/'manifest.json').read_text(encoding='utf-8'))
    for name,item in manifest['files'].items():
        data=(project/name).read_bytes().replace(b'\r\n',b'\n')
        if hashlib.sha256(data).hexdigest()!=item['after_normalized_sha256']:raise ValueError('Reviewed fix not present: '+name)
    for name in ['models/crc_dn21_seed42_best.pth','models/dn21_folder_classification/train_crc_dn21 (1).py']:
        if not (project/name).is_file():raise ValueError('Required real test resource missing: '+name)
    output=project.parent/'ZY-PATH-evidence'/('verify-fix-'+datetime.now().astimezone().strftime('%Y%m%d-%H%M%S'))
    output.mkdir(parents=True,exist_ok=False);git_record(project,output)
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR, qVersion
    import torch
    versions={name:importlib.metadata.version(name) for name in ['pytest','pytest-qt','torch','PyQt5']}
    versions.update({'python':sys.version,'platform':sys.platform,'qt_runtime':qVersion(),'qt_compiled':QT_VERSION_STR,'pyqt':PYQT_VERSION_STR,'cuda_available':torch.cuda.is_available(),'torch_threads':torch.get_num_threads(),'Qt_plugin_requested':'windows','display_font_dpi_override':os.environ.get('QT_FONT_DPI'),'scope':'HEAD plus recorded working-tree repair; native Qt tests, not full manual GUI acceptance.'})
    (output/'environment.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
    records={}
    try:
        for name,selectors in [('related',RELATED),('full',[])]:
            print('\nRunning '+name+'\n',flush=True)
            records[name]=run_batch(project,output/name,selectors)
            if records[name]['exit_code']!=0:break
    finally:
        git_record(project,output,'post-')
        (output/'summary.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
        print('\nUpload evidence folder: '+str(output),flush=True)
    return 0 if 'full' in records and records['full']['exit_code']==0 else 1

if __name__=='__main__':sys.exit(main())
