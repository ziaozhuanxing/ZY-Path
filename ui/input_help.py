"""Plain-language help and availability messages for model/image input controls."""

from dataclasses import dataclass
from html import escape

from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QTextBrowser,
    QVBoxLayout,
)

from ui.language import LANGUAGES, tr, translate_for
from core.spatial_sampling import source_tile_size
from ui.explicit_combo_box import ExplicitComboBox


@dataclass(frozen=True)
class ScaleReadiness:
    available: bool
    reasons: tuple[str, ...]
    tile_size: tuple[int, int] | None = None

    def explanation(self, language=None):
        def display(source):
            return tr(source) if language is None else translate_for(language, source)

        if self.available:
            return display("Ready: image MPP and the model's tissue field are known.")
        messages = {
            "no_image": "Upload an image first.",
            "no_profile": "The model has no input settings. Open Model requirements to configure it.",
            "whole_image": "This model uses whole-image inputs; patch-scale matching does not apply.",
            "no_field": "The model's physical tissue field is not specified; entering image MPP alone cannot enable matching.",
            "no_mpp": "Image MPP is unknown. Use Image sampling if you know it, or keep pixel settings.",
            "calibration_error": "Image calibration needs correction. See the calibration message below.",
            "geometry": "The requested field cannot be sampled safely. Check image MPP and the model field.",
        }
        prefix = display("Matching unavailable:")
        return prefix + "\n" + "\n".join(display(messages[reason]) for reason in self.reasons)


def scale_readiness(profile, calibration, *, has_image, calibration_error=""):
    reasons = []
    if not has_image:
        reasons.append("no_image")
    if profile is None:
        reasons.append("no_profile")
    elif profile.input_scope != "patch":
        reasons.append("whole_image")
    elif profile.matching_field_um is None:
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
            "<p>Open <b>Input and scale → Image sampling</b> to review the image, model and sampling together. The preview updates before anything is applied. For a larger patch-classification image, it selects Tiled analysis automatically; Cancel keeps your previous image settings.</p>"
            "<p>This keeps <b>the amount of tissue in a model input</b> consistent, even when images have different pixel sizes. It is separate from stain or colour processing.</p>"
            "<p>Matching needs two facts: <b>image MPP</b> (micrometres covered by one image pixel) and <b>model tissue field</b> (physical width and height represented by one training patch). Neither is inferred from the image filename or from cell appearance.</p>"
            "<p><b>Why can tissue matching be unavailable?</b> The current reason is shown below. An image can have known MPP while the model field is still unknown. Entering MPP does not establish the model field.</p>"
            "<p><b>Example for the built-in CRC classifier:</b> its field is 112 x 112 micrometres. At 0.5 MPP a field uses 224 x 224 source pixels; at 0.252 MPP it uses about 444 x 444. These values are not a segmentation preset.</p>"
            "<p>For a patch classifier, choose <b>Tiled analysis</b> to analyse a larger image. Physical-mode Single image must contain exactly one model field. Matching is optional; leaving it off keeps the configured pixel workflow.</p>"
            "<p><b>Edge handling:</b> by default the built-in CRC classifier resizes small edge crops in Pixel settings and skips incomplete edge strips in Match tissue scale. <b>Cover borders with full-sized regions</b> uses overlapping complete crops. Each mode remembers its own choice for the current image.</p>"
            "<p><b>Built-in UPerNet segmentation:</b> Pixel settings use 1000 × 1000 source pixels and a 512-pixel stride. Match tissue scale uses the current image MPP to sample approximately 67.2 × 67.2 µm per crop and keeps the same overlap proportion. Both modes resize each crop to 224 × 224. The matched target is the project's nominal 0.300 µm/px at model input.</p>"
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
            "<p><b>Model requirements</b> keeps common fields visible and places reader, resize, edge and stride controls under <b>Advanced preprocessing &amp; tiling</b>. The optional field calculator needs the original training crop <b>before resizing</b> and that crop's known MPP; it supplies no guessed values.</p>"
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
            "<p>Saving a model field does not provide calibration for a picture. Enter or inspect the picture's MPP in <b>Image sampling</b>.</p>"
        ),
    },
    "zh": {
        "scale": (
            "物理尺度匹配是什么",
            "<p>在 <b>输入与尺度 → 图像采样</b> 中，可以一起检查图片、模型和取样方法。预览会在应用之前实时更新；选择组织尺度匹配后，大图会自动使用分块分析。取消不会应用这次图片和取样设置。</p>"
            "<p>作用是让模型每次看到<b>相同大小的组织范围</b>，即使不同图片的像素大小不同。它与染色、颜色处理是分开的。</p>"
            "<p>需要两份信息：<b>图片 MPP</b>（这张图一个像素对应多少微米），以及<b>模型组织视野</b>（训练时一块图代表的实际组织宽度和高度）。不能凭文件名、细胞外观或单纯的像素宽高推断。</p>"
            "<p><b>为什么组织尺度匹配不可用？</b>下面会列出当前缺少什么。图片有 MPP，不代表模型的视野就已知；只填写图片 MPP，不能补出模型的训练视野。</p>"
            "<p><b>内置 CRC 分类模型的例子：</b>模型每块看 112 × 112 微米。图片为 0.5 MPP 时，对应原图 224 × 224 像素；为 0.252 MPP 时，约为 444 × 444 像素。这不是分割模型的通用设置。</p>"
            "<p>较大的分类图片通常选择 <b>分块分析</b>。开启匹配时，整图分类 必须恰好是一块模型视野。不开启匹配，继续按原有像素设置运行。</p>"
            "<p><b>边缘处理：</b>内置结直肠分类模型在像素模式下默认缩放小边缘块，分析整张图。匹配组织尺度时，默认跳过放不下完整视野的边缘。选择<b>用完整尺寸裁块覆盖边缘</b>会使用相互重叠的完整块，两种模式会分别记住这张图的选择。</p>"
            "<p><b>内置 UPerNet 分割：</b>像素设置使用原图 1000 × 1000 像素裁块和 512 像素步长。匹配组织尺度根据当前图像 MPP 换算裁块和步长，使每块约覆盖 67.2 × 67.2 微米，并维持相同的重叠比例。两种模式都将每块缩放至 224 × 224。匹配目标是模型输入的标称尺度 0.300 微米／像素。</p>"
        ),
        "image": (
            "图像尺度：图片尺度怎么填",
            "<p><b>这里描述图片，不是设置模型。</b>MPP 的单位是微米/像素。例如 0.5 MPP，表示沿这一方向，一个像素对应 0.5 微米。</p>"
            "<ul><li><b>使用文件中的 MPP：</b>使用图片或配套校准文件中已有的数值。读不到可靠信息时，这项不可选。</li>"
            "<li><b>输入已知 MPP：</b>填写扫描或导出信息中确认的数值。点击数字框，全选后可直接输入小数，例如 0.252。示例数值不是对当前图片的推荐。</li>"
            "<li><b>MPP 未知：</b>不知道就保留未知，继续用像素模式。不要从图片宽高、打印 DPI 或 20×/40× 字样猜。</li></ul>"
            "<p><b>X / Y</b>分别表示横向、纵向。勾选 <b>两轴使用相同 MPP</b> 后，只填 X，Y 自动跟随且不能单独改；只有来源明确给出两轴不同数值时，才取消勾选后分别填写。</p>"
            "<p><b>应用到当前图像</b> 将选择用于当前图片，不修改图片像素或原文件元数据；<b>取消</b> 不应用这次修改。换一张图片后，不会沿用上一张的手动 MPP。</p>"
            "<p>只裁剪、不缩放，MPP 不变；缩放过的导出图，需要用缩放后的校准。某张 SVS 确认的 0.252 MPP 不能直接套给其他图片。</p>"
            "<p>填写 MPP 不等于自动启用尺度匹配；模型的组织视野也必须已知。具体条件见尺度匹配帮助。</p>"
        ),
        "model": (
            "模型输入：模型输入配置是什么",
            "<p><b>模型要求</b> 默认显示常用项目，读取、缩放、边缘和步长放在可展开的 <b>高级预处理与分块</b> 中。可选视野计算器需要<b>缩放前的原始训练裁块</b>和这批原始像素的已知 MPP，不自动填写猜测值。</p>"
            "<p><b>这里描述模型需要什么，不是填写图片 MPP。</b>内置模型的要求只供查看，无需修改。本地模型可以保存自己的配置，不改变权重。</p>"
            "<ul><li><b>类别标签：</b>类别名称，顺序必须与模型输出相同；数量也必须一致。</li>"
            "<li><b>网络输入尺寸：</b>送入模型的小图宽、高，单位是像素。224 × 224 像素不等于实际组织视野。</li>"
            "<li><b>归一化：</b>raw255 保留 0–255；imagenet 先除以 255，再用 ImageNet 均值和标准差处理。Custom 必须填写真实的乘数、均值和标准差；Embedded 表示模型内部已经做归一化，外部不重复做。</li>"
            "<li><b>图像解码与缩放方式：</b>图片读取和缩放方式，应与训练验证或配套推理代码一致。</li>"
            "<li><b>整图／组织裁块：</b>模型一次分析整图，还是局部组织块。</li>"
            "<li><b>预期组织视野：</b>一块训练图对应的实际组织宽、高，单位是微米。没有可靠记录就都留空；不要在这里填图片 MPP。</li>"
            "<li><b>原图裁块／步长：</b>参考切块大小和移动步长；步长较小会使分割处理区域重叠。</li>"
            "<li><b>边缘规则：</b>Skip 跳过不足一块的边缘；Reflect 用镜像像素补边；缩放不完整裁块 保留旧像素流程的边缘缩放方式。</li>"
            "<li><b>输出：</b>logits 需要转为概率；probabilities 已经是概率，不能重复转换。</li></ul>"
            "<p><b>导入设置文件</b> 读取这份权重对应的 JSON 配置；<b>保存模型设置</b> 校验后保存配套配置文件。更换权重后，旧配置不能直接沿用。输入兼容检查不等于验证准确率。</p>"
            "<p>模型视野不能代替图片校准；图片 MPP 要到 <b>图像采样</b> 查看或填写。</p>"
        ),
    },
    "ja": {
        "scale": (
            "物理スケール合わせ",
            "<p><b>入力とスケール → 画像サンプリング</b>で、画像、モデル、サンプリングを一緒に確認できます。設定を変えるとプレビューが更新されます。大きな画像でタイル解析に切り替わる場合も適用前に分かります。</p>"
            "<p>スケール合わせは、画像の解像度が異なっても<b>モデルが見る組織の実際の範囲</b>をそろえるための設定です。染色や色の調整とは別の処理です。</p>"
            "<p>必要なのは<b>画像の MPP</b>（1 ピクセルあたりの長さ）と<b>モデルの組織範囲</b>（学習時のタイルに相当する実際の幅と高さ）です。ファイル名や画像寸法、細胞の見た目からは判断しません。</p>"
            "<p><b>利用できない場合</b>は、下の現在の状態を確認してください。画像の MPP が分かっていてもモデルの範囲が未指定なら、スケール合わせは行えません。</p>"
            "<p><b>内蔵 CRC 分類モデルの例：</b>組織範囲は 112 × 112 µm です。0.5 MPP の画像では 224 × 224 ピクセル、0.252 MPP では約 444 × 444 ピクセルを切り出します。</p>"
            "<p>大きな画像には<b>タイル解析</b>を選びます。スケール合わせで画像全体を分類するには、画像がちょうどモデルの 1 タイル分の範囲である必要があります。</p>"
            "<p><b>画像端の処理：</b>内蔵 CRC 分類モデルの既定値では、ピクセル設定は画像端の小さいタイルをリサイズし、画像全体を解析します。"
            "組織スケールを合わせると、規定サイズに満たない端の部分は既定で除外します。"
            "規定サイズで画像端を覆う設定では、端のタイルが重なります。この画像での設定はサンプリング方法ごとに保持します。</p>"
            "<p><b>内蔵 UPerNet セグメンテーション：</b>ピクセル設定では元画像から 1000 × 1000 ピクセルを切り出し、ストライドは 512 ピクセルです。組織スケールを合わせる場合、画像の MPP に基づいて約 67.2 × 67.2 µm を切り出し、重なりの割合を維持します。どちらも各領域を 224 × 224 にリサイズします。モデル入力の公称目標は 0.300 µm/px です。</p>"
        ),
        "image": (
            "画像のスケールの入力方法",
            "<p><b>この設定は画像のためのものです。</b>MPP は 1 ピクセルあたりの長さ（µm）です。0.5 MPP なら、その軸の 1 ピクセルが 0.5 µm に相当します。</p>"
            "<ul><li><b>ファイルの MPP を使用：</b>画像または対応するキャリブレーションファイルの値を使います。有効な値がない場合は選択できません。</li>"
            "<li><b>既知の MPP を入力：</b>この画像を撮影、スキャン、または出力した際に記録された値を入力します。0.252 のような小数を直接入力できます。</li>"
            "<li><b>MPP が不明：</b>ピクセル設定で続けられます。画像寸法、印刷 DPI、20× や 40× の表記のみからは判断できません。</li></ul>"
            "<p>X は水平方向、Y は垂直方向です。両軸で同じ値を選ぶと、Y は X に従います。</p>"
            "<p>適用は現在の画像に限られます。画像の画素やメタデータを書き換えません。キャンセルでは今回の入力を破棄します。</p>"
            "<p>リサイズを伴わない切り出しでは MPP はそのままです。リサイズした画像では出力後のキャリブレーション値を使ってください。スケール合わせにはモデルの組織範囲も必要です。</p>"
        ),
        "model": (
            "モデル入力設定の項目",
            "<p><b>モデルの入力要件</b>では、よく使う項目を表示します。読み込み方式、リサイズ、画像端の処理、ストライドは<b>前処理とタイルの詳細設定</b>にあります。</p>"
            "<p>内蔵モデルの要件は参照専用です。ローカルモデルの設定を保存しても重みは変更されません。組織範囲の計算では、リサイズ前の学習用タイルと既知の MPP を使います。</p>"
            "<ul><li><b>クラスラベル：</b>モデル出力と同じ個数・順序で、1 行に 1 つ入力します。</li>"
            "<li><b>ネットワーク入力サイズ：</b>モデルへ渡す画像のピクセル寸法です。組織の物理的な幅や高さとは別に指定します。</li>"
            "<li><b>正規化：</b>raw255 は値を 0～255 のまま使用し、imagenet は 255 で割ってから ImageNet の平均と標準偏差を適用します。custom は指示された倍率、平均、標準偏差を使用します。embedded はモデル内部で処理します。</li>"
            "<li><b>デコーダー／リサイズ：</b>学習時の検証や推論手順で指定された方式を選びます。</li>"
            "<li><b>解析単位：</b>画像全体または局所の組織タイルです。</li>"
            "<li><b>想定する組織範囲：</b>学習用タイル 1 枚に対応する µm 単位の範囲です。仕様がない場合は未指定にします。現在の画像の MPP はここに入力しません。</li>"
            "<li><b>参照タイル／ストライド：</b>切り出しの大きさと間隔です。ストライドが小さいとセグメンテーション領域は重なります。</li>"
            "<li><b>画像端の処理：</b>除外、反射パディング、小さいタイルのリサイズから、仕様に合うものを選びます。</li>"
            "<li><b>出力：</b>logits は一度だけ確率へ変換し、probabilities は検証してそのまま使用します。</li></ul>"
            "<p>対応する重みの JSON 設定を読み込むか、入力内容を検証して保存します。重みが変わった場合は設定を確認し直してください。入力の互換性と予測精度は別々に評価します。</p>"
            "<p>現在の画像の MPP を参照・設定するには<b>画像サンプリング</b>を開きます。</p>"
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
        row.addWidget(QLabel(tr("Help language"), self))
        self.language = ExplicitComboBox(self)
        for code, name in LANGUAGES:
            self.language.addItem(name, code)
        active = QApplication.instance().property("zyLanguage")
        if active is None:
            active = {QLocale.Chinese: "zh", QLocale.Japanese: "ja"}.get(QLocale.system().language(), "en")
        self.language.setCurrentIndex(max(0, self.language.findData(active)))
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
            heading = translate_for(language, "Current status")
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
