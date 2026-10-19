"""Scoped line/C-call observations for two existing tests; no assertion changes."""
from __future__ import annotations
import faulthandler
import json
import linecache
import os
from pathlib import Path
import sys
import time

ROOT=os.environ.get('ZY_TRACE_PROJECT','').replace('\\','/').rstrip('/').casefold()+'/'
TARGETS={'test_missing_custom_model_warns_without_changing_panel','test_selection_and_double_click_emit_record_ids'}
_stream=None
_old_trace=None
_old_profile=None
_old_qt_handler=None
_old_exception=None
_observer=None
_active=False


def record(kind,**data):
    if _stream is not None:
        _stream.write(json.dumps({'time_ns':time.perf_counter_ns(),'kind':kind,**data},ensure_ascii=True,default=str)+'\n')
        _stream.flush()


def source_frame(frame):
    path=frame.f_code.co_filename.replace('\\','/').casefold()
    return bool((ROOT!='/' and path.startswith(ROOT) and '/.venv/' not in path)
                or path.endswith('/pathlib.py') or path.endswith('/pytestqt/qtbot.py'))


def tracer(frame,event,arg):
    if not source_frame(frame):return None
    data={'file':frame.f_code.co_filename,'line':frame.f_lineno,'function':frame.f_code.co_name}
    if event=='line':data['source']=linecache.getline(frame.f_code.co_filename,frame.f_lineno).rstrip()
    if event=='exception':data['exception_type']=getattr(arg[0],'__name__',str(arg[0]));data['message']=str(arg[1])[:500]
    record('PY_'+event.upper(),**data)
    return tracer


def profiler(frame,event,arg):
    if event in ('c_call','c_return','c_exception') and source_frame(frame):
        record(event.upper(),file=frame.f_code.co_filename,line=frame.f_lineno,function=frame.f_code.co_name,
               native_function=getattr(arg,'__qualname__',getattr(arg,'__name__',type(arg).__name__)))


def install_qt_observer():
    global _old_qt_handler,_observer
    from PyQt5.QtCore import QObject,QEvent,QtFatalMsg,qInstallMessageHandler
    from PyQt5.QtWidgets import QApplication,QTableWidget
    _old_qt_handler=qInstallMessageHandler(qt_message)
    app=QApplication.instance()
    if app is None:return
    record('QT_PLATFORM',platform=app.platformName())
    class Observer(QObject):
        def eventFilter(self,watched,event):
            try:
                if event.type() in (QEvent.MouseButtonPress,QEvent.MouseButtonRelease,QEvent.MouseButtonDblClick):
                    parent=getattr(watched,'parentWidget',lambda:None)()
                    if isinstance(parent,QTableWidget) and watched is parent.viewport():
                        index=parent.indexAt(event.pos())
                        record('TABLE_MOUSE',event_type=int(event.type()),x=event.pos().x(),y=event.pos().y(),
                               row=index.row(),column=index.column(),selected_rows=[x.row() for x in parent.selectionModel().selectedRows()])
            except Exception as error:record('OBSERVER_ERROR',error=type(error).__name__)
            return False
    _observer=Observer(app);app.installEventFilter(_observer)


def qt_message(kind,context,message):
    record('QT_MESSAGE',message_type=int(kind),message=message)
    if int(kind)==3:
        try:
            with Path(os.environ['ZY_TRACE_FILE']).with_name('fatal-python-stack.log').open('a') as stack:
                faulthandler.dump_traceback(file=stack,all_threads=True)
        except Exception:pass
    if _old_qt_handler is not None:_old_qt_handler(kind,context,message)
    else:os.write(2,('Qt: '+message+'\n').encode('utf-8',errors='replace'))


def exception_hook(kind,value,tb):
    record('PY_UNHANDLED',exception_type=kind.__name__,message=str(value)[:1000])
    _old_exception(kind,value,tb)


def pytest_runtest_call(item):
    global _stream,_old_trace,_old_profile,_old_exception,_active
    if item.originalname not in TARGETS:return
    filename=Path(os.environ['ZY_TRACE_FILE'])
    _stream=filename.open('a',encoding='utf-8')
    record('START',test=item.nodeid,scope='Observation only; no source edits, local values, model outputs or assertions changed.')
    _old_trace=sys.gettrace();_old_profile=sys.getprofile();_old_exception=sys.excepthook
    install_qt_observer()
    sys.excepthook=exception_hook
    _active=True
    sys.settrace(tracer);sys.setprofile(profiler)


def pytest_runtest_teardown(item,nextitem):
    global _active,_stream,_observer
    if not _active:return
    sys.settrace(_old_trace);sys.setprofile(_old_profile)
    if sys.excepthook is exception_hook:sys.excepthook=_old_exception
    from PyQt5.QtCore import qInstallMessageHandler
    from PyQt5.QtWidgets import QApplication
    qInstallMessageHandler(_old_qt_handler)
    app=QApplication.instance()
    if app is not None and _observer is not None:app.removeEventFilter(_observer)
    record('END',test=item.nodeid)
    _stream.close();_stream=None;_active=False
