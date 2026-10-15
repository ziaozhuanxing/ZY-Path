from pathlib import Path
from collections.abc import Mapping

import torch
from transformers import UperNetConfig, UperNetForSemanticSegmentation


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "UPerNet_TME_tissue-panoptils_best_model_100ep.pth"
)

LABELS = [
    "Exclude",
    "Cancerous epithelium",
    "Stroma",
    "TILs",
    "Normal epithelium",
    "Junk/Debris",
    "Blood",
    "Other",
    "Whitespace/Empty",
]


def main():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"找不到权重文件：{MODEL_PATH}\n"
            "请解压 ZIP，并把 .pth 文件放进 models 文件夹。"
        )

    print(f"权重路径：{MODEL_PATH}")
    print(f"文件大小：{MODEL_PATH.stat().st_size / 1024**2:.1f} MiB")
    print(f"PyTorch：{torch.__version__}")

    # 先在 CPU 上加载，减少加载阶段的显存占用。
    print("\n读取本地权重……")
    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
        weights_only=True,
    )

    if not isinstance(checkpoint, Mapping):
        raise TypeError(
            "权重不是参数字典，需要根据实际保存格式调整加载代码。"
        )

    # 导师 notebook 直接加载 state_dict。
    # 同时兼容常见的外层 checkpoint 包装。
    if isinstance(checkpoint.get("state_dict"), Mapping):
        state_dict = checkpoint["state_dict"]
        print("保存格式：checkpoint['state_dict']")
    elif isinstance(checkpoint.get("model_dict"), Mapping):
        state_dict = checkpoint["model_dict"]
        print("保存格式：checkpoint['model_dict']")
    else:
        state_dict = checkpoint
        print("保存格式：直接参数字典")

    if not state_dict or not all(
        isinstance(key, str) and isinstance(value, torch.Tensor)
        for key, value in state_dict.items()
    ):
        raise ValueError(
            "没有识别到纯模型参数字典。请把此处报错发来检查。"
        )

    print(f"参数项数量：{len(state_dict)}")
    print("前五个参数：")
    for key in list(state_dict)[:5]:
        print(f"  {key}: {tuple(state_dict[key].shape)}")

    print("\n读取导师使用的网络配置……")
    config = UperNetConfig.from_pretrained(
        "openmmlab/upernet-swin-base"
    )
    config.num_labels = len(LABELS)
    config.id2label = dict(enumerate(LABELS))
    config.label2id = {
        label: index for index, label in enumerate(LABELS)
    }

    model = UperNetForSemanticSegmentation(config)

    print("严格加载权重……")
    # 不忽略缺失参数或形状不匹配。
    model.load_state_dict(state_dict, strict=True)

    del checkpoint
    del state_dict

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"预测设备：{device}")
    if device.type == "cuda":
        print(f"GPU：{torch.cuda.get_device_name(0)}")

    model = model.to(device).eval()

    # 构造 RGB 测试输入，使用 notebook 的 ImageNet 标准化。
    # 这里只检查模型运行，不使用它评估准确率。
    image = torch.rand(1, 3, 224, 224, device=device)
    mean = image.new_tensor(
        [0.485, 0.456, 0.406]
    ).view(1, 3, 1, 1)
    std = image.new_tensor(
        [0.229, 0.224, 0.225]
    ).view(1, 3, 1, 1)
    image = (image - mean) / std

    print("\n执行一次分割预测……")
    with torch.inference_mode():
        logits = model(pixel_values=image).logits

    if logits.ndim != 4:
        raise ValueError(
            f"预期四维分割输出，实际形状：{tuple(logits.shape)}"
        )

    if logits.shape[0] != 1 or logits.shape[1] != len(LABELS):
        raise ValueError(
            f"预期单张图、九类输出，实际：{tuple(logits.shape)}"
        )

    if not torch.isfinite(logits).all().item():
        raise ValueError("模型输出含 NaN 或无穷大。")

    mask = logits.argmax(dim=1)[0]

    print(f"输入形状：{tuple(image.shape)}")
    print(f"输出形状：{tuple(logits.shape)}")
    print(f"掩膜形状：{tuple(mask.shape)}")
    print(f"模型状态：{'train' if model.training else 'eval'}")

    print("\n类别编号（来自导师 notebook）：")
    for index, label in enumerate(LABELS):
        print(f"  {index}: {label}")

    print("\n检查通过：权重严格加载成功，九类分割推理可以运行。")
    print("注意：此检查不代表模型的病理预测准确率已验证。")


if __name__ == "__main__":
    main()