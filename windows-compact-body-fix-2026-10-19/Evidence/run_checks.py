from pathlib import Path
import json,os,subprocess,hashlib
r=Path('/workspace/ZY-Path');o=Path(__file__).parent/'linux-regression';o.mkdir(exist_ok=True)
env=dict(os.environ,QT_QPA_PLATFORM='offscreen')
for key,name in [('APPDATA','appdata'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('MPLCONFIGDIR','mpl')]:
 p=o/name;p.mkdir(exist_ok=True);env[key]=str(p)
related=['tests/test_action_panel.py','tests/test_worker_lifetime.py','tests/test_history_panel.py','tests/test_main_window_rerun.py','tests/test_cancellation_and_model_defaults.py','tests/test_inference_panel.py','tests/test_linked_image_comparison.py','tests/test_classification_results_layout.py','tests/test_segmentation_results_layout.py','tests/test_screen_fit_and_tile_grid.py','tests/test_window_lifecycle_and_theme.py']
for name,args,extra in [('related',related,{}),('large-font',['tests/test_action_panel.py','tests/test_history_panel.py','tests/test_linked_image_comparison.py','tests/test_classification_results_layout.py','tests/test_segmentation_results_layout.py','tests/test_screen_fit_and_tile_grid.py'],{'QT_FONT_DPI':'168'}),('full',[],{})]:
 cmd=[str(r/'.venv/bin/python'),'-m','pytest',*args,'-ra','--tb=long','--color=no','--junitxml='+str(o/(name+'.xml'))]
 (o/(name+'-command.json')).write_text(json.dumps({'command':cmd,'environment':{k:env[k] for k in ['QT_QPA_PLATFORM','APPDATA']},'extra':extra},indent=2))
 with (o/(name+'.log')).open('wb') as f:p=subprocess.run(cmd,cwd=r,env=dict(env,**extra),stdout=f,stderr=subprocess.STDOUT)
 (o/(name+'-exit-code.txt')).write_text(str(p.returncode));print(name,p.returncode,(o/(name+'.log')).read_text()[-1100:],flush=True)
 if p.returncode and name!='full':break
patch=subprocess.check_output(['git','diff','--binary'],cwd=r)
(o/'working-diff.patch').write_bytes(patch)
(o/'source-state.json').write_text(json.dumps({'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r).decode().strip(),'status':subprocess.check_output(['git','status','--porcelain'],cwd=r).decode(),'tracked_patch_sha256':hashlib.sha256(patch).hexdigest(),'worker_test_sha256':hashlib.sha256((r/'tests/test_worker_lifetime.py').read_bytes()).hexdigest()},indent=2))
