# NDB_XXX_pollen_allergy_v2

## ステータス（2026-04-05 リポジトリ照合）

- **原稿**: `Manuscript_pollen_allergy.qmd`（プロジェクトルート）
- **参考文献**: `references.bib`
- Phase 進捗は README 後段を参照。記述とフォルダ実体がずれたら実体を正とする。

## プロジェクト概要

**タイトル**: 花粉・PM2.5/SPM×抗アレルギー薬（v2改善版）

**研究デザイン**: 都道府県単位の生態学的研究（N=47）

**NDBバージョン**: No.10 (FY2023)

## 研究目的

実測花粉データ（ウェザーニューズ Open Data API）とPM2.5/SPMの複合曝露が抗アレルギー薬処方に与える影響を検証する。

## v1からの改善点

1. **実測花粉データ**: ウェザーニューズ Open Data API 2023年花粉（森林率→実測値）
2. **SPM追加**: PM2.5に加えてSPMも分析（相関r=0.789）
3. **アレルギー特異的**: コード441,449,131,132のみ（264外用消炎剤を除外）

## データソース

### 曝露変数
- **花粉データ**: ウェザーニューズ Open Data API 2023年（grain/m³）
- **PM2.5**: 環境省大気汚染物質広域監視システム（2021-2023年3年平均）
- **SPM**: 同上（2021-2023年3年平均）

### アウトカム
- **NDB処方薬**: アレルギー特異的（コード441, 449, 131, 132）
  - 441: 抗ヒスタミン剤
  - 449: その他のアレルギー用薬
  - 131: 鼻炎用点鼻薬
  - 132: 鼻炎用内服薬
  - **除外**: 264（外用消炎剤）→ v1でノイズと判明

### 共変量
- 人口密度
- 高齢化率

## 主要結果

### Model 5（PM2.5モデル）
- **R²**: 0.357
- **pollen**: β=63.2/grain (p=0.014*)
- **pop_density**: β=251.2 (p=0.004**)

### Model 6（SPM代替モデル）← 最重要発見
- **R²**: 0.469
- **pollen×SPM交互作用**: β=33,247 (p=0.020*)
- **pollen単独**: β=71.8 (p=0.008**)

### 花粉指標の比較
- **pollen_count（実測）**: R²=0.357
- **forest_ratio（v1）**: R²=0.242
- **ΔAIC**: 7.7（実測値の優位性）

### 感度分析
- **7/8仕様でpollen p<0.05**（頑健性確認）
- **HC3のみ p=0.082**（限界有意）
- **Moran's I**: 全モデルで非有意（空間的自己相関なし）

## ファイル構成

```
projects/NDB_XXX_pollen_allergy_v2/
├── README.md                          # このファイル
├── Manuscript_pollen_allergy.qmd      # 論文原稿（英語）
├── references.bib                     # 参考文献
├── vancouver.csl                      # 引用スタイル
├── data/
│   └── interim/                       # 中間データ
│       ├── pollen_2023.csv           # ウェザーニューズ花粉データ
│       ├── pm25_spm_2021_2023.csv    # PM2.5/SPM 3年平均
│       └── allergy_prescription.csv  # 抗アレルギー薬処方量
├── results/
│   └── figures/                       # 図表
│       ├── model5_scatter.png        # Model 5 散布図
│       ├── model6_interaction.png    # Model 6 交互作用プロット
│       └── sensitivity_forest.png    # 感度分析 Forest plot
└── docs/
    └── implementation_plan.md         # 実装計画
```

## 投稿先

### 第一希望
- **Environmental Research** (IF: 8.3)

### 第二希望
- **Science of The Total Environment** (IF: 9.8)

## Phase進捗

- [x] Phase 1: 花粉データ取得（ウェザーニューズ API）
- [x] Phase 2: PM2.5/SPMデータ取得（環境省）
- [x] Phase 3: NDB処方薬データ抽出（441,449,131,132）
- [x] Phase 4: データ統合
- [x] Phase 5: 回帰モデル構築（Model 5, 6）
- [x] Phase 6: 感度分析（8仕様）
- [x] Phase 7: 論文執筆

**進捗**: 7/7 完了（100%）

## 技術メモ

### NDB処方薬ファイルの注意
- 薬効分類コード・名称は先頭行のみ、2行目以降はNaN
- **必須修正**: `df['薬効分類コード'].ffill()` で前方補完してからフィルタ

### PM2.5とSPMの多重共線性
- **相関**: r=0.789（高い相関）
- **対応**: 同一モデルに同時投入不可 → Model 5とModel 6で分離

### ウェザーニューズ Open Data API
- URL: `https://weathernews.jp/s/pollen/open_data/`
- 2023年花粉データ（都道府県別）
- grain/m³ 単位

## 主要スクリプト

1. `01_fetch_pollen_data.py`: ウェザーニューズAPI花粉データ取得
2. `02_fetch_pm25_spm.py`: 環境省PM2.5/SPMデータ取得
3. `03_extract_ndb_allergy.py`: NDB抗アレルギー薬抽出
4. `04_data_integration.py`: データ統合
5. `05_regression_models.py`: Model 5, 6 回帰分析
6. `06_sensitivity_analysis.py`: 8仕様感度分析
7. `07_visualization.py`: 図表作成

## v1との比較

| 項目 | v1 (pollen_pm25_spatial) | v2 (pollen_allergy_v2) |
|------|-------------------------|------------------------|
| **花粉指標** | 森林率（代理指標） | 実測花粉（grain/m³） |
| **大気汚染** | PM2.5のみ | PM2.5 + SPM |
| **アウトカム** | コード264含む | 441,449,131,132のみ |
| **R²** | <0.02（Null Result） | 0.357（Model 5）, 0.469（Model 6） |
| **pollen有意性** | 非有意 | p=0.014* (Model 5), p=0.008** (Model 6) |

## 関連プロジェクト

- **NDB_XXX_pollen_pm25_spatial**: v1（Null Result → 投稿断念）
- **NDB_XXX_pollen_dermatitis**: 花粉×気象×外用消炎剤（皮膚炎）

## 更新履歴

- **2026-03-16**: プロジェクト開始（v1のNull Resultを受けて改善版）
- **2026-03-16**: Phase 1-7完了
- **2026-03-16**: 論文原稿完成（HTML/DOCX出力）

---

**PI**: PI（要更新）
**Students**: TBD
**Status**: Completed (投稿準備中)
