# CP2 content revision change log

241 recorded content/index changes. Existing styles and application source preserved.

## 1. Acknowledgements — Original paragraph 14

**Before:** I would like to thank my supervisor, Dr Wan Siti Halimatul Munirah Wan Yahya @ Wan Ahmad, for the guidance provided throughout this capstone project. The project developed from the CP1 proposal into an implemented desktop application through repeated review of the analysis workflow, model integration and user interface.

**After:** I would like to thank my supervisor, Dr Wan Siti Halimatul Munirah Wan Yahya @ Wan Ahmad, for her guidance throughout this capstone project, for providing the reference classification training code, and for providing the segmentation model and inference notebook. I conducted the classification training and evaluation and developed the desktop application, including model integration, result inspection, history, export and the associated interaction workflows.

**Reason:** Clarify supervisor and student contributions using confirmed provenance.

## 2. Abstract — Original paragraph 17

**Before:** Histopathology image analysis increasingly uses deep learning, but applying a trained model still requires users to manage compatibility, preprocessing, result interpretation and analysis records. This project develops ZY-Path, a local desktop application that brings these activities into a graphical workflow for education and exploratory research. The implementation uses PyQt5 for the interface, PyTorch for CPU inference and SQLite for persistent history. It supports compatible pretrained model files, whole-image classification, explicit tiled classification, segmentation, linked original/result inspection and PNG/PDF export. The built-in classification integration follows a custom nine-class DenseNet contract: RGB float32 input, raw255 pixel values, a 224 × 224 network input and a fixed model class order. Tiled analysis classifies non-overlapping source crops and reports area-weighted estimated coverage, distinctly from pixel segmentation. Original-image tile dimensions are editable; the 512 × 512 starting value is not claimed to match an unverified training scale. The segmentation integration uses a separate UPerNet/Swin Base pathway with its own preprocessing, labels and overlapping-tile fusion. Model validation and inference run outside the GUI thread, while cooperative cancellation, task-specific model defaults and recorded rerun parameters support a controlled workflow. At the documented implementation revision, automated verification recorded 355 passed tests, one failed test caused by absent real model weights and one collection error caused by a missing training script. These results establish substantial software-level evidence but do not establish diagnostic accuracy. User acceptance testing and independent model evaluation have not yet been completed; their protocols, instruments and result templates are supplied without invented findings. ZY-Path's contribution is an inspectable, record-oriented desktop integration, rather than a new neural architecture, a whole-slide processing platform or a clinically validated diagnostic system.

**After:** To make trained histopathology models accessible through a traceable graphical workflow, this project developed ZY-Path, a PyQt5 desktop application combining CPU-based PyTorch inference, Single image and Tiled analysis classification, UPerNet segmentation, linked image inspection, SQLite history, recorded rerun and PNG/PDF export. Evaluation of the custom nine-class DenseNet on 7,180 CRC-VAL-HE-7K images recorded 90.68% accuracy and 88.59% macro-F1, with consistent per-image predictions and aggregate reports; earlier Linux regression tests supplied software-level evidence, while the latest Windows pytest invocation stopped during collection and a separate Windows session recorded successful loading and structural validation of the real classifier. The contribution is a model-aware desktop integration for education and exploratory research, with user acceptance testing, segmentation accuracy, systematic performance measurement and clean-machine executable deployment remaining to be evaluated.

**Reason:** Replace the long defensive abstract with three evidence-based sentences and distinguish prediction, software and Windows evidence.

## 3. 1.1 Background and Motivation — Original paragraph 191

**Before:** Existing pathology platforms already offer sophisticated graphical inspection and analysis. QuPath provides an open-source image-analysis environment; Slideflow includes real-time whole-slide visualisation through Slideflow Studio; and WSInfer integrates reusable pretrained models with QuPath (Bankhead et al., 2017; Dolezal et al., 2024; Kaczmarzyk et al., 2024). The motivation for ZY-Path is therefore a narrower workflow need: to organise compatible model loading, source-image analysis, understandable result inspection and local inference records in a compact desktop application. The project does not depend on claiming that existing platforms have no GUI or cannot support reproducible work.

**After:** Existing pathology platforms offer graphical inspection and analysis: QuPath provides an extensible image-analysis environment, Slideflow Studio supports whole-slide visualisation, and WSInfer integrates reusable pretrained models with QuPath (Bankhead et al., 2017; Dolezal et al., 2024; Kaczmarzyk et al., 2024). ZY-Path addresses a focused workflow within this landscape by connecting supported local model loading, distinct analysis modes, spatial inspection and persistent inference records in one desktop application.

**Reason:** Emphasise the project motivation without repeated negative comparisons.

## 4. 1.2 Problem Formulation — Original paragraph 200

**Before:** These questions guide the requirements and evaluation. In CP2, “direct loading” means loading supported, trusted model representations under a validated contract; it does not mean arbitrary compatibility with every file carrying a .pt or .pth extension. “Reproducibility” means restoring recorded workflow parameters under stable dependencies and files, rather than guaranteeing immutable data or identical outcomes after external files have changed.

**After:** In this project, direct loading refers to trusted model representations with supported input/output and metadata contracts. Recorded rerun restores a previous analysis configuration under stable files and dependencies. These operational definitions guide the requirements and evaluation; their boundaries are discussed in Section 4.5.3.

**Reason:** Consolidate repeated compatibility and reproducibility qualifications.

## 5. 1.2.1 Problem Statement — Original paragraph 204

**Before:** Third, completed analyses need continuity. Users should be able to retrieve a record, inspect its saved presentation, distinguish a stored result from a new run, export a report and rerun the recorded model/mode/parameters. Current preferences must not silently rewrite a historical analysis. These are specific workflow requirements; they are not assertions that competing systems lack all history or provenance capabilities.

**After:** Third, completed analyses need continuity. Users should be able to retrieve a record, inspect its saved result, export a report and rerun its recorded model, mode and parameters. Keeping these settings separate from current preferences makes the previous analysis intelligible and reduces manual reconstruction of its configuration.

**Reason:** State the engineering requirement positively.

## 6. 1.3 Hypothesis — Original paragraph 208

**Before:** For the planned pilot, SUS is a descriptive usability measure, and a score near the commonly cited average of 68 is a contextual benchmark, not a diagnostic threshold or a guaranteed project result (Brooke, 1996; Bangor et al., 2009). No hypothesis is declared statistically accepted from development tests alone. A single-condition pilot also cannot establish superiority over another platform without an appropriate comparative design.

**After:** For the planned pilot, SUS provides a descriptive measure of perceived usability; its interpretation will use the actual sample, tasks and score distribution (Brooke, 1996; Bangor et al., 2009). Hypothesis assessment combines the technical evidence with the corresponding user evidence rather than treating software tests as responses to a usability survey.

**Reason:** Remove an unsupported universal numeric benchmark and retain cited evaluation principles.

## 7. 1.4 Project Objectives — Original paragraph 218

**Before:** Tiled classification, cancellation, task-specific model defaults and responsive comparison views refine these objectives rather than introduce a new training or diagnostic objective. O1's local-runtime implementation is distinguished from a distributable Windows executable: packaging remains an intended deployment step until a clean-machine build has been verified.

**After:** Tiled analysis, cancellation, task-specific model defaults and responsive comparison views refine these objectives. O1 is implemented through local source execution without an application server; producing and validating a standalone executable is a further deployment objective addressed in Sections 4.3.5 and 5.2.

**Reason:** Separate implemented local execution from unverified packaging.

## 8. 1.5 Scope of Work — Original paragraph 222

**Before:** The built-in classification integration expects nine ordered classes: ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR and TUM. The built-in segmentation integration has a different nine-label vocabulary. Their colour maps and statistics remain separate. Tile width and height begin at an editable 512 × 512 source pixels; their physical scale, magnification and consistency with the training crop scale remain unconfirmed.

**After:** The built-in classifier uses the ordered classes ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR and TUM. Segmentation has a separate nine-label vocabulary and palette. Classification source tiles begin at an editable 512 × 512 pixels, with training-scale equivalence explicitly unconfirmed; the consequences of source scale and edge resizing are discussed in Section 4.5.3.

**Reason:** Keep the actual setting and centralise its detailed limitation.

## 9. 1.5 Scope of Work — Original paragraph 225

**Before:** ZY-Path does not provide any training loops, loss functions, optimizers, or hyperparameter tuning; users must supply fully trained models.

**After:** The desktop application is inference-only. Classification training was carried out separately using the reference code provided by my supervisor; the resulting model was then integrated into ZY-Path. Training loops and hyperparameter tuning are not exposed through the GUI.

**Reason:** Distinguish author-performed external training from application scope.

## 10. 1.5 Scope of Work — Original paragraph 235

**Before:** The local-runtime scope also has prerequisites. Model files must exist, and the UPerNet path requires a locally cached verified configuration. A complete offline deployment must include these dependencies before disconnecting. The present cloud checkout lacks the real weight files, so it cannot establish real-weight end-to-end accuracy or deployment completeness.

**After:** Local execution requires the selected model files and, for UPerNet reconstruction, its verified configuration in the local Hugging Face cache. Windows source execution and real-classifier validation are documented in Section 4.3.3; offline package verification is addressed separately in Section 4.3.5.

**Reason:** Remove obsolete blanket missing-weight and missing-evaluation claims.

## 11. 1.6 Research Significance — Original paragraph 238

**Before:** From an educational point of view, this project offers anyone with a keen interest in histopathology a chance to experiment with AI-powered histopathology analysis and to play with its functions without any programming skills. The no-code design philosophy around AI technologies fosters learning and experimentation for a wider pool of potential AI users.

**After:** For education, the interface gives students and researchers a way to explore supported model outputs without writing inference code. Visible modes, class legends, source comparisons and retrievable records connect technical settings to the interpretation of a result.

**Reason:** Replace promotional proposal wording with concrete implemented mechanisms.

## 12. 1.6 Research Significance — Original paragraph 244

**Before:** These links to SDG 3 and SDG 4 are motivations and potential contributions. They are not measurements of health impact, educational improvement or clinical safety. Such outcomes would require studies beyond the current software verification and planned pilot UAT.

**After:** SDG 3 and SDG 4 provide the wider motivation for the project. The present evaluation concerns engineering behaviour and classification performance; the planned UAT will examine the educational/research workflow from the intended users’ perspective.

**Reason:** Avoid repeating the full clinical and educational-impact disclaimer.

## 13. 2.1 Introduction — Original paragraph 248

**Before:** The review is organised thematically rather than as a claim of an exhaustive systematic review. Foundational papers, platform publications and primary software documentation are used to explain design decisions. No database search protocol, screening count or meta-analysis was performed, and none is claimed. Comparisons describe documented purposes and capabilities; commercial licensing and deployment options may change and are not treated as permanently established limitations.

**After:** The review follows a thematic narrative approach, combining foundational research, platform publications and primary technical documentation. Each theme is linked to an implementation decision or evaluation requirement. Platform comparisons concern documented capabilities and their relevance to the selected task, with source limitations recorded in the reference audit.

**Reason:** State the review method without lengthy defensive exclusions.

## 14. 2.2.1 Digital histopathology and the unit of analysis — Original paragraph 251

**Before:** Histopathology, which involves the examination of tissue sections stained with dyes like hematoxylin and eosin under a light microscope, continues to be the gold standard for diagnosing a broad range of diseases including malignancy. Pathologists make diagnoses by visual assessment of cellular morphology, cellular architecture, and the spatial organization of cells. Though, this process itself is subjective, laborious, and with potential intra-observer and inter-observer variation, particularly when dealing with borderline lesions or unusual tissue types.

**After:** Histopathology examines stained tissue to interpret cellular morphology and tissue architecture. H&E images provide patterns relevant to diagnosis and research, while digital analysis translates those images into computational inputs (Litjens et al., 2017). The unit of analysis must be explicit because an image patch, a larger raster region and a whole-slide pyramid have different sampling and resource requirements.

**Reason:** Improve grammar and remove duplicated background exposition.

## 15. 2.2.1 Digital histopathology and the unit of analysis — Original paragraph 252

**Before:** Digital pathology permits image sharing and computational analysis, but a tissue patch, a larger raster region and a whole-slide pyramid are different data objects. A crop's tissue scale depends on how the image was acquired and sampled, not only its pixel dimensions. The NCT-CRC-HE-100K collection provides 100,000 nine-class colorectal tissue patches, and CRC-VAL-HE-7K provides a related external validation collection (Kather et al., 2019). These published datasets motivate the class vocabulary, but their published results cannot be assigned to a different model without evaluation.

**After:** NCT-CRC-HE-100K contains 100,000 colorectal tissue patches across nine categories, while CRC-VAL-HE-7K provides a separate labelled evaluation collection (Kather et al., 2019). This project used the former for training and internal validation and the latter for the recorded 7,180-image test. The actual split manifests and measured results are described in Sections 3.3.2 and 4.3.4.

**Reason:** Connect published dataset context to the newly supplied project evidence.

## 16. 2.2.1 Digital histopathology and the unit of analysis — Original paragraph 253

**Before:** Published information about dataset patch size does not prove the acquisition scale of an arbitrary user image or the exact training pipeline behind a particular weight file. ZY-Path therefore exposes source tile dimensions while retaining an explicit unconfirmed-scale status. This is an implementation consequence of the literature's patch-level setting, rather than evidence that every 512-pixel crop is equivalent to a training example.

**After:** Dataset identity and pixel dimensions alone do not specify the physical field of view of an arbitrary imported raster image. Consequently, ZY-Path exposes source crop dimensions independently of network input dimensions. Section 4.5.3 discusses the resulting scale and generalisation limits.

**Reason:** Consolidate the scale discussion and avoid assuming training-matched 512-pixel crops.

## 17. 2.2.2 Classification architectures and pretrained deployment — Original paragraph 255

**Before:** The two main duties involved are comparable to ZY-Path. Image classification applies a categorical label, e.g. benign vs. malignant, to an input image patch. Image segmentation generates a pixel-wise mask to separate structures of interest (tumor regions, glands, cell nuclei, etc.) from background tissue. Both tasks indeed have very standard neural net architectures. For the classification, ResNet (He et al., 2016), VGG, DenseNet (Huang et al., 2017) and EfficientNet (Tan & Le, 2019) families are frequently adopted.

**After:** Image classification assigns a category to an image or patch, whereas semantic segmentation assigns categories to spatial locations. ZY-Path supports both tasks through separate model pathways. Residual networks, DenseNet and EfficientNet illustrate alternative classification designs based on residual learning, dense feature reuse and compound scaling respectively (He et al., 2016; Huang et al., 2017; Tan & Le, 2019).

**Reason:** Repair the incoherent CP1 opening and align the architecture discussion.

## 18. 2.2.2 Classification architectures and pretrained deployment — Original paragraph 256

**Before:** Dense connectivity concatenates earlier feature maps into later layers, encouraging feature reuse (Huang et al., 2017). The architecture family must be distinguished from a particular configuration. The supplied CRC training script constructs a custom DenseNet with four blocks of two dense layers; it is not a standard DenseNet-121 checkpoint and not the ResNet-50 anticipated in CP1. Architectural literature explains the design vocabulary but does not demonstrate the accuracy, calibration or CPU speed of this implementation.

**After:** DenseNet concatenates earlier feature maps into later layers to encourage feature reuse (Huang et al., 2017). The classifier trained for this project uses four dense blocks with two dense layers each. Its precise configuration, rather than a generic family name, governs checkpoint reconstruction and is reported in Section 3.3.2.

**Reason:** Correct the architecture without repeating multiple excluded alternatives.

## 19. 2.2.2 Classification architectures and pretrained deployment — Original paragraph 257

**Before:** Residual networks and EfficientNet remain useful comparative foundations: residual connections address optimisation in deep networks, while compound scaling studies model depth, width and input resolution (He et al., 2016; Tan & Le, 2019). ZY-Path does not implement a new architecture or run a controlled architecture benchmark. Its loader reconstructs supported architectures from metadata and checks their executable output contract.

**After:** Architecture selection and application integration answer different questions. Residual networks and EfficientNet provide useful comparative foundations (He et al., 2016; Tan & Le, 2019), while ZY-Path concentrates on reconstructing supported models from metadata and presenting their outputs under explicit contracts. The project evaluates its chosen classifier rather than conducting an architecture benchmark.

**Reason:** Clarify the comparison and actual evaluation scope.

## 20. 2.2.2 Classification architectures and pretrained deployment — Original paragraph 258

**Before:** Transfer learning can reduce the burden of obtaining task-specific models, but deploying an already trained model is not itself evidence that transfer learning was used. In particular, the supplied training script directly instantiates DenseNet and does not load ImageNet weights. The thesis therefore describes it as an externally trained classifier, without claiming verified ImageNet fine-tuning. Model training and optimisation remain outside the GUI's scope.

**After:** Reusing a trained model for application inference is distinct from fine-tuning an ImageNet model. The classification training code directly instantiates DenseNet without loading pretrained ImageNet weights. I trained that configuration separately before integrating the selected checkpoint into the application; the GUI itself remains inference-only.

**Reason:** Reflect actual student training and avoid unverified ImageNet transfer-learning claims.

## 21. 2.2.3 Semantic segmentation and multiscale context — Original paragraph 261

**Before:** Segmentation assigns labels to a spatial output grid. When a network's prediction grid differs from the source image, a restoration rule is required. Averaging class probabilities before choosing a label and interpolating an already discrete label map are different operations. The implemented UPerNet path blends overlapping probabilities on a reduced-resolution lattice, obtains its label map and restores labels with nearest-neighbour interpolation. Its pixel coverage therefore describes the restored predicted mask; it does not establish subpixel accuracy or expert agreement at tissue boundaries.

**After:** Segmentation predicts categories on a spatial grid. UPerNet’s overlapping-window pathway combines class probabilities before selecting labels, then restores the discrete mask with nearest-neighbour interpolation. This preserves label identities during restoration and provides the basis for the software’s pixel-coverage statistics; predictive boundary quality requires separate annotated-mask evaluation.

**Reason:** Keep methodological distinction while reducing duplicated caveats.

## 22. 2.2.5 No-code interaction and transparent constraints — Original paragraph 269

**Before:** This leads to a distinction between simplicity and concealment. Whole-image and tiled analysis are explicit modes; source tile dimensions are stated in pixels; a resize backend is named precisely; and historical records retain the mode actually used. These choices make the system more inspectable while keeping network construction and tensor handling outside the user's normal workflow.

**After:** No-code interaction is implemented through explicit task controls and interpretable defaults. The mode, source dimensions and resize backend are visible before execution, and a historical record preserves the settings actually used. Separating model adapters, presentation and persistence also localises responsibility for changes, consistent with modular software design principles (Gamma et al., 1994).

**Reason:** Restore a relevant CP1 design reference and connect it to implementation.

## 23. 2.2.6 Persistence and reproducible workflows — Original paragraph 271

**Before:** SQLite provides a self-contained relational database suitable for local structured storage (SQLite, n.d.). The CP1 choice of a serverless database remains appropriate for a single-user desktop tool. A history record can connect an image path, model path, task, parameters and saved result without requiring a separate database service.

**After:** Persistent analysis records connect an image, model, task, parameters and saved output. For a single-user desktop workflow, an embedded database avoids administering a separate database service. SQLite’s implementation role is described once in Section 2.6; this section concerns the reproducibility requirements placed on the stored records.

**Reason:** Remove the duplicate SQLite introduction.

## 24. 2.2.6 Persistence and reproducible workflows — Original paragraph 272

**Before:** Replaying a record nevertheless has limits. A path identifies a location, not immutable file content. A model or image may be replaced at the same path, dependencies may change and external artifacts may be removed. The present application retains useful provenance but does not persist a cryptographic identity for every input/model or a complete environment lock with each run. Accordingly, this report uses “recorded rerun” and “workflow reproducibility” rather than claiming fully immutable or universally deterministic reproduction.

**After:** A recorded configuration supports rerun only while its referenced files and compatible dependencies remain available. ZY-Path therefore uses the term recorded rerun for restoring the saved task, model and analysis parameters. Section 4.5.3 distinguishes this workflow continuity from immutable provenance.

**Reason:** Centralise the detailed provenance limitation.

## 25. 2.2.7 Human-centred design and evaluation — Original paragraph 275

**Before:** The SUS is one of the most used tools for evaluating usability in software development and in healthcare related applications. It includes ten Likert-scale questions and delivers a quantitative evaluation of the perceived usability with a very short measurement time. SUS has been validated in various application areas and allows for comparison to existing studies.

**After:** The System Usability Scale is a ten-item questionnaire for perceived usability (Brooke, 1996). Bangor et al. (2009) provide an interpretive framework relating SUS scores to adjective ratings. These sources support the planned instrument and contextual interpretation, while task outcomes and qualitative observations explain which interactions influence the score.

**Reason:** Replace the uncited inherited paragraph with specific supported claims.

## 26. 2.3.1 QuPath — Original paragraph 280

**Before:** The relevant difference is workflow focus. ZY-Path concentrates on selecting supported local PyTorch models, inspecting three explicitly distinguished output types and recalling individual inference records. QuPath should be viewed as a stronger general image-analysis environment, not as a GUI-deficient baseline. No timed comparison or user study against QuPath has been performed.

**After:** QuPath’s whole-slide, annotation and extensibility functions serve a broader image-analysis task. ZY-Path instead centres on supported local model files and individual analysis records. This is a comparison of workflow scope; the performance and usability questions require the empirical design discussed in Section 4.5.2.

**Reason:** Remove repetitive unperformed-comparison disclaimers.

## 27. 2.3.2 Slideflow and Slideflow Studio — Original paragraph 283

**Before:** Compared with this broader research environment, ZY-Path intentionally excludes model training, multiple-instance learning and native whole-slide data management. Its smaller scope may simplify a specific local inference task, but that possibility remains a usability hypothesis until evaluated. A feature-rich platform is not inherently less usable; its suitability depends on the task and user population.

**After:** Slideflow’s training and whole-slide capabilities address a broader research lifecycle. ZY-Path selects the inference-and-record portion of that lifecycle for individual users. This trade-off motivates a task-based usability study rather than an assumption that fewer features necessarily produce a better interface.

**Reason:** Strengthen critical synthesis and reduce repeated limitations.

## 28. 2.3.3 WSInfer and QuPath integration — Original paragraph 286

**Before:** ZY-Path differs in its standalone, record-centred presentation, explicit single/tiled classifier modes and combined local history/export controls. These are implementation choices rather than proof of a superior inference engine. WSInfer's whole-slide context and model distribution ecosystem address requirements that ZY-Path does not attempt to cover.

**After:** WSInfer provides a close precedent for accessible pretrained-model inference. ZY-Path’s particular design combines explicit Single image/Tiled analysis controls, linked result inspection and local record retrieval/export. The comparison concerns this arrangement of functions within a raster-image application.

**Reason:** State the project positioning without repeating novelty disclaimers.

## 29. 2.3.5 Commercial environments — Original paragraph 292

**Before:** Consequently, the comparison does not assert that all commercial systems prohibit custom models, require continuous internet access or lack history. The more defensible project distinction is local control over the implemented workflow and source code, within the compatibility and maintenance limits of a student-developed application.

**After:** For this project, local control of the source code, model selection and analysis records is the relevant deployment choice. Product-specific licensing, import and support arrangements require current primary documentation; they are not treated as universal disadvantages of commercial systems.

**Reason:** Avoid unsupported commercial comparisons.

## 30. 2.4 Comparative Evaluation of Existing Systems — Original paragraph 294

**Before:** The comparison in Table 2.1 is qualitative and based on published purposes and primary platform descriptions. “Not evaluated” is used where a capability was not independently investigated. A feature is not marked absent simply because it was not part of the review. No aggregate superiority score is calculated because the systems solve different problems.

**After:** Table 2.1 compares platform purposes and documented workflow scope. It separates an unexamined capability from an absent one and uses no aggregate ranking because the applications address different tasks. Source publications are cited in Sections 2.3.1–2.3.5.

**Reason:** Provide comparison provenance and concise interpretation.

## 31. 2.5 Identified Research Gaps and Project Positioning — Original paragraph 300

**Before:** These needs refine the CP1 gap analysis. They do not establish the absence of similar functionality in every academic or commercial system. The project's contribution is an implemented combination tailored to individual educational/research use. It introduces no novel neural network, no clinical decision rule and no claim that classification tiles replace pixel segmentation.

**After:** The resulting project position is a focused desktop integration for individual educational and research use. Its research value lies in connecting model compatibility, spatial interpretation and record continuity as observable requirements, building on the graphical inference precedents identified above.

**Reason:** Reduce repeated defensive novelty statements.

## 32. 2.6 Technological Infrastructure and Implementation Considerations — Original paragraph 304

**Before:** SQLite is a serverless, embedded, relational database engine, where the complete database (definitions, tables, indices, and the data itself) is stored in a single cross-platform file on disk. Its zero-configuration design enables the storing of structured data without having to use an external database server. This is what makes SQLite perfectly suited for local desktop applications such as ZY-Path, where inference records (image paths, model paths, prediction outputs, timestamps) must be persisted reliably in a DBA-free environment.

**After:** SQLite stores structured records in an embedded, serverless database, making it suitable for a local application without a separately administered database service (Kreibich, 2010; SQLite, n.d.). In ZY-Path it links inference identity and timestamps to task-specific metadata and saved artifacts. Parameterised operations and transactions provide the database component of persistence, while external artifact handling remains the coordinator’s responsibility.

**Reason:** Consolidate SQLite discussion and restore a relevant CP1 technical book.

## 33. 2.6 Technological Infrastructure and Implementation Considerations — Original paragraph 305

**Before:** PyQt5 provides native windows, widgets, layouts, signals and worker threads (Riverbank Computing, n.d.; The Qt Company, n.d.). The current spatial viewer uses QGraphicsView rather than only a scaled QLabel. This allows source-coordinate transformations, linked navigation and vector grid painting after the image has been scaled. PyTorch supplies model evaluation and inference_mode (Paszke et al., 2019); NumPy and Pillow support image/tensor conversion (NumPy Developers, n.d.; Pillow Contributors, n.d.). Matplotlib is used for the single-image classification probability chart (Hunter, 2007), while spatial overlays are generated from image arrays. fpdf2, rather than an unresolved ReportLab/fpdf2 alternative, is the implemented PDF library.

**After:** PyQt5 supplies windows, layouts, signals and worker threads (Riverbank Computing, n.d.; The Qt Company, n.d.). QGraphicsView provides source-coordinate transformations, linked navigation and vector grid painting. PyTorch supplies model execution and inference_mode (Paszke et al., 2019); NumPy and Pillow support image conversion (NumPy Developers, n.d.; Pillow Contributors, n.d.). Matplotlib renders the Single image probability chart (Hunter, 2007), and fpdf2 generates structured PDF reports (fpdf2 Contributors, n.d.). These choices connect the interface to a local scientific-Python stack without a web backend.

**Reason:** Restore concise technical rationale and add the implemented report library citation.

## 34. 2.6 Technological Infrastructure and Implementation Considerations — Original paragraph 307

**Before:** The architecture does not make every installation automatically offline-ready. UPerNet reconstruction requests a configuration from the local Hugging Face cache with local_files_only=True. A deployment package must therefore include the verified configuration and real weights in advance. PyInstaller remains a packaging recommendation (PyInstaller Development Team, n.d.); the reviewed checkout contains no verified executable/specification or clean-Windows-machine test result.

**After:** UPerNet reconstruction loads its configuration from the local Hugging Face cache with local_files_only=True. Preparing a redistributable application therefore requires packaging the permitted weights, cached configuration and runtime dependencies. PyInstaller is a candidate tool for this future deployment step (PyInstaller Development Team, n.d.); the current deployment evidence is assessed in Section 4.3.5.

**Reason:** Describe the dependency accurately and reference the deployment status once.

## 35. 3.1 Overview of System Methodology — Original paragraph 315

**Before:** The project uses iterative implementation and regression-driven refinement of the CP1 design. Each iteration starts from a workflow requirement or observed defect, inspects the relevant code and data contract, implements the smallest coherent correction, and verifies both the changed behaviour and adjacent functions. Windows user reports informed several interface corrections; automated Qt tests supplied repeatable regression evidence. This is an engineering development method, not a clinical trial or a completed experimental comparison of models.

**After:** I developed ZY-Path through iterative implementation and regression-driven refinement of the CP1 design. Each iteration connected a requirement or observed defect to the affected code, an implementation change and an appropriate regression check. Observations during Windows testing informed interface corrections, while automated Qt tests made those cases repeatable.

**Reason:** Replace AI collaboration and external-review narration with author-centred academic prose.

## 36. 3.1 Overview of System Methodology — Original paragraph 318

**Before:** Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the reviewed Python modules.

**After:** Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the project’s Python modules.

**Reason:** Remove review-process wording from the caption.

## 37. 3.1 Overview of System Methodology — Original paragraph 319

**Before:** The software baseline for the results in this report is branch codex-ready-2026-10-15 at commit 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. The reviewed training attachment is train_crc_dn21.py, not a missing similarly named file assumed to exist in the repository. Runtime claims are based on application source and recorded tests; training design claims are based on the attachment. Neither source substitutes for real weight files or independent evaluation data.

**After:** The application baseline is revision 1f3e01e. Classification methods are documented by the supervisor-provided training code, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C records complete version identifiers and the evidence sources used for each type of result.

**Reason:** Keep short revision information in the body and establish actual evidence and contribution sources.

## 38. 3.2.2 Non-Functional Requirements — Original paragraph 328

**Before:** The CP1 coverage target of at least 80% on core/data modules remains an evaluation target, not an observed result. The recorded pytest runs did not produce a coverage report. Likewise, a large test count is not evidence that every hardware, accessibility or packaging requirement has been met.

**After:** The CP1 target of at least 80% coverage of core/data remains an unmeasured target because the recorded pytest commands did not generate a coverage report. Requirements therefore retain separate implementation and verification status rather than inferring coverage from the number of passing tests.

**Reason:** Preserve the unmeasured coverage target concisely.

## 39. 3.2.3 Ethical Considerations — Original paragraph 331

**Before:** Only authorised, de-identified images should be used in demonstrations and UAT. Source filenames, directory names and report metadata can contain personal information even when the visible image is anonymised. Consent and institutional requirements should be checked before collecting participant data or distributing images. No ethics-approval number or participant consent is claimed without supporting records.

**After:** Demonstrations and UAT should use authorised, de-identified images. Source paths and exported metadata require inspection as well as the visible image. Participant consent and institutional requirements will be recorded with the UAT materials in Appendix B.

**Reason:** Avoid repeated pre-emptive statements about absent approvals.

## 40. 3.2.4 Accessibility Compliance — Original paragraph 336

**Before:** WCAG 2.2 informs the review of contrast, keyboard operation and non-colour cues, while recognising that this is a desktop application rather than a web page (W3C, 2023). No formal WCAG conformance, assistive-technology certification or complete screen-reader audit has been performed. A Windows-native keyboard/scale check, contrast audit of all text states, accessible-name review and screen-reader walkthrough remain necessary before claiming compliance.

**After:** WCAG 2.2 informs the review of keyboard access, contrast and non-colour cues, adapted to a desktop interface (W3C, 2023). Native assistive-technology testing and a complete contrast/accessibility audit are further evaluation activities; their present status is included in Section 4.5.3.

**Reason:** Centralise the accessibility limitation.

## 41. 3.2.4 Accessibility Compliance — Original paragraph 337

**Before:** The nine-class palette is a display aid, not a claim that all colour pairs are equally distinguishable for every user. Text legends, tile details and statistics provide redundant information. Checked, hovered and keyboard-focused result controls use stable geometry, and mouse focus no longer adds a thick frame that could obscure their usable area. These measures support accessibility without implying a completed accessibility study.

**After:** The nine-class palette is accompanied by names, counts and numerical statistics so interpretation does not depend on colour alone. Stable control geometry and a visible keyboard focus cue support mouse and keyboard interaction. These design choices are evaluated through controlled interaction tests and the planned user study.

**Reason:** Describe implemented accessibility mechanisms without repeated disclaimers.

## 42. 3.3.1 Model representations and executable validation — Original paragraph 341

**Before:** The supervisor-style CRC checkpoint supplies DenseNet configuration, class labels, raw255 preprocessing and a 224 × 224 input size. The dedicated UPerNet state-dictionary path uses a verified Swin Base configuration already available in the local Hugging Face cache and a strict weight load. Missing configuration or mismatched state shapes produces an actionable validation error rather than a random replacement network.

**After:** The CRC checkpoint contains DenseNet configuration, class labels, raw255 preprocessing and a 224 × 224 input size. The UPerNet state-dictionary path reconstructs the nine-class Swin Base configuration from the local Hugging Face cache and loads the weights strictly. Missing configuration or incompatible state shapes produces an actionable validation error.

**Reason:** Replace supervisor-style wording with the actual checkpoint contract.

## 43. 3.3.2 Classification model and training-reference audit — Original paragraph 343

**Before:** 3.3.2 Classification model and training-reference audit

**After:** 3.3.2 Classification training and model configuration

**Reason:** Replace the file-audit heading with the actual methodology.

## 44. 3.3.2 Classification model and training-reference audit — Original paragraph 344

**Before:** The supplied train_crc_dn21.py constructs torchvision.models.DenseNet using growth_rate=32, block_config=(2, 2, 2, 2), num_init_features=64, bn_size=4, drop_rate=0 and num_classes=9. The four two-layer blocks make the precise configuration important: describing the built-in model as ResNet-50 or standard DenseNet-121 would be inaccurate.

**After:** Using the reference training code provided by my supervisor, I trained torchvision.models.DenseNet with growth_rate=32, block_config=(2, 2, 2, 2), num_init_features=64, bn_size=4, drop_rate=0 and num_classes=9. The training logs report 416,457 parameters. The class order is ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR and TUM.

**Reason:** Document the actual model and student training contribution.

## 45. 3.3.2 Classification model and training-reference audit — Original paragraph 345

**Before:** The dataset loader reads images with OpenCV and converts BGR to RGB. The validation transform is Albumentations Resize(224, 224) followed by ToTensorV2; the dataset then converts the result to float. No divide-by-255 or ImageNet normalisation is present in that path. The training transform additionally specifies vertical/horizontal flips, hue adjustment, rotation and a random-sized crop. The reference code uses CUDA, a weighted cross-entropy objective, Adam (learning rate 0.001; weight decay 10⁻⁶) and ReduceLROnPlateau. These facts describe the supplied script, not a training run reproduced in this project.

**After:** The training loader decodes images with OpenCV, converts BGR to RGB and applies Albumentations Resize(224, 224), vertical/horizontal flips, hue adjustment, rotation and a random-sized crop. Validation uses Resize followed by ToTensorV2 and float conversion. Values remain on the raw255 scale. Training used class-weighted cross-entropy, Adam with initial learning rate 0.001 and weight decay 10⁻⁶, and ReduceLROnPlateau with factor 0.5, patience 3 and minimum learning rate 10⁻⁶; batch size was 32 with two data-loading workers.

**Reason:** Replace script-only uncertainty with verified training settings.

## 46. 3.3.2 Classification model and training-reference audit — Original paragraph 346

**Before:** The script records training/validation metrics and supports resume, but the metric files, manifests, completed-run logs and real checkpoint are absent from the evidence package. Its default epoch count is not the verified number of completed epochs. It also checks disjoint image paths, which does not itself prove patient-level separation. Accordingly, no training curve, independent accuracy or completed epoch count is invented in Chapter 4.

**After:** The seed-42 manifests partition NCT-CRC-HE-100K into 80,002 training and 19,998 validation images using stratified patch-level sampling. Manifest file hashes agree with the experiment configuration, and their relative image paths are disjoint. Training continued to 30 epochs despite the initial experiment directory name ending in 10ep; the checkpoint at epoch 26 had the lowest recorded validation loss. The training logs identify an NVIDIA L4, distinct from the CPU-only Windows application environment.

**Reason:** Add actual split, resume history, selection rule and training hardware without conflating environments.

## 47. 3.3.2 Classification model and training-reference audit — Original paragraph 347

**Before:** The separately supplied config.py describes a three-class thyroid workflow and cannot establish the colorectal class order or source tile scale. It is excluded as evidence for the nine-class CRC contract. Neither attachment establishes the physical magnification or original-pixel dimensions of every image used to train the actual classifier.

**After:** The formal nine-class run is identified by its manifests, completed metrics, checkpoint and test-7k outputs. Older three-class scripts and smoke-check experiments remain development materials and are not used to establish the CRC results. Training/validation file-path separation is verified; patient- or slide-level isolation requires grouping information not present in those manifests.

**Reason:** Select the correct experiment and state the actual granularity of separation.

## 48. 3.3.3 Classification preprocessing and resize provenance — Original paragraph 351

**Before:** The training attachment invokes Albumentations Resize without an explicit interpolation argument. Inspected library defaults are consistent with OpenCV linear, but the exact training library version is unavailable. Pillow bilinear and OpenCV INTER_LINEAR can differ in coordinate sampling, antialiasing and rounding; sharing a descriptive term such as “bilinear” is not proof of tensor identity. The implementation therefore preserves the legacy default and records the alternative, rather than changing preprocessing to improve the appearance of a particular prediction.

**After:** The recorded evaluation environment used Albumentations 1.3.1 and OpenCV 4.8.1. Its transform calls A.Resize(224, 224) without overriding interpolation, using the library’s default linear resize. Pillow bilinear and OpenCV INTER_LINEAR can differ in resampling and rounding; the application preserves its legacy Pillow default and records the selected backend. Section 4.3.4 therefore attributes the reported model metrics to the recorded Albumentations evaluation pipeline.

**Reason:** Use the newly available library versions and distinguish evaluation from application backend.

## 49. 3.3.4 Explicit classification modes and crop geometry — Original paragraph 356

**Before:** For W=3552, H=3536 and w=h=512, there are seven columns and seven rows, hence 49 tiles. The final column is 480 pixels wide and the final row is 464 pixels high. The bottom-right crop contains 222,720 pixels rather than 262,144 pixels. A deterministic fixture verifies this arithmetic and that all source pixels are covered once. It does not verify the predicted tissue classes of a real image.

**After:** For W=3552, H=3536 and w=h=512, Equation 3.1 gives seven columns and seven rows, or 49 tiles. The final column is 480 pixels wide, the final row 464 pixels high, and the bottom-right area 222,720 pixels. A deterministic fixture verifies these coordinates and complete non-overlapping coverage.

**Reason:** Keep the verified geometry and consolidate prediction limitations elsewhere.

## 50. 3.3.4 Explicit classification modes and crop geometry — Original paragraph 357

**Before:** The choice of source crop size changes the field of view presented to a fixed 224 × 224 network. A 512-pixel source crop resized to 224 is a different sampling operation from a native 224-pixel patch, unless acquisition scale and intended field of view establish equivalence. The interface therefore states that training scale is unconfirmed and that 512 × 512 is only an editable starting value.

**After:** Source crop dimensions determine the field of view before resampling to 224 × 224. The interface keeps this choice explicit and labels the 512 × 512 starting value as unconfirmed relative to training scale. The evaluation consequences are discussed in Section 4.5.3.

**Reason:** Reduce repeated scale disclaimers while retaining the interface’s actual claim.

## 51. 3.3.6 Segmentation pathway and label restoration — Original paragraph 370

**Before:** The built-in segmentation path uses independent defaults: source tile=1000, stride=512, network input=224 and batch size=1 on CPU. These must not be confused with the user-editable 512 × 512 classification source tiles. The generic compatible segmentation path processes its prepared tensor and restores an argmax label map through OutputParser; it does not use the classifier tile statistics.

**After:** My supervisor provided the segmentation model and the reference notebook predict-upernet-tme-tissue-overlap.ipynb; I did not participate in segmentation training. The notebook constructs a nine-label UPerNet using the openmmlab/upernet-swin-base configuration. Its large-image example uses source tile=1000 and stride=512, which are the application defaults; network input is 224 × 224. The application runs the path on CPU with batch size one, while the notebook example requests CUDA and its function defaults to batch size eight.

**Reason:** Establish the source and contribution boundary and distinguish actual example settings from function defaults.

## 52. 3.3.6 Segmentation pathway and label restoration — Original paragraph 371

**Before:** For the UPerNet path, tile_positions includes the final axis position so the complete source extent is covered. Images smaller than a source tile are reflect-padded for this segmentation pathway. Patches are resized with Pillow bilinear and ImageNet-normalised. Per-patch softmax probabilities are blended on a lower-resolution canvas using a two-dimensional Hann window with a small positive floor. The weighted result is normalised, converted to class labels, restored using nearest-neighbour interpolation and cropped to the original dimensions.

**After:** For the UPerNet pathway, the final window on each axis is aligned with the image edge. Images smaller than a source tile are reflect-padded. Each RGB patch is resized with Pillow bilinear, scaled to 0–1 and normalised with ImageNet mean (0.485, 0.456, 0.406) and standard deviation (0.229, 0.224, 0.225). Softmax probabilities are accumulated on a reduced-resolution canvas with a two-dimensional Hann window plus 0.001, normalised by accumulated weights, converted to labels and restored by nearest-neighbour interpolation before cropping to the original dimensions.

**Reason:** Describe the supplied reference algorithm precisely, independently of classification raw255.

## 53. 3.3.6 Segmentation pathway and label restoration — Original paragraph 375

**Before:** Custom-model compatibility remains constrained. Executable output validation does not guarantee semantically correct labels or arbitrary colour-map support. The built-in nine-label path is the documented reference; additional custom architectures/classes require matching metadata and explicit verification rather than assuming every segmentation model is supported.

**After:** The nine-label order and RGB colours in Table 3.4 match the reference notebook. Generic compatible segmentation models use a separate prepared-tensor and OutputParser pathway. The model filename’s 100ep and panoptils strings are retained as identifiers; training duration and dataset provenance are not inferred from those strings.

**Reason:** Verify the palette and prevent unsupported training claims from filenames.

## 54. 3.4.1 Principles and information hierarchy — Original paragraph 394

**Before:** Task and classification mode are visible before running. Status messages identify validation, inference, cancellation and completion. Completed result metadata remains distinct from a new pending selection. The design applies visibility, consistency, recognition and user control from the usability literature, but a claim of reduced cognitive load awaits the planned user evaluation.

**After:** Task and classification mode are visible before running. Status messages distinguish validation, inference, cancellation and completion, while completed-result metadata remains separate from a pending selection. These decisions apply visibility, consistency, recognition and user control from the usability literature (Nielsen, 1994; Yen & Bakken, 2012); their effect on perceived usability will be assessed through the planned UAT.

**Reason:** Tie design principles to sources and state the empirical question once.

## 55. 3.4.3 Control states, settings and help — Original paragraph 402

**Before:** Guide & Support provides numbered sections, a fixed Contents menu, previous/next buttons and a reading-aware section indicator. System Information displays read-only runtime/library/configuration text before copying it; the copy confirmation expires after 2.5 seconds. About reports version 1.0. These features improve discoverability, but they are not a substitute for observed participant understanding.

**After:** Guide & Support provides numbered guidance, persistent Contents navigation, previous/next actions and a reading-aware indicator. System Information displays runtime and dependency information before copying it, with confirmation expiring after 2.5 seconds. About reports version 1.0. Together these controls make configuration and support information discoverable within the application.

**Reason:** Remove repeated disclaimers from implementation description.

## 56. 3.4.4 Responsive windows and platform limits — Original paragraph 405

**Before:** Automated checks include small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. They verify Qt-level layout and state behaviour, not Windows-native title-bar buttons, taskbar docking or multi-monitor driver behaviour. Final Windows screenshots and the manual sequence “maximise → restore → resize smaller → maximise → restore” remain part of the acceptance checklist.

**After:** Automated checks cover small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The Windows record dated 19 October 2026 additionally records normal, maximised and minimised states with fullscreen=false in the reported normal/maximised entries. Section 4.3.3 distinguishes those observations from the remaining native acceptance tasks.

**Reason:** Integrate partial native evidence without claiming unrecorded restore or resize success.

## 57. 3.6.1 Development Testing — Original paragraph 427

**Before:** Unit testing is an independent verification of a single software component. In ZY-Path, unit testing can be applied in model loading, image preprocessing, inference execution, and SQLite operations.

**After:** Development verification combines component checks with cross-module tests using pytest and pytest-qt. The tests exercise model contracts, preprocessing, inference routing, persistence and user interaction at their observable interfaces.

**Reason:** Compress textbook definitions into the project’s actual method.

## 58. 3.6.1 Development Testing — Original paragraph 428

**Before:** Integration testing checks if there is any problem among modules after they are integrated. Since ZY-Path combines image processing, AI inference, database management, and graphical user interface (GUI) elements, integration testing verifies that data is seamlessly transferred across the entire inference pipeline.

**After:** Controlled cases use known in-memory networks, synthetic tensors and raster images, temporary SQLite databases and isolated QSettings stores. Real-file availability checks remain separate, so successful fixtures cannot substitute for the presence or validation of production model files.

**Reason:** Preserve the meaningful fixture/real-model distinction.

## 59. 3.6.1 Development Testing — Original paragraph 429

**Before:** Development tests use pytest and pytest-qt. Small in-memory networks, synthetic tensors, generated raster images, temporary SQLite databases and isolated QSettings files make failures reproducible without distributing the real large weights. These are test doubles with known behaviour, not placeholder production models. The real built-in paths are deliberately left unchanged so their missing-file failure remains visible.

**After:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.2 gives the host hardware and separates its installed GPU from the actual computation device.

**Reason:** Add the current real test environment and avoid a GPU acceleration claim.

## 60. 3.6.3 Manual System Testing — Original paragraph 437

**Before:** Required scenarios include startup with present/missing defaults; both classification modes; segmentation; cancel/close while busy; source/result comparison; Fit and 1:1; narrow/wide docking; maximise/restore; history retrieval and rerun after preferences change; deletion; PNG/PDF export; English calendar; and keyboard/padding clicks. The uploaded local Windows reports motivated corrections, but unstructured user observations are not recast as a completed formal acceptance protocol.

**After:** The acceptance cases include both classification modes, segmentation, cancellation, source comparison, Fit/1:1, narrow/wide transitions, maximise/restore, recorded rerun, deletion, export, calendar interaction and task-specific defaults. Development observations motivate regression cases; a formal case receives a Pass status only when its expected outcome has an execution record. The limited Windows observations currently available are reported in Section 4.3.3.

**Reason:** Replace external user-report narration and define evidence-based manual status.

## 61. 3.6.4 User Acceptance Testing (UAT) — Original paragraph 444

**Before:** A complete score requires all ten valid responses. Missing answers are not treated as zero and are not silently imputed. Report the number of valid SUS forms, mean, standard deviation and range; a median/IQR and a cautiously interpreted interval can be added for the small pilot. Feature ratings retain their own denominators and exclude “not used” responses rather than treating them as the lowest score.

**After:** Score each participant only when all ten responses are valid integers from 1 to 5, then calculate the sample mean, sample standard deviation, median and range; the IQR may also be reported. Missing items remain unscored. Independent and assisted task completion are separate outcomes, and feature ratings exclude Not used with their own denominators.

**Reason:** Align the UAT method with requested participant-level scoring and reporting.

## 62. 3.6.5 Testing Summary — Original paragraph 447

**Before:** The reported test baseline is the completed recorded run for the reviewed source revision, not a new unexecuted command. The complete suite was run with --continue-on-collection-errors so available tests still executed despite one missing-script collection failure. Passing, failed and collection-error counts are reported explicitly in Chapter 4. No tests were deleted, skipped or weakened to conceal these prerequisites.

**After:** Automated outcomes are identified by date, environment, command and revision. The historical Linux run used --continue-on-collection-errors and executed available cases. The latest Windows command did not use that option and stopped after a collection error, leaving no passing-test count for that invocation. Table 4.1 preserves both records without merging their counts.

**Reason:** Prevent transferring historical passes or command flags to the interrupted Windows run.

## 63. 3.6.6 Requirements Traceability Matrix — Original paragraph 449

**Before:** The matrix connects objectives, requirements, implementation and executable evidence. “Verified with fixtures” denotes software behaviour established without the real production weights. “Pending” is used for absent model, UAT, packaging or platform evidence. A requirement can be implemented while its real-weight or user-level acceptance remains incomplete.

**After:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify historical fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**Reason:** Update the matrix evidence categories.

## 64. 3.6.6 Requirements Traceability Matrix — Original paragraph 452

**Before:** This matrix is also a reporting control. A green UI test cannot change the status of missing weights, UAT or packaging to “verified”. Appendix C provides the evidence-file index, and Chapter 4 discusses the residual gaps against these requirements.

**After:** Appendix C indexes the supporting records. Fixture tests, model evaluation, native observations and UAT each address different acceptance questions, so the matrix records their scope separately.

**Reason:** Remove repeated defensive colour-test rhetoric.

## 65. 3.8 Summary — Original paragraph 459

**Before:** The methodology turns the CP1 workflow into an explicit, model-aware desktop implementation. Classification and segmentation use independent contracts; tiled classification preserves actual source areas; history restores recorded analysis settings; and the GUI supports controlled cancellation and spatial inspection. The evaluation plan separates fixture-based engineering evidence from the real-weight, Windows-native and user studies that remain necessary. Chapter 4 reports only the results supported by the available evidence.

**After:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses historical controlled tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**Reason:** Reflect newly available completed classification and Windows evidence.

## 66. 4.1 Introduction — Original paragraph 462

**Before:** This chapter reports the implemented software and its available verification results. The evidence baseline is source revision 1f3e01e on codex-ready-2026-10-15 and the corresponding recorded pytest logs dated 17 October 2026. Screenshots captured in the cloud are Linux/Qt development views. Where generated images or known synthetic outputs are used, they demonstrate interface behaviour only and are labelled accordingly.

**After:** This chapter reports implementation and evaluation at application revision 1f3e01e. It combines the historical Linux/offscreen-Qt tests of 17 October 2026, the Windows test and launch record of 19 October 2026, and the classification training/evaluation outputs. Development captures identify their environment; figures derived from synthetic fixtures are distinguished from real-model results.

**Reason:** Remove branch and cloud wording while retaining dates and environment distinctions.

## 67. 4.1 Introduction — Original paragraph 463

**Before:** The evidence does not include real model weight files in this checkout, independent classification/segmentation evaluation, completed UAT responses or a verified clean-machine Windows executable. These are material limits. The chapter therefore distinguishes implemented functionality, controlled verification, reported Windows observations and pending acceptance evidence instead of presenting all requirements as unconditionally passed.

**After:** Results are organised into implementation behaviour, automated verification, Windows runtime observations, classification performance and the planned UAT. The evidence boundaries, including segmentation evaluation, performance measurement and deployment, are consolidated in Section 4.5.3.

**Reason:** Replace obsolete evidence-absence claims and centralise limitations.

## 68. 4.2.1 Implemented workflow and scope — Original paragraph 467

**Before:** The application remains usable through source execution on Windows, as reported by the project user. That observation is distinct from a packaged executable test. The current repository has no verified distributable build, and the real built-in files are absent from the cloud checkout. The implementation result is therefore a source-based application with substantial automated evidence and remaining deployment prerequisites.

**After:** The Windows session on 19 October 2026 launched the application from its virtual environment and recorded successful loading and validation of crc_dn21_seed42_best.pth as a nine-class DenseNet with output shape (1, 9). This establishes source-based startup and classifier integration for that session. The observed workflow and window states are detailed in Section 4.3.3.

**Reason:** Use the concrete recorded startup result without claiming all application tasks ran.

## 69. 4.2.2 Classification results and spatial inspection — Original paragraph 473

**Before:** Figure 4.2. Tiled classification interface with source/result comparison and the revised result toggles. Linux/Qt capture using synthetic source/output data; not a real-weight or diagnostic result.

**After:** Figure 4.2. Tiled classification interface with source/result comparison and revised result toggles. Source: author’s Linux/offscreen-Qt development capture; synthetic fixture, not a model result.

**Reason:** Identify the source and explicitly label the synthetic fixture.

## 70. 4.2.2 Classification results and spatial inspection — Original paragraph 475

**Before:** A previously reported Windows run used a 3552 × 3536 source with 512 × 512 crops and yielded 49 tiles, predominantly STR. The count is consistent with the geometry, but the class distribution alone cannot validate the prediction. The code/test audit verifies actual source cropping, RGB/raw255 preparation, ordered softmax probabilities and area accounting under controlled fixtures. Without the real weights, source image and independent tissue annotations, it cannot decide whether that reported distribution reflects tissue content, scale/domain effects or predictive error.

**After:** The 3552 × 3536 geometry example produces 49 crops at a 512 × 512 setting, with smaller right and bottom edges. Controlled tests verify unique source crops, RGB/raw255 preparation, class order, edge handling and area conservation. The tissue accuracy of a tiled map requires a separately defined ground-truth and scale protocol; the patch-classification results in Section 4.3.4 do not measure that map.

**Reason:** Separate the geometry fixture and patch evaluation without relying on informal earlier prediction observations.

## 71. 4.2.3 Segmentation results — Original paragraph 478

**Before:** The UI and large-image segmentation algorithm have controlled regression coverage, including output dimensions, class counts and blending behaviour. The supplied config.py is not evidence for this segmentation model, and the project does not infer segmentation accuracy from a matching classification region. A real-weight screenshot and a labelled evaluation set are required for stronger conclusions.

**After:** The reference notebook establishes the segmentation architecture, preprocessing, labels and probability-fusion procedure. Controlled software tests cover restored dimensions, class counts and blending behaviour. Segmentation predictive performance is treated separately: annotated-mask metrics were not available for this model, as discussed in Section 4.5.3.

**Reason:** Use the actual segmentation evidence and remove irrelevant three-class config discussion.

## 72. 4.2.5 Settings, cancellation and interface polish — Original paragraph 488

**Before:** Figure 4.7. Implemented Guide & Support page with fixed Contents navigation and numbered guidance. Linux/Qt development capture; contact/guide content is interface evidence rather than UAT feedback.

**After:** Figure 4.7. Implemented Guide & Support page with persistent Contents navigation and numbered guidance. Source: author’s Linux/offscreen-Qt development capture; this is interface evidence.

**Reason:** Replace cloud/AI-review wording with a clear source and environment.

## 73. 4.2.5 Settings, cancellation and interface polish — Original paragraph 491

**Before:** Figure 4.8. English history-calendar popup under a simulated Chinese default locale. Linux/Qt capture; the selected date is test input.

**After:** Figure 4.8. English history-calendar popup with a simulated Chinese default locale. Source: author’s Linux/offscreen-Qt development capture; the selected date is test input.

**Reason:** Use a neutral environment and source description.

## 74. 4.3.1 Recorded automated results — Original paragraph 496

**Before:** The complete recorded command used pytest -q --continue-on-collection-errors --tb=short with QT_QPA_PLATFORM=offscreen and isolated writable application/configuration/cache directories. The command completed with a non-zero exit status because two known prerequisites remained missing. The final summary was “1 failed, 355 passed, 14 warnings, 1 error in 110.70s”. The duration is test-suite execution time in the cloud, not a per-image inference benchmark.

**After:** The latest Windows invocation on 19 October 2026 collected 356 items and encountered one collection error in tests/test_train_crc_resume.py. Execution stopped during collection: the summary reported 13 warnings and 1 error in 24.76 seconds, with exit code 2. No passing or executed-failure count was obtained for this invocation. The command did not include --continue-on-collection-errors.

**Reason:** Replace the old run as the current result without inventing passes or counting an unobserved weight failure.

## 75. 4.3.1 Recorded automated results — Original paragraph 497

**Before:** Table 4.1. Recorded automated verification outcomes at revision 1f3e01e

**After:** Table 4.1. Automated verification records by date and environment at revision 1f3e01e

**Reason:** Make the historical/latest distinction explicit in the table title.

## 76. 4.3.1 Recorded automated results — Original paragraph 499

**Before:** These runs overlap; their counts must not be added as if they represented independent test cases. A collection error can prevent a module's tests from being discovered, so a pass percentage based simply on 355/(355+1+1) would be misleading. The outcome supports the available executable cases while preserving the incomplete collection and missing production artifacts.

**After:** The earlier Linux/offscreen-Qt full run dated 17 October used pytest -q --continue-on-collection-errors --tb=short and recorded 355 passed, 1 failed, 14 warnings and 1 collection error in 110.70 seconds. Related regression and simulated-DPI runs are subsets, not additional passes. Both 110.70 and 24.76 seconds measure pytest invocations, not image inference.

**Reason:** Retain the historical record in its own scope and prevent pass/time aggregation.

## 77. 4.3.1 Recorded automated results — Original paragraph 501

**Before:** Figure 4.10. Recorded pytest command/outcome excerpt and scope notes. Reproduced from saved logs for the reviewed revision; not a model-performance chart.

**After:** Figure 4.10. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.1.

**Reason:** Stop the old test figure from implying it is the latest Windows result.

## 78. 4.3.1 Recorded automated results — Original paragraph 502

**Before:** The failed case is tests/test_main_window_inference.py::test_default_builtin_paths_keep_real_classification_and_segmentation_models. Its assertion fails because models/crc_dn21_seed42_best.pth is absent. The segmentation real-weight file is also absent from the checkout, but this failing assertion first reports the classification path. No real model was manufactured to make this availability test pass.

**After:** The historical failed case was test_default_builtin_paths_keep_real_classification_and_segmentation_models in tests/test_main_window_inference.py, which first reported the absent classification weight in that Linux installation. This failure belongs to the historical run. The later Windows collection interruption provides no observation of that case’s outcome, while the separate application log records successful loading of the real classifier.

**Reason:** Separate the historical missing-weight failure from current Windows statistics.

## 79. 4.3.1 Recorded automated results — Original paragraph 503

**Before:** The collection error occurs in tests/test_train_crc_resume.py when it attempts to read models/dn21_folder_classification/train_crc_dn21 (1).py. The separately uploaded train_crc_dn21.py is useful reference material, but it was not copied into this expected path to disguise the repository problem. No tests were deleted, skipped or reported as passing through import bypasses.

**After:** The current collection error is FileNotFoundError for models/dn21_folder_classification/train_crc_dn21 (1).py. During collection, tests/test_train_crc_resume.py reads that path and extracts normalize_model_settings and validate_resume_config through AST. The actual training script is available in the research materials, but its absence at the repository’s expected path remains a test prerequisite to reconcile. The 13 warnings concern Matplotlib use of Pyparsing parseString, resetCache and enablePackrat deprecated interfaces.

**Reason:** Explain the exact current error and warnings without copying files or weakening tests.

## 80. 4.3.2 Challenges, resolutions and evidence — Original paragraph 507

**Before:** The resolutions address reproducible implementation defects or ambiguity. They do not use segmentation as classification ground truth, change a model to force expected tissue proportions or hide errors by reducing the test scope. The traceability matrix reflects these limits: F04–F05 and F07 have strong controlled evidence, while model accuracy, clean packaging and empirical usability remain separate open items.

**After:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.3.4, and Table 3.6 retains the environment-specific scope of the software tests. The current collection error prevents a claim that the latest Windows full suite passed.

**Reason:** Update the evidence summary and avoid stale all-metrics-pending wording.

## 81. 4.3.3 Manual and predictive validation status — Original paragraph 508

**Before:** 4.3.3 Manual and predictive validation status

**After:** 4.3.3 Windows startup and window-state observations

**Reason:** Name the actually recorded native evidence.

## 82. 4.3.3 Manual and predictive validation status — Original paragraph 509

**Before:** Windows user observations were valuable because offscreen Qt tests had not exposed every native layout problem. Their role was to trigger diagnosis and regression cases, not to establish a completed clinical or usability study. The current evidence package still requires a documented final native run at the reviewed revision, with normal/maximised windows, narrow/wide docking, representative display scales and real model/input artifacts.

**After:** The Windows command .\.venv\Scripts\python.exe main.py recorded loading and validation of the built-in classifier around 14:23:46 on 19 October 2026. Loading completed with source=checkpoint; validation identified DenseNet, task=classification, nine classes and output shape (1, 9), and MainWindow accepted the result. A TypedStorage deprecation warning preceded successful loading. PowerShell’s NativeCommandError wrapper included an INFO message and was followed by continuing application logs, so that wrapper alone is not treated as an application crash.

**Reason:** Describe exactly what the application record establishes and interpret stderr wrapping correctly.

## 83. 4.3.3 Manual and predictive validation status — Original paragraph 510

**Before:** There is no verified independent accuracy, macro-F1, confusion matrix, calibration metric, segmentation Dice or IoU for the integrated real models. The proposal's statement of accuracy above 94% cannot be retained as a project result. Published NCT results describe the published experiments; the training script's metric calculations describe intended measurement; neither supplies this project's missing evaluation outputs.

**After:** The recorded Qt platform is windows, with devicePixelRatio=2.0 and availableGeometry=[0, 0, 1280, 758] in logical coordinates. A normal-window entry gives geometry=[641, 26, 638, 731], frame=[640, 0, 640, 758] and minimum=[320, 240]. The state record includes normal (maximized=false, fullscreen=false), subsequent maximisation (maximized=true, fullscreen=false) and a later minimised entry. These are observed state transitions; no physical monitor resolution is derived from the logical geometry.

**Reason:** Use the supplied window measurements without inferring physical resolution or extra successful actions.

## 84. 4.3.3 Manual and predictive validation status — Original paragraph 511

**Before:** The supplementary evaluation checklist specifies model checksum, source dataset/manifests, patient/slide-level separation, preprocessing/backend, source scale, per-class support and independently generated metrics. These details are prerequisites for attributing any future number to the actual deployed model.

**After:** This session establishes startup, real-classifier structural validation and the stated window-state observations. It contains no completed image inference or formal all-feature acceptance record. Restore after maximisation, edge dragging, restart geometry restoration, clipping checks and normal exit remain acceptance cases in Appendix D.

**Reason:** Bound the Windows evidence to actual recorded actions.

## 85. 4.4 User Acceptance Testing Results — Original paragraph 513

**Before:** UAT has not yet been conducted or supplied. This section is structured for the actual results and includes explicit fields rather than simulated participants, fabricated percentages or invented quotations. The instrument and scoring workbook are complete, but an empty template is not an empirical finding. Until data are collected, H2 and the user-performance aspect of H3 remain untested.

**After:** UAT results await collection. Appendix B provides the tasks, questionnaire and scoring rules; the tables below reserve the actual participant and outcome data. H2 and the user-performance component of H3 will be assessed after those responses are available.

**Reason:** Keep necessary UAT placeholders with concise academic wording.

## 86. 4.4.4 System Performance and Acceptability — Original paragraph 529

**Before:** The saved 110.70-second pytest duration is not suitable for this subsection as an inference-time result. Similarly, a single reported 0.6-second Windows prediction, without a fixed protocol and hardware/context, cannot establish a general latency claim.

**After:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the historical Linux suite duration of 110.70 seconds is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**Reason:** Update the timing caveat to the current records and remove an unsupported historic single-run comparison.

## 87. 4.4.5 Qualitative Feedback Analysis — Original paragraph 533

**Before:** The Windows feedback already used during development is reported in Section 4.3 as informal defect evidence. It is not combined with future UAT survey responses as if both came from the same sampling protocol. This separation keeps design iteration useful without overstating the formality of the current usability evidence.

**After:** Development observations and the Windows startup/state record are discussed in Section 4.3.3. UAT responses will be analysed under the participant and task protocol in Appendix B rather than pooled with those engineering observations.

**Reason:** Separate informal development observations from future UAT without external user-report wording.

## 88. 4.5.1 Achievement of Research Objectives — Original paragraph 538

**Before:** The most defensible achievement is implementation feasibility under a constrained contract. The system now exposes choices that the proposal either assumed or left implicit, including the distinction between source tile size and network input, backend-specific resizing and tile coverage versus global confidence. These are substantive engineering outcomes even though they do not establish diagnostic performance.

**After:** The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. Classification evaluation supplies additional model evidence, while the latest Windows record supplies startup and state evidence under a CPU-only runtime.

**Reason:** Update the achievement discussion with completed evidence.

## 89. 4.5.1 Achievement of Research Objectives — Original paragraph 539

**Before:** H1 is supported in the controlled software setting. The correctness components of H3 are also supported by restoration and rerun tests. H2 and claims about reduced time/cognitive load require actual users, while deployment-level acceptance requires the missing artifacts and native checks. The report therefore avoids calling every objective fully validated.

**After:** H1 is supported at the controlled implementation level and by successful real-classifier loading on Windows. Historical restoration and rerun tests support the technical component of H3. H2 and user-efficiency claims await UAT; the interrupted latest test run and remaining deployment checks qualify the level of system acceptance.

**Reason:** Avoid treating structural startup as completed inference or full objective validation.

## 90. 4.5.3 Limitations and Constraints — Original paragraph 544

**Before:** First, the system depends on pretrained PyTorch models provided by users or default model and does not include model training functionality.

**After:** The application integrates trained models and provides no GUI training or annotation workflow. I trained and evaluated the classifier separately; the segmentation model and reference notebook were provided by my supervisor. Segmentation training data, optimisation settings and Dice/IoU results were not available. The checkpoint filename is therefore used as an identifier rather than evidence of its dataset or completed training epochs.

**Reason:** Replace numbered boilerplate with the actual training contribution and unavailable segmentation provenance.

## 91. 4.5.3 Limitations and Constraints — Original paragraph 545

**Before:** Third, collaborative annotation and multi-user access are not supported because the system focuses on standalone desktop deployment.

**After:** Large raster-image tiling is implemented, extending the original proposal, but native WSI pyramid reading, memory-bounded streaming and physical-scale extraction remain outside scope. Full-size source arrays, maps and restored masks consume memory. Source tile dimensions are editable, and the 512 × 512 classification starting value has no established physical-scale equivalence to the training images; non-square edge crops are resized anisotropically to the network input.

**Reason:** Restore the missing whole-slide limitation and explain the raster/WSI distinction.

## 92. 4.5.3 Limitations and Constraints — Original paragraph 546

**Before:** Fourth, prediction performance is dependent on the quality, architecture, and training data of the supplied AI models.

**After:** The classifier evaluation uses a stratified patch-level training/validation split and a separately named CRC-VAL-HE-7K test collection. Relative filenames are disjoint, but the available manifests do not establish patient- or slide-level isolation or rule out image-content duplicates. The 90.68% accuracy and 88.59% macro-F1 describe the recorded Albumentations test pipeline. The application’s legacy Pillow backend and arbitrary larger source crops may present different inputs; calibration, tiled-analysis ground truth and clinical generalisation were not evaluated.

**Reason:** Consolidate predictive limitations and distinguish recorded evaluation from every application mode.

## 93. 4.5.3 Limitations and Constraints — Original paragraph 547

**Before:** Finally, the system is intended for educational and research purposes only and should not be considered a replacement for professional medical diagnosis.

**After:** Software verification is incomplete across environments. The historical Linux run preserves its 355 passes, one failed availability check and one collection error; the latest Windows invocation stopped during collection with one error and no pass count. The later clean-worktree check is a post-test observation, and no corresponding post-check HEAD output was provided. Passing fixtures and observed window states cannot fill those missing execution records.

**Reason:** State the exact current and historical test limits, including the post-test provenance caveat.

## 94. 4.5.3 Limitations and Constraints — Original paragraph 548

**Before:** Additional CP2 limitations are material. Real classification and segmentation weights are missing from the cloud environment, and the resume-test collection depends on an absent script. The attached training code does not identify the original source scale or supply completed training/evaluation logs. The editable classification tile size is exploratory, and anisotropic resizing of non-square edge crops can alter morphology presented to the model.

**After:** The Windows application record establishes startup and classifier validation, followed by normal, maximised and minimised states. It does not establish completed inference for either task, maximise-to-restore behaviour, manual resizing, all-control visibility or normal exit. Native acceptance, assistive-technology checks and UAT remain to be completed. No coverage percentage was produced by the recorded test commands.

**Reason:** Group the native acceptance and accessibility limitations without adding unexecuted passes.

## 95. 4.5.3 Limitations and Constraints — Original paragraph 549

**Before:** Large raster tiling does not provide native gigapixel WSI streaming. Full-size source arrays, class maps and restored masks still consume memory, and the UPerNet probability canvas has its own resource cost. GPU inference, batched classification and whole-slide physical-scale extraction are not established runtime features. CPU timings depend on the actual model and hardware; none are generalised from the test suite.

**After:** Performance and deployment also remain unverified. Although the Windows hardware is documented, no repeated stage-level benchmark separates loading, preprocessing, forward inference, fusion/statistics, GUI display, saving and export. The installed RTX 4060 was not used by PyTorch 2.1.2+cpu. There are no PyInstaller build records, matched packaged artifacts, clean-machine acceptance records or offline deployment checks, so source execution is the present delivery level.

**Reason:** Use actual CPU runtime and preserve all unmeasured deployment/performance boundaries.

## 96. 4.5.3 Limitations and Constraints — Original paragraph 550

**Before:** Structural validation cannot guarantee semantic class correctness, calibration or file safety. The generic custom-model workflow is limited to supported input/output conventions and implementation-tested label handling. Full pickled modules may need their defining Python classes and carry deserialisation risks. There is no universal architecture loader, clinical validation or secure sandbox.

**After:** Structural model checks establish supported tensor and metadata conventions, not semantic label accuracy, calibrated confidence or file safety. Full pickled modules can require their original Python classes and execute code during deserialisation. Use is restricted to trusted model sources; the application is an educational/research integration without clinical validation or a model-security sandbox.

**Reason:** Consolidate compatibility, security and clinical-use limits.

## 97. 4.5.3 Limitations and Constraints — Original paragraph 551

**Before:** History references mutable filesystem paths and is not a complete provenance archive. It does not guarantee that the bytes at a path are unchanged. There is also no implemented automatic backup, multi-user access control or atomic transaction encompassing all external artifacts. A completed record improves traceability but is not a certified clinical audit trail.

**After:** History references mutable filesystem paths and does not provide immutable per-run file identities, automatic backup, multi-user access control or an atomic transaction covering all external artifacts. It supports local workflow continuity rather than a certified clinical audit trail. These are specific persistence and collaboration limits of the implemented design.

**Reason:** Consolidate provenance and standalone-workflow constraints.

## 98. 4.5.3 Limitations and Constraints — Original paragraph 552

**Before:** Finally, offscreen Qt and DPI simulations do not prove final Windows-native docking, window-manager or assistive-technology behaviour. The latest controls/calendar changes have repeatable input tests and screenshots, but a final native acceptance pass is still required. No UAT responses, independent metrics, coverage percentage or clean-machine executable evidence are supplied.

**After:** The archived evidence includes the Windows pytest text/XML outputs, exit-code file, saved commit, environment records and application log, alongside the classification experiment files. The post-test clean-worktree observation is documented separately because no git-status.txt or accompanying post-check HEAD output was saved. Appendix C distinguishes those direct artifacts from the later observation.

**Reason:** Use newly received original logs and preserve the post-test provenance caveat.

## 99. 4.5.4 Implications for Future Development — Original paragraph 554

**Before:** Future work should first close the evidence gaps rather than add unrelated features. Confirm model provenance and training/source scales, restore the missing test prerequisite, evaluate real models on independently separated data and collect the planned user study. These steps determine whether the implemented workflow is fit for its intended educational/research use.

**After:** The immediate priorities are to reconcile the expected training-script path and rerun the full suite, complete the Windows acceptance cases and UAT, and establish patient/slide grouping and source scale for further model evaluation. Segmentation evaluation requires authorised aligned masks and confirmed label provenance. These tasks address identified uncertainty before adding new features.

**Reason:** Reflect completed classification evaluation and prioritise actual remaining gaps.

## 100. 4.6 Summary — Original paragraph 558

**Before:** The implementation delivers a substantial local inference workflow and controlled evidence for its crop geometry, state handling, inspection and persistence semantics. The recorded full-suite outcome is 355 passed, one failed and one collection error; the unresolved prerequisites remain explicit. UAT, independent model accuracy, final native acceptance and clean packaging are incomplete, so the conclusions are limited to demonstrated software behaviour and a prepared evaluation plan.

**After:** ZY-Path implements local model-aware inference, spatial inspection and record continuity. The classifier’s recorded 7,180-image evaluation gives 90.68% accuracy and 88.59% macro-F1. Historical Linux tests and the latest Windows invocation retain separate outcomes: the latter stopped during collection with one error and no pass count. Windows startup and real-classifier validation were recorded; formal UAT, remaining native acceptance, performance benchmarking and clean-machine packaging are further evaluation activities.

**Reason:** Synchronise the chapter summary with all current evidence streams.

## 101. 5.1 Conclusion — Original paragraph 563

**Before:** Controlled verification supports many of these implementation claims. At the reviewed revision, 355 tests passed, one real-file availability test failed and one missing-script collection error remained. Related controls/history/layout regressions and simulated DPI checks passed. These outcomes should not be converted into a claim of complete deployment readiness or clinical accuracy: the real model artifacts, independent model metrics, UAT responses and final Windows acceptance evidence are not included.

**After:** The classification evaluation recorded 6,511 correct predictions from 7,180 images, corresponding to 90.68% accuracy and 88.59% macro-F1. Historical Linux tests provide controlled software evidence. On 19 October 2026, Windows pytest stopped during collection with one error and no obtained pass count, while a separate application session successfully loaded and validated the real nine-class classifier. These outcomes support distinct parts of the implementation and its evaluation, as detailed in Chapter 4.

**Reason:** Update the conclusion without conflating prediction accuracy, test passes and startup validation.

## 102. 5.1 Conclusion — Original paragraph 564

**Before:** The research questions are consequently answered at different levels. A model-aware local GUI workflow is technically feasible and implemented. The recorded restoration/rerun logic supports workflow continuity under stable files and dependencies. Whether the interface improves users' interpretation, satisfaction or efficiency remains an empirical question for the prepared UAT. The project's conclusion is therefore a demonstrated engineering integration with clearly identified evaluation limits.

**After:** The research questions are answered at different levels. A model-aware local GUI workflow is implemented, and recorded restoration/rerun logic supports continuity under stable files and dependencies. Classification has a documented test result; perceived usability, interpretation and efficiency remain questions for the planned UAT. The contribution is an integrated research/education workflow whose acceptance and deployment boundaries are specified in Section 4.5.3.

**Reason:** State the completed work positively with one limitations cross-reference.

## 103. 5.2 Future Work and Recommendations — Original paragraph 566

**Before:** The immediate priority is evidence completion. Supply the verified built-in weights and cached configuration; reconcile the absent resume-test script with the intended repository layout; capture final Windows runs at the reported commit; and perform independent model evaluation with known patient/slide separation, source scale and preprocessing. No software test should be removed to make this process appear complete.

**After:** The first priority is completing verification: restore the genuine training script at the intended repository location, record a new full-suite result, finish Windows acceptance and evaluate segmentation with authorised ground truth if it becomes available. Further classifier studies should document patient/slide separation, source scale, calibration and application backend effects. Test assertions and error reporting should be preserved throughout.

**Reason:** Replace obsolete requests for already supplied classification results.

## 104. 5.3 Research Contributions — Original paragraph 574

**Before:** The fourth contribution is an auditable evaluation package. Requirements are connected to source modules and named tests; missing prerequisites remain failures/errors; and a complete UAT instrument, scoring template and screenshot/evaluation checklist support subsequent evidence collection. These are software-engineering contributions and reusable evaluation materials, not a novel neural architecture or a clinically validated diagnostic method.

**After:** The fourth contribution is an auditable evaluation package connecting requirements, named software tests, the classification training/test outputs and platform-specific execution records. It includes per-class metrics and a confusion matrix, explicit unresolved test prerequisites, and prepared UAT instruments. The work contributes an engineering integration and its documented evaluation rather than a new neural architecture.

**Reason:** Add actual model evaluation evidence and reduce repeated clinical disclaimers.

## 105. 5.4 Summary — Original paragraph 576

**Before:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Its present contribution is best understood as an inspectable research/education application supported by controlled software evidence. Completing independent predictive evaluation, UAT, native acceptance and verified packaging will determine the strength of future claims about usability, generalisation and deployment readiness.

**After:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the historical controlled tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**Reason:** Update the final summary with completed classification and partial native evidence.

## 106. A.1 Proposal baseline — Original paragraph 609

**Before:** The following planning tables are retained from CP1 as historical proposal baselines. Their week labels describe the plan at that stage; they are not retrospectively presented as actual implementation dates or proof that every planned evaluation was completed. In particular, the proposed accuracy study, UAT and executable packaging still require the evidence identified in this report.

**After:** Tables A.1 and A.2 retain the CP1 planning baseline as a historical record. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

**Reason:** Explicitly quarantine conflicting CP1 planning text without rewriting the historical proposal.

## 107. A.3 Completion sequence — Original paragraph 618

**Before:** Before final submission, first confirm the cover fields and research-document requirements, then capture current Windows evidence and assemble authorised model/data artifacts. Resolve the missing repository prerequisite without bypassing its test. Next conduct independent model evaluation and the consented UAT pilot, update Chapter 4 with actual results, and revise Chapter 5 only to the extent those results justify. Finally update contents/figure/table fields, check citations and screenshots, and validate the packaged application if distribution is claimed.

**After:** Before submission, confirm the cover fields, complete authorised Windows screenshots and UAT, reconcile the missing test prerequisite and record a new full-suite result. Retain the classification evaluation and add any supported segmentation evidence. Update conclusions only from actual findings, then refresh document fields and apply the agreed final formatting. Verify a clean-machine package before claiming executable distribution.

**Reason:** Update the completion sequence and respect content-before-format workflow.

## 108. C.1 Source baseline — Original paragraph 651

**Before:** Repository: ziaozhuanxing/ZY-Path. Branch: codex-ready-2026-10-15. Reviewed revision: 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. The thesis artifact preparation did not change application source or push a new revision. The supplied CRC training script and unrelated three-class config are external reference attachments, not newly installed production models.

**After:** Repository: ziaozhuanxing/ZY-Path. Application branch: codex-ready-2026-10-15. Recorded test revision: 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Windows project: E:\ZY-PATH. Windows evidence directory: E:\ZY-PATH-evidence\20261019-142119. A later git status --porcelain=v1 --untracked-files=all produced no output, establishing a clean worktree at that later check. git-status.txt was not created during testing; no post-check git rev-parse HEAD output was provided, so the later HEAD is not represented as independently reverified.

**Reason:** Keep complete branch/hash and local evidence paths in the appendix and preserve temporal provenance.

## 109. C.2 Evidence interpretation — Original paragraph 655

**Before:** The full log establishes what executed and what did not. The related/scale logs are subsets and are not additive. Generated images and known synthetic outputs establish geometry, display and state behaviour; they do not establish tissue accuracy. Previous Windows reports establish observed issues and one local launch, but do not supply the final formal acceptance log for all features. The pending-evidence checklist identifies what still needs to be collected.

**After:** The archived Linux logs preserve the 17 October outcomes. The Windows originals include pytest-full.log, pytest.xml, pytest-exit-code.txt, commit.txt, windows-app.log, dependencies.txt, hardware.txt, python-version.txt, runtime-device.txt and test-date.txt. The text log and XML agree on one collection error, and the exit file records 2; JUnit tests=1 represents the collection-error entry, not one passed test or 356 executed tests. The XML duration is 24.755 seconds and the console rounds it to 24.76. Classification records support recomputed CSV consistency and checkpoint identity; the author confirms that the deployed file was renamed from that checkpoint. Model inference was not rerun as part of this consistency verification.

**Reason:** Cross-check received text/XML/exit records and prevent misreading the JUnit summary.

## 110. D.1 Native acceptance record — Original paragraph 658

**Before:** For each case record actual date, tester, application commit, Python/version, Windows build, CPU/RAM, display scale, available screen geometry, sample/model identifier, expected outcome, actual outcome and evidence filename. Use Pass, Fail, Blocked or Not run. Do not mark a case Pass because a Linux offscreen equivalent passed.

**After:** For each acceptance case record date, tester, revision, Windows/Python/dependency versions, hardware, Qt display metrics, model/input identity, expected outcome, actual outcome and evidence file. The 19 October record provides partial W01 startup evidence and partial W02 window-state evidence; restoration and the full action sequences remain unverified. The remaining cases in Table D.1 have no completed acceptance outcome in this record. Their criteria must not be converted into Pass entries from Linux fixture results.

**Reason:** Record partial native acceptance against the actual case list without inventing formal passes.

## 111. E.1 Classification — Original paragraph 665

**Before:** Before evaluation, record the actual checkpoint checksum, architecture/configuration, class order, preprocessing profile, backend/library versions and input dimensions. Identify the labelled dataset version, patient/slide grouping, source image scale and any overlap with training or tuning data. File-path disjointness alone is not evidence of patient-level independence.

**After:** The completed classification evaluation used CRC-VAL-HE-7K with 7,180 labelled images. The selected epoch-26 checkpoint SHA-256 is 8f89bd825641fba276066b54432b5d73a62b11ed6c0d70bb94c9f0bc7e2fe325; the experiment file best_model.pth was renamed crc_dn21_seed42_best.pth for application use. The hash of the experiment checkpoint agrees with its evaluation summary. The original dataset URL is https://zenodo.org/records/1214456; the manifests identify NCT-CRC-HE-100K for training/validation and CRC-VAL-HE-7K for testing.

**Reason:** Replace a purely future protocol with the completed evaluation identity and provenance.

## 112. E.1 Classification — Original paragraph 666

**Before:** For single-image classification, compute a confusion matrix, per-class support, precision, recall and F1, macro-F1 and accuracy on the specified independent set. State whether images are native patches or resized larger regions. If tiled analysis is evaluated, define its ground-truth unit and sampling scale separately; an image-level class label cannot validate every tile or a pixel-coverage map. If calibration is claimed, supply an explicit calibration protocol and metric rather than interpreting softmax confidence as calibration.

**After:** The recorded test preprocessing was OpenCV RGB decoding followed by Albumentations 1.3.1 Resize(224, 224), ToTensorV2 and float32 raw255, with OpenCV 4.8.1. The environment record lists Python 3.10.22, PyTorch 2.1.2+cu121, torchvision 0.16.2+cu121 and scikit-learn 1.3.2. Accuracy, macro-F1, class metrics and confusion counts were recomputed from the prediction CSV and agree with the report. Future evaluations should document patient/slide grouping, content-duplicate checks, physical scale and backend equivalence, and define separate ground truth for Tiled analysis.

**Reason:** Report available evaluation settings and reserve genuinely uncompleted checks.

## 113. E.2 Segmentation — Original paragraph 668

**Before:** Use authorised independently annotated masks with the same class vocabulary. Record the original spatial scale, label alignment, ignored/background policy, tile/stride/input settings and restoration method. Compute per-class IoU/Dice and aggregate values with clear denominator/exclusion rules. Classification outputs must not serve as segmentation ground truth, and a visually pleasing overlay does not substitute for expert-labelled masks.

**After:** The supervisor-provided inference notebook establishes the model configuration and label mapping but contains no independently annotated test-set evaluation. The segmentation training dataset, training procedure and Dice/IoU report were not obtained. A future evaluation requires authorised aligned masks, patient/slide separation, the same label vocabulary, an explicit ignored-label policy and recorded tile/stride/input settings; per-class and aggregate IoU/Dice should then be calculated with documented denominator rules.

**Reason:** State the confirmed absence of segmentation training and accuracy evidence.

## 114. E.3 Runtime and deployment — Original paragraph 670

**Before:** Benchmark a predefined set of source dimensions and tile settings on a recorded CPU/RAM/OS environment. Separate cold model loading, preprocessing/inference, artifact saving and export. Repeat runs under a fixed protocol and report appropriate distribution summaries and peak memory. The whole pytest duration must not be used as per-image inference time. A clean-machine package test should verify required weights/configuration, file permissions, offline operation and both tasks before executable deployment is described as complete.

**After:** Use the documented Windows CPU environment as a benchmark baseline, fixing source dimensions, model, classification mode, resize backend and tile settings. Time cold model loading separately from warm repeated runs; measure preprocessing, forward inference, reconstruction/statistics, GUI display, saving and export as distinct stages. Report repeat count, mean, sample standard deviation, median and range, with memory measurements where available. The recorded pytest durations are excluded from inference timing. Packaging verification additionally requires a matched PyInstaller build record and artifact revision, clean-machine task checks and an offline dependency test; these remain planned activities.

**Reason:** Specify the requested future performance/deployment protocol without filling unmeasured values.

## 115. Existing table 1, row 6, column 3 — Table cell

**Before:** Narrower raster-image scope; independent accuracy, UAT and packaging validation remain pending

**After:** Focused raster-image workflow; classifier evaluated on 7,180 test images; UAT and package validation pending

**Reason:** Reflect actual classifier evaluation in the platform comparison.

## 116. Existing table 3, row 4, column 3 — Table cell

**Before:** Windows-native behaviour still requires final device verification

**After:** Partial native state observations recorded; complete device/accessibility acceptance pending

**Reason:** Use partial Windows evidence without implying all layout checks passed.

## 117. Existing table 3, row 7, column 3 — Table cell

**Before:** Real weights/cache/package completeness are not verified in this checkout

**After:** Real classifier loads on Windows; complete offline package and clean-machine deployment unverified

**Reason:** Remove blanket absence of real-model validation.

## 118. Existing table 7, row 2, column 3 — Table cell

**Before:** Structural checks verified; real built-in file availability fails

**After:** Historical structural fixtures verified; Windows real-classifier load/validation recorded; latest availability test not executed

**Reason:** Separate historical fixture and latest native evidence.

## 119. Existing table 7, row 3, column 3 — Table cell

**Before:** Fixture-verified; predictive accuracy pending

**After:** Historical fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.3.4

**Reason:** Add completed classifier metrics without implying all backends were evaluated.

## 120. Existing table 7, row 6, column 3 — Table cell

**Before:** Coordinates/zoom/grid verified in Qt; Windows native confirmation pending

**After:** Historical Qt coordinate/grid checks; native startup/state observations only; complete Windows case pending

**Reason:** Bound Windows confirmation to recorded actions.

## 121. Existing table 7, row 7, column 3 — Table cell

**Before:** Temporary persistence verified; known real-file test fails

**After:** Historical temporary persistence tests; historical availability failure; latest Windows invocation blocked at collection

**Reason:** Preserve chronology of the availability failure.

## 122. Existing table 7, row 14, column 3 — Table cell

**Before:** Qt-level evidence; native device and accessibility audit pending

**After:** Historical Qt fixtures; normal/maximised/minimised Windows states recorded; restore/docking/accessibility pending

**Reason:** Distinguish state transitions from complete native acceptance.

## 123. Existing table 7, row 15, column 3 — Table cell

**Before:** Relevant checks pass; immutable provenance not implemented

**After:** Historical fixture checks pass; latest full Windows invocation interrupted; immutable provenance not implemented

**Reason:** Avoid presenting old fixture passes as the latest full-suite outcome.

## 124. Existing table 8, row 1, column 3 — Table cell

**Before:** Verify real checkpoint, source scale and representative tensor equivalence

**After:** Confirm source scale, deployed-backend input equivalence and dataset grouping; retain supplied checkpoint checksum

**Reason:** Reflect the now available classification weight and evaluation evidence.

## 125. Existing table 8, row 2, column 3 — Table cell

**Before:** Supply verified weights/cache and test a clean Windows package

**After:** Verify segmentation resources and permitted caches in a clean Windows package

**Reason:** Avoid requesting classification files already provided.

## 126. Existing table 8, row 10, column 3 — Table cell

**Before:** Complete independent model/UAT studies before stronger conclusions

**After:** Complete UAT, remaining native cases and segmentation evaluation; preserve the current collection failure

**Reason:** Update the remaining evidence tasks.

## 127. Existing table 15, row 0, column 0 — Table cell

**Before:** Run

**After:** Run / environment

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 128. Existing table 15, row 1, column 0 — Table cell

**Before:** Full pytest, continuing after collection errors

**After:** 19 Oct 2026: Windows full invocation; revision 1f3e01e

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 129. Existing table 15, row 1, column 1 — Table cell

**Before:** 355

**After:** Not obtained

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 130. Existing table 15, row 1, column 2 — Table cell

**Before:** 1

**After:** Not obtained

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 131. Existing table 15, row 1, column 4 — Table cell

**Before:** Full suite is not green; both missing-file issues remain visible

**After:** 356 items collected; stopped during collection; 13 warnings; 24.76 s; exit 2

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 132. Existing table 15, row 2, column 0 — Table cell

**Before:** Result-control/history/comparison/grid/layout regressions

**After:** 17 Oct 2026: Linux/offscreen Qt; full run with --continue-on-collection-errors

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 133. Existing table 15, row 2, column 1 — Table cell

**Before:** 83

**After:** 355

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 134. Existing table 15, row 2, column 2 — Table cell

**Before:** 0

**After:** 1

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 135. Existing table 15, row 2, column 3 — Table cell

**Before:** 0

**After:** 1

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 136. Existing table 15, row 2, column 4 — Table cell

**Before:** Related controlled regressions pass

**After:** Historical record; 14 warnings; 110.70 s; missing-file issues

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 137. Existing table 15, row 3, column 0 — Table cell

**Before:** New input/locale tests at Qt scale factor 1.5

**After:** 17 Oct 2026: related result-control/history/comparison/grid/layout cases

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 138. Existing table 15, row 3, column 1 — Table cell

**Before:** 7

**After:** 83

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 139. Existing table 15, row 3, column 4 — Table cell

**Before:** Simulated 150% scaling; not Windows-native proof

**After:** Historical controlled regression subset

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 140. Existing table 15, row 4, column 0 — Table cell

**Before:** New input/locale tests at Qt scale factor 2

**After:** 17 Oct 2026: Qt scale factor 1.5

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 141. Existing table 15, row 4, column 4 — Table cell

**Before:** Simulated 200% scaling; not Windows-native proof

**After:** Historical simulated 150% scale; not native acceptance

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 142. Existing table 15, row 5, column 0 — Table cell

**Before:** New input/locale tests at Qt scale factor 2

**After:** 17 Oct 2026: Qt scale factor 2

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 143. Existing table 15, row 5, column 4 — Table cell

**Before:** Simulated 200% scaling; not Windows-native proof

**After:** Historical simulated 200% scale; not native acceptance

**Reason:** Separate the interrupted latest invocation from historical runs; do not invent an executed count.

## 144. Existing table 16, row 1, column 2 — Table cell

**Before:** Inspect metadata and training attachment; retain actual class order

**After:** Use the actual nine-class DenseNet/raw255 metadata, training records and class order

**Reason:** Replace attachment-audit wording with confirmed methodology.

## 145. Existing table 16, row 1, column 3 — Table cell

**Before:** Loader/preprocessor/tile fixtures; real predictive metrics still absent

**After:** Historical loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**Reason:** Replace obsolete claim that all predictive metrics are absent.

## 146. Existing table 16, row 5, column 3 — Table cell

**Before:** Small-screen/font tests; native Windows verification remains pending

**After:** Historical small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**Reason:** Limit native evidence to actual observations.

## 147. Existing table 20, row 1, column 2 — Table cell

**Before:** Feasibility supported with controlled models; clean offline package not verified

**After:** Local source startup and real-classifier validation recorded on Windows; clean offline package not verified

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 148. Existing table 20, row 2, column 2 — Table cell

**Before:** Structural integration verified; real built-in availability incomplete

**After:** Supported contracts implemented; real classifier loaded and validated on Windows; complete latest suite blocked at collection

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 149. Existing table 20, row 3, column 2 — Table cell

**Before:** Algorithms/parameters tested; independent real-model accuracy pending

**After:** Classifier test accuracy 90.68% and macro-F1 88.59% in the recorded pipeline; segmentation and tiled predictive evaluation pending

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 150. Existing table 20, row 4, column 2 — Table cell

**Before:** Qt-level behaviour verified; UAT and final native checks pending

**After:** Historical Qt fixtures and partial native state observations; formal interaction acceptance and UAT pending

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 151. Existing table 20, row 5, column 2 — Table cell

**Before:** Temporary-artifact/report tests pass; final demonstration screenshots pending

**After:** Historical temporary-artifact/report tests pass; current Windows export demonstration pending

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 152. Existing table 20, row 6, column 2 — Table cell

**Before:** Controlled persistence verified; immutable provenance/backup not implemented

**After:** Historical controlled persistence checks; immutable provenance and backup not implemented

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 153. Existing table 20, row 7, column 2 — Table cell

**Before:** Recorded-parameter semantics verified; user-efficiency advantage untested

**After:** Historical recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**Reason:** Synchronise objective assessment with recorded model, historical software and partial native evidence.

## 154. Existing table 23, row 1, column 1 — Table cell

**Before:** Reviewed ui/, core/ and data/ modules with regression tests

**After:** Project ui/, core/ and data/ modules with historical regression tests

**Reason:** Remove external review narration.

## 155. Existing table 23, row 7, column 0 — Table cell

**Before:** Real-weight evaluation and complete test prerequisites

**After:** Classifier training and evaluation

**Reason:** Separate completed model evaluation from test prerequisite repair.

## 156. Existing table 23, row 7, column 1 — Table cell

**Before:** Required artifacts absent from the cloud checkout

**After:** 30-epoch record, epoch-26 checkpoint, 7,180 predictions and matching metrics

**Reason:** Use received genuine evaluation evidence.

## 157. Existing table 23, row 7, column 2 — Table cell

**Before:** Pending

**After:** Recorded accuracy 90.68%, macro-F1 88.59%; grouping/backend limits documented

**Reason:** Update the milestone accurately.

## 158. Existing table 23, row 8, column 1 — Table cell

**Before:** Prepared instruments; no completed dataset supplied

**After:** Partial Windows startup/state record; no UAT responses or complete native acceptance record

**Reason:** Record the actual Windows evidence level.

## 159. Existing table 23, row 8, column 2 — Table cell

**Before:** Pending

**After:** Partial native evidence; formal acceptance and UAT pending

**Reason:** Keep the status qualified.

## 160. Existing table 25, row 2, column 1 — Table cell

**Before:** core/preprocessor.py; train_crc_dn21.py attachment

**After:** core/preprocessor.py; supervisor-provided train_crc_dn21.py and experiment records

**Reason:** Use academic provenance for training and runtime sources.

## 161. Existing table 25, row 4, column 1 — Table cell

**Before:** core/large_image_segmentation.py; core/inference_engine.py

**After:** core/large_image_segmentation.py; core/inference_engine.py; supervisor-provided inference notebook

**Reason:** Include the genuine segmentation reference source.

## 162. Existing table 25, row 10, column 1 — Table cell

**Before:** Saved full/related/scale pytest logs

**After:** 17 Oct 2026 Linux full/related/scale logs; 19 Oct Windows execution record

**Reason:** Date and distinguish the test evidence.

## 163. Existing table 25, row 10, column 2 — Table cell

**Before:** Reported counts, exit outcome and known missing-file failures

**After:** Historical outcomes; current collection interruption; command/environment context

**Reason:** Avoid transferring old failures or passes to current execution.

## 164. 3.6.1 Development Testing — Original paragraph 429

**Before:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.2 gives the host hardware and separates its installed GPU from the actual computation device.

**After:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.3 gives the host hardware and separates its installed GPU from the actual computation device.

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 165. 4.3.2 Challenges, resolutions and evidence — Original paragraph 505

**Before:** Table 4.2. Implementation challenges and verified resolutions

**After:** Table 4.3. Implementation challenges and verified resolutions

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 166. 4.4.1 Participant Demographics — Original paragraph 515

**Before:** Table 4.3. UAT participant profile — awaiting actual responses

**After:** Table 4.6. UAT participant profile — awaiting actual responses

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 167. 4.4.2 Quantitative Results — Original paragraph 519

**Before:** Table 4.4. UAT quantitative summary — awaiting valid data

**After:** Table 4.7. UAT quantitative summary — awaiting valid data

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 168. 4.4.3 Feature Usage and Ratings — Original paragraph 523

**Before:** Table 4.5. Feature ratings — awaiting actual use and responses

**After:** Table 4.8. Feature ratings — awaiting actual use and responses

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 169. 4.5.1 Achievement of Research Objectives — Original paragraph 536

**Before:** Table 4.6. Objective achievement and outstanding evidence

**After:** Table 4.9. Objective achievement and outstanding evidence

**Reason:** Renumber chapter-four tables to include the new environment and model-evaluation tables.

## 170. 4.3.1 — Added paragraph

**Before:** [Not present]

**After:** The Windows command was .\.venv\Scripts\python.exe -m pytest -ra --tb=long --color=no --junitxml=<evidence-directory>\pytest.xml, executed in the project virtual environment. Appendix C records the project/evidence paths and the temporal limits of the saved revision and worktree observations.

**Reason:** Add evidence-based content.

## 171. 4.3.1 — Added paragraph

**Before:** [Not present]

**After:** Table 4.2. Windows test host and actual CPU runtime on 19 October 2026

**Reason:** Add a table derived from the recorded evidence.

## 172. 4.3.1 — Table 4.2. Windows test host and actual CPU runtime on 19 October 2026

**Before:** [Not present]

**After:** [["Category", "Recorded specification", "Interpretation"], ["Operating system", "Microsoft Windows 11 Home Chinese Edition; 10.0.22621, Build 22621; 64-bit", "Native win32 pytest/application environment"], ["CPU", "13th Gen Intel Core i9-13900HX; 24 cores; 32 logical processors", "PyTorch CPU threads: 24"], ["Memory", "15.81 GiB physical RAM", "Collection used 2³⁰ bytes although its field was named RAM_GB"], ["Installed GPU", "NVIDIA GeForce RTX 4060 Laptop GPU; driver 32.0.15.6094", "Installed hardware only; not used for these runs"], ["Actual compute", "PyTorch 2.1.2+cpu; CUDA available=False", "CPU execution; no GPU acceleration claim"], ["Python/test stack", "Python 3.10.22; pytest 9.1.1; pluggy 1.6.0; anyio 4.15.1; pytest-qt 4.5.0", "Versions from the Windows test record"], ["GUI stack", "PyQt5 5.15.11; Qt runtime 5.15.2; Qt compiled 5.15.2", "Recorded DPR 2.0; screen geometry reported in logical coordinates"]]

**Reason:** Present genuine measurements with their source and interpretation.

## 173. 4.3.1 — Added paragraph

**Before:** [Not present]

**After:** Source: Windows test/environment record dated 19 October 2026; full revision and evidence-file index in Appendix C. Installed GPU specifications are separated from the actual CPU runtime.

**Reason:** Add evidence-based content.

## 174. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** 4.3.4 Classification training and test results

**Reason:** Add evidence-based content.

## 175. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** The formal experiment uses the seed-42 NCT-CRC-HE-100K manifests with 80,002 training and 19,998 validation images. Their hashes match config.json, and relative paths do not overlap. The training log identifies an NVIDIA L4. This training environment is separate from the CPU-only Windows application session.

**Reason:** Add evidence-based content.

## 176. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.11 illustrates the epoch-to-epoch variation in validation loss and accuracy.

**Reason:** Add evidence-based content.

## 177. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Figure 4.11. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.

**Reason:** Add a real-data plot with its evidence source.

## 178. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Table 4.4. Classification evaluation summary

**Reason:** Add a table derived from the recorded evidence.

## 179. 4.3.4 — Table 4.4. Classification evaluation summary

**Before:** [Not present]

**After:** [["Measure", "Recorded / recomputed result", "Scope"], ["Test collection", "CRC-VAL-HE-7K; 7,180 images", "Separate from the internal training/validation manifests"], ["Correct / incorrect", "6,511 / 669", "Recomputed from predictions.csv"], ["Test accuracy", "90.682451%", "6,511 / 7,180"], ["Test macro-F1", "0.885879 (88.59%)", "Unweighted mean of nine class F1 values"], ["Internal validation", "99.09% accuracy; 99.09% macro-F1", "Selected epoch 26; not the external test result"], ["Checkpoint identity", "Epoch-26 best_model.pth", "SHA-256 matches summary.json; renamed for application use"]]

**Reason:** Present genuine measurements with their source and interpretation.

## 180. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Source: metrics.csv, test-7k/summary.json and test-7k/predictions.csv from the classification experiment; values were cross-checked by recomputing the recorded predictions.

**Reason:** Add evidence-based content.

## 181. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Table 4.5. Class-wise classification performance on 7,180 test images

**Reason:** Add a table derived from the recorded evidence.

## 182. 4.3.4 — Table 4.5. Class-wise classification performance on 7,180 test images

**Before:** [Not present]

**After:** [["Class (support)", "Precision (%)", "Recall (%)", "F1 (%)"], ["ADI (1,338)", "97.43", "84.90", "90.73"], ["BACK (847)", "98.83", "100.00", "99.41"], ["DEB (339)", "79.76", "98.82", "88.27"], ["LYM (634)", "95.17", "99.37", "97.22"], ["MUC (1,035)", "96.59", "93.14", "94.84"], ["MUS (592)", "61.24", "73.14", "66.67"], ["NORM (741)", "90.21", "94.47", "92.29"], ["STR (421)", "79.14", "65.80", "71.85"], ["TUM (1,233)", "95.58", "96.43", "96.00"]]

**Reason:** Present genuine measurements with their source and interpretation.

## 183. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Source: classification_report.csv, cross-checked against the per-image predictions; support is the number of true-class test images. Rounded displayed values may differ slightly from calculations using the full-precision CSV.

**Reason:** Add evidence-based content.

## 184. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Figure 4.12. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.

**Reason:** Add a real-data plot with its evidence source.

## 185. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** Performance varies substantially by category. BACK has F1 99.41%, while MUS and STR have F1 66.67% and 71.85%. The largest off-diagonal count is ADI predicted as MUS (192 images); MUS/STR confusion is bidirectional (73 MUS→STR and 74 STR→MUS). DEB recall is 98.82% but precision is 79.76%, showing that high sensitivity for one class can coexist with false positives. These differences justify presenting class-wise results alongside accuracy.

**Reason:** Add evidence-based content.

## 186. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** The selected-epoch validation accuracy exceeds the test accuracy by approximately 8.41 percentage points. This observed gap suggests sensitivity to the evaluation collection and motivates analysis of grouping, stain/scale and domain differences; the records do not isolate a causal explanation. A high internal validation score therefore does not remove the need for the separate test collection.

**Reason:** Add evidence-based content.

## 187. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** All 7,180 prediction rows have consistent class argmax, maximum softmax score and probability sums. Recalculated accuracy, macro-F1, per-class values and confusion counts agree with the saved reports, and the selected weight hash agrees with summary.json. This is a consistency verification of recorded evaluation outputs, not a fresh inference rerun on the original test images. Appendix E records the complete checksum and preprocessing/dependency details.

**Reason:** Add evidence-based content.

## 188. 4.3.4 — Added paragraph

**Before:** [Not present]

**After:** The results apply to the recorded OpenCV/Albumentations raw255 pipeline. The legacy application default remains Pillow bilinear; arbitrary 512-pixel source crops and tiled coverage require their own scale and ground-truth design. Patient/slide isolation and backend equivalence are limitations discussed in Section 4.5.3.

**Reason:** Add evidence-based content.

## 189. 4.3.5 — Added paragraph

**Before:** [Not present]

**After:** 4.3.5 Runtime and deployment verification status

**Reason:** Add evidence-based content.

## 190. 4.3.5 — Added paragraph

**Before:** [Not present]

**After:** The hardware and CPU runtime are documented in Table 4.2, but no repeated stage-level measurements were recorded for loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving or export. Cold and warm runs have not been separately summarised. Appendix E.3 defines the benchmark protocol; no measured latency, mean, standard deviation or throughput is filled in here.

**Reason:** Add evidence-based content.

## 191. 4.3.5 — Added paragraph

**Before:** [Not present]

**After:** The demonstrated delivery route is source execution in a Windows virtual environment. No PyInstaller build log, version-matched packaged artifact, clean-machine acceptance record or offline execution record was available. Standalone executable and fully offline deployment verification remain future work, separate from successful source startup.

**Reason:** Add evidence-based content.

## 192. Appendix C, Table C.1 — Added evidence source

**Before:** [Not present]

**After:** E11 | Classification manifests, config.json, metrics.csv, training logs and best_model.pth | Recorded data split, 30 epochs, selected epoch and checkpoint identity

**Reason:** Index received training/inference materials and distinguish archival status of the Windows records.

## 193. Appendix C, Table C.1 — Added evidence source

**Before:** [Not present]

**After:** E12 | Classification test-7k predictions/report/matrix/summary files | Recorded 7,180-image metrics; independently recomputed CSV consistency

**Reason:** Index received training/inference materials and distinguish archival status of the Windows records.

## 194. Appendix C, Table C.1 — Added evidence source

**Before:** [Not present]

**After:** E13 | Supervisor-provided predict-upernet-tme-tissue-overlap.ipynb | Segmentation architecture, independent preprocessing, labels and overlap fusion

**Reason:** Index received training/inference materials and distinguish archival status of the Windows records.

## 195. Appendix C, Table C.1 — Added evidence source

**Before:** [Not present]

**After:** E14 | 19 Oct 2026 originals: pytest-full.log, pytest.xml, pytest-exit-code.txt, commit.txt, test-date.txt and environment files | Current collection interruption, exit 2, recorded revision and CPU test environment; originals cross-checked

**Reason:** Index received training/inference materials and distinguish archival status of the Windows records.

## 196. Appendix C, Table C.1 — Added evidence source

**Before:** [Not present]

**After:** E15 | 19 Oct 2026 original windows-app.log | Successful startup/real-classifier validation and limited window states; no completed image inference or all-feature acceptance

**Reason:** Index received training/inference materials and distinguish archival status of the Windows records.

## 197. Table source, original index 1 — Added paragraph

**Before:** [Not present]

**After:** Source: platform publications and product documentation cited in Sections 2.3.1–2.3.5; ZY-Path scope from the project implementation.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 198. Table source, original index 2 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s requirements derived from the CP1 objectives and implemented workflows.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 199. Table source, original index 3 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s quality requirements and recorded verification scope.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 200. Table source, original index 4 — Added paragraph

**Before:** [Not present]

**After:** Source: classification checkpoint class order and the application’s classification display palette; colours are display metadata.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 201. Table source, original index 5 — Added paragraph

**Before:** [Not present]

**After:** Source: supervisor-provided segmentation notebook; labels and RGB values match the application constants.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 202. Table source, original index 6 — Added paragraph

**Before:** [Not present]

**After:** Source: project database schema, task metadata and QSettings implementation.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 203. Table source, original index 7 — Added paragraph

**Before:** [Not present]

**After:** Source: named project tests, the historical Linux test logs, classification records and Windows execution record; statuses retain their evidence scope.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 204. Table source, original index 8 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s implementation risk assessment.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 205. Table source, original index 15 — Added paragraph

**Before:** [Not present]

**After:** Source: saved Linux logs dated 17 October 2026 and the Windows test record dated 19 October 2026. Historical subset counts overlap.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 206. Table source, original index 16 — Added paragraph

**Before:** [Not present]

**After:** Source: implementation changes and associated historical regression cases at revision 1f3e01e.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 207. Table source, original index 17 — Added paragraph

**Before:** [Not present]

**After:** Source: planned UAT protocol; no participant data have been collected.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 208. Table source, original index 18 — Added paragraph

**Before:** [Not present]

**After:** Source: planned SUS/task analysis rules (Brooke, 1996); results await actual responses.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 209. Table source, original index 19 — Added paragraph

**Before:** [Not present]

**After:** Source: planned feature-specific UAT questions; results await actual responses.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 210. Table source, original index 20 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s synthesis of the implementation, recorded tests, classifier evaluation and partial Windows runtime evidence.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 211. Table source, original index 21 — Added paragraph

**Before:** [Not present]

**After:** Source: CP1 proposal planning baseline, retained as historical planned activities.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 212. Table source, original index 22 — Added paragraph

**Before:** [Not present]

**After:** Source: CP1 proposal’s CP2 plan; proposed model, performance and deployment targets are not achieved-result statements.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 213. Table source, original index 23 — Added paragraph

**Before:** [Not present]

**After:** Source: project revision history, classification experiment outputs and Windows execution record.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 214. Table source, original index 24 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s UAT task protocol.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 215. Table source, original index 25 — Added paragraph

**Before:** [Not present]

**After:** Source: project modules, experiment files and identified test records listed in the table.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 216. Table source, original index 26 — Added paragraph

**Before:** [Not present]

**After:** Source: author’s Windows acceptance protocol. Expected evidence describes the acceptance criterion, not an observed Pass.

**Reason:** Add an explicit source and avoid treating a planned table as a result.

## 217. References — Added paragraph

**Before:** [Not present]

**After:** fpdf2 Contributors (n.d.) fpdf2: Simple PDF generation for Python. Project documentation. https://github.com/py-pdf/fpdf2

**Reason:** Restore a relevant CP1 design/storage or implemented-library source.

## 218. References — Added paragraph

**Before:** [Not present]

**After:** Gamma, E., Helm, R., Johnson, R. and Vlissides, J. (1994) Design Patterns: Elements of Reusable Object-Oriented Software. Reading, MA: Addison-Wesley.

**Reason:** Restore a relevant CP1 design/storage or implemented-library source.

## 219. References — Added paragraph

**Before:** [Not present]

**After:** Kreibich, J.A. (2010) Using SQLite. Sebastopol, CA: O’Reilly Media.

**Reason:** Restore a relevant CP1 design/storage or implemented-library source.

## 220. 3.5.1 Use Case Diagram — Original paragraph 410

**Before:** Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities.

**After:** Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities. Source: author, based on the implemented application.

**Reason:** Make the UML figure source explicit.

## 221. 3.5.2 Sequence Diagram — Original paragraph 414

**Before:** Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records.

**After:** Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records. Source: author, based on the implemented application.

**Reason:** Make the UML figure source explicit.

## 222. 3.5.3 Class Diagram — Original paragraph 419

**Before:** Figure 3.5. Implementation-level class diagram. Relationships represent principal ownership or dependency, not a generated inventory of every method.

**After:** Figure 3.5. Implementation-level class diagram. Relationships represent principal ownership or dependency, not a generated inventory of every method. Source: author, based on the implemented application.

**Reason:** Make the UML figure source explicit.

## 223. 3.5.4 Activity Diagram — Original paragraph 424

**Before:** Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits.

**After:** Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits. Source: author, based on the implemented application.

**Reason:** Make the UML figure source explicit.

## 224. Table of Contents — Index label

**Before:** 3.3.2 Classification model and training-reference audit

**After:** 3.3.2 Classification training and model configuration

**Reason:** Match the revised section heading without changing its style.

## 225. Table of Contents — Index label

**Before:** 4.3.3 Manual and predictive validation status

**After:** 4.3.3 Windows startup and window-state observations

**Reason:** Match the revised section heading without changing its style.

## 226. Contents / figure / table index — cap_Figure_3_1

**Before:** Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the reviewed Python modules.	20

**After:** Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the project’s Python modules.	20

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 227. Contents / figure / table index — cap_Figure_3_3

**Before:** Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities.	35

**After:** Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities. Source: author, based on the implemented application.	35

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 228. Contents / figure / table index — cap_Figure_3_4

**Before:** Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records.	36

**After:** Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records. Source: author, based on the implemented application.	36

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 229. Contents / figure / table index — cap_Figure_3_5

**Before:** Figure 3.5. Implementation-level class diagram. Relationships represent principal ownership or dependency, not a generated inventory of every method.	37

**After:** Figure 3.5. Implementation-level class diagram. Relationships represent principal ownership or dependency, not a generated inventory of every method. Source: author, based on the implemented application.	37

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 230. Contents / figure / table index — cap_Figure_3_6

**Before:** Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits.	38

**After:** Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits. Source: author, based on the implemented application.	38

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 231. Contents / figure / table index — cap_Figure_4_2

**Before:** Figure 4.2. Tiled classification interface with source/result comparison and the revised result toggles. Linux/Qt capture using synthetic source/output data; not a real-weight or diagnostic result.	48

**After:** Figure 4.2. Tiled classification interface with source/result comparison and revised result toggles. Source: author’s Linux/offscreen-Qt development capture; synthetic fixture, not a model result.	48

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 232. Contents / figure / table index — cap_Figure_4_7

**Before:** Figure 4.7. Implemented Guide & Support page with fixed Contents navigation and numbered guidance. Linux/Qt development capture; contact/guide content is interface evidence rather than UAT feedback.	51

**After:** Figure 4.7. Implemented Guide & Support page with persistent Contents navigation and numbered guidance. Source: author’s Linux/offscreen-Qt development capture; this is interface evidence.	51

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 233. Contents / figure / table index — cap_Figure_4_8

**Before:** Figure 4.8. English history-calendar popup under a simulated Chinese default locale. Linux/Qt capture; the selected date is test input.	51

**After:** Figure 4.8. English history-calendar popup with a simulated Chinese default locale. Source: author’s Linux/offscreen-Qt development capture; the selected date is test input.	51

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 234. Contents / figure / table index — cap_Figure_4_10

**Before:** Figure 4.10. Recorded pytest command/outcome excerpt and scope notes. Reproduced from saved logs for the reviewed revision; not a model-performance chart.	53

**After:** Figure 4.10. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.1.	53

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 235. Contents / figure / table index — cap_Table_4_1

**Before:** Table 4.1. Recorded automated verification outcomes at revision 1f3e01e	52

**After:** Table 4.1. Automated verification records by date and environment at revision 1f3e01e	52

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 236. Contents / figure / table index — cap_Table_4_2

**Before:** Table 4.2. Implementation challenges and verified resolutions	54

**After:** Table 4.3. Implementation challenges and verified resolutions	54

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 237. Contents / figure / table index — cap_Table_4_3

**Before:** Table 4.3. UAT participant profile — awaiting actual responses	55

**After:** Table 4.6. UAT participant profile — awaiting actual responses	55

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 238. Contents / figure / table index — cap_Table_4_4

**Before:** Table 4.4. UAT quantitative summary — awaiting valid data	56

**After:** Table 4.7. UAT quantitative summary — awaiting valid data	56

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 239. Contents / figure / table index — cap_Table_4_5

**Before:** Table 4.5. Feature ratings — awaiting actual use and responses	57

**After:** Table 4.8. Feature ratings — awaiting actual use and responses	57

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 240. Contents / figure / table index — cap_Table_4_6

**Before:** Table 4.6. Objective achievement and outstanding evidence	58

**After:** Table 4.9. Objective achievement and outstanding evidence	58

**Reason:** Synchronise the index label with its caption/heading while preserving the page field.

## 241. Contents, List of Figures and List of Tables — Cached page-reference fields

**Before:** [{"head_3": "vi"}, {"head_4": "vii"}, {"head_12": "7"}, {"head_18": "10"}, {"head_22": "12"}, {"head_23": "13"}, {"head_24": "13"}, {"head_25": "13"}, {"head_27": "14"}, {"head_28": "14"}, {"head_31": "16"}, {"head_32": "17"}, {"head_33": "18"}, {"head_34": "19"}, {"head_35": "19"}, {"head_36": "21"}, {"head_37": "21"}, {"head_38": "22"}, {"head_39": "23"}, {"head_41": "24"}, {"head_42": "24"}, {"head_43": "25"}, {"head_44": "26"}, {"head_45": "26"}, {"head_46": "27"}, {"head_47": "28"}, {"head_49": "30"}, {"head_51": "32"}, {"head_52": "32"}, {"head_53": "33"}, {"head_55": "34"}, {"head_68": "43"}, {"head_75": "49"}, {"head_76": "49"}, {"head_77": "50"}, {"head_78": "52"}, {"head_79": "52"}, {"new_4_3_4_Classification_training_and_test": ""}, {"new_4_3_5_Runtime_and_deployment_verificat": ""}, {"head_82": "55"}, {"head_83": "55"}, {"head_84": "56"}, {"head_85": "57"}, {"head_86": "57"}, {"head_87": "58"}, {"head_88": "58"}, {"head_89": "58"}, {"head_90": "59"}, {"head_91": "60"}, {"head_92": "61"}, {"head_93": "61"}, {"head_94": "63"}, {"head_95": "63"}, {"head_96": "64"}, {"head_97": "64"}, {"head_98": "65"}, {"head_99": "66"}, {"head_100": "68"}, {"head_101": "68"}, {"head_102": "68"}, {"head_103": "73"}, {"head_104": "74"}, {"head_105": "74"}, {"head_106": "74"}, {"head_107": "75"}, {"head_108": "75"}, {"head_109": "76"}, {"head_110": "77"}, {"head_111": "77"}, {"head_112": "78"}, {"head_113": "78"}, {"head_114": "79"}, {"head_115": "79"}, {"head_116": "79"}, {"head_117": "80"}, {"head_118": "80"}, {"head_119": "80"}, {"head_120": "81"}, {"head_121": "81"}, {"cap_Figure_2_1": "11"}, {"cap_Figure_3_1": "20"}, {"cap_Figure_4_1": "47"}, {"cap_Figure_4_2": "48"}, {"cap_Figure_4_4": "49"}, {"cap_Figure_4_5": "50"}, {"cap_Figure_4_6": "50"}, {"cap_Figure_4_7": "51"}, {"cap_Figure_4_8": "51"}, {"cap_Figure_4_9": "52"}, {"new_Figure_4_11__Classification_training_a": ""}, {"new_Figure_4_12__Nine_class_confusion_matr": ""}, {"cap_Table_2_1": "15"}, {"cap_Table_3_1": "21"}, {"cap_Table_3_2": "22"}, {"cap_Table_3_3": "28"}, {"cap_Table_3_4": "29"}, {"cap_Table_3_5": "30"}, {"cap_Table_4_1": "52"}, {"new_Table_4_2__Windows_test_host_and_actua": ""}, {"new_Table_4_4__Classification_evaluation_s": ""}, {"new_Table_4_5__Class_wise_classification_p": ""}, {"cap_Table_4_3": "55"}, {"cap_Table_4_4": "56"}, {"cap_Table_4_5": "57"}, {"cap_Table_4_6": "58"}, {"cap_Table_A_1": "68"}, {"cap_Table_A_2": "70"}, {"cap_Table_A_3": "73"}, {"cap_Table_B_1": "75"}, {"cap_Table_C_1": "78"}, {"cap_Table_D_1": "79"}]

**After:** [{"head_3": "vii"}, {"head_4": "ix"}, {"head_12": "6"}, {"head_18": "9"}, {"head_22": "11"}, {"head_23": "12"}, {"head_24": "12"}, {"head_25": "12"}, {"head_27": "13"}, {"head_28": "13"}, {"head_31": "15"}, {"head_32": "16"}, {"head_33": "17"}, {"head_34": "18"}, {"head_35": "18"}, {"head_36": "20"}, {"head_37": "20"}, {"head_38": "21"}, {"head_39": "22"}, {"head_41": "23"}, {"head_42": "23"}, {"head_43": "24"}, {"head_44": "25"}, {"head_45": "25"}, {"head_46": "26"}, {"head_47": "27"}, {"head_49": "29"}, {"head_51": "31"}, {"head_52": "31"}, {"head_53": "32"}, {"head_55": "33"}, {"head_68": "44"}, {"head_75": "48"}, {"head_76": "48"}, {"head_77": "49"}, {"head_78": "51"}, {"head_79": "51"}, {"new_4_3_4_Classification_training_and_test": "55"}, {"new_4_3_5_Runtime_and_deployment_verificat": "59"}, {"head_82": "59"}, {"head_83": "60"}, {"head_84": "60"}, {"head_85": "61"}, {"head_86": "62"}, {"head_87": "62"}, {"head_88": "63"}, {"head_89": "63"}, {"head_90": "64"}, {"head_91": "64"}, {"head_92": "66"}, {"head_93": "67"}, {"head_94": "68"}, {"head_95": "68"}, {"head_96": "69"}, {"head_97": "69"}, {"head_98": "70"}, {"head_99": "71"}, {"head_100": "74"}, {"head_101": "74"}, {"head_102": "74"}, {"head_103": "79"}, {"head_104": "80"}, {"head_105": "81"}, {"head_106": "81"}, {"head_107": "81"}, {"head_108": "81"}, {"head_109": "83"}, {"head_110": "83"}, {"head_111": "83"}, {"head_112": "84"}, {"head_113": "84"}, {"head_114": "85"}, {"head_115": "86"}, {"head_116": "86"}, {"head_117": "87"}, {"head_118": "87"}, {"head_119": "87"}, {"head_120": "88"}, {"head_121": "88"}, {"cap_Figure_2_1": "10"}, {"cap_Figure_3_1": "19"}, {"cap_Figure_4_1": "46"}, {"cap_Figure_4_2": "47"}, {"cap_Figure_4_4": "48"}, {"cap_Figure_4_5": "49"}, {"cap_Figure_4_6": "49"}, {"cap_Figure_4_7": "50"}, {"cap_Figure_4_8": "50"}, {"cap_Figure_4_9": "51"}, {"new_Figure_4_11__Classification_training_a": "56"}, {"new_Figure_4_12__Nine_class_confusion_matr": "58"}, {"cap_Table_2_1": "14"}, {"cap_Table_3_1": "20"}, {"cap_Table_3_2": "21"}, {"cap_Table_3_3": "27"}, {"cap_Table_3_4": "28"}, {"cap_Table_3_5": "29"}, {"cap_Table_4_1": "51"}, {"new_Table_4_2__Windows_test_host_and_actua": "52"}, {"new_Table_4_4__Classification_evaluation_s": "56"}, {"new_Table_4_5__Class_wise_classification_p": "57"}, {"cap_Table_4_3": "60"}, {"cap_Table_4_4": "60"}, {"cap_Table_4_5": "61"}, {"cap_Table_4_6": "63"}, {"cap_Table_A_1": "74"}, {"cap_Table_A_2": "76"}, {"cap_Table_A_3": "79"}, {"cap_Table_B_1": "81"}, {"cap_Table_C_1": "84"}, {"cap_Table_D_1": "86"}]

**Reason:** Refresh cached page references against the rendered content review PDF; keep existing styles and field instructions.
