"""Compare real tile inputs against standalone crop inference without changing weights."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv2
import numpy as np
from PIL import Image
import torch

from core.classification_tiles import ClassificationTileSpec, exploratory_metadata, predict_classification_tiles
from core.inference_engine import InferenceEngine
from core.model_loader import ModelLoader
from core.preprocessor import Preprocessor


def resize_comparison(image):
    legacy = Preprocessor('raw255', resize_backend='pillow_bilinear').transform(image)
    opencv = Preprocessor('raw255', resize_backend='opencv_linear').transform(image)
    delta = (legacy - opencv).abs()
    return {'source_size': list(image.size), 'input_size': [224, 224],
            'mean_absolute_difference_raw255': float(delta.mean()),
            'maximum_absolute_difference_raw255': float(delta.max()),
            'fraction_different_channel_values': float((delta != 0).float().mean())}


def audit(model_path, image_path, width=512, height=512, backend='pillow_bilinear'):
    loaded = ModelLoader().load_with_info(model_path)
    validation = ModelLoader.validate(loaded.model)
    if validation.task_type != 'classification':
        raise ValueError('Choose a classification model, not segmentation.')
    spec = ClassificationTileSpec.from_metadata(exploratory_metadata(width, height, backend),
                                                loaded.classes or [], loaded.preprocess_profile)
    with Image.open(image_path) as source:
        image = source.convert('RGB')
    inputs = []
    handle = loaded.model.register_forward_pre_hook(lambda _module, args: inputs.append(args[0].detach().cpu().clone()))
    try:
        tiled = predict_classification_tiles(image, loaded.model, spec)
    finally:
        handle.remove()
    analysis = tiled['classification_analysis']
    comparisons = []
    with tempfile.TemporaryDirectory(prefix='zy-crop-audit-') as directory:
        for index in sorted({0, len(inputs) // 2, len(inputs) - 1}):
            tile = analysis['tiles'][index]
            crop = image.crop(tile['box'])
            filename = Path(directory) / f'crop-{index}.png'
            crop.save(filename)
            direct_inputs = []
            handle = loaded.model.register_forward_pre_hook(lambda _module, args: direct_inputs.append(args[0].detach().cpu().clone()))
            try:
                result = InferenceEngine(model_path, filename, 'classification', loaded_model=loaded,
                    classification_mode='single_image', classification_resize_backend=backend).run_pipeline()
            finally:
                handle.remove()
            expected = Preprocessor('raw255', resize_backend=backend).transform(crop)
            comparisons.append({
                'tile_index': index, 'box': tile['box'],
                'crop_sha256': hashlib.sha256(crop.tobytes()).hexdigest(),
                'tile_tensor_equals_direct_tensor': torch.equal(inputs[index], direct_inputs[-1]),
                'tile_tensor_equals_expected_crop': torch.equal(inputs[index], expected),
                'label_matches': tile['label'] == result['label'],
                'probabilities_match': tile['probabilities'] == result['probabilities'],
                'tile_label': tile['label'], 'tile_confidence': tile['confidence'],
                'resize_comparison': resize_comparison(crop),
            })
    return {'model_path': str(Path(model_path).resolve()), 'image_path': str(Path(image_path).resolve()),
            'image_size': list(image.size), 'tile_size': [width, height], 'resize_backend': backend,
            'edge_policy': 'crop_then_resize', 'classes': list(spec.classes), 'preprocess': spec.preprocess,
            'tile_count': len(inputs), 'tile_counts': analysis['tile_counts'], 'pixel_counts': analysis['pixel_counts'],
            'area_ratios': analysis['area_ratios'], 'representative_crops': comparisons,
            'limitation': 'Consistency checks do not establish biological classification accuracy or training-scale compatibility.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--image', type=Path)
    parser.add_argument('--tile-width', type=int, default=512)
    parser.add_argument('--tile-height', type=int, default=512)
    parser.add_argument('--resize-backend', choices=['pillow_bilinear', 'opencv_linear'], default='pillow_bilinear')
    parser.add_argument('--resize-only', action='store_true', help='Measure resize methods on synthetic patterns; no weights needed.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    if args.resize_only:
        rng = np.random.default_rng(42)
        texture = Image.fromarray(rng.integers(0, 256, (512, 512, 3), dtype=np.uint8))
        gradient = np.linspace(0, 255, 512, dtype=np.uint8)[None, :, None]
        smooth = Image.fromarray(np.broadcast_to(gradient, (512, 512, 3)).copy())
        report = {'opencv_version': cv2.__version__, 'synthetic_texture': resize_comparison(texture),
                  'synthetic_gradient': resize_comparison(smooth),
                  'training_evidence': 'Uploaded source uses A.Resize(224,224) with no interpolation override. Inspected Albumentations 1.3.1 and 2.0.8 default to cv2.INTER_LINEAR; exact training versions are unavailable.'}
    else:
        if args.model is None or args.image is None:
            parser.error('--model and --image are required unless --resize-only is selected')
        report = audit(args.model, args.image, args.tile_width, args.tile_height, args.resize_backend)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
