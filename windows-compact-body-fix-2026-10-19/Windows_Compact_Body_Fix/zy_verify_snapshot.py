"""Read-only Qt environment and post-failure geometry snapshots; no event tracing."""
import json
import os
from pathlib import Path
import sys

_observed=False

def rect(value):return list(value.getRect())
def size(value):return [value.width(),value.height()]

def save(record):
    path=os.environ.get('ZY_VERIFY_SNAPSHOTS')
    if path:
        with Path(path).open('a',encoding='utf-8') as f:f.write(json.dumps(record,default=str)+'\n')
    print('[ZY verification] '+json.dumps(record,default=str),file=sys.__stderr__,flush=True)

def app_instance():
    module=sys.modules.get('PyQt5.QtWidgets')
    return module.QApplication.instance() if module else None

def pytest_runtest_call(item):
    global _observed
    if _observed:return
    app=app_instance()
    if app is None:return
    _observed=True
    from PyQt5.QtCore import qVersion
    save({'kind':'Qt environment','platform_plugin':app.platformName(),'qt_runtime':qVersion(),
          'font_point_size':app.font().pointSizeF(),
          'screens':[{'available':rect(s.availableGeometry()),'logical_dpi':s.logicalDotsPerInch(),'dpr':s.devicePixelRatio()} for s in app.screens()]})

def pytest_runtest_logreport(report):
    if not report.failed:return
    app=app_instance()
    if app is None:return
    from PyQt5 import sip
    widgets=[]
    for w in app.allWidgets():
        if sip.isdeleted(w) or type(w).__name__ not in ('MainWindow','ActionPanel','InferencePanel','ClassificationResult','SegmentationResult','ModelSettingsPage'):continue
        try:
            if not w.isVisible():continue
            info={'type':type(w).__name__,'geometry':rect(w.geometry()),'rect':rect(w.rect()),'minimum':size(w.minimumSize()),'minimum_size_hint':size(w.minimumSizeHint()),'size_hint':size(w.sizeHint())}
            if type(w).__name__=='MainWindow':
                h=w.windowHandle();m=h.frameMargins()
                info.update({'frame':rect(w.frameGeometry()),'available':rect(w._available_geometry()),'normal':rect(w.normalGeometry()),'maximized':w.isMaximized(),'fullscreen':w.isFullScreen(),'native_frame_margins':[m.left(),m.top(),m.right(),m.bottom()]})
            for name in ['controls_scroll','body_scroll','legend_scroll','image_page_scroll']:
                scroll=getattr(w,name,None)
                if scroll is not None:
                    info[name]={'geometry':rect(scroll.geometry()),'viewport':rect(scroll.viewport().rect()),'range_x':[scroll.horizontalScrollBar().value(),scroll.horizontalScrollBar().maximum()],'range_y':[scroll.verticalScrollBar().value(),scroll.verticalScrollBar().maximum()]}
            for name in ['run_button','rerun_button','tile_details_button']:
                button=getattr(w,name,None)
                if button is not None:
                    point=button.mapTo(w,button.rect().topLeft())
                    info[name]={'position':[point.x(),point.y()],'size':size(button.size()),'size_hint':size(button.sizeHint())}
            if hasattr(w,'cards'):
                info['legend_cards']=[{'size':size(card.size()),'minimum_size_hint':size(card.minimumSizeHint())} for card,*_ in w.cards]
            widgets.append(info)
        except RuntimeError as error:widgets.append({'type':type(w).__name__,'observation_error':str(error)})
    save({'kind':'post-failure geometry','test':report.nodeid,'phase':report.when,'widgets':widgets})
