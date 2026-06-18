# How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment

**アウトカム定義が処方ベース疫学の生態学的推論を変える：自然実験**

---

## Overview / 概要

### English

This repository contains analysis code for a nationwide ecological study examining how **outcome definition** influences ecological inference in prescription-based epidemiology. Using Japan's 47 prefectures and seasonal pollen exposure as a natural-experiment signal, we compared three outcome definitions — an allergy-specific prescription index, a pharmacologically heterogeneous comparator, and a pharmacologically unrelated negative control — under identical exposure data, covariates, and regression frameworks.

**Key finding**: Outcome definition changed recoverable ecological signal by **1.72-fold** (R² = 0.469 vs. 0.272) under identical exposure and models. Pollen associations were significant in 7/8 sensitivity specifications for the allergy-specific outcome, compared with 5/6 for the best comparator model. A pharmacologically unrelated negative control (oral hypoglycaemic agents) showed no pollen association, confirming signal differences reflected outcome specificity rather than ecological confounding.

**Study design**: Cross-sectional ecological study | N = 47 prefectures | Fiscal Year 2023  
**OSF pre-registration**: https://osf.io/yuc4a (registered 18 June 2026)

**Manuscript**: Saito H, Ohira T. How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment. *(In submission, Journal of Clinical Epidemiology, 2026)*

### 日本語

本リポジトリは、処方ベース疫学における**アウトカム定義**が生態学的推論に与える影響を定量化した全国生態学研究の解析コードを公開するものです。日本47都道府県を分析単位とし、花粉曝露を自然実験シグナルとして、アレルギー特異的処方・薬理学的異種比較アウトカム・陰性対照の3定義を、同一の曝露データ・共変量・回帰枠組みで比較しました。

**主要結果**: アウトカム定義により回収可能な生態学的シグナルが**1.72倍**異なりました（R² = 0.469 対 0.272）。アレルギー特異的アウトカムでは花粉関連が8仕様中7仕様で有意、比較アウトカムでは最良モデルで6仕様中5仕様でした。陰性対照（経口血糖降下薬）では全仕様で花粉関連なし。

**研究デザイン**: 横断的生態学的研究 | N = 47 都道府県 | 2023 年度（令和 5 年度）  
**OSF 事前登録**: https://osf.io/yuc4a（2026 年 6 月 18 日登録）

---

## Data Sources / データソース

| Source | Variables | 説明 |
|--------|-----------|------|
| NDB Open Data No.10 (MHLW, FY2023) | Allergy-specific Rx (codes 441, 449, 131, 132); comparator (264); negative control (396); per 100,000 pop. | 抗アレルギー薬・比較・陰性対照処方量 |
| Weathernews Open Data API (2023 season) | Cumulative pollen count at prefecture-capital sites (grains/cm²) | 花粉実測データ（都道府県庁所在地） |
| Japan Atmospheric Environmental Observation System (NIES, 2021–2023) | PM2.5 and SPM: 3-year prefecture means | PM2.5・SPM 3年平均値 |
| National Census / Population Statistics | Aging rate (%), population density (per km²) | 高齢化率・人口密度 |

> **Note / 注意**: NDB raw data are not included in this repository and are not redistributable.  
> NDB 生データは本リポジトリに含まれておらず、再配布できません。集計オープンデータは厚生労働省ウェブサイトから入手可能です: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

---

## Repository Structure / リポジトリ構造

```
NDB_pollen_allergy/
├── README.md
├── requirements.txt                    # Python dependencies / 依存ライブラリ
├── scripts/                            # Analysis scripts (run in order) / 解析スクリプト（番号順に実行）
│   ├── 01_extract_prescriptions.py     # NDB prescription data extraction / NDB処方薬データ抽出
│   ├── 02a_extract_pm25.py             # PM2.5 data extraction / PM2.5データ抽出
│   ├── 02b_extract_spm.py              # SPM data extraction / SPMデータ抽出
│   ├── 02c_prepare_pollen_data.py      # Pollen data preparation / 花粉データ準備
│   ├── 02d_extract_hanako_pollen.py    # Hanako pollen data / はなこさん花粉データ
│   ├── 02e_download_weathernews_pollen.py  # Weathernews pollen download / ウェザーニューズ花粉取得
│   ├── 03_integrate_dataset.py         # Dataset integration / データセット統合
│   ├── 04_statistical_analysis.py      # Main regression analysis / 主要回帰分析
│   ├── 05_visualization.py             # Figure generation / 図表作成
│   ├── 06_sensitivity_analysis.py      # Sensitivity analyses (8 specifications) / 感度分析（8仕様）
│   └── 07_diabetes_negative_control.py # Negative control analysis / 陰性対照解析
├── data/
│   └── interim/                        # Intermediate data (excluded from repo) / 中間データ（リポジトリ除外）
├── results/
│   └── figures/                        # Output figures / 出力図表
└── 04_Manuscripts/
    ├── Manuscript_How_Outcome_Definition.qmd              # Quarto source (submission version)
    ├── How_Outcome_Definition_Changes_Ecological_Inference_20260618.docx  # Submission DOCX
    ├── cover_letter_JCE.md                                # Cover letter for JCE
    ├── highlights_jce.txt                                 # JCE Highlights (≤85 chars each)
    ├── STROBE_RECORD_checklist_20260618.md                # Reporting checklist
    ├── OSF_preregistration_draft_20260618.md              # OSF analysis plan (registered)
    ├── AI_USE_DISCLOSURE.md                               # AI use disclosure
    ├── references.bib                                     # Reference library
    └── vancouver.csl                                      # Citation style
```

---

## Reproduction / 再現手順

### Prerequisites / 必要環境

- Python ≥ 3.10
- [Quarto](https://quarto.org/) (for manuscript rendering / 論文レンダリング用)

### Installation / インストール

```bash
git clone https://github.com/haruki00430/NDB_pollen_allergy.git
cd NDB_pollen_allergy
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Data Preparation / データ準備

1. Download NDB Open Data No.10 from MHLW and place Excel files under `data/raw/`.  
   NDB オープンデータ第 10 回を厚生労働省からダウンロードし `data/raw/` に配置してください。

2. Pollen and air quality data are downloaded automatically by scripts 02a–02e.  
   花粉・大気質データはスクリプト 02a〜02e で自動取得されます。

### Analysis / 解析実行

Run scripts 01 through 07 in order:  
スクリプトを 01 から 07 の順に実行してください：

```bash
python scripts/01_extract_prescriptions.py
python scripts/02a_extract_pm25.py
python scripts/02b_extract_spm.py
python scripts/02c_prepare_pollen_data.py
python scripts/02e_download_weathernews_pollen.py
python scripts/03_integrate_dataset.py
python scripts/04_statistical_analysis.py
python scripts/05_visualization.py
python scripts/06_sensitivity_analysis.py
python scripts/07_diabetes_negative_control.py
```

---

## Citation / 引用

If you use this code, please cite the associated manuscript and code repository:  
本コードを使用する場合は、論文とコードリポジトリの両方を引用してください：

**Manuscript**:
> Saito H, Ohira T. How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment. *(In submission, Journal of Clinical Epidemiology, 2026)*

**Code repository**:
> Saito H. Analysis code for "How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology" [Software]. Zenodo. 2026. https://doi.org/10.5281/zenodo.XXXXXXX

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

**OSF Analysis Plan**:
> Saito H, Ohira T. How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment — Analysis Plan. OSF Registries. 2026. https://osf.io/yuc4a

---

## Ethics / 倫理事項

This study used publicly available aggregate data. Individual informed consent was not required, and institutional ethics review was not applicable in accordance with Japanese ethical guidelines for epidemiological research.

本研究は公表集計データを使用しており、個人の同意取得および倫理審査委員会の審査は不要です（疫学研究に関する倫理指針に準拠）。

---

## License / ライセンス

Analysis code is released under the [MIT License](LICENSE).  
NDB Open Data is provided by the Ministry of Health, Labour and Welfare of Japan and is not redistributable as part of this repository.

解析コードは MIT ライセンスで公開しています。NDB オープンデータは厚生労働省が提供するものであり、本リポジトリから再配布することはできません。
