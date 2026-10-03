"""Start the ZY-Path desktop application."""

import sys

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import apply_theme


def main() -> None:
	"""Start the ZY-Path desktop application."""
	application = QApplication(sys.argv)
	apply_theme(application)
	window = MainWindow()
	window.show()
	sys.exit(application.exec_())


if __name__ == "__main__":
	main()
