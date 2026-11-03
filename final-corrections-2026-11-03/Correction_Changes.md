### Table 3.7 / R10 / Existing control

Before: Keep participant outcomes, model evaluation and dated manual acceptance separate; obtain independent segmentation labels and source-matched release records.

After: Separate software, model, platform and user evidence.

Reason: Restore the distinct existing control; keep future evaluation/provenance actions in Remaining action.

### 4.1

Before: This chapter reports the implemented system and the source states identified in Appendix C. The complete 548-case automated Windows result applies to d9fb8e5; the 15-case manual acceptance applies to the final revision fbe152a. Interface figures illustrate separate recorded analyses from 30–31 October and do not establish their capture-time source revisions. Section 4.2 presents workflows and classifier evaluation, Section 4.3 reports software tests and native observations, and Section 4.4 reports the ten-participant UAT results.

After: This chapter reports the implemented system and the source states identified in Appendix C. The complete 548-case automated Windows result applies to d9fb8e5; the 15-case manual acceptance applies to the final revision fbe152a. The figures retain their displayed analysis-record dates, which are distinct from capture dates and capture-time software revisions. Section 4.2 presents workflows and classifier evaluation, Section 4.3 reports software tests and native observations, and Section 4.4 reports the ten-participant UAT results.

Reason: Remove the incorrect blanket 30–31 October analysis range and distinguish analysis, export and screenshot dates.

### Appendix C.1

Before: The interface captures date from 30–31 October 2026, including overview record #84 and segmentation record #86, classification inspection, History, recorded Re-run and defaults. Figure 4.6 uses one actual PDF, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. Capture-time commits were not recorded. These interface examples therefore retain their dates without being attributed to d9fb8e5 or fbe152a; their source identities remain separate from the dated automated and manual records.

After: The interface figures illustrate separately dated analysis records, including record #48 on 23 October 2026 and records #84/#86 on 31 October. Figure 4.6 reproduces one PDF for record #65: the analysis time is 25 October, while export occurred on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. Analysis timestamps and export dates do not determine when a screenshot was captured, and capture-time commits were not recorded. Each example therefore retains its own captioned record identity without being attributed to d9fb8e5 or fbe152a. The automated and manual executions have separate dated source records.

Reason: Describe the actual displayed record dates without inventing a single screenshot-capture range.

### Table C.1 / E24 / Source

Before: Author’s Windows captures from 30–31 Oct 2026; CRC-VAL-HE-7K patch; two-page PDF and segmentation JSON.

After: Author’s Windows interface figures with separately dated analysis records, including #48 (23 Oct) and #84/#86 (31 Oct); dataset patch, PDF and segmentation JSON.

Reason: Replace a blanket capture-date assertion with individually documented analysis dates.

### 3.3.2

Before: Class weights are calculated as w_c = 1 − n_c / Σ_j n_j from the training counts; they are not inverse-frequency weights. Cross-entropy uses a summed reduction, with epoch reporting normalised by the accumulated class-weight denominator. The script seeds Python, NumPy, PyTorch and the data-loader generator with 42, seeds workers from their PyTorch worker seed, disables cuDNN benchmarking and requests deterministic cuDNN behaviour. Continuation restores the model, optimizer and scheduler states. The reported results describe this recorded run; no multi-seed training-variation study was conducted.

After: Class weights are calculated as w_c = 1 − n_c / Σ_j n_j from the training counts; they are not inverse-frequency weights. Cross-entropy uses a summed reduction, with epoch reporting normalised by the accumulated class-weight denominator. The script seeds Python, NumPy, PyTorch and the data-loader generator with 42, seeds workers from their PyTorch worker seed, disables cuDNN benchmarking and requests deterministic cuDNN behaviour. Continuation restores the model, optimiser and scheduler states. The reported results describe this recorded run; no multi-seed training-variation study was conducted.

Reason: Use British spelling in ordinary prose; code identifiers and reference titles remain unchanged.

### Appendix D.1

Before: On 2 November 2026, I performed the 15 Windows checks in Table D.1 on revision fbe152a5e4bbe14ad6dcc682468ad571d2efd33c; all met their criteria. I used Windows 11 Home Chinese Edition 22H2 (OS Build 22621.3593), a 2560 × 1600 display and 175% scaling. Environment information was recorded at 21:59:01 UTC+08:00; this is the environment-capture time, not a timed start/end interval for the cases. Git status was clean when the revision was recorded. The observations below document my confirmation of the checklist outcomes; screenshots or a continuous recording were not required. W09 covers 175% scaling only.

After: On 2 November 2026, I checked W01–W15 at revision fbe152a5e4bbe14ad6dcc682468ad571d2efd33c. All met the detailed acceptance criteria. The system was Windows 11 Home Chinese Edition 22H2 (OS Build 22621.3593), with a 2560 × 1600 display and 175% scaling. I recorded the source and environment at 21:59:01 UTC+08:00; Git status was clean at that point. Table D.1 summarises my confirmation of the specified checklist outcomes, rather than a contemporaneous observer log. The record contains no individual case timings and W09 covers 175% scaling only.

Reason: Retain the author’s explicit confirmation while identifying the checklist-based nature of the detailed wording and the actual display scope.

### Table D.1 / column heading

Before: Observed behaviour / outcome

After: Confirmed acceptance outcome / summary

Reason: Avoid presenting confirmed checklist summaries as independently transcribed observer notes.

### Table D.1 caption

Before: Table D.1. Windows manual acceptance procedures and observed outcomes.	105

After: Table D.1. Windows manual acceptance procedures and confirmed outcomes.

Reason: Align the caption with the actual checklist confirmation method.

### Table D.1 source

Before: Source: my 2 November 2026 Windows manual checks at fbe152a; accompanying case records: Windows_Manual_Acceptance_Record.csv/.xlsx.

After: Source: my 2 November 2026 confirmation of the detailed Windows checklist at fbe152a; case records: Windows_Manual_Acceptance_Record.csv/.xlsx.

Reason: State the confirmed-checklist provenance directly.

### Table of Contents; List of Figures; List of Tables

Before: 172 static cached page labels; actual PAGEREF instruction count was 0.

After: 172 functional PAGEREF fields restored with begin/instruction/separator/result/end structure and existing body bookmarks.

Reason: Restore F9 page updating and independently verify actual Word fields and rendered PDF labels against their targets.