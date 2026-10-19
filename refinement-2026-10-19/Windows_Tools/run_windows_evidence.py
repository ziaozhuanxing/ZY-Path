"""Repair genuine test resources and collect Windows evidence without changing tests."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

SCRIPT_SHA='c2e9f7b0c124e9f1cc9d4a9d27e0f70e788bd2e7bffb6ad8609307c535cf135e'
MODEL_SHA='8f89bd825641fba276066b54432b5d73a62b11ed6c0d70bb94c9f0bc7e2fe325'
CLASSES=['ADI','BACK','DEB','LYM','MUC','MUS','NORM','STR','TUM']

def file_sha256(path: Path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def archive_member(archive: Path, suffix: str):
    with zipfile.ZipFile(archive) as z:
        matches=[p for p in z.namelist() if p.replace('\\','/').endswith(suffix)]
        if len(matches)!=1:raise ValueError(f'Expected one {suffix} in {archive}; found {len(matches)}')
        return z.read(matches[0])

def install_script(archive: Path, project: Path):
    source=archive_member(archive,'train_crc_dn21.py')
    if hashlib.sha256(source).hexdigest()!=SCRIPT_SHA:raise ValueError('Training script differs from the verified original; no project file replaced.')
    target=project/'models/dn21_folder_classification/train_crc_dn21 (1).py'
    if target.exists():
        if target.read_bytes()!=source:raise ValueError(f'Different existing file preserved: {target}')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(source)
    return target

def git_record(project: Path, output: Path, prefix=''):
    for filename,args in [('commit.txt',['rev-parse','HEAD']),('git-status.txt',['status','--porcelain=v1','--untracked-files=all'])]:
        p=subprocess.run(['git','--no-optional-locks','-C',str(project),*args],capture_output=True,check=True)
        (output/(prefix+filename)).write_bytes(p.stdout)

def logged_run(command, project: Path, directory: Path, filename: str):
    (directory/'command.json').write_text(json.dumps(command,indent=2),encoding='utf-8')
    with (directory/filename).open('wb') as f:
        p=subprocess.Popen(command,cwd=project,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline,b''):
            f.write(line);f.flush();print(line.decode('utf-8',errors='replace'),end='',flush=True)
        code=p.wait()
    (directory/'exit-code.txt').write_text(str(code)+'\n',encoding='ascii')
    return code

def dataset_root(archive: Path):
    target=archive.parent/'CRC-VAL-HE-7K-unpacked'
    if not target.exists():
        target.mkdir()
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                destination=(target/name.replace('\\','/')).resolve()
                if not destination.is_relative_to(target.resolve()):raise ValueError('Unsafe ZIP path')
            z.extractall(target)
    candidates=[target,*[p for p in target.iterdir() if p.is_dir()]]
    matching=[p for p in candidates if all((p/c).is_dir() for c in CLASSES)]
    if len(matching)!=1:raise ValueError(f'Expected a unique nine-class directory under {target}')
    return matching[0]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['retest','evaluate'])
    parser.add_argument('--project-root',type=Path,default=Path(r'E:\ZY-PATH'))
    parser.add_argument('--training-archive',type=Path,default=Path(r'E:\补全信息\dn21_folder_classification (1).zip'))
    parser.add_argument('--dataset-archive',type=Path,default=Path(r'E:\补全信息\CRC-VAL-HE-7K.zip'))
    parser.add_argument('--evidence-root',type=Path)
    args=parser.parse_args()
    if os.name!='nt':raise ValueError('Run this wrapper on the actual Windows machine; no Windows test is simulated here.')
    project=args.project_root.resolve()
    if not (project/'main.py').is_file():raise ValueError('Project root does not contain main.py')
    expected_python=project/'.venv/Scripts/python.exe'
    if Path(sys.executable).resolve()!=expected_python.resolve():raise ValueError('Run with the project .venv\\Scripts\\python.exe to preserve the tested environment.')
    evidence_root=args.evidence_root or project.parent/'ZY-PATH-evidence'
    output=evidence_root/(args.action+'-'+datetime.now().astimezone().strftime('%Y%m%d-%H%M%S'))
    output.mkdir(parents=True,exist_ok=False)
    (output/'test-date.txt').write_text(datetime.now().astimezone().isoformat(),encoding='utf-8')
    git_record(project,output)
    if args.action=='retest':
        target=install_script(args.training_archive,project)
        (output/'training-script-sha256.txt').write_text(SCRIPT_SHA+'  '+str(target),encoding='utf-8')
        models={}
        for name in ['crc_dn21_seed42_best.pth','UPerNet_TME_tissue-panoptils_best_model_100ep.pth']:
            p=project/'models'/name
            models[name]={'present':p.is_file(),'sha256':file_sha256(p) if p.is_file() else None}
        (output/'model-availability.json').write_text(json.dumps(models,indent=2),encoding='utf-8')
        version_code="import platform,sys,torch,os;from PyQt5.QtCore import QT_VERSION_STR,PYQT_VERSION_STR,qVersion;print(platform.platform());print(sys.version);print('torch:',torch.__version__);print('CUDA:',torch.cuda.is_available());print('CPU threads:',torch.get_num_threads());print('QT_QPA_PLATFORM:',os.environ.get('QT_QPA_PLATFORM'));print('PyQt:',PYQT_VERSION_STR,'Qt compiled:',QT_VERSION_STR,'Qt runtime:',qVersion())"
        versions=subprocess.run([sys.executable,'-B','-c',version_code],capture_output=True,check=True)
        (output/'runtime.txt').write_bytes(versions.stdout+versions.stderr)
        deps=subprocess.run([sys.executable,'-m','pip','freeze'],capture_output=True,check=True)
        (output/'dependencies.txt').write_bytes(deps.stdout)
        # No test selection, import workaround, offscreen override, or continue flag.
        code=logged_run([sys.executable,'-m','pytest','-ra','--tb=long','--color=no','--junitxml='+str(output/'pytest.xml')],project,output,'pytest-full.log')
        (output/'pytest-exit-code.txt').write_text(str(code)+'\n',encoding='ascii')
    else:
        root=dataset_root(args.dataset_archive)
        model=project/'models/crc_dn21_seed42_best.pth'
        if file_sha256(model)!=MODEL_SHA:raise ValueError('Model differs from the verified epoch-26 checkpoint; no comparison score inferred.')
        reference=archive_member(args.training_archive,'experiments/crc-dn21-seed42-10ep/test-7k/predictions.csv')
        refpath=output/'reference-predictions.csv';refpath.write_bytes(reference)
        (output/'dataset-archive-sha256.txt').write_text(file_sha256(args.dataset_archive),encoding='ascii')
        script=Path(__file__).with_name('evaluate_application_classifier.py')
        command=[sys.executable,'-u',str(script),'--project-root',str(project),'--data-root',str(root),'--model',str(model),
                 '--output-dir',str(output/'application-pillow'),'--resize-backend','pillow_bilinear','--reference-predictions',str(refpath)]
        code=logged_run(command,project,output,'evaluation.log')
    git_record(project,output,'post-')
    print(f'\nEvidence directory: {output}\nExit code: {code}')
    return code

if __name__=='__main__':sys.exit(main())
