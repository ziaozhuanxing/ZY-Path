# Prepare a calibrated CRC image from a whole slide

The optional `scripts/extract_calibrated_roi.py` tool prepares a native-resolution
PNG for the existing raster-image application. It does not add whole-slide
inference to the main application and does not run a model or generate tissue
labels.

## Scope

The reference is the CRC classifier's documented 224-pixel input at nominal
0.5 micrometres/pixel: 112 micrometres per side. The tool reads both MPP axes
from OpenSlide, calculates the nearest integer source crop for that field and
prepares a grid of complete crops. It never infers MPP from objective power or
print DPI and never silently assumes 0.5 for an unknown source.

For example, a source at 0.252 MPP gives 444-pixel source tiles and a
4440 x 4440 ROI for a 10 x 10 grid. The effective input sampling after resizing
444 to 224 is 0.4995 MPP; the small difference is recorded rather than hidden.
Anisotropic source sampling is handled separately for width and height.

This preset is for the CRC classifier. It does not establish the breast
segmentation model's training field or replace its independent preprocessing.

## Optional Windows dependencies

Install the two pinned packages in a directory outside the application venv.
Pillow and PyQt5 are already present in the application environment. No CUDA,
extra model weights, image-codec build tools or main requirements changes are
needed. The package versions provide Python 3.10/64-bit Windows wheels.

```powershell
$python = "E:\ZY-PATH\.venv\Scripts\python.exe"
$packages = Join-Path $env:LOCALAPPDATA "ZY-Path\wsi-tools-20261107\packages"
& $python -m pip install --target $packages --no-deps --only-binary=:all: --upgrade openslide-python==1.4.7 openslide-bin==4.0.1.2
```

With the repository script available:

```powershell
& $python "E:\ZY-PATH\scripts\extract_calibrated_roi.py" --packages $packages --slide "E:\YOUR_SLIDE.svs" --output-root "E:\ZY-PATH-evidence\calibrated-roi"
```

`--expect-mpp 0.252` can verify a previously inspected source. It is a check,
not a metadata override. If the source differs, extraction stops.

## Selecting a region

1. The tool reads a bounded low-resolution pyramid level for the overview. If
   no suitable level is available, it stops instead of decoding a huge
   full-resolution image as a thumbnail.
2. Click an area containing tissue. The yellow box shows the exact region to
   be read. Moving or resizing the window does not change source coordinates.
3. Choose **Save native ROI**. The region is read from level zero without
   resizing, stain conversion or padding. Near an edge the box is moved inside
   the source. Missing transparent source pixels cause a request to choose
   another region; they are not replaced with invented tissue.
4. The terminal prints the output files and the source-tile dimensions to use
   in the main application's Tiled analysis mode.

Outputs are placed in a new run directory:

- `roi_native.png`: the native-resolution source crop for analysis. Calibration
  is embedded as a versioned `zypath.calibration` PNG text entry.
- `roi_native.png.calibration.json`: source filename/size, level-zero box,
  source sampling, tile recommendation, reference field, effective sampling,
  library versions, tool hash and output PNG checksum.
- `overview_display_only.png`: the overview used for selection. Its role is
  explicitly marked; it is not the native-resolution analysis image.

The original slide is opened for reading. Existing ROI files are not
overwritten. Partial output is cleaned up if writing fails. A source crop is
limited to 25 million pixels; use a smaller `--grid` if necessary.

## Using the ROI in ZY-Path

Upload `roi_native.png`. The application reads its calibration tag and sidecar,
checks dimensions and verifies the PNG checksum at inference. Select the model
appropriate to the intended task. **Match physical scale** uses that model's
documented field, rather than blindly applying this tool's CRC convenience value.
For the known CRC classifier, choose Tiled analysis and enable matching; the
0.252 MPP example produces 100 complete 444-pixel crops. History Re-run retains
the recorded model profile and calibration. See [input profiles](INPUT_PROFILES.md).

For the supplied UPerNet reference, the model's physical field has not been
established, so physical matching is unavailable. The ROI's source MPP remains
visible and recorded; no 0.5 MPP segmentation assumption is made.

Native pixel extraction does not stain-normalise an image or restore detail
absent from a coarse source. A model's accuracy needs independently labelled
tissue regions; manually selecting an ROI is not ground-truth annotation.
Do not infer an independent test cohort solely from a different file folder.

## Noninteractive inspection

`--thumbnail-only` saves the overview and exits. For a known source coordinate,
provide both `--centre-x` and `--centre-y` to save without opening the selector.
`--grid` defaults to 10 and can be set from 1 to 20 within the memory/slide-size
limits. TIFF page numbers are not supplied as OpenSlide levels; the tool reads
native level metadata from the reader and always extracts the ROI at level 0.

Automated checks use synthetic fixtures. Native library integration and an
interactive selector were exercised on a synthetic tiled pyramid in the
development environment. That is not a Windows run or a prediction result on
the user's TCGA slide.
