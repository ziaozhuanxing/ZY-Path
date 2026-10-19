"""Read-only pytest observations; preserve the suite's Qt setup and assertions."""
from __future__ import annotations
import json
import os
import sys


def emit(label, value):
    print('[ZY diagnostic] '+label+' '+json.dumps(value,ensure_ascii=True,default=str),file=sys.__stderr__,flush=True)


def rect(rectangle):
    return [rectangle.x(),rectangle.y(),rectangle.width(),rectangle.height()]


def observe_qt(include_widgets=False):
    module=sys.modules.get('PyQt5.QtWidgets')
    if module is None:return
    app=module.QApplication.instance()
    if app is None:return
    from PyQt5.QtCore import qVersion
    record={'qt_runtime':qVersion(),'platform_plugin':app.platformName(),'QT_QPA_PLATFORM':os.environ.get('QT_QPA_PLATFORM'),
            'screens':[{'available':rect(s.availableGeometry()),'device_pixel_ratio':s.devicePixelRatio(),'logical_dpi':s.logicalDotsPerInch()} for s in app.screens()]}
    if include_widgets:
        windows=[]
        for w in app.topLevelWidgets():
            if type(w).__name__ not in ('MainWindow','HistoryPanel','InferencePanel'):continue
            info={'type':type(w).__name__,'visible':w.isVisible(),'geometry':rect(w.geometry()),'frame':rect(w.frameGeometry()),
                  'minimum':[w.minimumWidth(),w.minimumHeight()],'size_hint':[w.sizeHint().width(),w.sizeHint().height()],
                  'maximized':w.isMaximized(),'fullscreen':w.isFullScreen()}
            panel=getattr(w,'inference_panel',None)
            if panel is not None:
                check=panel.built_in_checkbox
                from PyQt5.QtGui import QFontMetrics
                info['inference_panel']={'width':panel.width(),'layout_size_hint':panel.layout().sizeHint().width(),
                    'checkbox_contents':rect(check.contentsRect()),'checkbox_text_width':QFontMetrics(check.font()).horizontalAdvance(check.text()),
                    'controls_viewport':rect(panel.controls_scroll.viewport().rect())}
            history=getattr(w,'history_panel',w if type(w).__name__=='HistoryPanel' else None)
            if history is not None:
                table=history.table
                info['history_table']={'viewport':rect(table.viewport().rect()),'rows':table.rowCount(),
                    'selected_ids':history.selected_record_ids(),'horizontal_scroll':table.horizontalScrollBar().value(),
                    'vertical_scroll':table.verticalScrollBar().value()}
                if table.rowCount()>1:
                    item=table.item(1,2)
                    if item is not None:info['history_table']['second_row_image_cell']=rect(table.visualItemRect(item))
            windows.append(info)
        record['windows']=windows
    emit('QT',record)


def pytest_sessionstart(session):
    emit('SESSION',{'python':sys.version,'os':sys.platform,'initial_QT_QPA_PLATFORM':os.environ.get('QT_QPA_PLATFORM')})


def observe_safely(include_widgets=False):
    try:observe_qt(include_widgets)
    except Exception as error:
        emit('OBSERVATION ERROR',{'type':type(error).__name__,'message':str(error)})


def pytest_runtest_logstart(nodeid, location):
    emit('BEGIN',nodeid)


def pytest_runtest_call(item):
    observe_safely()


def pytest_runtest_logreport(report):
    emit('REPORT',{'nodeid':report.nodeid,'phase':report.when,'outcome':report.outcome})
    if report.failed:
        print('[ZY diagnostic] IMMEDIATE FAILURE\n'+report.longreprtext,file=sys.__stderr__,flush=True)
    if report.failed or (report.when=='call' and any(x in report.nodeid for x in ('test_selection_and_double_click_emit_record_ids','test_minimum_window_fits_panel_content_and_elides_filenames'))):
        observe_safely(include_widgets=True)
