"""Plain-language help and availability messages for model/image input controls."""

from dataclasses import dataclass
from html import escape

from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QTextBrowser,
    QVBoxLayout,
)

from core.spatial_sampling import source_tile_size
from ui.explicit_combo_box import ExplicitComboBox


@dataclass(frozen=True)
class ScaleReadiness:
    available: bool
    reasons: tuple[str, ...]
    tile_size: tuple[int, int] | None = None

    def explanation(self, language="en"):
        chinese = language == "zh"
        if self.available:
            return ("图片 MPP 和模型组织视野均已知，可以启用尺度匹配。"
                    if chinese else "Ready: image MPP and the model's tissue field are known.")
        messages = {
            "no_image": ("Upload an image first.", "请先上传图片。"),
            "no_profile": ("The model has no input settings. Open Model input to configure it.", "模型尚无输入配置，请打开 Model input 设置。"),
            "whole_image": ("This model uses whole-image inputs; patch-scale matching does not apply.", "该模型按整张图片分析，不适用分块物理尺度匹配。"),
            "no_field": ("The model's physical tissue field is not specified. Existing pixel settings remain in use; entering image MPP alone cannot enable matching.", "模型没有已确认的组织物理视野，继续使用原有像素流程。只填写图片 MPP 也不能开启匹配。"),
            "no_mpp": ("Image MPP is unknown. Use Image scale if you have its known MPP; otherwise keep pixel settings.", "图片 MPP 未知。如果有可靠数值，可在 Image scale 填写；否则保留像素流程。"),
            "calibration_error": ("Image calibration needs correction. See the calibration message below.", "图片校准信息有错误，请查看下面的具体说明并更正。"),
            "geometry": ("The requested field cannot be sampled safely. Check image MPP and the model field.", "当前数值无法形成有效的取样区域，请核对图片 MPP 和模型视野。"),
        }
        prefix = "暂不可用：" if chinese else "Matching unavailable:"
        return prefix + "\n" + "\n".join(messages[reason][1 if chinese else 0] for reason in self.reasons)


def scale_readiness(profile, calibration, *, has_image, calibration_error=""):
    reasons = []
    if not has_image:
        reasons.append("no_image")
    if profile is None:
        reasons.append("no_profile")
    elif profile.input_scope != "patch":
        reasons.append("whole_image")
    elif profile.field_um is None:
        reasons.append("no_field")
    if has_image:
        if calibration_error:
            reasons.append("calibration_error")
        elif calibration is None or calibration.mpp is None:
            reasons.append("no_mpp")
    tile = None
    if not reasons:
        try:
            tile = source_tile_size(profile, calibration)
        except ValueError:
            reasons.append("geometry")
    return ScaleReadiness(not reasons, tuple(reasons), tile)


HELP_TEXT = {
    "en": {
        "scale": (
            "Physical scale matching",
            "<p>This keeps <b>the amount of tissue in a model input</b> consistent, even when images have different pixel sizes. It is separate from stain or colour processing.</p>"
            "<p>Matching needs two facts: <b>image MPP</b> (micrometres covered by one image pixel) and <b>model tissue field</b> (physical width and height represented by one training patch). Neither is inferred from the image filename or from cell appearance.</p>"
            "<p><b>Why can the checkbox be unavailable?</b> The current reason is shown below. An image can have known MPP while the model field is still unknown. Entering MPP does not establish the model field.</p>"
            "<p><b>Example for the built-in CRC classifier:</b> its field is 112 x 112 micrometres. At 0.5 MPP a field uses 224 x 224 source pixels; at 0.252 MPP it uses about 444 x 444. These values are not a segmentation preset.</p>"
            "<p>For a patch classifier, choose <b>Tiled analysis</b> to analyse a larger image. Physical-mode Single image must contain exactly one model field. Matching is optional; leaving it off keeps the configured pixel workflow.</p>"
            "<p><b>The supplied UPerNet segmentation model:</b> its inference code specifies 1000-pixel crops, stride 512 and a 224-pixel network input, but does not establish a physical field. Those pixel settings are retained. No target MPP is guessed.</p>"
        ),
        "image": (
            "Image scale: what to enter",
            "<p><b>Image scale describes the picture, not the model.</b> MPP means micrometres per pixel. For example, at 0.5 MPP each pixel covers 0.5 micrometres along that axis.</p>"
            "<ul><li><b>Use MPP from file:</b> use the explicit calibration already read from this image or its companion calibration file. This option is unavailable when the file has no usable MPP.</li>"
            "<li><b>Enter known MPP:</b> type the value from acquisition/export information. You can select all text in the number box and type a decimal such as 0.252. Examples are not suggested values for your image.</li>"
            "<li><b>MPP unknown:</b> leave it unspecified and continue with pixel settings. Do not guess from image width, print DPI or a 20x/40x label.</li></ul>"
            "<p><b>X / Y</b> mean horizontal / vertical. With <b>Same MPP</b> selected, enter X once; Y follows and cannot be edited separately. Uncheck it only when the source specifies different values for the two axes.</p>"
            "<p><b>Apply to this image</b> uses your selection for the current image; it does not rewrite its pixels or metadata. <b>Cancel</b> keeps the previous selection. A new image does not inherit manual MPP from this one.</p>"
            "<p>Cropping without resizing retains MPP. Resizing changes it, so use calibration for the actual exported image. The 0.252 MPP verified for one SVS does not automatically apply to other pictures.</p>"
            "<p>Recording MPP does not automatically enable matching: the model's tissue field must also be known. Use the matching help for that requirement.</p>"
        ),
        "model": (
            "Model input: what the settings mean",
            "<p><b>Model input describes the model's requirements, not the image's MPP.</b> Built-in requirements are shown for reference and do not need editing. Local models can save their own settings without modifying weights.</p>"
            "<ul><li><b>Class labels:</b> one name per output, in the original output order. The number of names must match the model.</li>"
            "<li><b>Network input size:</b> width and height of the small pixel image entering the model. 224 x 224 is a pixel size, not a physical field.</li>"
            "<li><b>Normalisation:</b> raw255 keeps values from 0 to 255; imagenet divides by 255 and applies ImageNet mean/std. Custom requires the actual multiplier, means and standard deviations. Embedded passes raw float32 pixels to a model that performs normalisation internally.</li>"
            "<li><b>Image reader / resize method:</b> use the same decoding and interpolation as the documented inference or validation process.</li>"
            "<li><b>Whole image / tissue patch:</b> whether a model input represents a complete picture or a local tissue region.</li>"
            "<li><b>Expected tissue field:</b> width and height in micrometres of one training patch. Leave both unspecified when not documented. Do not enter source-image MPP in these boxes.</li>"
            "<li><b>Source crop / stride:</b> the reference crop size and distance between crops. A smaller stride creates overlap for tiled segmentation.</li>"
            "<li><b>Edge policy:</b> Skip excludes incomplete fields; Reflect pads a small crop with reflected border pixels; Resize partial crops retains the legacy pixel-mode behaviour.</li>"
            "<li><b>Output:</b> logits are converted to probabilities once; probabilities are used directly and validated.</li></ul>"
            "<p><b>Import settings file</b> reads a model profile JSON for these weights. <b>Save model settings</b> validates the fields and writes a companion settings file. Changing the model weights makes its old settings invalid. Input compatibility does not establish prediction accuracy.</p>"
            "<p>Saving a model field does not provide calibration for a picture. Enter or inspect the picture's MPP in <b>Image scale</b>.</p>"
        ),
    },
    "zh": {
        "scale": (
            "物理尺度匹配是什么",
            "<p>作用是让模型每次看到<b>相同大小的组织范围</b>，即使不同图片的像素大小不同。它与染色、颜色处理是分开的。</p>"
            "<p>需要两份信息：<b>图片 MPP</b>（这张图一个像素对应多少微米），以及<b>模型组织视野</b>（训练时一块图代表的实际组织宽度和高度）。不能凭文件名、细胞外观或单纯的像素宽高推断。</p>"
            "<p><b>为什么无法勾选？</b>下面会列出当前缺少什么。图片有 MPP，不代表模型的视野就已知；只填写图片 MPP，不能补出模型的训练视野。</p>"
            "<p><b>内置 CRC 分类模型的例子：</b>模型每块看 112 × 112 微米。图片为 0.5 MPP 时，对应原图 224 × 224 像素；为 0.252 MPP 时，约为 444 × 444 像素。这不是分割模型的通用设置。</p>"
            "<p>较大的分类图片通常选择 <b>Tiled analysis</b>。开启匹配时，Single image 必须恰好是一块模型视野。不开启匹配，继续按原有像素设置运行。</p>"
            "<p><b>当前内置 UPerNet 分割模型：</b>收到的推理代码指定了 1000 像素切块、512 像素步长和 224 像素输入，但没有给出可靠的物理视野。因此保留该像素流程，不猜测目标 MPP。</p>"
        ),
        "image": (
            "Image scale：图片尺度怎么填",
            "<p><b>这里描述图片，不是设置模型。</b>MPP 的单位是微米/像素。例如 0.5 MPP，表示沿这一方向，一个像素对应 0.5 微米。</p>"
            "<ul><li><b>Use MPP from file：</b>使用图片或配套校准文件中已有的数值。读不到可靠信息时，这项不可选。</li>"
            "<li><b>Enter known MPP：</b>填写扫描或导出信息中确认的数值。点击数字框，全选后可直接输入小数，例如 0.252。示例数值不是对当前图片的推荐。</li>"
            "<li><b>MPP unknown：</b>不知道就保留未知，继续用像素模式。不要从图片宽高、打印 DPI 或 20×/40× 字样猜。</li></ul>"
            "<p><b>X / Y</b>分别表示横向、纵向。勾选 <b>Same MPP</b> 后，只填 X，Y 自动跟随且不能单独改；只有来源明确给出两轴不同数值时，才取消勾选后分别填写。</p>"
            "<p><b>Apply to this image</b> 将选择用于当前图片，不修改图片像素或原文件元数据；<b>Cancel</b> 不应用这次修改。换一张图片后，不会沿用上一张的手动 MPP。</p>"
            "<p>只裁剪、不缩放，MPP 不变；缩放过的导出图，需要用缩放后的校准。某张 SVS 确认的 0.252 MPP 不能直接套给其他图片。</p>"
            "<p>填写 MPP 不等于自动启用尺度匹配；模型的组织视野也必须已知。具体条件见尺度匹配帮助。</p>"
        ),
        "model": (
            "Model input：模型输入配置是什么",
            "<p><b>这里描述模型需要什么，不是填写图片 MPP。</b>内置模型的要求只供查看，无需修改。本地模型可以保存自己的配置，不改变权重。</p>"
            "<ul><li><b>Class labels：</b>类别名称，顺序必须与模型输出相同；数量也必须一致。</li>"
            "<li><b>Network input size：</b>送入模型的小图宽、高，单位是像素。224 × 224 像素不等于实际组织视野。</li>"
            "<li><b>Normalisation：</b>raw255 保留 0–255；imagenet 先除以 255，再用 ImageNet 均值和标准差处理。Custom 必须填写真实的乘数、均值和标准差；Embedded 表示模型内部已经做归一化，外部不重复做。</li>"
            "<li><b>Image reader / resize method：</b>图片读取和缩放方式，应与训练验证或配套推理代码一致。</li>"
            "<li><b>Whole image / tissue patch：</b>模型一次分析整图，还是局部组织块。</li>"
            "<li><b>Expected tissue field：</b>一块训练图对应的实际组织宽、高，单位是微米。没有可靠记录就都留空；不要在这里填图片 MPP。</li>"
            "<li><b>Source crop / stride：</b>参考切块大小和移动步长；步长较小会使分割处理区域重叠。</li>"
            "<li><b>Edge policy：</b>Skip 跳过不足一块的边缘；Reflect 用镜像像素补边；Resize partial crops 保留旧像素流程的边缘缩放方式。</li>"
            "<li><b>Output：</b>logits 需要转为概率；probabilities 已经是概率，不能重复转换。</li></ul>"
            "<p><b>Import settings file</b> 读取这份权重对应的 JSON 配置；<b>Save model settings</b> 校验后保存配套配置文件。更换权重后，旧配置不能直接沿用。输入兼容检查不等于验证准确率。</p>"
            "<p>模型视野不能代替图片校准；图片 MPP 要到 <b>Image scale</b> 查看或填写。</p>"
        ),
    },
}


def configure_help_window(dialog):
    # Windows' default context-help cursor needs per-widget WhatsThis handlers.
    # Use a labelled, working Help action instead of a nonfunctional title-bar '?'.
    dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)


class InputHelpDialog(QDialog):
    def __init__(self, topic, parent=None, *, readiness=None):
        super().__init__(parent)
        configure_help_window(self)
        self.setWindowModality(Qt.WindowModal)
        self.topic, self.readiness = topic, readiness
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Help language / 帮助语言", self))
        self.language = ExplicitComboBox(self)
        self.language.addItem("English", "en")
        self.language.addItem("简体中文", "zh")
        self.language.setCurrentIndex(1 if QLocale.system().language() == QLocale.Chinese else 0)
        row.addWidget(self.language)
        row.addStretch()
        layout.addLayout(row)
        self.browser = QTextBrowser(self)
        self.browser.setOpenExternalLinks(False)
        layout.addWidget(self.browser, 1)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Close, self)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.language.currentIndexChanged.connect(self.refresh)
        self.refresh()
        available = self.screen().availableGeometry()
        self.resize(min(660, max(320, available.width() - 40)), min(590, max(300, available.height() - 80)))

    def refresh(self, *unused):
        language = self.language.currentData()
        title, body = HELP_TEXT[language][self.topic]
        self.setWindowTitle(title)
        if self.readiness is not None:
            heading = "当前状态" if language == "zh" else "Current status"
            body += "<h3>" + heading + "</h3><p>" + escape(self.readiness.explanation(language)).replace("\n", "<br>") + "</p>"
        self.browser.setHtml("<h2>" + title + "</h2>" + body)


def show_input_help(owner, topic, *, readiness=None):
    dialog = getattr(owner, "_input_help_dialog", None)
    if dialog is None:
        dialog = InputHelpDialog(topic, owner, readiness=readiness)
        owner._input_help_dialog = dialog
    else:
        dialog.topic, dialog.readiness = topic, readiness
        dialog.refresh()
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    return dialog
