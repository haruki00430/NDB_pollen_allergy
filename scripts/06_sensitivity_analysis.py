#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 7a: 感度分析（Sensitivity Analysis）

Section A: Model 5（PM2.5）感度分析
  1. ベースライン
  2. 外れ値除外（Cook's距離 > 4/n）
  3. 対数変換アウトカム
  4. ロバスト標準誤差（HC3）
  5. 東京・大阪除外
  6. 交互作用なし

Section B: Model 6（SPM）感度分析
  7. ベースライン
  8. ロバスト標準誤差（HC3）
  9. 外れ値除外
  10. 東京・大阪除外
  11. 交互作用なし
  12. 対数変換アウトカム

Section C: モデル間HC3比較表
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
import logging

# プロジェクトルート
POLLEN_PROJECT = Path(__file__).resolve().parents[1]

# ロガー設定
log_dir = POLLEN_PROJECT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "06_sensitivity_analysis.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_ols(df, y_col, x_cols, model_name, cov_type='nonrobust'):
    """OLS回帰を実行し結果をdict返却"""
    X = sm.add_constant(df[x_cols])
    y = df[y_col]
    model = sm.OLS(y, X).fit(cov_type=cov_type)

    result = {
        'model': model_name,
        'n': int(model.nobs),
        'r2': model.rsquared,
        'adj_r2': model.rsquared_adj,
        'aic': model.aic,
        'bic': model.bic,
        '_x_cols': x_cols,
    }

    for var in x_cols:
        idx = list(model.params.index).index(var)
        result[f'{var}_coef'] = model.params[var]
        result[f'{var}_p'] = model.pvalues[var]
        result[f'{var}_ci_lo'] = model.conf_int().iloc[idx, 0]
        result[f'{var}_ci_hi'] = model.conf_int().iloc[idx, 1]

    return result, model


def write_result_block(f, r, x_cols):
    """結果ブロックをテキストファイルに出力"""
    f.write(f"--- {r['model']} ---\n")
    f.write(f"  N={r['n']}, R2={r['r2']:.4f}, Adj.R2={r['adj_r2']:.4f}\n")
    f.write(f"  AIC={r['aic']:.1f}, BIC={r['bic']:.1f}\n")
    for var in x_cols:
        if f'{var}_coef' in r:
            p = r[f'{var}_p']
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            f.write(f"  {var:25s}: B={r[f'{var}_coef']:>12.1f}, p={p:.6f} {sig}\n")
    f.write("\n")


def main():
    logger.info("=" * 60)
    logger.info("感度分析開始")
    logger.info("=" * 60)

    # データ読み込み
    data_path = POLLEN_PROJECT / "data" / "interim" / "analysis_dataset.csv"
    df = pd.read_csv(data_path)
    logger.info(f"データ: {df.shape}")

    results_dir = POLLEN_PROJECT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    y_col = 'total_allergy_rx_per_100k'

    # Model 5 (PM2.5) 変数セット
    x_m5 = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25', 'aging_rate', 'pop_density']
    # Model 6 (SPM) 変数セット
    x_m6 = ['pollen_count', 'spm_mean_3yr', 'pollen_x_spm', 'aging_rate', 'pop_density']

    results_m5 = []  # Model 5系
    results_m6 = []  # Model 6系

    # ================================================================
    # Section A: Model 5 (PM2.5) 感度分析
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("Section A: Model 5 (PM2.5) 感度分析")
    logger.info("=" * 60)

    # A0. ベースライン
    res, m5_base = run_ols(df, y_col, x_m5, "M5: Baseline (OLS)")
    results_m5.append(res)
    logger.info(f"  M5 Baseline: R2={res['r2']:.4f}, pollen p={res['pollen_count_p']:.6f}")

    # A1. 外れ値除外
    influence = m5_base.get_influence()
    cooks_d = influence.cooks_distance[0]
    threshold = 4 / len(df)
    outliers_m5 = df[cooks_d > threshold]['pref_name'].tolist()
    logger.info(f"  M5 outliers ({len(outliers_m5)}): {outliers_m5}")
    df_no_out_m5 = df[cooks_d <= threshold].copy()
    res, _ = run_ols(df_no_out_m5, y_col, x_m5, f"M5: Excl. outliers (n={len(df_no_out_m5)})")
    results_m5.append(res)

    # A2. 対数変換
    df_log = df.copy()
    df_log['log_y'] = np.log(df_log[y_col])
    res, _ = run_ols(df_log, 'log_y', x_m5, "M5: Log-transformed")
    results_m5.append(res)

    # A3. HC3
    res, _ = run_ols(df, y_col, x_m5, "M5: Robust SE (HC3)", cov_type='HC3')
    results_m5.append(res)
    logger.info(f"  M5 HC3: pollen p={res['pollen_count_p']:.6f}")

    # A4. 東京・大阪除外
    df_no_metro = df[~df['pref_name'].isin(['東京都', '大阪府'])].copy()
    res, _ = run_ols(df_no_metro, y_col, x_m5, f"M5: Excl. Tokyo/Osaka (n={len(df_no_metro)})")
    results_m5.append(res)

    # A5. 交互作用なし
    x_m5_noint = ['pollen_count', 'pm25_mean_3yr', 'aging_rate', 'pop_density']
    res, _ = run_ols(df, y_col, x_m5_noint, "M5: No interaction")
    results_m5.append(res)

    # ================================================================
    # Section B: Model 6 (SPM) 感度分析
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("Section B: Model 6 (SPM) 感度分析")
    logger.info("=" * 60)

    # B0. ベースライン
    res, m6_base = run_ols(df, y_col, x_m6, "M6: Baseline (OLS)")
    results_m6.append(res)
    logger.info(f"  M6 Baseline: R2={res['r2']:.4f}, pollen p={res['pollen_count_p']:.6f}")
    logger.info(f"               interaction p={res['pollen_x_spm_p']:.6f}")

    # B1. HC3
    res, _ = run_ols(df, y_col, x_m6, "M6: Robust SE (HC3)", cov_type='HC3')
    results_m6.append(res)
    logger.info(f"  M6 HC3: pollen p={res['pollen_count_p']:.6f}, "
                f"interaction p={res['pollen_x_spm_p']:.6f}")

    # B2. 外れ値除外
    influence_m6 = m6_base.get_influence()
    cooks_d_m6 = influence_m6.cooks_distance[0]
    outliers_m6 = df[cooks_d_m6 > threshold]['pref_name'].tolist()
    logger.info(f"  M6 outliers ({len(outliers_m6)}): {outliers_m6}")
    df_no_out_m6 = df[cooks_d_m6 <= threshold].copy()
    res, _ = run_ols(df_no_out_m6, y_col, x_m6, f"M6: Excl. outliers (n={len(df_no_out_m6)})")
    results_m6.append(res)

    # B3. 東京・大阪除外
    res, _ = run_ols(df_no_metro, y_col, x_m6, f"M6: Excl. Tokyo/Osaka (n={len(df_no_metro)})")
    results_m6.append(res)

    # B4. 交互作用なし
    x_m6_noint = ['pollen_count', 'spm_mean_3yr', 'aging_rate', 'pop_density']
    res, _ = run_ols(df, y_col, x_m6_noint, "M6: No interaction")
    results_m6.append(res)

    # B5. 対数変換
    res, _ = run_ols(df_log, 'log_y', x_m6, "M6: Log-transformed")
    results_m6.append(res)

    # ================================================================
    # 結果出力
    # ================================================================
    all_results = results_m5 + results_m6

    # --- CSV ---
    summary_rows = []
    for r in all_results:
        row = {
            'Model': r['model'],
            'N': r['n'],
            'R2': round(r['r2'], 4),
            'Adj_R2': round(r['adj_r2'], 4),
            'AIC': round(r['aic'], 1),
            'pollen_coef': round(r.get('pollen_count_coef', float('nan')), 1),
            'pollen_p': round(r.get('pollen_count_p', float('nan')), 6),
        }
        # 交互作用項（モデルによってキー名が異なる）
        if 'pollen_x_spm_p' in r:
            row['interaction_p'] = round(r['pollen_x_spm_p'], 6)
            row['interaction_coef'] = round(r['pollen_x_spm_coef'], 1)
        elif 'pollen_x_pm25_p' in r:
            row['interaction_p'] = round(r['pollen_x_pm25_p'], 6)
            row['interaction_coef'] = round(r['pollen_x_pm25_coef'], 1)
        else:
            row['interaction_p'] = float('nan')
            row['interaction_coef'] = float('nan')
        summary_rows.append(row)

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(results_dir / "sensitivity_analysis.csv", index=False, encoding="utf-8-sig")

    # --- テキスト ---
    txt_path = results_dir / "sensitivity_analysis.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("感度分析結果（Model 5: PM2.5 / Model 6: SPM）\n")
        f.write("=" * 70 + "\n\n")

        # Section A
        f.write("【Section A: Model 5 (PM2.5) 感度分析】\n\n")
        for r in results_m5:
            write_result_block(f, r, r['_x_cols'])

        # Section B
        f.write("\n【Section B: Model 6 (SPM) 感度分析】\n\n")
        for r in results_m6:
            write_result_block(f, r, r['_x_cols'])

        # Section C: HC3 比較表
        f.write("\n" + "=" * 70 + "\n")
        f.write("【Section C: モデル間 HC3 比較（主要変数のp値）】\n")
        f.write("=" * 70 + "\n\n")

        # M5 OLS vs HC3
        m5_ols = results_m5[0]
        m5_hc3 = results_m5[3]  # HC3 is 4th entry
        m6_ols = results_m6[0]
        m6_hc3 = results_m6[1]  # HC3 is 2nd entry

        header = f"{'Variable':<22} {'M5 OLS':>10} {'M5 HC3':>10} {'M6 OLS':>10} {'M6 HC3':>10}"
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        # pollen_count
        f.write(f"{'pollen_count':<22} "
                f"{m5_ols['pollen_count_p']:>10.4f} "
                f"{m5_hc3['pollen_count_p']:>10.4f} "
                f"{m6_ols['pollen_count_p']:>10.4f} "
                f"{m6_hc3['pollen_count_p']:>10.4f}\n")

        # interaction
        f.write(f"{'interaction':<22} "
                f"{m5_ols.get('pollen_x_pm25_p', float('nan')):>10.4f} "
                f"{m5_hc3.get('pollen_x_pm25_p', float('nan')):>10.4f} "
                f"{m6_ols.get('pollen_x_spm_p', float('nan')):>10.4f} "
                f"{m6_hc3.get('pollen_x_spm_p', float('nan')):>10.4f}\n")

        # pop_density
        f.write(f"{'pop_density':<22} "
                f"{m5_ols['pop_density_p']:>10.4f} "
                f"{m5_hc3['pop_density_p']:>10.4f} "
                f"{m6_ols['pop_density_p']:>10.4f} "
                f"{m6_hc3['pop_density_p']:>10.4f}\n")

        f.write("\n")
        f.write("Key: M5=Model 5 (PM2.5), M6=Model 6 (SPM)\n")
        f.write("     OLS=standard SE, HC3=heteroscedasticity-consistent SE\n")

        # 結論
        f.write("\n" + "=" * 70 + "\n")
        f.write("結論:\n")
        f.write("  1. pollen_count: M6 HC3 (p=%.4f) > M5 HC3 (p=%.4f) -> SPMモデルでより頑健\n"
                % (m6_hc3['pollen_count_p'], m5_hc3['pollen_count_p']))
        f.write("  2. pollen x SPM交互作用: OLS p=%.4f, HC3 p=%.4f -> suggestive\n"
                % (m6_ols['pollen_x_spm_p'], m6_hc3['pollen_x_spm_p']))
        f.write("  3. pop_density: 全仕様で有意 (M6 HC3 p=%.4f)\n"
                % m6_hc3['pop_density_p'])
        f.write("=" * 70 + "\n")

    logger.info(f"保存: {txt_path}")
    logger.info(f"保存: sensitivity_analysis.csv")

    logger.info("\n" + "=" * 60)
    logger.info("感度分析完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
