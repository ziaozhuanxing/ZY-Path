"""Start the ZY-Path desktop application."""

import logging
import sys

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QApplication

from utils.version import APP_VERSION
from utils.logging_setup import configure_logging
from ui.main_window import MainWindow
from ui.theme import apply_theme


def main() -> None:
	"""Start the ZY-Path desktop application."""
	log_path = configure_logging()
	logging.getLogger(__name__).info("Starting ZY-Path %s; diagnostics: %s", APP_VERSION, log_path)
	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
	QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
	application = QApplication(sys.argv)
	application.setApplicationName("ZY-Path")
	application.setApplicationVersion(APP_VERSION)
	settings = QSettings("ZY-Path", "ZY-Path")
	theme = settings.value("appearance/theme", "Light", type=str)
	apply_theme(application, theme)
	window = MainWindow(settings=settings)
	window.show()
	sys.exit(application.exec_())


if __name__ == "__main__":
	main()
