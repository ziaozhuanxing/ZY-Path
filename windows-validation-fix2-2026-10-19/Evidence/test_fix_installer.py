from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess
import pytest

ROOT=Path(__file__).parent
REPO=Path('/workspace/ZY-Path')

@pytest.fixture
def setup_bundle(tmp_path):
    bundle=tmp_path/'bundle';shutil.copytree(ROOT/'Windows_Validation_Fix2',bundle,ignore=shutil.ignore_patterns('__pycache__'))
    project=tmp_path/'project';project.mkdir()
    manifest=json.loads((bundle/'manifest.json').read_text())
    for name,item in manifest['files'].items():
        if None in item['allowed_before_normalized_sha256']:continue
        p=project/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=REPO))
    subprocess.run(['git','init','-q',str(project)],check=True)
    subprocess.run(['git','-C',str(project),'add','.'],check=True)
    subprocess.run(['git','-C',str(project),'-c','user.name=Installer test','-c','user.email=installer@example.invalid','commit','-qm','Fixture source baseline'],check=True)
    manifest['baseline']=subprocess.check_output(['git','-C',str(project),'rev-parse','HEAD']).decode().strip()
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    spec=importlib.util.spec_from_file_location('fix_'+tmp_path.name,bundle/'apply_regression_fix.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,project,bundle,manifest

@pytest.mark.parametrize('ending',[b'\n',b'\r\n'])
def test_applies_all_files_with_exact_backup_and_is_idempotent(setup_bundle,tmp_path,ending):
    module,project,bundle,manifest=setup_bundle
    originals={}
    for name in manifest['files']:
        path=project/name
        if path.exists():
            path.write_bytes(path.read_bytes().replace(b'\n',ending));originals[name]=path.read_bytes()
    # Support the already-applied width correction from the Windows evidence.
    name='ui/inference_panel.py';(project/name).write_bytes((bundle/'payload'/name).read_bytes().replace(b'\n',ending));originals[name]=(project/name).read_bytes()
    backup=module.apply_fix(project,tmp_path/'evidence')
    record=json.loads((backup/'patch-record.json').read_text())
    for item in record['files']:
        name=item['path']
        if name in originals:assert (backup/'original'/name).read_bytes()==originals[name]
    for name,item in manifest['files'].items():
        data=(project/name).read_bytes()
        assert module.digest(data)==item['after_normalized_sha256']
        if name in originals:assert data.replace(b'\r\n',b'\n').replace(b'\n',ending)==data
    assert module.apply_fix(project,tmp_path/'evidence') is None

@pytest.mark.parametrize('changed_name',['ui/image_comparison.py','tests/test_worker_lifetime.py'])
def test_unrecognized_edit_rejected_before_any_write(setup_bundle,tmp_path,changed_name):
    module,project,bundle,manifest=setup_bundle
    path=project/changed_name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((path.read_bytes() if path.exists() else b'')+b'\n# unrelated user edit\n')
    before={name:(project/name).read_bytes() if (project/name).exists() else None for name in manifest['files']}
    with pytest.raises(ValueError,match='Unrecognized edits preserved'):
        module.apply_fix(project,tmp_path/'evidence')
    assert before=={name:(project/name).read_bytes() if (project/name).exists() else None for name in manifest['files']}
    assert not (tmp_path/'evidence').exists()


def test_updates_previous_reviewed_bundle_without_overwriting_other_files(setup_bundle,tmp_path):
    module,project,bundle,manifest=setup_bundle
    previous=Path('/workspace/artifacts/windows-crash-trace-20261019-190334/Windows_Regression_Fix')
    previous_manifest=json.loads((previous/'manifest.json').read_text())
    for name in previous_manifest['files']:
        path=project/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((previous/'payload'/name).read_bytes().replace(b'\n',b'\r\n'))
    unrelated=project/'notes.txt';unrelated.write_bytes(b'User notes: preserve these bytes')
    module.apply_fix(project,tmp_path/'evidence')
    assert unrelated.read_bytes()==b'User notes: preserve these bytes'
    for name,item in manifest['files'].items():assert module.digest((project/name).read_bytes())==item['after_normalized_sha256']
