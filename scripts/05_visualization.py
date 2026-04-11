#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6: 可視化（7枚の図表生成）

入力: analysis_dataset.csv, regression_results, correlation_matrix
出力: 7枚のPNG図表（300 DPI）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
from scipy import stats as scipy_stats
import statsmodels.api as sm
import logging

# プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[3]
POLLEN_PROJECT = Path(__file__).resolve().parents[1]

# ロガー設定
log_dir = POLLEN_PROJECT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "05_visualization.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 日本語フォント設定
try:
    from ndb_library.viz import set_japanese_font
    set_japanese_font()
except ImportError:
    plt.rcParams['font.family'] = ['Meiryo', 'MS Gothic', 'Yu Gothic']
    plt.rcParams['axes.unicode_minus'] = False


def fig1_scatter_pollen_pm25(df, fig_dir):
    """Fig 1: 散布図 - 花粉飛散数 & PM2.5 vs 総処方量"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Pollen vs Total Rx
    ax = axes[0]
    ax.scatter(df['pollen_count'], df['total_allergy_rx_per_100k'] / 1e6,
               c='#2196F3', alpha=0.7, edgecolors='white', s=60)
    # 回帰直線
    x = df['pollen_count']
    y = df['total_allergy_rx_per_100k'] / 1e6
    slope, intercept, r, p, se = scipy_stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, 'r-', linewidth=2)
    ax.set_xlabel('花粉飛散指数', fontsize=12)
    ax.set_ylabel('総アレルギー薬処方量\n(百万/10万人)', fontsize=12)
    ax.set_title(f'(A) 花粉飛散数 vs 総処方量\nr={r:.3f}, p={p:.4f}', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Panel B: PM2.5 vs Total Rx
    ax = axes[1]
    ax.scatter(df['pm25_mean_3yr'], df['total_allergy_rx_per_100k'] / 1e6,
               c='#FF5722', alpha=0.7, edgecolors='white', s=60)
    x = df['pm25_mean_3yr']
    slope, intercept, r, p, se = scipy_stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, 'r-', linewidth=2)
    ax.set_xlabel('PM2.5 年平均値 (μg/m³)', fontsize=12)
    ax.set_ylabel('総アレルギー薬処方量\n(百万/10万人)', fontsize=12)
    ax.set_title(f'(B) PM2.5 vs 総処方量\nr={r:.3f}, p={p:.4f}', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = fig_dir / "fig1_scatter_pollen_pm25.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 1: {out_path}")


def fig2_correlation_heatmap(df, fig_dir):
    """Fig 2: 相関ヒートマップ"""
    cols = [
        'pollen_count', 'forest_ratio_pct', 'pm25_mean_3yr', 'spm_mean_3yr',
        'total_allergy_rx_per_100k', 'antihistamine_per_100k',
        'eye_drops_per_100k', 'nasal_sprays_per_100k',
        'aging_rate', 'pop_density'
    ]
    labels = [
        '花粉飛散数', '森林面積率', 'PM2.5', 'SPM',
        '総処方量', '抗ヒスタミン', '眼科用剤', '耳鼻科用剤',
        '高齢化率', '人口密度'
    ]
    available = [(c, l) for c, l in zip(cols, labels) if c in df.columns]
    cols_avail = [c for c, _ in available]
    labels_avail = [l for _, l in available]

    corr = df[cols_avail].corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1,
                xticklabels=labels_avail, yticklabels=labels_avail,
                ax=ax, square=True, linewidths=0.5)
    ax.set_title('変数間相関行列（下三角）', fontsize=14, pad=20)
    plt.tight_layout()

    out_path = fig_dir / "fig2_correlation_heatmap.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 2: {out_path}")


def fig3_forest_plot(df, fig_dir):
    """Fig 3: Forest plot（Model 5の標準化係数）"""
    y = df['total_allergy_rx_per_100k']
    x_cols = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25', 'aging_rate', 'pop_density']
    X = sm.add_constant(df[x_cols])
    model = sm.OLS(y, X).fit()

    # 標準化係数
    std_coefs = []
    labels_jp = {
        'pollen_count': '花粉飛散数',
        'pm25_mean_3yr': 'PM2.5',
        'pollen_x_pm25': '花粉 × PM2.5',
        'aging_rate': '高齢化率',
        'pop_density': '人口密度'
    }
    for col in x_cols:
        beta_std = model.params[col] * df[col].std() / y.std()
        se_std = model.bse[col] * df[col].std() / y.std()
        ci_lower = beta_std - 1.96 * se_std
        ci_upper = beta_std + 1.96 * se_std
        p = model.pvalues[col]
        std_coefs.append({
            'variable': labels_jp.get(col, col),
            'beta_std': beta_std,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'p': p
        })

    df_coef = pd.DataFrame(std_coefs)

    fig, ax = plt.subplots(figsize=(10, 5))
    y_pos = range(len(df_coef))

    colors = ['#2196F3' if p < 0.05 else '#9E9E9E' for p in df_coef['p']]
    ax.barh(y_pos, df_coef['beta_std'], color=colors, alpha=0.7, height=0.6)
    ax.errorbar(df_coef['beta_std'], y_pos,
                xerr=[df_coef['beta_std'] - df_coef['ci_lower'],
                      df_coef['ci_upper'] - df_coef['beta_std']],
                fmt='none', color='black', capsize=4, linewidth=1.5)

    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_coef['variable'], fontsize=12)
    ax.set_xlabel('標準化回帰係数 (95% CI)', fontsize=12)
    ax.set_title('Model 5: フルモデルの標準化係数', fontsize=14)

    # 有意な変数にアスタリスク
    for i, row in df_coef.iterrows():
        if row['p'] < 0.001:
            ax.text(row['ci_upper'] + 0.02, i, '***', fontsize=12, va='center')
        elif row['p'] < 0.01:
            ax.text(row['ci_upper'] + 0.02, i, '**', fontsize=12, va='center')
        elif row['p'] < 0.05:
            ax.text(row['ci_upper'] + 0.02, i, '*', fontsize=12, va='center')

    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()

    out_path = fig_dir / "fig3_forest_plot.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 3: {out_path}")


def fig4_model_comparison(df_models, fig_dir):
    """Fig 4: モデル比較（R²とAIC）"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    main_models = df_models[df_models['model'].str.startswith('Model')].copy()
    if len(main_models) == 0:
        logger.warning("モデル比較データがありません")
        plt.close()
        return

    x = range(len(main_models))
    labels = [m.replace('Model ', 'M') for m in main_models['model']]

    # Panel A: R²
    ax = axes[0]
    bars = ax.bar(x, main_models['r2'], color='#4CAF50', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('R²', fontsize=12)
    ax.set_title('(A) 決定係数 R²', fontsize=13)
    ax.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, main_models['r2']):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8)

    # Panel B: AIC
    ax = axes[1]
    bars = ax.bar(x, main_models['aic'], color='#FF9800', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('AIC', fontsize=12)
    ax.set_title('(B) 赤池情報量規準 AIC', fontsize=13)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(main_models['aic'].min() - 15, main_models['aic'].max() + 5)

    plt.tight_layout()
    out_path = fig_dir / "fig4_model_comparison.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 4: {out_path}")


def fig5_subgroup_analysis(df, fig_dir):
    """Fig 5: 副次解析バーチャート（薬効分類別）"""
    outcomes = {
        'antihistamine_per_100k': '抗ヒスタミン剤',
        'eye_drops_per_100k': '眼科用剤',
        'nasal_sprays_per_100k': '耳鼻科用剤'
    }
    exposures = {
        'pollen_count': '花粉飛散数',
        'pm25_mean_3yr': 'PM2.5',
        'spm_mean_3yr': 'SPM'
    }

    results = []
    for out_key, out_label in outcomes.items():
        for exp_key, exp_label in exposures.items():
            r, p = scipy_stats.pearsonr(df[exp_key], df[out_key])
            results.append({
                'outcome': out_label,
                'exposure': exp_label,
                'r': r,
                'p': p,
                'sig': '*' if p < 0.05 else ''
            })

    df_res = pd.DataFrame(results)

    fig, ax = plt.subplots(figsize=(12, 6))
    n_outcomes = len(outcomes)
    n_exposures = len(exposures)
    bar_width = 0.25
    x = np.arange(n_outcomes)
    colors = ['#2196F3', '#FF5722', '#9C27B0']

    for i, (exp_key, exp_label) in enumerate(exposures.items()):
        subset = df_res[df_res['exposure'] == exp_label]
        bars = ax.bar(x + i * bar_width, subset['r'], bar_width,
                       label=exp_label, color=colors[i], alpha=0.8)
        for j, (bar, row) in enumerate(zip(bars, subset.itertuples())):
            if row.sig:
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.02,
                        '*', ha='center', fontsize=14, fontweight='bold')

    ax.set_xticks(x + bar_width)
    ax.set_xticklabels([l for l in outcomes.values()], fontsize=12)
    ax.set_ylabel('Pearson r', fontsize=12)
    ax.set_title('薬効分類別 × 曝露変数別 Pearson相関係数', fontsize=14)
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    out_path = fig_dir / "fig5_subgroup_analysis.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 5: {out_path}")


def fig6_pollen_comparison(df, fig_dir):
    """Fig 6: 花粉指標比較（pollen_count vs forest_ratio）"""
    fig, ax = plt.subplots(figsize=(8, 7))

    ax.scatter(df['forest_ratio_pct'], df['pollen_count'],
               c='#4CAF50', alpha=0.7, edgecolors='white', s=60)

    r, p = scipy_stats.pearsonr(df['forest_ratio_pct'], df['pollen_count'])
    x = df['forest_ratio_pct']
    y = df['pollen_count']
    slope, intercept, _, _, _ = scipy_stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, 'r--', linewidth=1.5)

    ax.set_xlabel('森林面積率 (%)', fontsize=12)
    ax.set_ylabel('花粉飛散指数', fontsize=12)
    ax.set_title(f'花粉指標の収束妥当性\nr={r:.3f}, p={p:.4f}', fontsize=14)
    ax.grid(True, alpha=0.3)

    # 特筆すべき都道府県をアノテーション
    for _, row in df.iterrows():
        if row['pollen_count'] <= 10 or row['pollen_count'] >= 100:
            ax.annotate(row['pref_name'], (row['forest_ratio_pct'], row['pollen_count']),
                        fontsize=8, alpha=0.7)

    plt.tight_layout()
    out_path = fig_dir / "fig6_pollen_comparison.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 6: {out_path}")


def fig7_ranking(df, fig_dir):
    """Fig 7: 都道府県ランキング（総処方量 Top/Bottom 10）"""
    df_sorted = df.sort_values('total_allergy_rx_per_100k', ascending=True)

    top10 = df_sorted.tail(10)
    bottom10 = df_sorted.head(10)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Top 10
    ax = axes[0]
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, 10))
    ax.barh(range(10), top10['total_allergy_rx_per_100k'] / 1e6, color=colors)
    ax.set_yticks(range(10))
    ax.set_yticklabels(top10['pref_name'], fontsize=11)
    ax.set_xlabel('総処方量 (百万/10万人)', fontsize=11)
    ax.set_title('処方量上位10都道府県', fontsize=13)
    ax.grid(True, alpha=0.3, axis='x')

    # Bottom 10
    ax = axes[1]
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 10))
    ax.barh(range(10), bottom10['total_allergy_rx_per_100k'] / 1e6, color=colors[::-1])
    ax.set_yticks(range(10))
    ax.set_yticklabels(bottom10['pref_name'], fontsize=11)
    ax.set_xlabel('総処方量 (百万/10万人)', fontsize=11)
    ax.set_title('処方量下位10都道府県', fontsize=13)
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    out_path = fig_dir / "fig7_ranking.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Fig 7: {out_path}")


def main():
    logger.info("=" * 60)
    logger.info("Phase 6: 可視化開始")
    logger.info("=" * 60)

    interim_dir = POLLEN_PROJECT / "data" / "interim"
    fig_dir = POLLEN_PROJECT / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir = POLLEN_PROJECT / "results"

    # データ読み込み
    df = pd.read_csv(interim_dir / "analysis_dataset.csv", encoding="utf-8-sig")
    logger.info(f"データ: {df.shape}")

    df_models = pd.read_csv(results_dir / "model_comparison.csv", encoding="utf-8-sig")
    logger.info(f"モデル比較: {len(df_models)}モデル")

    # 図表生成
    fig1_scatter_pollen_pm25(df, fig_dir)
    fig2_correlation_heatmap(df, fig_dir)
    fig3_forest_plot(df, fig_dir)
    fig4_model_comparison(df_models, fig_dir)
    fig5_subgroup_analysis(df, fig_dir)
    fig6_pollen_comparison(df, fig_dir)
    fig7_ranking(df, fig_dir)

    logger.info("\n" + "=" * 60)
    logger.info(f"Phase 6 完了: 7枚の図表を {fig_dir} に生成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
