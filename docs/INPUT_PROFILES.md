# Model inputs and image calibration

Model weights, their input requirements and the calibration of an image are
separate objects. A model input profile describes the boundary tensor and
sampling policy. Image calibration describes the actual source pixels. The
application combines them only when physical matching is explicitly enabled.

## Using physical matching

1. Select a model and upload an image.
2. **Model input…** shows the selected model's requirements. **Image scale…**
   shows file calibration or accepts known X/Y MPP for the displayed image.
   Values entered for one image do not become defaults for another image.
3. Enable **Match physical scale** when both source MPP and a documented model
   tissue field are available. Otherwise pixel mode remains available.
4. A patch classifier normally uses **Tiled analysis**. Single image in physical
   mode requires exactly one complete model field; a larger image is not silently
   compressed into that field.

The checkbox displays its current availability reason next to the controls.
**Help** beside it opens an explanation with the current missing requirements;
the help window offers English and Simplified Chinese. Incomplete matched
Single image fields are identified before Run is enabled. Selecting Tiled
analysis or correcting the image calibration updates the run state immediately.

In **Image scale**, **Use MPP from file** is available only when calibration was
found. Otherwise choose **MPP unknown — keep pixel settings**, or enter a
known manual value. With **Same MPP** selected, Y follows X and cannot be edited
separately. **Apply to this image** applies the selection to the current input;
it does not rewrite the image. Cancel leaves the previous selection unchanged.

Built-in **Model input** windows are view-only and offer **Close** and **Help**.
They do not show inactive Save/Import controls. A local-model editor provides
**Save model settings** and **Import settings file (JSON)**; custom multiplier,
mean and standard-deviation fields appear only for custom normalisation.
For a model not yet validated, an explanatory import window identifies the
settings JSON and provides **Import and validate**. Settings JSON is neither
a weight file nor an image. Both input windows have functioning Help buttons
in place of Windows' unused title-bar context-help cursor.

The known CRC checkpoint is identified by its SHA-256, not by its filename or
architecture. Its documented field is 112 x 112 um, corresponding to 224 pixels
at nominal 0.5 um/px. Source tile dimensions are `round(field_um / source_mpp)`
on each axis. A 0.252 MPP source therefore uses 444 x 444 original pixels. The
effective network sampling is 0.4995 MPP, including integer rounding. These
values belong to this model, not to all classifiers or segmenters.

The built-in UPerNet reference adapter retains the supplied 1000-pixel crops,
512-pixel stride, Pillow bilinear 224-pixel input, ImageNet normalisation and
Hann-weighted overlap fusion. Its physical field is not established by the
available inference code. No guessed MPP or automatic physical resampling is
assigned to it. UPerNet multiscale features are not an image-calibration reader.
Its automatic reference profile is bound to the weight SHA-256 recorded in the
user's native Windows resource manifests, not to an architecture or filename.
An unrecognized UPerNet state dictionary requires its own profile; it does not
inherit the built-in tissue classes or preprocessing.

## Configuring a local model

**Model input…** edits an input profile without modifying weights. It saves
`<model filename>.zypath-model.json` beside the model, for example
`classifier.pth.zypath-model.json`. Ordered labels must match its output count
and any labels declared in its checkpoint. Import supports the same JSON schema.
For a model that fails the legacy 224-pixel validation probe, use **Model input…**
to import its documented profile first, then validate it again.

Profiles are associated with the model file SHA-256. Replacing a model or editing
its profile requires revalidation. A checkpoint may instead contain the same
dictionary under `zypath_input_profile`; omit its `model_sha256` there, since an
embedded object cannot contain its own enclosing file's checksum. The loader
binds it to the actual file. Conflicting embedded/external profiles are rejected.

The supported boundary is an RGB float32 NCHW tensor. Input sizes and class
counts are configurable. Standard adapters support mutually exclusive
classification `(N,C)` and segmentation `(N,C,H,W)` tensors, or an object exposing
`.logits`. Outputs must declare logits or probabilities; probabilities are
validated and are not softmaxed twice. Single-logit binary, multilabel, arbitrary
multi-output and non-RGB model contracts require additional adapters. A bare
state dictionary still requires a reconstructable supported architecture.

Normalisation options are `raw255`, `imagenet`, `custom` and `embedded`.
`embedded` supplies raw 0–255 float32 pixels without external normalisation;
use it only when that is the model's actual entry contract. `custom` computes
`(pixels * input_scale - mean) / std` per RGB channel. Profile `input_size` is
the tensor size entering the model, including a model that internally resizes.
The software does not infer internal transformations or execute profile code.

This example is a template for a three-class patch classifier, not a claim
about any supplied weights. Replace the checksum and every input setting with
the actual model specification. A null `field_um` disables physical matching.

```json
{
  "schema": "zypath.model-profile.v1",
  "model_sha256": "REPLACE_WITH_THE_MODEL_FILE_SHA256",
  "task_type": "classification",
  "classes": ["class_a", "class_b", "class_c"],
  "input_size": [256, 256],
  "normalization": "imagenet",
  "image_decoder": "pillow_rgb",
  "resize_backend": "pillow_bilinear",
  "input_scope": "patch",
  "field_um": null,
  "tile_size": [256, 256],
  "stride": [256, 256],
  "edge_policy": "skip",
  "pixel_edge_policy": "crop_then_resize",
  "output_kind": "logits",
  "adapter": "standard",
  "note": "Record the actual training/inference specification here."
}
```

For a standard tiled segmenter set `task_type` to `segmentation`, `input_scope`
to `patch`, and supply its actual crop/stride/input settings and ordered labels.
When its physical field is documented, source crop dimensions and overlap are
adapted to image MPP; probabilities are fused before restoring a discrete mask
to source coordinates. `input_scope: image` performs whole-image segmentation.
The UPerNet reference adapter remains separate so its established numerical
path is not changed by generic-adapter development.

## Calibration sources and validation

The reader accepts the native ROI tool's embedded `zypath.calibration` entry
and `.calibration.json`, explicit OME PhysicalSizeX/Y with units, and Aperio MPP.
It does not derive MPP from print DPI, objective power, cell appearance or a
dataset name. Anisotropic X/Y calibration is retained. Decoder EXIF rotation
swaps axes when necessary; manual values refer to the displayed image axes.

An external image-calibration sidecar requires the image checksum and dimensions.
For other calibrated raster images its schema is:

```json
{
  "schema": "zypath.image-calibration.v1",
  "image_sha256": "REPLACE_WITH_THE_IMAGE_FILE_SHA256",
  "image_size_px": [1000, 800],
  "pixel_size_um": [0.25, 0.25],
  "calibration_source": "State the verified export or acquisition source"
}
```

Header inspection in the interface does not decode a whole-slide image. The
existing raster-image interface is not a native whole-slide inference viewer;
use the optional ROI extractor for a bounded source region. Its CRC convenience
recommendation does not replace the selected model's input profile.

## Edges, records and limitations

Physical-mode classification supports complete-field `skip` edges or explicit
`reflect` padding. It does not stretch a partial edge field to a full input.
Skipped edge pixels are unanalysed, retain the original image in overlays and
are recorded separately. Class coverage uses full-image area; mean probabilities
use analysed area. Consequently coverage may sum to less than 100% for skip
edges. Reflect padding introduces synthetic border pixels and must be an
appropriate declared policy. Pixel mode retains a separate configurable edge
policy for legacy behaviour.

History saves the input-profile snapshot, model/image checksums, calibration
source, actual source crops and effective field. Re-run uses those recorded
values and rejects changed model inputs or image bytes. It does not borrow the
current image calibration or settings. Old records without a profile retain
their legacy inference path. PDF/PNG metadata retains the recorded calibration;
an export does not establish new model accuracy.

Resizing does not restore missing source detail. Neither scale matching nor
input-contract validation establishes cross-organ performance or accuracy.
Stain normalisation is not automatically added: it needs its own reproducible,
model-compatible procedure and reference. Training augmentations are not
prediction-time transformations.
