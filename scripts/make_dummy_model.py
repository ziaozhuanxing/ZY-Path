"""Create small random models for exercising the ZY-Path interface."""

import sys
from pathlib import Path

import torch
from torch import nn
from torchvision.models import DenseNet


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
	"""Write a small DenseNet checkpoint and a TorchScript segmenter."""
	models_dir = PROJECT_ROOT / "models"
	models_dir.mkdir(parents=True, exist_ok=True)

	builtin_model = DenseNet(
		growth_rate=4,
		block_config=(1, 1),
		num_init_features=8,
		bn_size=2,
		drop_rate=0,
		num_classes=9,
	)
	class_names = ["ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM"]
	builtin_path = models_dir / "builtin_model.pth"
	torch.save(
		{
			"model_dict": builtin_model.state_dict(),
			"growth_rate": 4,
			"block_config": (1, 1),
			"num_init_features": 8,
			"bn_size": 2,
			"drop_rate": 0,
			"num_classes": 9,
			"classes": class_names,
			"preprocess": "imagenet",
		},
		builtin_path,
	)

	segmentation_model = nn.Conv2d(3, 4, kernel_size=1).eval()
	segmentation_path = models_dir / "dummy_segmentation.pt"
	traced_model = torch.jit.trace(
		segmentation_model,
		torch.rand((1, 3, 224, 224)),
	)
	traced_model.save(str(segmentation_path))

	print(builtin_path)
	print(segmentation_path)
	print(
		"These are random dummy models for testing the interface only; "
		"predictions are meaningless."
	)


if __name__ == "__main__":
	main()