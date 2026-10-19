from pathlib import Path
import importlib.util,json,shutil,subprocess
import pytest
R=Path(__file__).parent;REPO=Path('/workspace/ZY-Path')

@pytest.fixture
def setup_bundle(tmp_path):
    bundle=tmp_path/'bundle';shutil.copytree(R/'Windows_Compact_Body_Fix',bundle,ignore=shutil.ignore_patterns('__pycache__'))
    manifest=json.loads((bundle/'manifest.json').read_text())
    verification=json.loads((bundle/'verification-manifest.json').read_text())
    previous=Path('/workspace/artifacts/windows-verify-fix-20261019-192518/Windows_Validation_Fix2/payload')
    project=tmp_path/'project';project.mkdir()
    for name in verification['files']:
        source=previous/name
        data=source.read_bytes() if source.exists() else subprocess.check_output(['git','show','HEAD:'+name],cwd=REPO)
        p=project/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    subprocess.run(['git','init','-q',str(project)],check=True)
    subprocess.run(['git','-C',str(project),'add','.'],check=True)
    subprocess.run(['git','-C',str(project),'-c','user.name=Installer test','-c','user.email=installer@example.invalid','commit','-qm','Previous reviewed source fixture'],check=True)
    manifest['baseline']=subprocess.check_output(['git','-C',str(project),'rev-parse','HEAD']).decode().strip()
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    spec=importlib.util.spec_from_file_location('compact_fix_'+tmp_path.name,bundle/'apply_regression_fix.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,project,manifest,verification

@pytest.mark.parametrize('ending',[b'\n',b'\r\n'])
def test_updates_only_delta_preserves_backups_endings_and_repeat(setup_bundle,tmp_path,ending):
    module,project,manifest,verification=setup_bundle
    for name in verification['files']:
        p=project/name;p.write_bytes(p.read_bytes().replace(b'\n',ending))
    originals={n:(project/n).read_bytes() for n in verification['files']}
    backup=module.apply_fix(project,tmp_path/'evidence')
    changed={n for n in verification['files'] if originals[n]!=(project/n).read_bytes()}
    assert changed=={'ui/action_panel.py','tests/test_screen_fit_and_tile_grid.py'}
    for n in changed:
        assert (backup/'original'/n).read_bytes()==originals[n]
        data=(project/n).read_bytes()
        assert data.replace(b'\r\n',b'\n').replace(b'\n',ending)==data
    for n,item in verification['files'].items():assert module.digest((project/n).read_bytes())==item['after_normalized_sha256']
    assert module.apply_fix(project,tmp_path/'evidence') is None

@pytest.mark.parametrize('changed_name',['ui/action_panel.py','ui/main_window.py'])
def test_rejects_unknown_delta_or_prerequisite_before_any_write(setup_bundle,tmp_path,changed_name):
    module,project,manifest,verification=setup_bundle
    p=project/changed_name;p.write_bytes(p.read_bytes()+b'\n# Unrelated edit to preserve\n')
    before={n:(project/n).read_bytes() for n in verification['files']}
    with pytest.raises(ValueError):module.apply_fix(project,tmp_path/'evidence')
    assert before=={n:(project/n).read_bytes() for n in verification['files']}
    assert not (tmp_path/'evidence').exists()
