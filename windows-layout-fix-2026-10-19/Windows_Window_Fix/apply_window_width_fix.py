"""Apply the reviewed one-file padding fix, preserving original bytes in a backup."""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

ORIGINAL_SHA='990ef518405e079078c869a1e32d128d54355e2362e4c06e8ed6fa8d16f7ba84'
FIXED_SHA='4a6167f678e639caf94bd4cf668585001fac31000049796660058064a14ff75a'


def apply_fix(project: Path, evidence_root: Path | None = None):
    target=project/'ui/inference_panel.py'
    data=target.read_bytes();normal=data.replace(b'\r\n',b'\n')
    digest=hashlib.sha256(normal).hexdigest()
    if digest==FIXED_SHA:
        print('The reviewed width fix is already present. No file changed.')
        return None
    if digest!=ORIGINAL_SHA:raise ValueError('ui/inference_panel.py differs from the verified baseline. Existing edits preserved; no file changed.')
    ending=b'\r\n' if b'\r\n' in data else b'\n'
    if normal.replace(b'\n',ending)!=data:raise ValueError('Mixed line endings; no file changed.')
    first=b'\t\tleft_margin, _, right_margin, _ = layout.getContentsMargins()\n'
    second=b'\t\t\tmax(240, content_width + left_margin + right_margin)\n'
    assert normal.count(first)==normal.count(second)==1
    changed=normal.replace(first,first+b'\t\touter_left, _, outer_right, _ = outer.getContentsMargins()\n').replace(second,b'\t\t\tmax(240, content_width + left_margin + right_margin + outer_left + outer_right)\n')
    assert hashlib.sha256(changed).hexdigest()==FIXED_SHA
    output=changed.replace(b'\n',ending)
    backup_root=evidence_root or project.parent/'ZY-PATH-evidence'
    backup=backup_root/('window-width-fix-'+datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True,exist_ok=False)
    (backup/'original_inference_panel.py').write_bytes(data)
    record={'file':'ui/inference_panel.py','original_sha256':hashlib.sha256(data).hexdigest(),'fixed_sha256':hashlib.sha256(output).hexdigest(),
            'original_normalized_sha256':ORIGINAL_SHA,'fixed_normalized_sha256':FIXED_SHA,'line_endings':'CRLF' if ending==b'\r\n' else 'LF',
            'scope':'Only include the existing outer left/right padding in the inference panel minimum width. Tests, model preprocessing and predictions unchanged.'}
    (backup/'patch-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    fd,name=tempfile.mkstemp(prefix='.inference-panel-width-',suffix='.tmp',dir=target.parent)
    temp=Path(name)
    try:
        with os.fdopen(fd,'wb') as f:f.write(output)
        shutil.copymode(target,temp)
        if target.read_bytes()!=data:raise ValueError('Source changed during verification. Original file preserved.')
        os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)
    print('Applied one-file width fix. Original backup: '+str(backup))
    return backup


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,default=Path(r'E:\ZY-PATH'))
    p.add_argument('--evidence-root',type=Path)
    args=p.parse_args()
    if os.name!='nt':raise ValueError('Run the supplied patch launcher on the Windows project; Linux helper tests are separate.')
    if not (args.project_root/'main.py').is_file():raise ValueError('Project main.py not found')
    apply_fix(args.project_root,args.evidence_root)


if __name__=='__main__':main()
