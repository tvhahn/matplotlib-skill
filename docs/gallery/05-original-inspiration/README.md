# 05 -- Original Inspiration

## What Changed
N/A -- this is the source material that inspired the skill, not an iteration on it.

## Why
Documents the origin of each chart pattern for the blog article. The matplotlib-chart skill was created by synthesizing visualization patterns from 4 existing projects. This gallery entry preserves the original figures that were used as reference during skill creation.

## Source Projects

| Project | Description |
|---------|-------------|
| **weibull-knowledge-informed-ml** | PhD research on knowledge-informed ML for predictive maintenance. Contributed horizontal bar, vertical bar, time series, violin, heatmap/spectrogram, and multi-panel patterns. |
| **Beautiful-Plots** | Tutorial repo demonstrating before/after matplotlib transformations. Contributed lollipop, decision boundary, and violin reference patterns. |
| **arxiv-code-search** | Research tool analyzing code availability in academic papers. Contributed PR/ROC curve and horizontal bar variant patterns. |
| **ml-tool-wear** | Anomaly detection for manufacturing tool wear. Contributed PR/AUC, distribution, and multi-panel visualization patterns. |

## Pattern Mapping

| Pattern | Name | Source Project | Images |
|---------|------|---------------|--------|
| 1 | Horizontal Bar | weibull | `loss_function_percentages.pdf/.svg` |
| 1 (variant) | Horizontal Bar | arxiv | `article_pcts_arxiv.png`, `article_pcts_by_publisher.png` |
| 2 | Vertical Bar | weibull | `correlations.pdf/.svg` |
| 3 | Time Series | weibull | `ims_rul_results.png/.pdf`, `femto_rul_results.png/.pdf` |
| 4 | Violin + Strip | weibull | `epoch_stop_dist.png/.pdf` |
| 4 (ref) | Violin | beautiful-plots | `violin_births.svg` |
| 5 | Lollipop | beautiful-plots | `beautiful_lollipop.png/.svg` (after), `original_lollipop.svg` (before), `energy_prod.svg` |
| 6 | Decision Boundary | beautiful-plots | `knn.png` (after), `original_decision.png` (before) |
| 7 | Heatmap/Spectrogram | weibull | `spectrogram_with_binned_example.png`, `ims_spectrograms_processed_data.png`, `femto_spectrograms_processed_data.png` |
| 8 | Multi-Panel Grid | weibull | `ims_rul_results.png`, `femto_rul_results.png` |
| 8 (variant) | Multi-Panel | ml-tool-wear | `multiple_recon_case_9_lowres.png`, `latent_space_recon_case_13_150dpi_3.png` |
| 9 | PR/ROC Curves | arxiv | `curve_12082548_rf_*.png`, `curve_29710817_ridge_*.png`, `curve_30082792_rf_*.png` |
| 9 (variant) | PR/AUC | ml-tool-wear | `prauc_lowres.png`, `prauc_params_1_600dpi.png` |
| -- | Distribution | ml-tool-wear | `dist_input_lowres.png`, `dist_latent_lowres.png` |

## Before vs After
- **Before:** These are the "before" -- the original research figures
- **After:** See `../00-original/` for the first skill-generated versions

## Files Modified
None -- source material only

## Lessons Learned
- Starting from real project figures (not synthetic examples) grounds the skill in actual use cases
- Four projects spanning different domains (predictive maintenance, tutorials, bibliometrics, manufacturing) produced enough variety to cover 9 distinct chart patterns
- The Beautiful-Plots before/after pairs were especially useful for defining the target aesthetic
