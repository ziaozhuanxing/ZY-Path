"""Start the ZY-Path desktop application."""

import sys

from PyQt5.QtWidgets import QApplication, QWidget


def main() -> None:
	"""Show the blank main window."""
	application = QApplication(sys.argv)
	window = QWidget()
	window.setWindowTitle("ZY-Path")
	window.setMinimumSize(1366, 768)
	window.show()
	sys.exit(application.exec_())


if __name__ == "__main__":
	main()
