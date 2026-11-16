"""Process-level regressions for deletion of a parent with an active Qt worker."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("worker_type", ["ModelValidationThread", "InferenceEngine"])
def test_parent_destruction_waits_for_running_worker(worker_type, tmp_path):
    # A separate process makes a native Qt abort observable as a failed assertion.
    # The controlled run method exercises thread ownership without loading a model.
    script = r'''
import sys
import threading
import time
from PyQt5 import sip
from PyQt5.QtCore import QCoreApplication, QEvent
from PyQt5.QtWidgets import QApplication, QWidget
from core.inference_engine import InferenceEngine, ModelValidationThread
if sys.platform != "win32":
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
app = QApplication([])
started = threading.Event()
completed = threading.Event()
def controlled_run(self):
    started.set()
    time.sleep(0.2)
    completed.set()
worker_class = globals()[sys.argv[1]]
worker_class.run = controlled_run
parent = QWidget()
if worker_class is ModelValidationThread:
    worker = worker_class("unused-path.pth", parent)
else:
    worker = worker_class("unused-path.pth", "unused-image.png", "classification", parent=parent)
worker.start()
assert started.wait(5), "Worker did not start"
assert not completed.is_set()
parent.deleteLater()  # Deliberate forced deletion, bypassing closeEvent.
QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
assert completed.is_set(), "Parent deletion returned before the worker stopped"
assert sip.isdeleted(parent)
assert sip.isdeleted(worker)
print("Parent and worker deleted safely after run completed")
'''
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    result = subprocess.run(
        [sys.executable, "-c", script, worker_type],
        cwd=Path(__file__).resolve().parents[1], env=env,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Parent and worker deleted safely" in result.stdout
