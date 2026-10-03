"""Open the history page with temporary sample database records."""

import sys
import tempfile
from pathlib import Path

from PyQt5.QtWidgets import QApplication

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from data.database_manager import DatabaseManager
from ui.main_window import MainWindow
from ui.theme import apply_theme


def main() -> int:
	"""Create sample records and show them in the application window."""
	application = QApplication(sys.argv)
	apply_theme(application)
	with tempfile.TemporaryDirectory(prefix="zy_path_history_demo_") as folder:
		db_path = Path(folder) / "history.db"
		manager = DatabaseManager(db_path)
		samples = [
			("images/thyroid_01.png", "Built-in model", "classification", "benign", 0.947),
			("images/thyroid_02.png", "models/custom.pt", "classification", "malignant", 0.812),
			("images/thyroid_03.png", "Built-in model", "classification", "non-thyroid", 0.901),
			("images/tissue_01.png", "models/segmenter.pth", "segmentation", None, None),
			("images/tissue_02.png", "Built-in model", "segmentation", None, None),
			("images/tissue_03.png", "models/segmenter.pth", "segmentation", None, None),
		]
		for image_path, model_path, task_type, label, confidence in samples:
			manager.insert_record(
				image_path,
				model_path,
				task_type,
				result_label=label,
				confidence=confidence,
			)

		window = MainWindow(db_path=db_path)
		window.show()
		print(f"Demo database: {db_path}")
		return application.exec_()


if __name__ == "__main__":
	sys.exit(main())