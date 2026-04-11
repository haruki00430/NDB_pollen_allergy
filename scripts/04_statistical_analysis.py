#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 5: 統計解析（階層的OLS回帰 + 空間分析）

入力: analysis_dataset.csv（47都道府県×16変数）
出力: 回帰結果、相関行列、記述統計、Moran's I

解析戦略:
  - Model 1-6: 花粉飛散数（pollen_count）を主曝露変数とした階層的OLS
  - Model A-B: 森林率（forest_ratio_pct）を代替花粉指標とした感度分析
  - 副次解析: 薬効分類別（antihistamine, eye_drops, nasal_sprays）
  - 空間分析: Moran's I + SLM/SEM（残差の空間的自己相関が有意な場合）

注意: PM2.5とSPMはr=0.806（高相関）のため同一モデルに同時投入しない。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml
import logging
from scipy import stats as scipy_stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

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
        logging.FileHandler(log_dir / "04_statistical_analysis.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def load_config():
    config_path = POLLEN_PROJECT / "config" / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def descriptive_statistics(df, results_dir):
    """記述統計量の算出"""
    logger.info("\n" + "=" * 60)
    logger.info("記述統計")
    logger.info("=" * 60)

    numeric_cols = df.select_dtypes(include='number').columns.drop('pref_code')
    desc_rows = []
    for col in numeric_cols:
        series = df[col]
        sw_stat, sw_p = scipy_stats.shapiro(series)
        desc_rows.append({
            'variable': col,
            'n': series.notna().sum(),
            'mean': series.mean(),
            'sd': series.std(),
            'median': series.median(),
            'iqr': series.quantile(0.75) - series.quantile(0.25),
            'min': series.min(),
            'max': series.max(),
            'shapiro_w': sw_stat,
            'shapiro_p': sw_p,
            'normal': 'Yes' if sw_p > 0.05 else 'No'
        })

    df_desc = pd.DataFrame(desc_rows)
    out_file = results_dir / "descriptive_statistics.csv"
    df_desc.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(f"保存: {out_file}")

    for _, row in df_desc.iterrows():
        logger.info(f"  {row['variable']}: mean={row['mean']:.2f}, sd={row['sd']:.2f}, "
                     f"Shapiro p={row['shapiro_p']:.4f} ({'Normal' if row['normal'] == 'Yes' else 'Non-normal'})")

    return df_desc


def correlation_matrix(df, results_dir):
    """相関行列の算出"""
    logger.info("\n" + "=" * 60)
    logger.info("相関行列")
    logger.info("=" * 60)

    analysis_cols = [
        'pollen_count', 'forest_ratio_pct', 'pm25_mean_3yr', 'spm_mean_3yr',
        'antihistamine_per_100k', 'eye_drops_per_100k', 'nasal_sprays_per_100k',
        'total_allergy_rx_per_100k', 'aging_rate', 'pop_density'
    ]
    available = [c for c in analysis_cols if c in df.columns]

    df_corr = df[available].corr()
    out_file = results_dir / "correlation_matrix.csv"
    df_corr.to_csv(out_file, encoding="utf-8-sig")
    logger.info(f"保存: {out_file}")

    # 主要な相関のみ表示
    outcome = 'total_allergy_rx_per_100k'
    if outcome in df_corr.columns:
        logger.info(f"\n{outcome} との相関:")
        for col in available:
            if col != outcome:
                r = df_corr.loc[outcome, col]
                _, p = scipy_stats.pearsonr(df[outcome], df[col])
                sig = '*' if p < 0.05 else ''
                logger.info(f"  {col}: r={r:.3f}, p={p:.4f} {sig}")

    return df_corr


def run_ols_model(df, y_col, x_cols, model_name, results_list):
    """OLS回帰モデルの実行"""
    y = df[y_col]
    X = sm.add_constant(df[x_cols])
    model = sm.OLS(y, X).fit()

    result_entry = {
        'model': model_name,
        'y': y_col,
        'x_vars': ', '.join(x_cols),
        'n': int(model.nobs),
        'r2': model.rsquared,
        'adj_r2': model.rsquared_adj,
        'aic': model.aic,
        'bic': model.bic,
        'f_stat': model.fvalue,
        'f_pvalue': model.f_pvalue,
    }
    results_list.append(result_entry)

    return model


def format_model_results(model, model_name, f):
    """モデル結果のフォーマット出力"""
    f.write(f"\n{'=' * 60}\n")
    f.write(f"{model_name}\n")
    f.write(f"{'=' * 60}\n")
    f.write(f"N={int(model.nobs)}, R²={model.rsquared:.4f}, Adj.R²={model.rsquared_adj:.4f}\n")
    f.write(f"AIC={model.aic:.2f}, BIC={model.bic:.2f}\n")
    f.write(f"F={model.fvalue:.4f}, p={model.f_pvalue:.6f}\n\n")

    f.write(f"{'Variable':<30} {'Coef':>12} {'SE':>12} {'t':>10} {'p':>12} {'95% CI':>30}\n")
    f.write(f"{'-' * 106}\n")

    for var in model.params.index:
        coef = model.params[var]
        se = model.bse[var]
        t = model.tvalues[var]
        p = model.pvalues[var]
        ci = model.conf_int().loc[var]
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        f.write(f"{var:<30} {coef:>12.4f} {se:>12.4f} {t:>10.4f} {p:>12.6f} "
                f"[{ci[0]:>12.2f}, {ci[1]:>12.2f}] {sig}\n")


def compute_vif(df, x_cols):
    """VIF（分散拡大係数）の計算"""
    X = sm.add_constant(df[x_cols])
    vif_data = []
    for i, col in enumerate(X.columns):
        if col == 'const':
            continue
        vif_val = variance_inflation_factor(X.values, i)
        vif_data.append({'variable': col, 'vif': vif_val})
    return pd.DataFrame(vif_data)


def spatial_analysis(df, model_residuals, results_dir, f):
    """空間的自己相関分析"""
    logger.info("\n" + "=" * 60)
    logger.info("空間分析")
    logger.info("=" * 60)

    try:
        import libpysal
        from esda.moran import Moran
    except ImportError:
        logger.warning("libpysal/esda がインストールされていません。空間分析をスキップします。")
        f.write("\n\n空間分析: libpysal/esda 未インストールのためスキップ\n")
        return

    # GeoJSON読み込みとQueen隣接行列構築
    try:
        import geopandas as gpd

        geojson_path = PROJECT_ROOT / "02_Data" / "master" / "spatial" / "prefectures_utf8.geojson"
        if not geojson_path.exists():
            geojson_path = PROJECT_ROOT / "02_Data" / "master" / "spatial" / "prefectures.geojson"

        gdf = gpd.read_file(geojson_path)
        logger.info(f"GeoJSON読み込み: {len(gdf)}件")

        # dissolve if needed (multiple polygons per prefecture)
        if len(gdf) > 47:
            # 都道府県名またはコードでdissolve
            name_col = [c for c in gdf.columns if 'nam' in c.lower() or 'name' in c.lower() or 'N03_001' in c]
            if name_col:
                gdf = gdf.dissolve(by=name_col[0]).reset_index()

        # Queen隣接行列
        w = libpysal.weights.Queen.from_dataframe(gdf)

        # 離島の補完（KNN=1）
        islands = [k for k, v in w.neighbors.items() if len(v) == 0]
        if islands:
            logger.info(f"離島（隣接なし）: {len(islands)}ノード → KNN=1で補完")
            w_knn = libpysal.weights.KNN.from_dataframe(gdf, k=1)
            for island in islands:
                w.neighbors[island] = w_knn.neighbors[island]
                w.weights[island] = w_knn.weights[island]

        w.transform = 'R'
        logger.info(f"空間重み行列: {w.n}ノード, 平均隣接数={w.mean_neighbors:.1f}")

    except Exception as e:
        logger.error(f"空間重み行列構築エラー: {e}")
        f.write(f"\n\n空間分析エラー: {e}\n")
        return

    # Moran's I（アウトカムと残差）
    f.write(f"\n\n{'=' * 60}\n")
    f.write(f"空間的自己相関分析 (Moran's I)\n")
    f.write(f"{'=' * 60}\n")

    moran_results = []

    # アウトカム変数のMoran's I
    outcome_cols = ['total_allergy_rx_per_100k', 'antihistamine_per_100k',
                    'eye_drops_per_100k', 'nasal_sprays_per_100k']

    for col in outcome_cols:
        if col in df.columns:
            try:
                vals = df[col].values
                if len(vals) == w.n:
                    mi = Moran(vals, w, permutations=999)
                    moran_results.append({
                        'variable': col,
                        'moran_i': mi.I,
                        'expected_i': mi.EI,
                        'p_value': mi.p_sim,
                        'z_score': mi.z_sim
                    })
                    sig = '*' if mi.p_sim < 0.05 else ''
                    f.write(f"  {col}: I={mi.I:.4f}, E[I]={mi.EI:.4f}, p={mi.p_sim:.4f} {sig}\n")
                    logger.info(f"  {col}: Moran's I={mi.I:.4f}, p={mi.p_sim:.4f} {sig}")
            except Exception as e:
                logger.warning(f"  {col}: Moran's I計算エラー: {e}")

    # 残差のMoran's I
    if model_residuals is not None and len(model_residuals) == w.n:
        try:
            mi_resid = Moran(model_residuals, w, permutations=999)
            moran_results.append({
                'variable': 'OLS_residuals',
                'moran_i': mi_resid.I,
                'expected_i': mi_resid.EI,
                'p_value': mi_resid.p_sim,
                'z_score': mi_resid.z_sim
            })
            sig = '*' if mi_resid.p_sim < 0.05 else ''
            f.write(f"\n  OLS残差: I={mi_resid.I:.4f}, E[I]={mi_resid.EI:.4f}, p={mi_resid.p_sim:.4f} {sig}\n")
            logger.info(f"  OLS残差: Moran's I={mi_resid.I:.4f}, p={mi_resid.p_sim:.4f} {sig}")

            # 残差の空間的自己相関が有意な場合、SLM/SEMを実行
            if mi_resid.p_sim < 0.05:
                f.write("\n残差の空間的自己相関が有意 → SLM/SEMを実行\n")
                try:
                    from spreg import GM_Lag, GM_Error

                    y = df['total_allergy_rx_per_100k'].values.reshape(-1, 1)
                    x_cols_spatial = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25',
                                     'aging_rate', 'pop_density']
                    x_cols_available = [c for c in x_cols_spatial if c in df.columns]
                    X = df[x_cols_available].values

                    # SLM
                    slm = GM_Lag(y, X, w=w, name_y='total_allergy_rx_per_100k',
                                 name_x=x_cols_available)
                    f.write(f"\n{'=' * 60}\n")
                    f.write(f"Spatial Lag Model (SLM)\n")
                    f.write(f"{'=' * 60}\n")
                    f.write(f"Pseudo-R² = {slm.pr2:.4f}\n")
                    f.write(f"Rho (spatial lag) = {slm.betas.flatten()[-1]:.4f}\n\n")
                    var_names = ['const'] + x_cols_available + ['W_y (rho)']
                    for i, name in enumerate(var_names):
                        beta = slm.betas.flatten()[i]
                        se = slm.std_err.flatten()[i] if i < len(slm.std_err.flatten()) else float('nan')
                        z = slm.z_stat[i][0] if i < len(slm.z_stat) else float('nan')
                        p = slm.z_stat[i][1] if i < len(slm.z_stat) else float('nan')
                        sig_s = '*' if p < 0.05 else ''
                        f.write(f"  {name:<30} β={beta:>12.4f}  SE={se:>12.4f}  z={z:>8.4f}  p={p:>8.4f} {sig_s}\n")

                    # SEM
                    sem = GM_Error(y, X, w=w, name_y='total_allergy_rx_per_100k',
                                   name_x=x_cols_available)
                    f.write(f"\n{'=' * 60}\n")
                    f.write(f"Spatial Error Model (SEM)\n")
                    f.write(f"{'=' * 60}\n")
                    f.write(f"Pseudo-R² = {sem.pr2:.4f}\n")
                    lam = sem.betas.flatten()[-1]
                    f.write(f"Lambda = {lam:.4f}\n\n")
                    var_names_sem = ['const'] + x_cols_available + ['lambda']
                    for i, name in enumerate(var_names_sem):
                        beta = sem.betas.flatten()[i]
                        se = sem.std_err.flatten()[i] if i < len(sem.std_err.flatten()) else float('nan')
                        z = sem.z_stat[i][0] if i < len(sem.z_stat) else float('nan')
                        p = sem.z_stat[i][1] if i < len(sem.z_stat) else float('nan')
                        sig_s = '*' if p < 0.05 else ''
                        f.write(f"  {name:<30} β={beta:>12.4f}  SE={se:>12.4f}  z={z:>8.4f}  p={p:>8.4f} {sig_s}\n")

                except Exception as e:
                    f.write(f"\nSLM/SEMエラー: {e}\n")
                    logger.error(f"SLM/SEMエラー: {e}")
        except Exception as e:
            logger.warning(f"  残差Moran's I計算エラー: {e}")

    # Moran's I結果を保存
    if moran_results:
        df_moran = pd.DataFrame(moran_results)
        df_moran.to_csv(results_dir / "moran_i_results.csv", index=False, encoding="utf-8-sig")
        logger.info(f"保存: moran_i_results.csv")


def main():
    logger.info("=" * 60)
    logger.info("Phase 5: 統計解析開始")
    logger.info("=" * 60)

    interim_dir = POLLEN_PROJECT / "data" / "interim"
    results_dir = POLLEN_PROJECT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # データ読み込み
    df = pd.read_csv(interim_dir / "analysis_dataset.csv", encoding="utf-8-sig")
    logger.info(f"データ: {df.shape}")

    # === 1. 記述統計 ===
    descriptive_statistics(df, results_dir)

    # === 2. 相関行列 ===
    correlation_matrix(df, results_dir)

    # === 3. 階層的OLS回帰 ===
    logger.info("\n" + "=" * 60)
    logger.info("階層的OLS回帰")
    logger.info("=" * 60)

    results_list = []
    y_col = 'total_allergy_rx_per_100k'

    # 結果テキストファイル
    results_file = results_dir / "regression_results.txt"
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("NDB_XXX_pollen_allergy_v2: 回帰分析結果\n")
        f.write("=" * 60 + "\n\n")

        # --- 主解析: pollen_count使用 ---
        f.write("【主解析: 花粉飛散数（pollen_count）を使用】\n")

        # Model 1: 花粉のみ
        m1 = run_ols_model(df, y_col, ['pollen_count'], 'Model 1: Pollen only', results_list)
        format_model_results(m1, 'Model 1: Pollen only', f)

        # Model 2: PM2.5のみ
        m2 = run_ols_model(df, y_col, ['pm25_mean_3yr'], 'Model 2: PM2.5 only', results_list)
        format_model_results(m2, 'Model 2: PM2.5 only', f)

        # Model 3: 花粉 + PM2.5
        m3 = run_ols_model(df, y_col, ['pollen_count', 'pm25_mean_3yr'],
                          'Model 3: Pollen + PM2.5', results_list)
        format_model_results(m3, 'Model 3: Pollen + PM2.5', f)

        # Model 4: + 交互作用
        m4 = run_ols_model(df, y_col, ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25'],
                          'Model 4: + Interaction', results_list)
        format_model_results(m4, 'Model 4: + Interaction (pollen × PM2.5)', f)

        # Model 5: フルモデル
        m5 = run_ols_model(df, y_col,
                          ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25', 'aging_rate', 'pop_density'],
                          'Model 5: Full (+ covariates)', results_list)
        format_model_results(m5, 'Model 5: Full (pollen + PM2.5 + interaction + covariates)', f)

        # Shapiro-Wilk on Model 5 residuals
        sw_stat, sw_p = scipy_stats.shapiro(m5.resid)
        f.write(f"\nShapiro-Wilk (Model 5 residuals): W={sw_stat:.4f}, p={sw_p:.4f}\n")

        # Model 6: SPM代替モデル
        m6 = run_ols_model(df, y_col,
                          ['pollen_count', 'spm_mean_3yr', 'pollen_x_spm', 'aging_rate', 'pop_density'],
                          'Model 6: SPM alternative', results_list)
        format_model_results(m6, 'Model 6: SPM alternative (pollen + SPM + interaction + covariates)', f)

        # --- 感度分析: forest_ratio使用 ---
        f.write("\n\n【感度分析: 森林面積率（forest_ratio_pct）を使用】\n")

        # Model A
        mA = run_ols_model(df, y_col,
                          ['forest_ratio_pct', 'pm25_mean_3yr', 'aging_rate', 'pop_density'],
                          'Model A: Forest + PM2.5 + covariates', results_list)
        format_model_results(mA, 'Model A: Forest ratio + PM2.5 + covariates', f)

        # Model B
        mB = run_ols_model(df, y_col,
                          ['forest_ratio_pct', 'pm25_mean_3yr', 'forest_x_pm25', 'aging_rate', 'pop_density'],
                          'Model B: Forest + PM2.5 + interaction + covariates', results_list)
        format_model_results(mB, 'Model B: Forest ratio + PM2.5 + interaction + covariates', f)

        # === 4. VIFチェック ===
        f.write(f"\n\n{'=' * 60}\n")
        f.write("VIF (Model 5)\n")
        f.write(f"{'=' * 60}\n")
        vif_cols = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25', 'aging_rate', 'pop_density']
        df_vif = compute_vif(df, vif_cols)
        for _, row in df_vif.iterrows():
            flag = " *** HIGH" if row['vif'] > 10 else ""
            f.write(f"  {row['variable']:<25} VIF={row['vif']:.2f}{flag}\n")
            logger.info(f"  VIF: {row['variable']} = {row['vif']:.2f}{flag}")

        # === 5. 花粉指標比較 ===
        f.write(f"\n\n{'=' * 60}\n")
        f.write("花粉指標比較: pollen_count vs forest_ratio_pct\n")
        f.write(f"{'=' * 60}\n")

        # 同じ共変量セットで比較
        m_pollen = run_ols_model(df, y_col,
                                 ['pollen_count', 'pm25_mean_3yr', 'aging_rate', 'pop_density'],
                                 'Comparison: Pollen', results_list)
        m_forest = run_ols_model(df, y_col,
                                 ['forest_ratio_pct', 'pm25_mean_3yr', 'aging_rate', 'pop_density'],
                                 'Comparison: Forest', results_list)

        f.write(f"\n  Pollen count model: R²={m_pollen.rsquared:.4f}, AIC={m_pollen.aic:.2f}\n")
        f.write(f"  Forest ratio model: R²={m_forest.rsquared:.4f}, AIC={m_forest.aic:.2f}\n")
        better = "Pollen count" if m_pollen.aic < m_forest.aic else "Forest ratio"
        f.write(f"  Better predictor (lower AIC): {better}\n")

        # === 6. 副次解析（薬効分類別） ===
        f.write(f"\n\n{'=' * 60}\n")
        f.write("副次解析: 薬効分類別OLS回帰\n")
        f.write(f"{'=' * 60}\n")

        subgroup_outcomes = {
            'antihistamine_per_100k': '抗ヒスタミン剤・アレルギー用薬',
            'eye_drops_per_100k': '眼科用剤',
            'nasal_sprays_per_100k': '耳鼻科用剤',
        }

        x_cols_sub = ['pollen_count', 'pm25_mean_3yr', 'pollen_x_pm25']

        for sub_y, sub_name in subgroup_outcomes.items():
            if sub_y in df.columns:
                m_sub = run_ols_model(df, sub_y, x_cols_sub,
                                      f'Subgroup: {sub_y}', results_list)
                f.write(f"\n--- {sub_name} ({sub_y}) ---\n")
                f.write(f"R²={m_sub.rsquared:.4f}, Adj.R²={m_sub.rsquared_adj:.4f}, AIC={m_sub.aic:.2f}\n")
                for var in m_sub.params.index:
                    if var != 'const':
                        p = m_sub.pvalues[var]
                        sig = '*' if p < 0.05 else ''
                        f.write(f"  {var}: β={m_sub.params[var]:.4f}, p={p:.4f} {sig}\n")

        # === 7. 空間分析 ===
        spatial_analysis(df, m5.resid.values, results_dir, f)

        f.write("\n\n" + "=" * 60 + "\n")
        f.write("解析完了\n")
        f.write("=" * 60 + "\n")

    logger.info(f"\n回帰結果テキスト: {results_file}")

    # モデル比較表を保存
    df_models = pd.DataFrame(results_list)
    df_models.to_csv(results_dir / "model_comparison.csv", index=False, encoding="utf-8-sig")
    logger.info(f"モデル比較表: model_comparison.csv")

    # 係数テーブル（Model 5）
    coef_data = []
    for var in m5.params.index:
        coef_data.append({
            'variable': var,
            'coefficient': m5.params[var],
            'std_error': m5.bse[var],
            't_value': m5.tvalues[var],
            'p_value': m5.pvalues[var],
            'ci_lower': m5.conf_int().loc[var, 0],
            'ci_upper': m5.conf_int().loc[var, 1],
        })
    df_coef = pd.DataFrame(coef_data)
    df_coef.to_csv(results_dir / "coefficient_table.csv", index=False, encoding="utf-8-sig")
    logger.info(f"係数テーブル: coefficient_table.csv")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 5 完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
