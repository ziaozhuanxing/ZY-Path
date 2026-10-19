"""Apply reviewed source additions only after checking every original file."""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib,json,os
from pathlib import Path
import shutil,subprocess,tempfile

def digest(data):
    return hashlib.sha256(data.replace(b"\r\n",b"\n")).hexdigest() if data is not None else None

def atomic_write(path,data):
    fd,temp=tempfile.mkstemp(prefix=".zy-reviewed-fix-",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:f.write(data)
        if path.exists():shutil.copymode(path,temp)
        os.replace(temp,path)
    finally:Path(temp).unlink(missing_ok=True)

def apply_fix(project,evidence_root=None):
    bundle=Path(__file__).resolve().parent
    manifest=json.loads((bundle/"manifest.json").read_text(encoding="utf-8"))
    head=subprocess.check_output(["git","--no-optional-locks","-C",str(project),"rev-parse","HEAD"]).decode().strip()
    if head!=manifest["baseline"]:raise ValueError("Repository HEAD differs from the reviewed baseline. No files changed.")
    for name,expected in manifest.get("prerequisites",{}).items():
        target=project/name
        if not target.is_file() or target.is_symlink() or digest(target.read_bytes())!=expected:
            raise ValueError("Previously reviewed second repair is absent or changed; no files changed: "+name)
    plan=[]
    for name,item in manifest["files"].items():
        target=project/name
        if target.is_symlink():raise ValueError("Symbolic link rejected: "+name)
        original=target.read_bytes() if target.exists() else None
        payload=(bundle/"payload"/name).read_bytes()
        if digest(payload)!=item["after_normalized_sha256"]:raise ValueError("Bundle checksum mismatch: "+name)
        current=digest(original)
        if current==item["after_normalized_sha256"]:continue
        if current not in item["allowed_before_normalized_sha256"]:raise ValueError("Unrecognized edits preserved; no files changed: "+name)
        ending=b"\r\n" if original and b"\r\n" in original else b"\n"
        if original is not None and original.replace(b"\r\n",b"\n").replace(b"\n",ending)!=original:raise ValueError("Mixed line endings; no files changed: "+name)
        plan.append((name,target,original,payload.replace(b"\n",ending)))
    if not plan:
        print("All reviewed fixes are already present. No files changed.")
        return None
    backup=(evidence_root or project.parent/"ZY-PATH-evidence")/("regression-fix-"+datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True,exist_ok=False)
    record={"HEAD":head,"files":[],"scope":"Incremental update: ActionPanel scrolling content may shrink vertically without stretching the whole body. Two added compact-viewport regression cases; original tests/assertions and all previous repairs retained. Models and preprocessing unchanged."}
    for name,target,original,output in plan:
        if original is not None:
            saved=backup/"original"/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(original)
        record["files"].append({"path":name,"previously_existed":original is not None,"before_sha256":hashlib.sha256(original).hexdigest() if original is not None else None,"after_sha256":hashlib.sha256(output).hexdigest()})
    (backup/"patch-record.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    applied=[]
    try:
        for name,target,original,output in plan:
            current=target.read_bytes() if target.exists() else None
            if current!=original:raise ValueError("Source changed during verification: "+name)
            atomic_write(target,output);applied.append((target,original))
    except Exception:
        for target,original in reversed(applied):
            if original is None:target.unlink(missing_ok=True)
            else:atomic_write(target,original)
        raise
    print("Reviewed fixes applied. Original backups: "+str(backup))
    return backup

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=Path(r"E:\ZY-PATH"))
    p.add_argument("--evidence-root",type=Path)
    args=p.parse_args()
    if os.name!="nt":raise ValueError("Run the installer on the Windows project.")
    apply_fix(args.project_root.resolve(),args.evidence_root)

if __name__=="__main__":main()
