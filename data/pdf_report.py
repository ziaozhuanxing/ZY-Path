"""Task-aware PDF presentation of saved results; no model inference is performed."""
from datetime import datetime
import hashlib
from pathlib import Path, PureWindowsPath

from fpdf import FPDF
from PIL import Image

from utils.paths import resource_path
from utils.version import APP_VERSION

DISCLAIMER = "For educational and research use only. Not a clinical diagnosis."


def _safe_pdf_text(value):
    # Unicode is preserved and written with the bundled font when necessary.
    return str(value)


def _filename(value):
    text = str(value or "")
    return PureWindowsPath(text).name if "\\" in text else Path(text).name


def _analysis(metadata):
    return metadata.get("segmentation_analysis") or metadata.get("classification_analysis") or {}


def _is_tiled(metadata):
    return (metadata.get("classification_mode") == "tiled_analysis"
            or (metadata.get("classification_analysis") or {}).get("mode") == "classification_tiles")


class _ReportPDF(FPDF):
    def __init__(self, logo_path=None, checkpoint=None):
        super().__init__(format="A4")
        self.checkpoint = checkpoint or (lambda: None)
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=18)
        self.alias_nb_pages()
        self.logo = None
        if logo_path is not None:
            with Image.open(logo_path) as source:
                self.logo = source.convert("RGBA")
                self.logo.thumbnail((96, 96), Image.Resampling.LANCZOS)

    def text_font(self, text="", style="", size=9):
        try:
            str(text).encode("latin-1")
            self.set_font("Helvetica", style, size)
        except UnicodeEncodeError:
            if "reportunicode" not in self.fonts:
                self.add_font("ReportUnicode", fname=str(resource_path("assets/fonts/NotoSansSC-Regular.ttf")))
            self.set_font("ReportUnicode", size=size)

    def header(self):
        title_x = self.l_margin
        if self.logo is not None:
            self.image(self.logo, x=self.l_margin, y=8, h=10)
            title_x += 16
        self.set_xy(title_x, 9)
        self.text_font(style="B", size=16)
        self.cell(self.w - self.r_margin - title_x, 10, "ZY-Path Analysis Report")
        self.set_draw_color(44, 82, 130)
        self.set_line_width(.4)
        self.line(self.l_margin, 23, self.w - self.r_margin, 23)
        self.set_y(27)

    def footer(self):
        self.set_y(-14)
        self.text_font(size=8)
        self.cell(0, 5, f"Page {self.page_no()} / {{nb}} | {DISCLAIMER}", align="C")


def _section(pdf, title, reserve=18):
    if pdf.get_y() + reserve > pdf.page_break_trigger:
        pdf.add_page()
    pdf.set_x(pdf.l_margin)
    pdf.text_font(title, "B", 11)
    pdf.set_text_color(44, 82, 130)
    pdf.cell(pdf.epw, 8, title)
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 8)
    pdf.set_text_color(0)


def _paragraph(pdf, text, size=8.5):
    pdf.set_x(pdf.l_margin)
    pdf.text_font(text, size=size)
    pdf.multi_cell(pdf.epw, 5, str(text), new_x="LMARGIN", new_y="NEXT")


def _height(pdf, text, width, size=9):
    pdf.text_font(text, size=size)
    return pdf.multi_cell(width, 5.5, str(text), dry_run=True, output="HEIGHT")


def _key_values(pdf, rows):
    key_width, value_width = 49, pdf.epw - 49
    for key, value in rows:
        pdf.checkpoint()
        value = str(value if value is not None else "Not recorded")
        height = max(7, _height(pdf, value, value_width - 4) + 2,
                     _height(pdf, key, key_width - 4) + 2)
        if height > pdf.page_break_trigger - 35:
            raise ValueError("A report field is too long to fit on a page.")
        if pdf.get_y() + height > pdf.page_break_trigger:
            pdf.add_page()
        y = pdf.get_y()
        pdf.set_draw_color(210, 218, 226)
        pdf.set_line_width(.15)
        pdf.set_fill_color(240, 244, 248)
        pdf.set_xy(pdf.l_margin, y)
        pdf.text_font(key, "B", 9)
        # Keep labels at the left margin; wrap long labels inside their cell.
        if _height(pdf, key, key_width - 4) <= 5.5:
            pdf.cell(key_width, height, key, border=1, fill=True)
        else:
            pdf.rect(pdf.l_margin, y, key_width, height, style="DF")
            pdf.set_xy(pdf.l_margin + 2, y + 1)
            pdf.multi_cell(key_width - 4, 5.5, key)
        pdf.rect(pdf.l_margin + key_width, y, value_width, height)
        pdf.set_xy(pdf.l_margin + key_width + 2, y + 1)
        pdf.text_font(value, size=9)
        pdf.multi_cell(value_width - 4, 5.5, value)
        pdf.set_xy(pdf.l_margin, y + height)
    pdf.ln(3)


def _add_metadata_table(pdf, metadata):
    """Compact overview, kept callable for existing report integrations."""
    _section(pdf, "Analysis summary")
    mode = metadata.get("classification_mode")
    rows = [("Model name", _filename(metadata.get("model_name", "Not recorded"))),
            ("Task type", metadata.get("task_type", "Not recorded")),
            ("Timestamp", metadata.get("timestamp", "Not recorded")),
            ("Image file", _filename(metadata.get("image_path", "Not recorded")))]
    if mode:
        rows.append(("Classification mode", str(mode).replace("_", " ")))
    if metadata.get("_report_image_size"):
        width, height = metadata["_report_image_size"]
        rows.append(("Image dimensions", f"{width} x {height} pixels"))
    if metadata.get("result_label") is not None:
        rows.append(("Aggregate tile label" if _is_tiled(metadata) else "Result label", metadata["result_label"]))
    if metadata.get("confidence") is not None:
        confidence = float(metadata["confidence"])
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be a number between 0 and 1.")
        rows.append(("Area-weighted mean probability" if _is_tiled(metadata) else "Confidence", f"{confidence:.1%}"))
    _key_values(pdf, rows)


def _image_gallery(pdf, original, result, metadata, color_map=None):
    analysis = _analysis(metadata)
    view = analysis.get("presentation", {}).get("view", "overlay")
    title = ("Classification probabilities" if metadata.get("task_type") == "classification" and not _is_tiled(metadata)
             else {"overlay": "Overlay", "original": "Original image", "color_map": "Class color map",
                   "segmentation_map": "Segmentation map"}.get(view, "Saved result"))
    images = [("Original image", original), (f"Result: {title}", result)]
    # If the saved presentation is already the pure map, do not print an
    # identical third panel. Overlay/original views still receive the map.
    if color_map is not None and view not in {"color_map", "segmentation_map"}:
        if color_map.size != original.size:
            raise ValueError("The class color map must match the source image coordinates.")
        images.append(("Class color map" if _is_tiled(metadata) else "Segmentation map", color_map))
    width = (pdf.epw - 4 * (len(images) - 1)) / len(images)
    frame_height = 60 if len(images) == 3 else 72
    _section(pdf, "Images", reserve=frame_height + 24)
    y = pdf.get_y()
    for index, (caption, image) in enumerate(images):
        x = pdf.l_margin + index * (width + 4)
        pdf.set_xy(x, y)
        pdf.text_font(caption, "B", 8)
        pdf.cell(width, 6, caption)
        top = y + 6
        pdf.set_draw_color(210, 218, 226)
        pdf.set_fill_color(250, 251, 253)
        pdf.rect(x, top, width, frame_height, style="DF")
        # Equal frames and the same scale for spatial images. Limit enlargement
        # of small sources to 72 dpi; preserve aspect ratio in every panel.
        scale = min((width - 2) / image.width, (frame_height - 2) / image.height, 25.4 / 72)
        w, h = image.width * scale, image.height * scale
        pdf.image(image, x=x + (width - w) / 2, y=top + (frame_height - h) / 2, w=w, h=h)
        pdf.set_xy(x, top + frame_height)
        pdf.text_font(size=7)
        pdf.cell(width, 5, f"{image.width} x {image.height} px")
    pdf.set_xy(pdf.l_margin, y + frame_height + 14)
    if (metadata.get("task_type") == "segmentation" or _is_tiled(metadata)) and color_map is None:
        _paragraph(pdf, "A separate class color map is unavailable for this saved result.")


def _table(pdf, title, headers, rows, widths, colors=None):
    colors = colors or {}

    def heading():
        y = pdf.get_y()
        pdf.set_fill_color(44, 82, 130)
        pdf.set_text_color(255)
        x = pdf.l_margin
        for text, width in zip(headers, widths):
            pdf.set_xy(x, y)
            pdf.text_font(text, "B", 8)
            pdf.cell(width, 7, text, border=1, fill=True)
            x += width
        pdf.set_xy(pdf.l_margin, y + 7)
        pdf.set_text_color(0)

    _section(pdf, title, reserve=23)
    heading()
    for row_index, values in enumerate(rows):
        pdf.checkpoint()
        height = max(7, *(_height(pdf, value, width - 4, 8.5) + 2 for value, width in zip(values, widths)))
        if height > pdf.page_break_trigger - 50:
            raise ValueError("A report table row is too long to fit on a page.")
        if pdf.get_y() + height > pdf.page_break_trigger:
            pdf.add_page()
            _section(pdf, f"{title} (continued)")
            heading()
        y, x = pdf.get_y(), pdf.l_margin
        for column, (value, width) in enumerate(zip(values, widths)):
            color = colors.get((row_index, column))
            pdf.set_draw_color(210, 218, 226)
            pdf.set_line_width(.15)
            pdf.set_fill_color(*(color or ((248, 250, 252) if row_index % 2 == 0 else (255, 255, 255))))
            pdf.rect(x, y, width, height, style="DF")
            if color:
                brightness = .299 * color[0] + .587 * color[1] + .114 * color[2]
                pdf.set_text_color(0 if brightness > 145 else 255)
            pdf.set_xy(x + 2, y + 1)
            pdf.text_font(value, size=8.5)
            pdf.multi_cell(width - 4, 5.5, str(value))
            pdf.set_text_color(0)
            x += width
        pdf.set_xy(pdf.l_margin, y + height)
    pdf.ln(3)


def _statistics(pdf, metadata):
    analysis = _analysis(metadata)
    if not analysis.get("classes"):
        return
    tiled = _is_tiled(metadata)
    size = analysis.get("image_size", metadata.get("_report_image_size", (0, 0)))
    total = size[0] * size[1]
    counts = analysis.get("tile_counts" if tiled else "pixel_counts", [])
    rows, colors = [], {}
    for position, item in enumerate(analysis["classes"]):
        index = item.get("index", position)
        count = counts[index] if 0 <= index < len(counts) else None
        if tiled:
            ratios = analysis.get("area_ratios", [])
            ratio = ratios[index] if 0 <= index < len(ratios) else None
        else:
            ratio = count / total if count is not None and total else None
        rgb = tuple(item["color"])
        rows.append((item["label"], f"RGB={list(rgb)}", f"{count:,}" if count is not None else "Unavailable",
                     f"{ratio:.2%}" if ratio is not None else "Unavailable"))
        colors[(position, 1)] = rgb
    _table(pdf, "Class statistics", ("Class", "Color (RGB)", "Tiles" if tiled else "Pixels",
                                    "Estimated coverage" if tiled else "Pixel coverage"),
           rows, (61, 43, 26, pdf.epw - 130), colors)
    _paragraph(pdf, "Coverage is estimated from tile classes and actual crop areas, including partial edge tiles; it is not pixel segmentation."
               if tiled else "Predicted class pixels / full image pixels; background and excluded labels included.")


def _fingerprint(path, checkpoint=None):
    if not path:
        return "Unavailable (model file not provided)"
    try:
        digest = hashlib.sha256()
        with Path(path).open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                if checkpoint is not None:
                    checkpoint()
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return "Unavailable (model file not accessible at export)"


def _details(pdf, metadata, options):
    analysis = _analysis(metadata)
    presentation = analysis.get("presentation", {})
    if analysis:
        pdf.add_page()
    _section(pdf, "Analysis details")
    rows = [("Software version at export", f"ZY-Path {APP_VERSION}"),
            ("Exported at", datetime.now().astimezone().isoformat(timespec="seconds"))]
    if options.get("record_id") is not None:
        rows.append(("History record", f"#{options['record_id']}"))
    if options.get("include_full_paths", False):
        rows.extend([("Image path", metadata.get("image_path", "Not recorded")),
                     ("Model path", metadata.get("model_path", analysis.get("model_path", "Not recorded")))])
    rows.extend((label, analysis[key]) for key, label in (
        ("preprocess", "Preprocessing"), ("input_size", "Network input"),
        ("tile_size", "Original-image tile size"), ("tile", "Original-image tile size"),
        ("stride", "Tile stride"), ("resize_backend", "Resize method"),
        ("edge_policy", "Edge crop policy"), ("area_denominator", "Coverage denominator"),
        ("device", "Inference device")) if key in analysis)
    if analysis:
        rows.extend([("Result view", presentation.get("view", "overlay")),
                     ("Overlay opacity", presentation.get("opacity", analysis.get("overlay_default_opacity", .4 if _is_tiled(metadata) else .2)))])
    if _is_tiled(metadata):
        rows.extend([("Analysis", "Classification tiles (not pixel segmentation)"),
                     ("Tile numbers", "Shown" if presentation.get("tile_numbers", False) else "Hidden"),
                     ("Scale matching", "Uploaded-image physical scale matching has not been verified."),
                     ("Summary", "Area-weighted mean probabilities; coverage estimated from tile classes")])
    model_path = metadata.get("model_path", analysis.get("model_path"))
    recorded_hash = metadata.get("model_sha256", analysis.get("model_sha256"))
    rows.extend([("Model SHA-256 (recorded)", recorded_hash or "Not recorded for this analysis"),
                 ("Model file SHA-256 at export", _fingerprint(model_path, pdf.checkpoint))])
    _key_values(pdf, rows)
    _paragraph(pdf, "The file checksum at export identifies the currently accessible model file. It does not establish which file was used for an older analysis.")
    if _is_tiled(metadata):
        if options.get("include_tile_details", True):
            pdf.add_page()
            _table(pdf, "Tile details", ("Tile #", "Source crop (x0, y0, x1, y1)", "Class", "Confidence"),
                   [(str(i), str(tile["box"]), tile["label"], f"{tile['confidence']:.2%}")
                    for i, tile in enumerate(analysis.get("tiles", []), 1)], (17, 94, 27, pdf.epw - 138))
        else:
            _paragraph(pdf, "Per-tile details were omitted by the selected PDF export option. Class statistics retain all tiles.")


def write_report(destination, original_path, result_path, metadata, *, options=None, color_map=None, progress=None):
    options = options or {}
    progress = progress or (lambda message, percent: None)
    progress("Preparing images", 10)
    metadata = dict(metadata)
    with Image.open(original_path) as image:
        original = image.convert("RGB").copy()
    with Image.open(result_path) as image:
        result = image.copy()
    metadata["_report_image_size"] = list(original.size)
    analysis = _analysis(metadata)
    if analysis.get("image_size") and list(original.size) != list(analysis["image_size"]):
        raise ValueError("Saved analysis and source image must share pixel coordinates.")
    if (metadata.get("task_type") == "segmentation" or _is_tiled(metadata)) and result.size != original.size:
        raise ValueError("The saved spatial result must match the source image coordinates.")
    logo = resource_path("assets/logo.png")
    stage = ["Generating report", 30]
    pdf = _ReportPDF(logo if logo.is_file() else None,
                     checkpoint=lambda: progress(*stage))
    progress(*stage)
    pdf.add_page()
    _add_metadata_table(pdf, metadata)
    _image_gallery(pdf, original, result, metadata, color_map)
    _statistics(pdf, metadata)
    stage[:] = ["Preparing analysis details and model checksum", 60]
    progress(*stage)
    _details(pdf, metadata, options)
    progress("Saving PDF", 90)
    pdf.output(str(destination))
