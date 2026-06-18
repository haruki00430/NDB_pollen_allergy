# Editorial Manager (JCE) 投稿手順書

**論文**: How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment  
**投稿先**: Journal of Clinical Epidemiology  
**EM URL**: https://www.editorialmanager.com/jclinepi/  
**作成日**: 2026-06-18

---

## 事前確認

手元に以下を用意してください：

| 必要事項 | 内容 |
|---------|------|
| EM アカウント | `m211039@fmu.ac.jp` で登録済みか確認 |
| 電話番号 | 国際形式：`+81-24-547-XXXX`（大学代表）または携帯番号 |
| submission_package/ | 下記6ファイル |
| ORCID × 2名 | HS: 0009-0009-7890-6068 / TO: 0000-0003-4532-7165 |

### submission_package/ ファイル一覧

| ファイル | 内容 |
|---------|------|
| `manuscript_main.docx` | ブラインド原稿（著者情報除去済み） |
| `title_page_JCE.docx` | タイトルページ（著者・所属・宣言事項） |
| `cover_letter_JCE.docx` | カバーレター |
| `highlights_jce.txt` | ハイライト5項目（≤85字） |
| `STROBE_RECORD_checklist_20260618.docx` | STROBE+RECORDチェックリスト |
| `Figure1_conceptual_model.png` | Figure 1（1800×1100 px, 300 dpi） |

---

## Step 1 — ログイン・アカウント設定

1. https://www.editorialmanager.com/jclinepi/ にアクセス
2. **"Login"** をクリック → メールアドレス + パスワードでログイン
   - 初回の場合 **"Register"** から新規登録（姓名・所属・メール・電話番号）
3. ログイン後、右上の **"Update My Information"** から：
   - 電話番号が入力されているか確認（なければここで入力）
   - ORCID 連携ボタンがあれば HS の ORCID（0009-0009-7890-6068）を接続

> EM は電話番号が未入力だと Submit ボタンが押せないケースがあります。先に確認しておくと安全です。

---

## Step 2 — 新規投稿の開始

1. Author メニューから **"Submit New Manuscript"** をクリック
2. **Article Type** の選択画面で：
   ```
   Original Research Article
   ```
   を選択 → **"Proceed"**

---

## Step 3 — タイトル・Abstract の入力

各フィールドに以下をコピペします：

**Title（タイトル）**
```
How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment
```

**Running Title（短縮タイトル）**
```
Outcome definition shapes ecological inference
```

**Abstract（抄録）**  
→ `manuscript_main.docx` を開いて Abstract 部分（294語）をそのままコピー

**Keywords（キーワード）**  
→ 1つずつ入力欄に貼り付け：
```
outcome misclassification
ecological inference
prescription data
outcome definition
measurement error
allergic rhinitis
Japan
```

---

## Step 4 — 著者情報の入力

**Corresponding author（HS）を最初に入力：**

| 項目 | 内容 |
|-----|------|
| First Name | Haruki |
| Last Name | Saito |
| Degree | MD（または空欄でも可） |
| Email | m211039@fmu.ac.jp |
| Phone | `+81-24-547-XXXX`（EM 登録電話番号） |
| Institution | Fukushima Medical University |
| Department | Department of Epidemiology |
| Country | Japan |
| ORCID | 0009-0009-7890-6068 |
| Corresponding? | **Yes** にチェック |

**2人目（TO）を追加：**  
**"Add Author"** ボタン →

| 項目 | 内容 |
|-----|------|
| First Name | Tetsuya |
| Last Name | Ohira |
| Email | （Ohira 先生のメールアドレス） |
| Institution | Fukushima Medical University |
| Department | Department of Epidemiology |
| ORCID | 0000-0003-4532-7165 |
| Corresponding? | No |

> 著者の順序はドラッグ＆ドロップで入れ替え可能です。HS → TO の順に並べてください。

---

## Step 5 — ファイルのアップロード

**"Attach Files"** セクションで、以下の順番・ファイル種別で1つずつアップロードします：

| 順番 | ファイル | File Designation（プルダウン選択） |
|:---:|---------|------|
| 1 | `title_page_JCE.docx` | **Title Page** |
| 2 | `manuscript_main.docx` | **Blinded Manuscript** |
| 3 | `Figure1_conceptual_model.png` | **Figure** |
| 4 | `cover_letter_JCE.docx` | **Cover Letter** |
| 5 | `highlights_jce.txt` | **Highlights** |
| 6 | `STROBE_RECORD_checklist_20260618.docx` | **Supplementary Material** または **Checklist** |

> 補足テーブル（S1–S12）は本文 DOCX の末尾に含まれているため、別途ファイルは不要です。

各ファイルをアップロードしたら **"Confirm"** → 全ファイル分繰り返します。

---

## Step 6 — 宣言事項の入力

EM のフォームに以下を入力します：

| 項目 | 内容 |
|-----|------|
| **Conflict of Interest** | `The authors declare no conflicts of interest.` |
| **Funding** | `None declared. No external funding was received for this study.` |
| **Ethics** | `This study used publicly available aggregate data. Individual informed consent was not required.` |
| **Data Availability** | `Analysis code is openly available on GitHub (https://github.com/haruki00430/NDB_pollen_allergy) and archived on Zenodo (https://doi.org/10.5281/zenodo.20747801).` |
| **Pre-registration** | `https://osf.io/yuc4a` |
| **AI Use** | `AI-assisted tools (Claude Sonnet 4.6, GPT-5.5, Gemini 3 Pro) were used for manuscript drafting and code development. The authors reviewed all outputs and take full responsibility.` |

---

## Step 7 — PDF プレビューの確認

全入力後に **"Build PDF for Approval"** ボタンをクリックします。

数分後にPDFが生成されます。以下を確認してください：

- [ ] タイトルページ（著者名・所属・連絡先）が正しく表示されている
- [ ] Abstract が完全に表示されている
- [ ] Figure 1 が正しい位置・解像度で表示されている
- [ ] ブラインド原稿に著者名・所属が残っていない
- [ ] 参考文献がすべて表示されている（20件）
- [ ] Supplementary Tables が末尾に含まれている

問題があれば **"Edit Submission"** で修正 → 再 PDF 生成。

---

## Step 8 — Submit

PDF確認後：

1. **"Approve PDF"** ボタンをクリック
2. 最終確認画面で内容を確認
3. **"Submit"** ボタンをクリック

送信完了後：

- 登録メールに **Manuscript ID**（例：`JCLINEPI-D-26-XXXXX`）が届きます
- EM の "Author Main Menu" → **"Submissions Being Processed"** から進捗確認可能
- 通常1〜3業務日以内に「査読送付」または「Desk Rejection」の連絡が来ます

---

## よくある問題と対処法

| 問題 | 対処 |
|-----|------|
| Submit ボタンが押せない | 電話番号未入力が原因。"Update My Information" で追加 |
| PDF ビルドがエラー | DOCX 内に特殊フォント/画像破損の可能性。PNG を JPEG に変換して再アップ |
| 著者の共著者招待メールが届く | TO先生に「EM からメールが届いたら承認してください」と事前連絡を |
| ファイル種別が見つからない | "Other" または "Supplementary Material" を選択 |

---

## 投稿後の対応

| 通知 | 対応 |
|-----|------|
| "Under Review" | 査読中。通常4〜8週間 |
| "Major Revision" | 査読コメントに回答 → Revision を EM からアップロード |
| "Minor Revision" | 軽微な修正 → 通常2〜4週間で再審査 |
| "Reject" | 他誌への転送を検討（投稿先候補リスト参照） |
| "Accept" | Zenodo に最終版をアップロード（DOI: 10.5281/zenodo.20747801 に紐付け） |
