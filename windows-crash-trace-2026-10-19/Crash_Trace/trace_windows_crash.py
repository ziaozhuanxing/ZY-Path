"""Trace the exact crashing test and its sequence; does not rerun the full suite."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone,timedelta
import hashlib,json,os
from pathlib import Path
import subprocess,sys

BATCHES=[
 ('missing-model-alone',['tests/test_main_window_rerun.py::test_missing_custom_model_warns_without_changing_panel']),
 ('rerun-sequence',['tests/test_main_window_rerun.py']),
 ('history-sequence',['tests/test_action_panel.py','tests/test_cancellation_and_model_defaults.py','tests/test_classification_modes_display.py','tests/test_classification_results_layout.py','tests/test_classification_tiles.py','tests/test_database_manager.py','tests/test_export_manager.py','tests/test_history_panel.py']),
]


def run_batch(project,directory,selectors,executable=None):
    directory.mkdir(parents=True,exist_ok=False)
    command=[str(executable or sys.executable),'-X','faulthandler','-u','-m','pytest','-p','zy_path_pytest_probe','-p','zy_crash_trace',
             '-vv','-ra','--tb=long','--color=no','--capture=tee-sys','-o','faulthandler_timeout=45','--junitxml='+str(directory/'pytest.xml'),*selectors]
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    env['PYTHONPATH']=str(Path(__file__).parent)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['ZY_TRACE_PROJECT']=str(project.resolve());env['ZY_TRACE_FILE']=str((directory/'execution-trace.jsonl').resolve())
    (directory/'command.json').write_text(json.dumps(command,indent=2),encoding='utf-8')
    start=datetime.now(timezone.utc)
    with (directory/'pytest-live.log').open('wb') as log:
        process=subprocess.Popen(command,cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline,b''):
            log.write(line);log.flush();print(line.decode('utf-8',errors='replace'),end='',flush=True)
        code=process.wait()
    result={'exit_code':code,'exit_code_hex':hex(code & 0xffffffff),'pid':process.pid,'start_utc':start.isoformat(),
            'end_utc':datetime.now(timezone.utc).isoformat(),'xml_generated':(directory/'pytest.xml').exists(),
            'scope':'Diagnostic subset with line/C-call observations; not a full-suite result or performance benchmark.'}
    (directory/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def collect_windows_error_events(directory,result):
    start=(datetime.fromisoformat(result['start_utc'])-timedelta(seconds=5)).isoformat()
    code=r'''$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $result=@();
$events=Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000;StartTime=([DateTimeOffset]::Parse('START_VALUE')).LocalDateTime} -ErrorAction SilentlyContinue;
foreach($e in $events){$data=@{};foreach($d in ([xml]$e.ToXml()).Event.EventData.Data){$data[[string]$d.Name]=[string]$d.'#text'};
if($data['AppName'] -notmatch '^python(w)?\.exe$'){continue}; $idText=$data['ProcessId'];$idNumber=-1;
try {if($idText.StartsWith('0x')){$idNumber=[Convert]::ToInt64($idText.Substring(2),16)}else{$idNumber=[long]$idText}}catch{};
if($idNumber -eq PID_VALUE){$result+=@{Time=$e.TimeCreated.ToString('o');Id=$e.Id;Provider=$e.ProviderName;Data=$data;Message=$e.Message}}};
ConvertTo-Json -InputObject @($result) -Depth 5'''
    code=code.replace('START_VALUE',start).replace('PID_VALUE',str(result['pid']))
    try:
        p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',code],capture_output=True,timeout=30)
        record={'query_exit_code':p.returncode,'stdout':p.stdout.decode('utf-8-sig',errors='replace'),'stderr':p.stderr.decode('utf-8-sig',errors='replace'),
                'scope':'Read-only Application Error (1000) events matched to this exact Python child PID. Empty output does not rule out a crash.'}
    except Exception as error:record={'query_error':str(error),'scope':'Event query unavailable; no system settings changed.'}
    (directory/'windows-application-events.json').write_text(json.dumps(record,indent=2),encoding='utf-8')


def git_record(project,output,prefix=''):
    for name,args in [('commit.txt',['rev-parse','HEAD']),('git-status.txt',['status','--porcelain=v1','--untracked-files=all']),('working-diff.patch',['diff','--binary'])]:
        p=subprocess.run(['git','--no-optional-locks','-C',str(project),*args],capture_output=True,check=True);(output/(prefix+name)).write_bytes(p.stdout)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path(r'E:\ZY-PATH'))
    args=parser.parse_args()
    if os.name!='nt':raise ValueError('Run on Windows; Linux helper checks cannot establish the Windows crash cause.')
    project=args.project_root.resolve()
    if Path(sys.executable).resolve()!=(project/'.venv/Scripts/python.exe').resolve():raise ValueError('Use the project virtual-environment Python.')
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(errors='replace')
    os.environ['QT_QPA_PLATFORM']='windows'
    output=project.parent/'ZY-PATH-evidence'/('crash-trace-'+datetime.now().astimezone().strftime('%Y%m%d-%H%M%S'))
    output.mkdir(parents=True,exist_ok=False);git_record(project,output)
    hashes={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in ['ui/main_window.py','ui/history_panel.py','ui/inference_panel.py','ui/classification_result.py','ui/image_comparison.py','core/model_loader.py','tests/test_main_window_rerun.py','tests/test_history_panel.py']}
    (output/'source-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    results={}
    for name,selectors in BATCHES:
        print('\nTracing '+name+'\n',flush=True)
        results[name]=run_batch(project,output/name,selectors)
        if results[name]['exit_code'] not in (0,1,2,3,4,5):collect_windows_error_events(output/name,results[name])
    git_record(project,output,'post-')
    (output/'summary.json').write_text(json.dumps({'batches':results,'scope':'Original tests/assertions retained. Scoped tracing and extra event observation can alter timing; use this for diagnosis, not final verification.'},indent=2),encoding='utf-8')
    print('\nUpload evidence directory: '+str(output),flush=True)
    return 0 if all(x['exit_code']==0 for x in results.values()) else 1


if __name__=='__main__':sys.exit(main())
