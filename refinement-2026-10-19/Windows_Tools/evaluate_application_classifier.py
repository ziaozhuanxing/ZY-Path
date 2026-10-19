"""Evaluate real labelled patches through ZY-Path's actual Single image core.

No GUI preferences, source files, histories or model weights are modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import platform
import subprocess
import sys
import time

CLASSES = ['ADI','BACK','DEB','LYM','MUC','MUS','NORM','STR','TUM']
EXTENSIONS = {'.tif','.tiff','.png','.jpg','.jpeg','.bmp'}

def decode_opencv_rgb(path: Path):
    """Decode file bytes so Windows paths containing Chinese characters work."""
    import cv2
    import numpy as np
    bgr=cv2.imdecode(np.frombuffer(path.read_bytes(),dtype=np.uint8),cv2.IMREAD_COLOR)
    if bgr is None:raise ValueError(f'OpenCV could not decode {path.name}')
    return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)

def collect_records(root: Path, expected_count: int):
    directories={p.name for p in root.iterdir() if p.is_dir()}
    if directories != set(CLASSES):
        raise ValueError(f'Expected exactly the nine class folders; found {sorted(directories)}')
    records=[];seen=set()
    for label,name in enumerate(CLASSES):
        files=sorted(p for p in (root/name).rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS)
        if not files:raise ValueError(f'No images in {name}')
        for p in files:
            if p.resolve() in seen:raise ValueError(f'Duplicate resolved image: {p}')
            seen.add(p.resolve());records.append((p,label,p.relative_to(root).as_posix()))
    if len(records)!=expected_count:raise ValueError(f'Expected {expected_count} images, found {len(records)}')
    return records

def summarise(matrix):
    n=sum(map(sum,matrix))
    if not n:raise ValueError('No evaluated samples')
    per={}
    for i,name in enumerate(CLASSES):
        true_positive=matrix[i][i];support=sum(matrix[i]);predicted=sum(row[i] for row in matrix)
        precision=true_positive/predicted if predicted else 0.0
        recall=true_positive/support if support else 0.0
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
        per[name]={'precision':precision,'recall':recall,'f1':f1,'support':support}
    return {'image_count':n,'correct_count':sum(matrix[i][i] for i in range(9)),
            'accuracy':sum(matrix[i][i] for i in range(9))/n,
            'macro_f1':sum(v['f1'] for v in per.values())/9,'per_class':per}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--resize-backend',choices=['pillow_bilinear','opencv_linear'],default='pillow_bilinear')
    parser.add_argument('--reference-predictions',type=Path)
    args=parser.parse_args()
    project=args.project_root.resolve();sys.path.insert(0,str(project))
    from core.model_loader import ModelLoader
    from core.preprocessor import Preprocessor
    from core.output_parser import OutputParser
    import numpy as np
    import torch
    import PIL
    from PIL import Image
    import cv2

    records=collect_records(args.data_root.resolve(),7180)
    if args.output_dir.exists():raise ValueError('Output directory already exists; use a new directory to preserve earlier results.')
    args.output_dir.mkdir(parents=True)
    weights=ModelLoader().load_with_info(args.model)
    validation=ModelLoader.validate(weights.model)
    if weights.classes!=CLASSES or weights.preprocess_profile!='raw255' or validation.task_type!='classification':
        raise ValueError('This evaluation requires the verified nine-class raw255 classifier.')
    preprocess=Preprocessor(profile='raw255',size=(224,224),resize_backend=args.resize_backend)
    reference={}
    if args.reference_predictions:
        with args.reference_predictions.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
                if row['relative_path'] in reference:raise ValueError('Duplicate reference prediction path')
                reference[row['relative_path']]=row
        if set(reference)!={record[2] for record in records}:raise ValueError('Reference CSV paths do not exactly match the evaluation images.')
    matrix=[[0]*9 for _ in range(9)];sizes=Counter();tensor_differences=0;max_tensor_difference=0.0
    reference_label_agreement=0;max_reference_probability_difference=0.0
    start=time.perf_counter();partial=args.output_dir/'predictions.partial.csv'
    header=['relative_path','true_class','predicted_class','max_softmax_score',*[f'probability_{c}' for c in CLASSES]]
    with partial.open('w',newline='',encoding='utf-8') as f,torch.inference_mode():
        writer=csv.writer(f);writer.writerow(header)
        for index,(path,true,relative) in enumerate(records,1):
            with Image.open(path) as source:
                source.seek(0);rgb=source.convert('RGB').copy()
            sizes[f'{rgb.width}x{rgb.height}']+=1
            tensor=preprocess.transform(rgb)
            # Diagnostic comparison uses the installed OpenCV version; the original
            # Albumentations evaluation is compared via its actual CSV if provided.
            cv_rgb=decode_opencv_rgb(path)
            cv_array=cv2.resize(cv_rgb,(224,224),interpolation=cv2.INTER_LINEAR).astype(np.float32)
            cv_tensor=torch.from_numpy(cv_array).permute(2,0,1).contiguous().unsqueeze(0)
            delta=float((tensor-cv_tensor).abs().max())
            tensor_differences+=int(delta!=0);max_tensor_difference=max(max_tensor_difference,delta)
            logits=ModelLoader.forward(weights.model,tensor)
            if not torch.isfinite(logits).all():raise ValueError(f'Non-finite model output for {relative}')
            parsed=OutputParser.parse_classification(logits,CLASSES)
            if abs(sum(parsed['probabilities'])-1)>1e-5:raise ValueError(f'Invalid probability sum for {relative}')
            predicted=int(parsed['class_index']);matrix[true][predicted]+=1
            writer.writerow([relative,CLASSES[true],parsed['label'],parsed['confidence'],*parsed['probabilities']])
            if reference:
                old=reference[relative]
                if old['true_class']!=CLASSES[true]:raise ValueError(f'Reference truth differs for {relative}')
                reference_label_agreement+=int(old['predicted_class']==parsed['label'])
                max_reference_probability_difference=max(max_reference_probability_difference,
                    max(abs(float(old[f'probability_{c}'])-p) for c,p in zip(CLASSES,parsed['probabilities'])))
            if index%100==0 or index==len(records):
                f.flush();print(f'Evaluated {index}/{len(records)}',flush=True)
    elapsed=time.perf_counter()-start
    partial.rename(args.output_dir/'predictions.csv')
    summary=summarise(matrix)
    try:revision=subprocess.check_output(['git','-C',str(project),'rev-parse','HEAD'],text=True).strip()
    except (OSError,subprocess.CalledProcessError):revision=None
    summary.update({'class_order':CLASSES,'task':'classification','mode':'single_image',
        'preprocess':'raw255','input_size':[224,224],'resize_backend':args.resize_backend,
        'model_sha256':hashlib.sha256(args.model.read_bytes()).hexdigest(),
        'application_revision':revision,'preprocessor_source_sha256':hashlib.sha256((project/'core/preprocessor.py').read_bytes()).hexdigest(),
        'source_dimensions':dict(sizes),'device':'cpu','cuda_used':False,
        'environment':{'python':platform.python_version(),'platform':platform.platform(),'torch':torch.__version__,
            'torch_cpu_threads':torch.get_num_threads(),'Pillow':PIL.__version__,'opencv':cv2.__version__,'numpy':np.__version__},
        'opencv_input_diagnostic':{'differing_images':tensor_differences,'maximum_absolute_tensor_difference':max_tensor_difference,
            'scope':'Installed OpenCV RGB decode and INTER_LINEAR vs selected application pipeline; not a claim of reproducing a different library version.'},
        'reference_predictions_comparison':{'enabled':bool(reference),'matching_labels':reference_label_agreement,
            'maximum_absolute_probability_difference':max_reference_probability_difference} if reference else None,
        'evaluation_loop_seconds':elapsed,
        'timing_scope':'Evaluation loop includes diagnostics and CSV writing; not a formal stage-level application benchmark.',
        'scope':'Actual Single image core pipeline on labelled patches; not tiled-analysis accuracy or patient-level validation.'})
    (args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2))
    with (args.output_dir/'classification_report.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['class','precision','recall','f1','support'])
        for name,v in summary['per_class'].items():w.writerow([name,v['precision'],v['recall'],v['f1'],v['support']])
    with (args.output_dir/'confusion_matrix.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['true\\pred',*CLASSES]);w.writerows([[c,*row] for c,row in zip(CLASSES,matrix)])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,8));ax.imshow(matrix,cmap='Blues')
    ax.set(xticks=range(9),yticks=range(9),xticklabels=CLASSES,yticklabels=CLASSES,
           xlabel='Predicted class',ylabel='True class',title=f'Application Single image: {args.resize_backend}')
    threshold=max(map(max,matrix))/2
    for i,row in enumerate(matrix):
        for j,value in enumerate(row):ax.text(j,i,str(value),ha='center',va='center',color='white' if value>threshold else 'black')
    fig.tight_layout();fig.savefig(args.output_dir/'confusion_matrix.png',dpi=160);plt.close(fig)
    print(f'Accuracy: {summary["accuracy"]:.8f}\nMacro-F1: {summary["macro_f1"]:.8f}\nOutput: {args.output_dir}',flush=True)

if __name__=='__main__':main()
