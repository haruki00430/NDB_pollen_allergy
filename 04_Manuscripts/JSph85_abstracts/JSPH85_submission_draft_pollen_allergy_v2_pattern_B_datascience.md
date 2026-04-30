# 第85回日本公衆衛生学会総会 演題登録ドラフト（Pattern B）

## 想定
- 第25分科会（関連諸科学: AI・データサイエンス）を主軸
- English Sessionとの親和性を強調

## 和文抄録案（提出用）

### 演題名（和文）
粒径整合性に基づく花粉×大気粒子複合曝露モデルの比較：NDBオープンデータを用いた都道府県別データサイエンス解析

### 本文（【目的】【方法】【結果】【考察】）
【目的】公衆衛生データサイエンスでは、曝露変数の定義が推定の頑健性を左右する。本研究は、花粉関連曝露モデリングにおいてPM2.5とSPMの粒径整合性の違いが推定性能に与える影響を定量比較し、代理指標（森林率）と実測花粉データの性能差を検証した。【方法】都道府県47単位の生態学的研究を実施した。アウトカムはNDBオープンデータ第10回（FY2023）の抗アレルギー薬処方量（薬効分類441、449、131、132；人口10万人当たり）とした。説明変数は2023年実測花粉飛散数、PM2.5およびSPMの2021-2023年平均、高齢化率、人口密度とした。PM2.5ベースのfull model（Model 5）とSPMベースのfull model（Model 6）を並列構築し、HC3ロバストSEと感度分析6仕様で頑健性を検証した。モデル評価はR2、AIC、係数の再現性で行った。【結果】Model 6はModel 5より適合が良好であった（R2=0.469 vs 0.357、AIC差=-9.0）。花粉主効果はModel 6でHC3後も有意（p=0.033）で、Model 5では有意性を失った（p=0.082）。花粉×SPM交互作用は通常SEで有意（p=0.020）、HC3で境界的（p=0.066）であった。Model 6では花粉主効果が感度分析6仕様すべてで有意（p=0.006-0.045）を維持した。さらに、実測花粉は森林率代理指標より性能が高かった（R2=0.357 vs 0.242、AIC差=7.7）。【考察】粒径整合性を考慮したSPMベース定義は、花粉関連リスク推定の頑健性を向上させる可能性がある。公衆衛生分野のデータサイエンス実装では、代理指標依存から実測曝露中心へ移行することが推奨される。

## English Session Abstract Draft

### Title
Particle-Size-Aware Exposure Modeling Improves Robustness of Pollen-Prescription Inference: A Prefecture-Level NDB Open Data Study

### Abstract (Background, Methods, Results, Conclusions)
**Background:** In public health data science, exposure definition is a major determinant of model robustness. We quantified whether particle-size-aware specification (SPM) improves pollen-prescription inference compared with PM2.5, and whether observed pollen counts outperform proxy indicators.

**Methods:** We analyzed all 47 Japanese prefectures in an ecological framework. The outcome was allergy-specific prescriptions per 100,000 population from the 10th NDB Open Data release (FY2023; codes 441, 449, 131, 132). Predictors included observed pollen counts (2023 season), 3-year mean PM2.5 and SPM (2021-2023), aging rate, and population density. We compared a PM2.5-based full model (Model 5) with an SPM-based full model (Model 6), and assessed robustness using HC3 standard errors plus six sensitivity specifications. Performance criteria were R2, AIC, and coefficient stability.

**Results:** Model 6 outperformed Model 5 (R2=0.469 vs 0.357; delta AIC=-9.0). The pollen main effect remained significant under HC3 in Model 6 (p=0.033), but not in Model 5 (p=0.082). The pollen x SPM interaction was significant under conventional standard errors (p=0.020) and marginal under HC3 (p=0.066). In Model 6, the pollen effect remained significant in all six sensitivity specifications (p=0.006-0.045). Observed pollen also outperformed forest-area proxy models (R2=0.357 vs 0.242; delta AIC=7.7).

**Conclusions:** Particle-size-aware SPM specification improves robustness of pollen-related public health inference relative to PM2.5-based specification. Replacing proxy-based exposure definitions with observed pollen data can strengthen reproducible evidence generation in environmental and computational public health.
