# User guide

## Start an analysis

1. Select Classification or Segmentation in the input panel.
2. Use the task's built-in model, or clear Use Built-in Model and browse to a
   trusted supported model. Wait for validation.
3. Choose Upload Image. PNG, JPEG, TIFF and BMP raster images are supported.
4. For Classification, choose Single image or Tiled analysis.
5. Check the model, image dimensions and analysis settings in the input summary,
   then select Run Inference.

The Run Inference button stays below the scrolling input controls. On a small
screen, scroll panels or adjust the dividers to access additional content.
The right-hand session panel identifies the displayed completed result.

Use Built-in Model changes the model source for the next run. A local model
choice is remembered for the current session: selecting built-in hides its
name, and clearing the checkbox restores the local choice and its validation
state. If no local model is selected or it is incompatible with the task, Run
Inference remains unavailable. Browsing and toggling do not change saved
startup defaults; use Settings > Models to save or restore those defaults.
Session continues to identify the model that produced the displayed result.

## Classification modes

Single image classifies the entire uploaded image after resizing it to the
network input. It does not automatically switch to tiling for a large image.

Choose Single image or Tiled analysis under **Task**. In pixel mode, Tiled
analysis uses the saved tile dimensions unless you set an override in
**Image sampling** for the current image. Select **Also save size as default**
to use that size for future images. The summary above **Run Inference** shows
the source crop, model input and planned tile count. Partial edge crops are
handled by the selected model's edge policy.

Run Inference captures the current choices and defaults when the job starts.
Opening a history item shows its saved result. **Re-run record** uses the
selected record's saved parameters. Changing preferences during inference
affects subsequent runs.

The initial setting for new preferences is 224 x 224 source pixels. Existing
custom dimensions are kept. It remains editable, and Square
copies the current width to the height once. The classifier's network input is
224 x 224. Source crop size and network input size have different purposes;
changing the source crop changes the scale of tissue presented to the model.
See [model details](MODELS.md#source-scale-and-network-input) before interpreting
results from a new image source.

OpenCV linear is the default classification resize. New analyses use the
training script's OpenCV colour reader, RGB ordering and, for the built-in
model, raw255 values. The previous Pillow default is upgraded once; you can
explicitly select legacy Pillow afterwards. Old history keeps its old reader
and backend. Training-time random augmentation is not applied during inference.

The result opens as an Overlay. Use the view menu for Class color map or
Original image. Opacity changes the blend; Tile boundaries and Tile numbers
show the recorded crop geometry and identifiers.

### Inspect individual crops

Click a tile in either image pane to display its original crop, coordinates,
class, confidence and dimensions. The corresponding Tile details row is
outlined. Clicking a row locates the same crop in the image. Previous and Next
navigate crops; Clear removes the temporary inspection.

Dragging pans instead of selecting a tile. On short result panels, the image
page and crop description scroll. The inspection highlight is temporary: it
does not change predictions, statistics, saved masks or exported pixels.

### Read classification statistics

The compact legend includes every recorded class, including zero counts.
Tile details opens a resizable drawer with the tile table and Class details
(RGB). Tables are read-only and support keyboard scrolling.

- Tile count assigns one count to each crop, including a partial crop.
- Estimated coverage assigns the predicted class to each crop's actual area
  and divides by the full image area.
- The stored aggregate class and probability use area-weighted mean tile
  probabilities. They are not a separate whole-image prediction.

Estimated tile coverage is different from segmentation pixel coverage.
Confidence is a model output probability, not a measured probability that a
pathological diagnosis is correct.

## Model inputs and image scale

Open **Input & scale → Image sampling…** to review the image's MPP, the
model's requirements and the planned sampling together. A live preview shows
the source crop, network input and number of regions before you apply them.
**Model requirements…** views a built-in model's requirements or saves a local
model's input profile without changing its weights.
Select **Match tissue scale** when the selected model has a documented tissue
field and the image has known MPP. The source crops are then calculated from
physical field rather than the pixel dimensions in Preferences. Otherwise use
pixel mode. New images do not inherit another image's manual MPP.

If the image has no calibration, enter its known MPP or leave it unknown and
use **Pixel settings**. When matching requires tiling, the preview explains
that applying the plan switches the current image to Tiled analysis.
**Cancel** discards image and sampling edits.
On a small window, the numerical preview stays visible while the form scrolls;
the illustration appears when there is enough vertical space.

For calibrated patch classification, select Tiled analysis. Single image must
contain exactly one expected physical field. Skipped edge strips are recorded
as unanalysed and retain their original pixels in overlays. The result page
shows analysed and unanalysed percentages above the class summary.

**Cover borders with full-sized regions** is an optional sampling choice for
patch classification. It moves complete border crops inward instead of
stretching partial crops or inventing padding. Border crops can overlap; the
overlap is divided at the midpoint between region centres so every source pixel
contributes to area statistics once. Tile details show the full model crop;
grid lines and clicking use the assigned area. An image smaller than one complete
field still cannot use this mode. This option does not change model weights,
preprocessing, MPP or the model's reference tissue field. Matching physical
field alone does not establish suitability for a different tissue or stain.

Recorded model
profiles and calibration are retained by history, Re-run and reports.
See [input profiles](INPUT_PROFILES.md) for local model formats and supported
contracts. The built-in segmentation reference has no established physical
field; it does not assume a target MPP from the classification dataset.

## Segmentation

Select Segmentation with its matching model. The built-in UPerNet path uses its
own classes, palette and overlapping-tile parameters. Classification tile
preferences do not change segmentation settings.

The viewer offers Overlay, Segmentation map and Original image. The initial
blend is 20% for the built-in overlapping UPerNet path. Generic segmentation
results retain their parser's initial blend. Details shows available analysis
parameters.

Segmentation tiles in the status bar counts the segmentation processing
regions, which can overlap. It does not indicate classification analysis;
classification uses a separate Classification tiles progress label. The
built-in segmentation region size and stride are independent of classification
tile preferences.

Pixel coverage is the class's predicted pixel count divided by all original
image pixels. Exclude, background and empty regions remain in the denominator.
The legend follows recorded segmentation class IDs and colours. Missing legacy
counts or artifacts are reported as unavailable.

## Compare and navigate images

Compare with original opens equal source/result panes. They appear side by side
on wider panels and vertically on narrower panels. **Link views** synchronizes
source coordinates, zoom and pan with one shared toolbar. Turn it off to show
independent controls in each pane.

Use the mouse wheel or + / - to zoom, drag to pan, Fit to fit the image, and 1:1
for one source pixel per physical display pixel. Fit reports its actual scale;
it is not necessarily 100%. Grid lines, tile numbers and inspection outlines
follow the same image coordinate transform.

Wheel zoom follows the pointer and respects small wheel/trackpad movements;
horizontal-only gestures do not change magnification. Linked panning updates
the other image without resetting the view being dragged. Drag the comparison
divider to preview its position, then release to resize the image panes. A
zoomed view keeps its source center and scale; Fit recomputes a common scale
for the available panes.

The main window supports normal, minimized and maximized states. Saved geometry
is checked against the current screen's available area. Reset Panel Layout in
Preferences restores panel proportions and image fitting.

## Cancel safely

During inference, Cancel inference replaces Run Inference. Cancellation waits
for the current model operation to finish, then discards the partial result.
Inputs remain locked while Cancelling is displayed. Previous completed results
remain available, and cancelled work does not add a history record.

Image selection decodes and verifies the file in the background. A newer
selection replaces a pending one. Model loading/validation and normal inference
result rendering, checksums and persistence also run on workers. Saving may take
a little longer than the model calculation. Cancellation before the history
commit removes this run's incomplete output; a completed commit wins over a
late cancellation and remains available as a saved result.

The input thumbnail is limited to 2048 pixels on its longest side. Sampling
continues to use original decoded dimensions and MPP, not thumbnail dimensions.
An estimated raster working-memory budget of 1536 MiB is checked before decoding;
segmentation fusion and retained class scores are budgeted separately as well.
This is a conservative application limit, not a promise about free RAM or model
activation memory. If a file exceeds it, export a smaller native-resolution ROI
with calibration; reducing image dimensions changes MPP. Whole-slide streaming
is not supplied by the ordinary image loader.

Closing during image loading, model validation, inference or PDF export waits for safe worker
cleanup. Avoid terminating the process if a cancellation is still completing.

## History and recorded rerun

Opening a record verifies and decodes its saved files in the background. The
last selected record wins when you switch quickly; an older task cannot replace
a newer view. The previous completed result stays visible while loading and
exports are disabled until the selection is resolved. **Cancel loading** keeps
the previous view. Clearing the view or deleting a record cancels pending loading.


New results record SHA-256 checksums for their saved result image, masks, labels
and metadata sidecar. History display and exports reject missing or changed
artifacts while retaining the database record and original input. Legacy records
remain accessible with a notice that output integrity was not recorded; they are
not silently relabelled as verified. File checksums detect accidental replacement
or corruption, not tampering by someone who can also rewrite the database.


History supports image/model keyword searches and local-date filters.
Double-click a row to restore its saved result and original-image thumbnail.
Single-image records show a
label and confidence; tiled records show a tile summary and estimated coverage.

Deselect rows, Esc while the table has focus, or a click on empty table space
deselects all records without closing the displayed result. Ctrl-click also
toggles individual rows; selecting a row alone does not open its result.

Select one record and choose **Re-run record** to use that record's model, task, mode,
source image and saved analysis parameters. Current defaults do not replace
recorded parameters. A successful rerun creates a new record.

Original images and model files must remain available. Missing files prevent
rerun; unavailable saved artifacts limit which legacy views can be restored.

Delete Selected or Delete requests confirmation. Record deletion also removes
associated result artifacts within the application's results directory.
It does not delete original source images or model files.

## Clear the current view

**Clear current view** in the right panel removes the input image, displayed analysis,
session details and history selection. Saved records and files, model choices,
analysis preferences and history filters are kept. Select another image to
start again, or open a saved record from History. Finish or cancel active
inference or PDF export before clearing the view.

## Export

Export PNG saves the selected full-resolution result presentation. Spatial
results also produce a .png.json sidecar with recorded task/model and analysis
information. Comparison panes are a viewing arrangement, not a combined PNG.

Export PDF includes source/result panels, the available class map, coloured
statistics, image dimensions and analysis details. A selected pure map is not
repeated in another panel. Missing legacy colour maps are identified explicitly.
The bundled report font preserves Chinese filenames without a font download.

Settings > Preferences > Export > PDF image quality offers **Standard** (default)
and **Original resolution** for classification and segmentation. Standard sizes
report images to their page panels at up to 300 DPI. Large photographs and
overlays use high-quality JPEG; class maps use nearest-neighbour resizing and
lossless encoding, and probability charts remain lossless. Small images are not
enlarged. Original resolution embeds the full image pixel dimensions with
lossless encoding and can produce substantially larger files. Choose it when
you need to inspect fine image details. The report identifies the selected
quality; source dimensions still describe the original image. This affects PDF
display copies only: PNG exports, source files, predictions, class colours,
coverage, tile details and saved history are unchanged. Already exported PDFs
must be exported again to use the new setting. File size and online-preview
availability depend on the image content, appendix length and preview service.

Session names wrap inside the right panel, including long unbroken filenames.
Select and copy a value or hover for its complete text; long names do not widen
the export buttons.

Preferences controls full paths and the per-tile appendix. Full paths are off
by default; tile details are on. Omitting tile rows preserves complete class
totals and coverage. The export-time model checksum is distinguished from any
checksum actually recorded with the original analysis.

PNG export also runs verification, presentation rendering and file writes in the
background, with progress and Cancel. It produces a matching `.png` / `.png.json`
pair. The PNG embeds an export ID; the JSON records that ID and the exported
PNG's SHA-256. The export metadata is a snapshot of the selected presentation.
Changing a later view does not change a running export.

Both files are completely staged before the old destinations are replaced.
Cancellation before commit leaves the previous pair unchanged. A normal commit
failure restores the old pair. If filesystem permissions prevent rollback,
the error names a recovery folder containing backup copies and transaction.json;
keep it until recovery is complete. Two separate file replacements cannot be
made atomic against sudden power loss; an interrupted commit leaves its recovery
folder available. Do not discard that folder or treat a mismatched pair as a
complete export. The completed PNG/JSON identity can be checked with
`data.png_bundle.verify_png_bundle`.

PDF generation runs in the background with progress and Cancel. An existing
destination is replaced only when the new report is complete. After saving,
Open export offers Open PDF and Open folder.

## Settings

| Page | Controls |
|---|---|
| Appearance | Light and Dark themes |
| Preferences | Export reminders/options, classification mode, tile dimensions, resize guide, class palettes and panel layout |
| Models | Separate validated classification/segmentation defaults and restore built-in controls |
| Guide & Support | Workflow guidance and contact information |
| System Information | Runtime versions and inspectable configuration; copy copies the displayed text |
| About | Version, developer, contact information and intended use |

The classification startup mode in Preferences applies at the next launch.
The Task selector changes the working mode during the current session.
Reset Classification restores the startup defaults of Single image, 224 x 224
and OpenCV linear. Model defaults, theme, history and export preferences are preserved.

Model defaults are saved only after compatibility validation. Moving or deleting
a custom default produces an unavailable status, with no silent model fallback.
See [validation limits](MODELS.md#compatibility-validation) for what the check
does and does not establish.


### Model validation details

Settings > Models shows the last validated input dimensions, output task/class
count, declared class order, normalization, reader/resize and physical field.
A model profile supplies its input geometry; the fallback compatibility probe is
224 x 224 RGB only when no profile is supplied. Supported local model profiles
are not restricted to nine classes. A successful compatibility probe does not
measure accuracy, prove class-label meaning or establish suitability for a tissue
or stain. Missing physical fields remain unspecified.
