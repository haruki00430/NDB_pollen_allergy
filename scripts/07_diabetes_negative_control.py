#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
陰性対照解析：糖尿病用剤（コード396）vs 花粉飛散数

大平先生 Comment #1 への対応：
  code 264（外用消炎剤）は花粉症に非特異的に使用される可能性があるため、
  花粉症と生物学的に無関係な薬剤コード（396 糖尿病用剤）を第2比較対照として追加。

出力:
  - data/interim/prescription_diabetes.csv
  - results/diabetes_negative_control_results.txt
  - results/tables/tbl_diabetes_negative_control.csv
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[3]
POLLEN_PROJECT = Path(__file__).resolve().parents[1]

log_dir = POLLEN_PROJECT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "07_diabetes_negative_control.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PRESCRIPTION_PATH = (
    PROJECT_ROOT
    / "02_Data/raw/NDB_OpenData/No.10/05_処方薬"
    / "01_公費レセプトを含まないデータ"
    / "01_処方薬（内服／外用／注射）"
)
TARGET_CLASSIFICATION = "糖尿病用剤"   # コード 396


def load_prescription_file(file_path):
    """NDB処方薬Excel → 都道府県別合計数量（ffill必須）"""
    logger.info(f"読み込み: {file_path.name}")
    df = pd.read_excel(file_path, header=[2, 3])

    new_columns = []
    for col in df.columns:
        if 'Unnamed' in str(col[1]):
            new_columns.append(str(col[0]).replace('\n', '').replace(' ', ''))
        else:
            new_columns.append(str(col[1]))
    df.columns = new_columns

    col0, col1 = df.columns[0], df.columns[1]
    df[col0] = df[col0].ffill()
    df[col1] = df[col1].ffill()

    df_target = df[df[col1] == TARGET_CLASSIFICATION].copy()
    if len(df_target) == 0:
        logger.warning(f"対象分類なし: {file_path.name}")
        return None

    logger.info(f"  {TARGET_CLASSIFICATION}: {len(df_target)}品目")
    pref_cols = df.columns[9:]

    for col in pref_cols:
        df_target[col] = pd.to_numeric(
            df_target[col].astype(str).str.strip().replace('-', pd.NA),
            errors='coerce'
        )

    df_sum = df_target[pref_cols].sum(min_count=1)
    results = [{"prefecture": p, "quantity": float(df_sum[p]) if pd.notna(df_sum[p]) else 0.0}
               for p in pref_cols]
    df_result = pd.DataFrame(results)
    df_result = df_result[~df_result['prefecture'].str.contains('全国|総計|合計', na=False)]
    logger.info(f"  合計: {len(df_result)}都道府県, 総数量={df_result['quantity'].sum():,.0f}")
    return df_result


def extract_diabetes_prescriptions():
    """院外＋院内の糖尿病用剤を合算"""
    f_ext = PRESCRIPTION_PATH / "【内服】外来（院外）_都道府県別薬効分類別数量.xlsx"
    f_int = PRESCRIPTION_PATH / "【内服】外来（院内）_都道府県別薬効分類別数量.xlsx"

    df_ext = load_prescription_file(f_ext) if f_ext.exists() else None
    df_int = load_prescription_file(f_int) if f_int.exists() else None

    if df_ext is not None and df_int is not None:
        df = df_ext.merge(df_int, on="prefecture", suffixes=("", "_int"), how="outer")
        df["quantity"] = df["quantity"].fillna(0) + df["quantity_int"].fillna(0)
        return df[["prefecture", "quantity"]]
    return df_ext or df_int


def run_ols(df, y_col, x_cols, label, out_f):
    y = df[y_col]
    X = sm.add_constant(df[x_cols])
    model = sm.OLS(y, X).fit()

    out_f.write(f"\n{'='*60}\n{label}\n{'='*60}\n")
    out_f.write(f"N={int(model.nobs)}, R²={model.rsquared:.4f}, Adj.R²={model.rsquared_adj:.4f}\n")
    out_f.write(f"AIC={model.aic:.2f}, F={model.fvalue:.4f}, p={model.f_pvalue:.6f}\n\n")
    out_f.write(f"{'Variable':<28} {'Coef':>14} {'SE':>14} {'p':>10} {'95% CI':>30}\n")
    out_f.write(f"{'-'*96}\n")
    for var in model.params.index:
        ci = model.conf_int().loc[var]
        sig = '***' if model.pvalues[var] < 0.001 else '**' if model.pvalues[var] < 0.01 \
              else '*' if model.pvalues[var] < 0.05 else ''
        out_f.write(
            f"{var:<28} {model.params[var]:>14.4f} {model.bse[var]:>14.4f} "
            f"{model.pvalues[var]:>10.6f} [{ci[0]:>12.2f}, {ci[1]:>12.2f}] {sig}\n"
        )
    return model


def sensitivity_analysis(df, y_col, x_cols_base, label, out_f):
    """6仕様の感度分析"""
    results = []
    specs = [
        ("Baseline OLS",         df.copy(),  x_cols_base, False),
        ("HC3 robust SE",        df.copy(),  x_cols_base, True),
        ("Excl. Cook's D",       None,       x_cols_base, False),
        ("Excl. Tokyo/Osaka",    None,       x_cols_base, False),
        ("No interaction",       df.copy(),  [c for c in x_cols_base if 'x_' not in c], False),
        ("Log-transformed Y",    df.copy(),  x_cols_base, False),
    ]

    # Cook's D 除外データ作成
    y = df[y_col]; X = sm.add_constant(df[x_cols_base])
    base_model = sm.OLS(y, X).fit()
    cooks = base_model.get_influence().cooks_distance[0]
    threshold = 4 / len(df)
    df_no_cook = df[cooks < threshold].copy()
    outliers = df[cooks >= threshold]['pref_name'].tolist() if 'pref_name' in df.columns else []

    # Tokyo/Osaka 除外データ
    df_no_metro = df[~df['pref_name'].isin(['東京都', '大阪府'])].copy() if 'pref_name' in df.columns \
                  else df[df['pop_density'] < 3000].copy()

    specs[2] = ("Excl. Cook's D", df_no_cook, x_cols_base, False)
    specs[3] = ("Excl. Tokyo/Osaka", df_no_metro, x_cols_base, False)

    out_f.write(f"\n{'='*60}\n感度分析: {label}\n{'='*60}\n")
    if outliers:
        out_f.write(f"Cook's D除外: {', '.join(outliers)}\n")

    out_f.write(f"\n{'仕様':<22} {'N':>4} {'R²':>7} {'Pollen p':>10} {'有意':>6}\n")
    out_f.write(f"{'-'*52}\n")

    for spec_name, df_sp, x_sp, use_hc3 in specs:
        y_sp = np.log(df_sp[y_col]) if spec_name == "Log-transformed Y" else df_sp[y_col]
        X_sp = sm.add_constant(df_sp[x_sp])
        m = sm.OLS(y_sp, X_sp).fit()
        if use_hc3:
            m = m.get_robustcov_results(cov_type='HC3')
        pvals = m.pvalues
        if hasattr(pvals, 'get'):
            p_pollen = pvals.get('pollen_count', float('nan'))
        else:
            # HC3 returns ndarray; map by position from X_sp columns
            col_list = list(X_sp.columns)
            idx = col_list.index('pollen_count') if 'pollen_count' in col_list else -1
            p_pollen = float(pvals[idx]) if idx >= 0 else float('nan')
        sig = '*' if p_pollen < 0.05 else ''
        out_f.write(f"{spec_name:<22} {int(m.nobs):>4} {m.rsquared:>7.4f} {p_pollen:>10.4f} {sig:>6}\n")
        results.append({
            'spec': spec_name, 'n': int(m.nobs), 'r2': m.rsquared,
            'pollen_p': p_pollen, 'sig': sig != ''
        })

    n_sig = sum(r['sig'] for r in results)
    out_f.write(f"\n有意仕様数: {n_sig}/6\n")
    return results


def main():
    logger.info("="*60)
    logger.info("陰性対照解析：糖尿病用剤（コード396）")
    logger.info("="*60)

    interim_dir = POLLEN_PROJECT / "data" / "interim"
    results_dir = POLLEN_PROJECT / "results"
    tables_dir = results_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: 糖尿病用剤を抽出 ──
    logger.info("\nStep 1: 糖尿病用剤（コード396）抽出")
    df_dm = extract_diabetes_prescriptions()
    if df_dm is None:
        logger.error("抽出失敗"); return
    out_rx = interim_dir / "prescription_diabetes.csv"
    df_dm.to_csv(out_rx, index=False, encoding="utf-8-sig")
    logger.info(f"保存: {out_rx}")

    # ── Step 2: analysis_dataset に結合 ──
    logger.info("\nStep 2: analysis_dataset に結合")
    df = pd.read_csv(interim_dir / "analysis_dataset.csv", encoding="utf-8-sig")

    df_dm_renamed = df_dm.rename(columns={"quantity": "dm_raw"})
    df_dm_renamed['pref_name'] = df_dm_renamed['prefecture']
    df = df.merge(df_dm_renamed[['pref_name', 'dm_raw']], on='pref_name', how='left')
    df['diabetes_rx_per_100k'] = (df['dm_raw'] / (df['population'] / 100_000)).round(1)

    logger.info(f"糖尿病用剤/10万人: mean={df['diabetes_rx_per_100k'].mean():.1f}, "
                f"sd={df['diabetes_rx_per_100k'].std():.1f}, "
                f"min={df['diabetes_rx_per_100k'].min():.1f}, "
                f"max={df['diabetes_rx_per_100k'].max():.1f}")
    logger.info(f"欠損: {df['diabetes_rx_per_100k'].isna().sum()}")

    # ── Step 3: 回帰解析 ──
    logger.info("\nStep 3: 回帰解析")
    results_file = results_dir / "diabetes_negative_control_results.txt"

    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("陰性対照解析：糖尿病用剤（コード396）\n")
        f.write("="*60 + "\n\n")
        f.write("設定: 花粉症と生物学的に無関係な薬剤を陰性対照として使用\n")
        f.write("期待: 花粉変数が非有意（pollen p > 0.05）\n\n")

        y_col = 'diabetes_rx_per_100k'

        # Model NC-1: Pollen only
        m_nc1 = run_ols(df, y_col, ['pollen_count'],
                        'Model NC-1: Pollen only (diabetes)', f)

        # Model NC-5: Full PM2.5 model（Model 5と対応）
        x_m5 = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25', 'aging_rate', 'pop_density']
        m_nc5 = run_ols(df, y_col, x_m5,
                        'Model NC-5: Full PM2.5 model (diabetes)', f)

        # Model NC-6: Full SPM model（Model 6と対応）
        x_m6 = ['pollen_count', 'spm_mean_3yr', 'pollen_x_spm', 'aging_rate', 'pop_density']
        m_nc6 = run_ols(df, y_col, x_m6,
                        'Model NC-6: Full SPM model (diabetes)', f)

        # 感度分析（Model NC-5ベース）
        sens_results = sensitivity_analysis(df, y_col, x_m5,
                                            'Model NC-5 (diabetes PM2.5)', f)

        # ── サマリー比較表 ──
        f.write(f"\n\n{'='*60}\n")
        f.write("アウトカム比較サマリー\n")
        f.write(f"{'='*60}\n")
        f.write(f"{'アウトカム':<28} {'最良R²':>8} {'Pollen p (best)':>18} {'感度分析有意/6':>16}\n")
        f.write(f"{'-'*72}\n")
        f.write(f"{'アレルギー特異的 (441+449+131+132)':<28} {'0.469':>8} {'0.008':>18} {'6/6':>16}\n")
        f.write(f"{'外用消炎剤 code 264':<28} {'0.272':>8} {'0.046 (Model 9のみ)':>18} {'5/6 (M9)':>16}\n")
        n_sig_dm = sum(r['sig'] for r in sens_results)
        f.write(f"{'糖尿病用剤 code 396':<28} {m_nc6.rsquared:>8.3f} "
                f"{m_nc6.pvalues.get('pollen_count', float('nan')):>18.4f} "
                f"{str(n_sig_dm) + '/6':>16}\n")

        f.write("\n\n" + "="*60 + "\n解析完了\n" + "="*60 + "\n")

    logger.info(f"結果保存: {results_file}")

    # ── Step 4: 表として出力 ──
    rows = [
        {"Outcome": "Allergy-specific (codes 441/449/131/132)",
         "Best_model": "Model 6 (SPM)", "Best_R2": 0.469, "Pollen_p_best": 0.008,
         "Sensitivity_sig": "6/6", "Interpretation": "Disease-aligned"},
        {"Outcome": "Topical anti-inflammatory (code 264)",
         "Best_model": "Model 10 (Sunshine)", "Best_R2": 0.272, "Pollen_p_best": 0.094,
         "Sensitivity_sig": "5/6 (Model 9 temp.)", "Interpretation": "Heterogeneous"},
        {"Outcome": "Diabetes medications (code 396)",
         "Best_model": "Model NC-6 (SPM)",
         "Best_R2": round(m_nc6.rsquared, 3),
         "Pollen_p_best": round(m_nc6.pvalues.get('pollen_count', float('nan')), 4),
         "Sensitivity_sig": f"{sum(r['sig'] for r in sens_results)}/6",
         "Interpretation": "True negative control"},
    ]
    df_tbl = pd.DataFrame(rows)
    tbl_path = tables_dir / "tbl_diabetes_negative_control.csv"
    df_tbl.to_csv(tbl_path, index=False, encoding="utf-8-sig")
    logger.info(f"表保存: {tbl_path}")

    # ── 最終サマリー ──
    logger.info("\n" + "="*60)
    logger.info("解析結果サマリー")
    logger.info("="*60)
    logger.info(f"糖尿病用剤 (NC-1) pollen p = {m_nc1.pvalues['pollen_count']:.4f}")
    logger.info(f"糖尿病用剤 (NC-5) pollen p = {m_nc5.pvalues['pollen_count']:.4f}, R²={m_nc5.rsquared:.4f}")
    logger.info(f"糖尿病用剤 (NC-6) pollen p = {m_nc6.pvalues['pollen_count']:.4f}, R²={m_nc6.rsquared:.4f}")
    logger.info(f"感度分析有意数: {sum(r['sig'] for r in sens_results)}/6")
    logger.info("="*60)


if __name__ == "__main__":
    main()
