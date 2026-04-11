#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 4: データ統合・人口標準化・交互作用項作成

入力: Phase 1-3の中間データ + 人口データ
出力: analysis_dataset.csv（47都道府県×分析変数）

統合対象:
  - 処方薬: antihistamine (441+449), eye_drops (131), nasal_sprays (132)
  - 曝露: PM2.5, SPM, 花粉飛散数, 森林率
  - 共変量: 高齢化率, 人口密度
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml
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
        logging.FileHandler(log_dir / "03_integrate_dataset.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    config_path = POLLEN_PROJECT / "config" / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_population_data():
    """人口推計データから都道府県別・総人口・65歳以上人口を取得"""
    pop_path = PROJECT_ROOT / "02_Data" / "raw" / "Statistics_Bureau" / "pop_2023_est.csv"
    df = pd.read_csv(pop_path, encoding='shift-jis')

    # area_code: 1000=北海道、2000=青森県...47000=沖縄県
    mask_sex = df['男女別'] == '男女計'
    mask_pop_type = df['人口'] == '総人口'
    mask_year = df['時間軸（年月日現在）'].str.contains('2021', na=False)

    # 総人口（全年齢）
    mask_total = mask_sex & mask_pop_type & mask_year & (df['年齢5歳階級'] == '総数')
    df_total = df[mask_total][['area_code', '全国・都道府県', 'value']].copy()
    df_total.columns = ['area_code', 'pref_name', 'total_pop_1000']
    df_total = df_total[df_total['area_code'].between(1000, 47000)]
    df_total['area_code'] = df_total['area_code'] // 1000
    df_total['population'] = df_total['total_pop_1000'] * 1000

    # 65歳以上人口（全角チルダ「〜」使用）
    age_65plus = ['65〜69歳', '70〜74歳', '75〜79歳', '80〜84歳', '85歳以上']
    mask_elderly = mask_sex & mask_pop_type & mask_year & df['年齢5歳階級'].isin(age_65plus)
    df_elderly = df[mask_elderly].groupby(['area_code', '全国・都道府県'])['value'].sum().reset_index()
    df_elderly.columns = ['area_code', 'pref_name', 'elderly_pop_1000']
    df_elderly = df_elderly[df_elderly['area_code'].between(1000, 47000)]
    df_elderly['area_code'] = df_elderly['area_code'] // 1000
    df_elderly['elderly_pop'] = df_elderly['elderly_pop_1000'] * 1000

    # 統合
    df_pop = df_total[['area_code', 'pref_name', 'population']].merge(
        df_elderly[['area_code', 'elderly_pop']],
        on='area_code',
        how='left'
    )
    df_pop['aging_rate'] = (df_pop['elderly_pop'] / df_pop['population'] * 100).round(1)

    # 面積データ（森林データから取得してpop_density計算）
    forest_path = POLLEN_PROJECT / "data" / "interim" / "forest_ratio_prefecture.csv"
    df_forest = pd.read_csv(forest_path, encoding='utf-8-sig')
    df_pop = df_pop.merge(
        df_forest[['pref_code', 'total_area_km2']].rename(columns={'pref_code': 'area_code'}),
        on='area_code',
        how='left'
    )
    df_pop['pop_density'] = (df_pop['population'] / df_pop['total_area_km2']).round(1)

    logger.info(f"人口データ: {len(df_pop)}都道府県")
    logger.info(f"  総人口平均: {df_pop['population'].mean():,.0f}人")
    logger.info(f"  高齢化率平均: {df_pop['aging_rate'].mean():.1f}%")
    logger.info(f"  人口密度平均: {df_pop['pop_density'].mean():.1f}人/km2")

    return df_pop


def main():
    logger.info("=" * 60)
    logger.info("Phase 4: データ統合開始")
    logger.info("=" * 60)

    config = load_config()
    interim_dir = POLLEN_PROJECT / "data" / "interim"

    # 都道府県コードマスタ
    pref_codes = pd.read_csv(
        PROJECT_ROOT / "02_Data" / "master" / "jis_codes" / "prefecture_codes.csv"
    )
    logger.info(f"都道府県マスタ: {len(pref_codes)}件")

    # === 1. 処方薬データ読み込み ===
    logger.info("\n--- 1. 処方薬データ読み込み ---")
    rx_vars = {}
    for var_key, var_info in config['outcome_variables'].items():
        file_path = interim_dir / f"prescription_{var_key}.csv"
        if file_path.exists():
            df_rx = pd.read_csv(file_path, encoding='utf-8-sig')
            rx_vars[var_key] = df_rx
            logger.info(f"  {var_key}: {len(df_rx)}行")
        else:
            logger.error(f"  {var_key}: ファイルが見つかりません: {file_path}")

    # === 2. PM2.5データ読み込み ===
    logger.info("\n--- 2. PM2.5データ読み込み ---")
    pm25_path = interim_dir / "pm25_prefecture.csv"
    df_pm25 = pd.read_csv(pm25_path, encoding='utf-8-sig')
    logger.info(f"  PM2.5: {len(df_pm25)}都道府県, mean={df_pm25['pm25_mean_3yr'].mean():.2f} μg/m3")

    # === 3. SPMデータ読み込み ===
    logger.info("\n--- 3. SPMデータ読み込み ---")
    spm_path = interim_dir / "spm_prefecture.csv"
    df_spm = pd.read_csv(spm_path, encoding='utf-8-sig')
    logger.info(f"  SPM: {len(df_spm)}都道府県, mean={df_spm['spm_mean_3yr'].mean():.4f} mg/m3")

    # === 4. 花粉データ読み込み（ウェザーニューズ2023年） ===
    logger.info("\n--- 4. 花粉データ読み込み（ウェザーニューズ2023年） ---")
    pollen_path = interim_dir / "pollen_weathernews_2023.csv"
    df_pollen = pd.read_csv(pollen_path, encoding='utf-8-sig')
    logger.info(f"  花粉: {len(df_pollen)}都道府県, mean={df_pollen['pollen_count'].mean():.1f}")

    # はなこさんデータも読み込み（感度分析用）
    hanako_path = interim_dir / "pollen_hanako_prefecture.csv"
    if hanako_path.exists():
        df_hanako = pd.read_csv(hanako_path, encoding='utf-8-sig')
        logger.info(f"  はなこさん（感度分析用）: {len(df_hanako)}都道府県, mean={df_hanako['pollen_count'].mean():.1f}")

    # === 5. 森林面積率データ読み込み ===
    logger.info("\n--- 5. 森林面積率データ読み込み ---")
    forest_path = interim_dir / "forest_ratio_prefecture.csv"
    df_forest = pd.read_csv(forest_path, encoding='utf-8-sig')
    logger.info(f"  森林率: {len(df_forest)}都道府県, mean={df_forest['forest_ratio_pct'].mean():.1f}%")

    # === 6. 人口データ読み込み ===
    logger.info("\n--- 6. 人口データ読み込み ---")
    df_pop = load_population_data()

    # === 7. データ統合 ===
    logger.info("\n--- 7. データ統合 ---")

    # ベース: 都道府県コードマスタ
    df = pref_codes.copy()
    logger.info(f"  ベース: {len(df)}行")

    # 処方薬データを結合（都道府県名でマッチ）
    for var_key, df_rx in rx_vars.items():
        var_name = config['outcome_variables'][var_key]['variable_name']
        col_name = [c for c in df_rx.columns if c != 'prefecture'][0]
        df_rx_renamed = df_rx.rename(columns={'prefecture': 'pref_name', col_name: f'raw_{var_key}'})
        df = df.merge(df_rx_renamed, on='pref_name', how='left')
        logger.info(f"  + {var_key}: {df[f'raw_{var_key}'].notna().sum()}マッチ")

    # PM2.5データを結合
    df = df.merge(
        df_pm25[['pref_code', 'pm25_mean_3yr']],
        on='pref_code',
        how='left'
    )
    logger.info(f"  + PM2.5: {df['pm25_mean_3yr'].notna().sum()}マッチ")

    # SPMデータを結合
    df = df.merge(
        df_spm[['pref_code', 'spm_mean_3yr']],
        on='pref_code',
        how='left'
    )
    logger.info(f"  + SPM: {df['spm_mean_3yr'].notna().sum()}マッチ")

    # 花粉データを結合（ウェザーニューズ2023年）
    df = df.merge(
        df_pollen[['pref_code', 'pollen_count']],
        on='pref_code',
        how='left'
    )
    logger.info(f"  + 花粉(WN2023): {df['pollen_count'].notna().sum()}マッチ")

    # はなこさんデータを結合（感度分析用）
    if hanako_path.exists():
        df = df.merge(
            df_hanako[['pref_code', 'pollen_count']].rename(columns={'pollen_count': 'pollen_hanako'}),
            on='pref_code',
            how='left'
        )
        logger.info(f"  + 花粉(はなこさん): {df['pollen_hanako'].notna().sum()}マッチ")

    # 森林面積率データを結合
    df = df.merge(
        df_forest[['pref_code', 'forest_ratio_pct']],
        on='pref_code',
        how='left'
    )
    logger.info(f"  + 森林率: {df['forest_ratio_pct'].notna().sum()}マッチ")

    # 人口データを結合
    df = df.merge(
        df_pop[['area_code', 'population', 'aging_rate', 'pop_density']].rename(
            columns={'area_code': 'pref_code'}
        ),
        on='pref_code',
        how='left'
    )
    logger.info(f"  + 人口: {df['population'].notna().sum()}マッチ")

    # === 8. 人口10万人あたり標準化 ===
    logger.info("\n--- 8. 人口10万人あたり標準化 ---")
    for var_key in rx_vars:
        raw_col = f'raw_{var_key}'
        per100k_col = config['outcome_variables'][var_key]['variable_name']
        df[per100k_col] = (df[raw_col] / (df['population'] / 100000)).round(1)
        logger.info(f"  {per100k_col}: mean={df[per100k_col].mean():.1f}")

    # 合計処方量
    per100k_cols = [config['outcome_variables'][k]['variable_name'] for k in rx_vars]
    df['total_allergy_rx_per_100k'] = df[per100k_cols].sum(axis=1).round(1)
    logger.info(f"  total_allergy_rx_per_100k: mean={df['total_allergy_rx_per_100k'].mean():.1f}")

    # === 9. 交互作用項（中心化後） ===
    logger.info("\n--- 9. 交互作用項作成（中心化後） ---")
    df['pollen_c'] = df['pollen_count'] - df['pollen_count'].mean()
    df['forest_c'] = df['forest_ratio_pct'] - df['forest_ratio_pct'].mean()
    df['pm25_c'] = df['pm25_mean_3yr'] - df['pm25_mean_3yr'].mean()
    df['spm_c'] = df['spm_mean_3yr'] - df['spm_mean_3yr'].mean()

    df['pollen_x_pm25'] = (df['pollen_c'] * df['pm25_c']).round(4)
    df['pollen_x_spm'] = (df['pollen_c'] * df['spm_c']).round(6)
    df['forest_x_pm25'] = (df['forest_c'] * df['pm25_c']).round(2)

    logger.info(f"  pollen_c mean: {df['pollen_c'].mean():.6f}")
    logger.info(f"  pm25_c mean: {df['pm25_c'].mean():.6f}")
    logger.info(f"  spm_c mean: {df['spm_c'].mean():.6f}")

    # === 10. PM2.5-SPM相関チェック ===
    logger.info("\n--- 10. PM2.5-SPM相関チェック ---")
    from scipy.stats import pearsonr
    r_pm_spm, p_pm_spm = pearsonr(df['pm25_mean_3yr'], df['spm_mean_3yr'])
    logger.info(f"  PM2.5 vs SPM: r={r_pm_spm:.3f}, p={p_pm_spm:.4f}")
    if abs(r_pm_spm) > 0.8:
        logger.warning(f"  高相関（r={r_pm_spm:.3f}）: PM2.5とSPMを同一モデルに同時投入しないこと！")
    else:
        logger.info(f"  相関は許容範囲（r<0.8）: 同一モデルへの投入可能")

    # pollen_count vs forest_ratio（収束妥当性）
    r_pf, p_pf = pearsonr(df['pollen_count'], df['forest_ratio_pct'])
    logger.info(f"  花粉飛散数 vs 森林率: r={r_pf:.3f}, p={p_pf:.4f}")

    # === 11. 最終データセット出力 ===
    logger.info("\n--- 11. 最終データセット出力 ---")
    output_cols = [
        'pref_code', 'pref_name', 'population',
        # アウトカム
        'antihistamine_per_100k', 'eye_drops_per_100k', 'nasal_sprays_per_100k',
        'total_allergy_rx_per_100k',
        # 曝露変数
        'pollen_count', 'pollen_hanako', 'forest_ratio_pct',
        'pm25_mean_3yr', 'spm_mean_3yr',
        # 交互作用項
        'pollen_x_pm25', 'pollen_x_spm', 'forest_x_pm25',
        # 共変量
        'aging_rate', 'pop_density'
    ]

    available_cols = [c for c in output_cols if c in df.columns]
    df_out = df[available_cols].copy()

    out_file = interim_dir / "analysis_dataset.csv"
    df_out.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(f"保存: {out_file}")
    logger.info(f"データ形状: {df_out.shape}")

    # === 検証 ===
    logger.info(f"\n=== 最終検証 ===")
    logger.info(f"行数: {len(df_out)} (期待: 47)")
    na_counts = df_out.isnull().sum()
    if na_counts.sum() > 0:
        logger.warning(f"欠損値あり:\n{na_counts[na_counts > 0].to_string()}")
    else:
        logger.info("欠損値: なし")

    logger.info(f"\n=== 全変数記述統計 ===")
    numeric_cols = df_out.select_dtypes(include='number').columns.drop('pref_code')
    for col in numeric_cols:
        logger.info(f"  {col}: mean={df_out[col].mean():.2f}, sd={df_out[col].std():.2f}, "
                     f"min={df_out[col].min():.2f}, max={df_out[col].max():.2f}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 4 完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
