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

## Classification modes

Single image classifies the entire uploaded image after resizing it to the
network input. It does not automatically switch to tiling for a large image.

Tiled analysis uses the original-image tile width and height in Preferences,
including when the image fits within one tile. The input summary shows the
planned tile count. Right and bottom edge crops contain their actual pixels;
partial crops are resized without padding or overlap.

The initial setting is 512 x 512 source pixels. It remains editable, and Square
copies the current width to the height once. The classifier's network input is
224 x 224. Source crop size and network input size have different purposes;
changing the source crop changes the scale of tissue presented to the model.
See [model details](MODELS.md#source-scale-and-network-input) before interpreting
results from a new image source.

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

## Segmentation

Select Segmentation with its matching model. The built-in UPerNet path uses its
own classes, palette and overlapping-tile parameters. Classification tile
preferences do not change segmentation settings.

The viewer offers Overlay, Segmentation map and Original image. The initial
blend is 20% for the built-in overlapping UPerNet path. Generic segmentation
results retain their parser's initial blend. Details shows available analysis
parameters.

Pixel coverage is the class's predicted pixel count divided by all original
image pixels. Exclude, background and empty regions remain in the denominator.
The legend follows recorded segmentation class IDs and colours. Missing legacy
counts or artifacts are reported as unavailable.

## Compare and navigate images

Compare with original opens equal source/result panes. They appear side by side
on wider panels and vertically on narrower panels. Link views synchronizes
source coordinates, zoom and pan; clear it for independent navigation.

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

Closing during model validation, inference or PDF export waits for safe worker
cleanup. Avoid terminating the process if a cancellation is still completing.

## History and recorded rerun

History supports image/model keyword searches and local-date filters.
Double-click a row to restore its saved result and original-image thumbnail.
Single-image records show a
label and confidence; tiled records show a tile summary and estimated coverage.

Clear Selection, Esc while the table has focus, or a click on empty table space
deselects all records without closing the displayed result. Ctrl-click also
toggles individual rows; selecting a row alone does not open its result.

Select one record and choose Re-run to use that record's model, task, mode,
source image and saved analysis parameters. Current defaults do not replace
recorded parameters. A successful rerun creates a new record.

Original images and model files must remain available. Missing files prevent
rerun; unavailable saved artifacts limit which legacy views can be restored.

Delete Selected or Delete requests confirmation. Record deletion also removes
associated result artifacts within the application's results directory.
It does not delete original source images or model files.

## Clear the current view

Clear view in the right panel removes the input image, displayed analysis,
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

Preferences controls full paths and the per-tile appendix. Full paths are off
by default; tile details are on. Omitting tile rows preserves complete class
totals and coverage. The export-time model checksum is distinguished from any
checksum actually recorded with the original analysis.

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

Mode changes in Preferences update the input panel and startup default. Restoring
a history record uses its recorded mode without rewriting that default.
Reset Classification restores Single image, 512 x 512 and Pillow bilinear;
model defaults, theme, history and export preferences are preserved.

Model defaults are saved only after compatibility validation. Moving or deleting
a custom default produces an unavailable status, with no silent model fallback.
See [validation limits](MODELS.md#compatibility-validation) for what the check
does and does not establish.
