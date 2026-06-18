# OSF Pre-registration Draft

**Status**: Draft — not yet submitted to OSF  
**Target journal**: Journal of Clinical Epidemiology  
**Created**: 2026-06-18  
**Corresponding author**: Haruki Saito  
**Co-author**: Tetsuya Ohira  

> このファイルは OSF 登録フォームへのコピー用下書きです。  
> OSF でプロジェクト作成後、Registration を freeze し、得られた URL を原稿 Methods の Study Registration に反映してください。

---

## Registration Title

How Outcome Definition Changes Ecological Inference in Prescription-Based Epidemiology: A Natural Experiment — Analysis Plan

---

## 1. Study Information

### 1.1 Study type

- **Design**: Cross-sectional ecological study  
- **Unit of analysis**: Japan's 47 prefectures (N = 47)  
- **Study period**: Fiscal year 2023 (NDB Open Data 10th edition)  
- **Registration type**: Inferential observational study (hypothesis-testing)  

### 1.2 Objectives

**Primary objective**

To quantify how ecological inference changes when exposure variables, covariates, and regression frameworks are held constant while the medication-based outcome varies in pharmacological specificity.

**Primary hypothesis**

An allergy-specific prescription outcome will recover a stronger and more robust pollen-associated signal than a pharmacologically heterogeneous comparator outcome under identical analytical conditions.

**Secondary hypotheses**

1. A pharmacologically unrelated negative control outcome (oral hypoglycemic agents) will show no consistent pollen association under the same framework.  
2. Sensitivity analyses will show greater stability of pollen coefficients for the allergy-specific outcome than for the heterogeneous comparator.  
3. Within the allergy-specific outcome, antihistamine/anti-allergy agents (codes 441/449) will show the strongest pollen association among drug subcategories.

### 1.3 Case study rationale

Seasonal pollen exposure in Japan provides a natural-experiment exposure with an established biological pathway to allergic disease. Pollen is used as a **tractable exposure signal** to evaluate outcome measurement properties; the contribution is methodological (outcome definition in prescription-based ecological inference), not etiological inference about pollen and allergy per se.

---

## 2. Data Sources (all publicly available aggregate data)

| Domain | Source | Variables |
|--------|--------|-----------|
| Prescription outcomes | NDB Open Data 10th ed. (FY2023) | Drug classification codes 441, 449, 131, 132, 264, 396; per 100,000 population |
| Pollen exposure | Weathernews Open Data API (2023 season) | Cumulative pollen count at prefecture-capital sites |
| Air pollution | Japan atmospheric environmental observation system | PM2.5 and SPM: 3-year prefecture means (2021–2023) |
| Demographics | National census / population statistics | Aging rate, population density |

**Exclusion**: Individual-level records are not used. No re-identification is attempted.

---

## 3. Outcome Definitions (prespecified)

### 3.1 Primary outcome (high specificity)

Sum of allergy-oriented medication groups, standardized per 100,000 population:

- Antihistamines and anti-allergy agents: codes **441, 449**  
- Ophthalmic preparations: code **131**  
- Nasal preparations: code **132**

### 3.2 Comparator outcome (low specificity)

- Topical anti-inflammatory agents: code **264**  
- Rationale: pharmacologically heterogeneous; includes non-allergic indications

### 3.3 Negative control outcome

- Oral hypoglycemic agents (diabetes medications): code **396**  
- Rationale: no established biological pathway from seasonal pollen to diabetes management

All three outcomes are analyzed with **identical** exposure data, covariates, and regression frameworks.

---

## 4. Exposure and Covariates (prespecified)

**Primary exposure**

- Pollen dispersal count (`pollen_count`, grains/cm², 2023 season cumulative)

**Secondary / adjustment exposures** (not simultaneously with SPM in the same model)

- PM2.5: 3-year prefecture mean  
- SPM: 3-year prefecture mean  
- *Note*: PM2.5 and SPM are highly correlated (r ≈ 0.79–0.81); modeled in **separate** specifications

**Covariates**

- Aging rate (%)  
- Population density (per km²)

**Alternative pollen indicator (sensitivity only)**

- Forest area ratio (proxy pollen indicator from v1 analysis)

---

## 5. Statistical Analysis Plan

### 5.1 Primary analysis framework

Ordinary least squares (OLS) regression at the prefecture level (N = 47).

**Hierarchical models (allergy-specific and code 264 comparator; parallel structure)**

| Model | Specification |
|-------|---------------|
| Model 1 | Pollen only |
| Model 2 | PM2.5 only |
| Model 3 | Pollen + PM2.5 |
| Model 4 | Pollen + PM2.5 + pollen × PM2.5 interaction |
| Model 5 | Model 4 + aging rate + population density (full PM2.5 model) |
| Model 6 | Pollen + SPM + pollen × SPM + aging rate + population density (full SPM model) |

**Primary contrast metrics**

1. Best-model R² (allergy-specific vs. code 264)  
2. Comparable-model R² gap (e.g., Model 5 PM2.5 specification)  
3. Pollen coefficient p-value and 95% CI in prespecified models  
4. Count of sensitivity specifications with pollen p < 0.05

**Primary inference model (allergy-specific)**

- Model 6 (SPM + interaction + covariates) as the best-fitting prespecified specification

### 5.2 Negative control analysis

Same hierarchical framework (Models NC-1, NC-5, NC-6) applied to code 396.

**Expected result**: No consistent pollen association across specifications.

### 5.3 Sensitivity analyses (prespecified)

Applied to Model 5 (PM2.5) and Model 6 (SPM) for allergy-specific outcome; parallel specifications for code 264:

1. Baseline OLS  
2. HC3 heteroscedasticity-consistent standard errors  
3. Exclusion of influential observations (Cook's distance > 4/n)  
4. Exclusion of Tokyo and Osaka (extreme population density)  
5. Removal of interaction term  
6. Log-transformation of prescription outcome  

**Robustness criterion**: Proportion of specifications with pollen p < 0.05 (e.g., 7/8 vs. 5/6).

### 5.4 Spatial diagnostics

- Global Moran's I on outcomes and residuals  
- Spatial lag / error models only if residual spatial autocorrelation is substantively indicated  
- *Prespecified interpretation*: Spatial diagnostics are descriptive; the primary contrast is outcome-specific signal recovery, not spatial modeling

### 5.5 Subgroup analysis (exploratory, prespecified)

Drug-category-specific OLS for antihistamines (441+449), ophthalmic (131), and nasal sprays (132) separately.

### 5.6 Software

- Python 3.x: pandas, statsmodels, scipy  
- Random seed: 42 (where applicable)  
- Analysis scripts: `scripts/01_extract_prescriptions.py` through `scripts/07_diabetes_negative_control.py`

---

## 6. Deviations from Plan

Any post-hoc analytical choices not listed above will be reported as deviations in the manuscript Methods or Supplementary Material. Models 7–11 (humidity, temperature, sunshine, precipitation) for the code 264 comparator were evaluated in parallel source analyses and are reported as supplementary hierarchical results (Supplementary Table S2); they were not part of the primary allergy-specific model hierarchy.

---

## 7. Reporting Guidelines

- STROBE (observational studies)  
- RECORD (routinely collected health data)  
- Completed checklists to be submitted as supplementary material at journal submission

---

## 8. Data and Code Availability (planned)

- **Data**: NDB Open Data and environmental data are publicly available; URLs in manuscript Data Availability  
- **Code**: GitHub repository `NDB_XXX_pollen_allergy_v2` (to be made public) + Zenodo DOI archive  
- **Results**: Prefecture-level aggregate outputs only; no individual-level data

---

## 9. Ethics

Public aggregate statistics only; ethics review not required.

---

## 10. Timeline Note

Primary statistical analyses were conducted between March and June 2026 prior to formal OSF registration. This registration documents the prespecified analytic framework as it was applied and locks the analysis plan before peer review. The registration date will be recorded at OSF freeze.

---

## OSF Submission Checklist

- [ ] Create OSF project: `pollen-outcome-definition-ecological-inference`  
- [ ] Select registration template (e.g., *Open Practice Badges* or *AsPredicted-style* custom)  
- [ ] Paste Sections 1–8 into registration form  
- [ ] Attach this file and `Manuscript_How_Outcome_Definition.qmd` as linked materials  
- [ ] Freeze registration → obtain URL (`https://osf.io/xxxxx`)  
- [ ] Replace `https://osf.io/XXXXX` in QMD Methods → Study Registration  
- [ ] Add registration URL to Cover letter

---

*Draft prepared for NDB_XXX_pollen_allergy_v2 / JCE submission workflow — 2026-06-18*
