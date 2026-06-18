# STROBE + RECORD Checklist

**論文タイトル**: How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment  
**著者**: Haruki Saito, Tetsuya Ohira  
**対象ジャーナル**: Journal of Clinical Epidemiology  
**作成日**: 2026-06-18  
**研究デザイン**: Cross-sectional ecological study（横断的生態学的研究）  

> STROBE（観察研究）＋ RECORD（ルーティン収集データ延長版）を統合したチェックリストです。  
> 出典: von Elm et al. *Lancet* 2007 (STROBE); Benchimol et al. *PLoS Med* 2015 (RECORD)

---

## PART 1: STROBE Checklist（観察研究共通）

### Title and Abstract

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 1a | よく使われる用語でデザインを示す | タイトル・Abstract Methods: "cross-sectional ecological study" | ✅ |
| 1b | 情報量があり均衡のとれたAbstractを提供する | Abstract: 構造化（Introduction or background / Methods / Results / Discussion） | ✅ |

### Introduction

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 2 | 科学的背景と根拠を説明する | Introduction §1–3: aggregate claims data・アウトカム定義の問題・先行研究の限界 | ✅ |
| 3 | 研究の目的を明示する | Introduction 最終段落: "We hypothesized that outcome definition would shape signal recovery…" | ✅ |

### Methods

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 4 | 研究デザインの主要要素を論文の早い段階で提示する | Methods §Study Design and Unit of Analysis | ✅ |
| 5 | 設定・場所・関連期間を記述する | Methods §Study Design: "Japan's 47 prefectures… fiscal year 2023" | ✅ |
| 6 | 参加者の適格基準・情報源・選択方法を述べる | Methods §Study Design: 47都道府県（行政単位・全数） | ✅ |
| 7 | アウトカム・曝露・潜在的交絡変数を明確に定義する | Methods §Prescription Outcomes: codes 441/449/131/132/264/396; §Exposure Variables and Covariates | ✅ |
| 8 | 各変数のデータ源と測定方法を述べる | Methods §Prescription Outcomes: NDB No.10; §Exposure Variables: Weathernews・NIES・国勢調査 | ✅ |
| 9 | バイアスの潜在的な原因と対処法を述べる | Methods §Robustness: HC3 robust SE・Cook's distance・都市部除外; §Negative Control設計 | ✅ |
| 10 | 研究サイズの決定方法を説明する | Methods §Study Design: N=47（日本の全都道府県、選択なし） | ✅ |
| 11 | 連続変数の取り扱いを説明する | Methods §Analytical Framework: OLS回帰・per 100,000人標準化 | ✅ |
| 12a | 使用したすべての統計的手法を述べる | Methods §Analytical Framework: 階層的OLS回帰（Model 1–6）・Moran's I | ✅ |
| 12b | サブグループ・交互作用の解析方法を述べる | Methods §Analytical Framework: pollen × PM2.5/SPM 交互作用モデル | ✅ |
| 12c | 欠損データへの対処法を説明する | 生態学的集計データのため個票欠損なし。花粉データカバレッジについてはResults内で言及 | ✅ |
| 12d | 横断研究の場合：標本抽出戦略を考慮した解析手法を述べる | 全47都道府県（標本抽出なし）；該当なしと明記可 | ✅ |
| 12e | 感度分析を述べる | Methods §Robustness: 8仕様（Baseline OLS・HC3・外れ値除外・都市部除外・交互作用除去・対数変換） | ✅ |

### Results

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 13a | 各段階の対象者数を報告する | N=47（全数）; Table 1: 記述統計 | ✅ |
| 13b | 非参加の理由を述べる | 該当なし（行政集計データ・全47都道府県） | ✅ N/A |
| 13c | フローダイアグラムの使用を検討する | 個票選択なし・不要 | ✅ N/A |
| 14a | 研究参加者の特性を示す | Results §Descriptive; Table 1（記述統計） | ✅ |
| 14b | 各変数で欠損データのある参加者数を示す | 花粉データ（prefecture-capital sites）の測定範囲をMethodsで言及 | ✅ |
| 15 | アウトカム事象数または要約指標を報告する | Results §Outcome Specificity: R²・β・p値を各モデルで報告 | ✅ |
| 16a | 非調整推定値と（該当時）交絡変数調整推定値を報告する | Results: Model 1（pollen only）→ Model 5/6（full adjusted）の段階的報告 | ✅ |
| 16b | 連続変数をカテゴリ化した場合、カテゴリ境界を報告する | 連続変数として使用；カテゴリ化なし | ✅ N/A |
| 16c | 相対リスクを絶対リスクに換算する検討 | 生態学的研究・個人リスク推定は範囲外 | ✅ N/A |
| 17 | 他の解析を報告する | Results §Sensitivity Analyses; §True Negative Control; Supplementary Tables S1–S12 | ✅ |

### Discussion

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 18 | 主要結果を要約する | Discussion §Principal Findings: 1.72倍差・方法論的含意 | ✅ |
| 19 | 限界を論じる | Discussion §Strengths and Limitations: エコロジカルデザイン・N=47・OTC未捕捉・統合解析の限界 | ✅ |
| 20 | 慎重な総合解釈を与える | Discussion §Implications; Conclusions | ✅ |
| 21 | 一般化可能性を論じる | Discussion §Implications for Claims-Based Environmental Health Research: 他国・他疾患への適用 | ✅ |

### Other Information

| No. | 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|---------|----------------|------|
| 22 | 資金源を述べる | Funding: "None declared." | ✅ |

---

## PART 2: RECORD Checklist（ルーティン収集データ追加項目）

> RECORD = Reporting of studies Conducted using Observational Routinely-collected health Data  
> STROBE項目番号に対応した拡張項目として記載する。

| No. | RECORD 推奨事項 | 原稿での対応箇所 | 状態 |
|-----|----------------|----------------|------|
| 1.1 | 使用データの種類（行政データ・電子医療記録等）をタイトルまたはAbstractで述べる | Abstract Methods: "NDB Open Data, fiscal year 2023" | ✅ |
| 4.1 | データベースの機関的特性・データベース固有の特性を述べる | Methods §Prescription Outcomes: "NDB Open Data 10th edition, covering fiscal year 2023" | ✅ |
| 5.1 | 曝露・アウトカム・交絡変数を特定するために使用したコード・アルゴリズム・ルールを述べる | Methods §Prescription Outcomes: drug classification codes 441, 449, 131, 132, 264, 396（厚労省分類） | ✅ |
| 6.1 | コードの妥当性確認（バリデーション）を述べる | NDB官定コード体系を使用；コード選択の根拠を各アウトカムで説明 | ✅ |
| 7.1 | 個人が複数のデータエントリーを持つ場合の対処法 | 都道府県集計データ（aggregate）のため個人同定なし・該当なし | ✅ N/A |
| 8.1 | 含めたすべての変数の理由を説明する | Methods §Exposure Variables and Covariates: 各変数の根拠を記述 | ✅ |
| 12.1 | データクリーニング方法を述べる | Methods: per 100,000人標準化・NDB公開集計値をそのまま使用 | ✅ |
| 12.2 | 複雑な標本抽出デザインへの対処法 | 全47都道府県（標本抽出なし）；该当なし | ✅ N/A |
| 13.1 | 研究集団の選択を詳細に記述する | Methods §Study Design: "Japan's 47 prefectures as the unit of analysis… All variables were aggregated at the prefecture level" | ✅ |
| 19.1 | 研究目的以外に収集されたデータ使用の含意を論じる | Discussion §Strengths and Limitations: 行政集計データの限界（OTC不捕捉・生態学的誤謬等） | ✅ |
| 22.1 | 補足情報へのアクセス方法を提供する | Data Availability: NDB公開URL; Analysis code: GitHub（採択後公開）; OSF: https://osf.io/yuc4a | ⚠️ |

---

## 要対応項目（⚠️）

| 項目 | 内容 | 対応方針 |
|------|------|---------|
| **RECORD 22.1** | Data Availability 文に GitHub URL と Zenodo DOI が未記載 | GitHub Public 化・Zenodo 登録後に QMD および DOCX を更新する |

---

## 提出時の対応

JCE では STROBE・RECORD チェックリストを **Supplementary Material** ファイルタイプで提出する（採択後 online-only 公開）。  
Editorial Manager 投稿時に本ファイルを `.docx` または `.pdf` 形式で添付すること。

---

## 参考文献

- von Elm E, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *Lancet*. 2007;370(9596):1453–1457.  
- Benchimol EI, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. *PLoS Med*. 2015;12(10):e1001885.
