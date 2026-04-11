#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2b: SPM（浮遊粒子状物質）データの抽出・都道府県別集計

入力: 大気汚染常時監視データ（TD{YYYY}1000.zip）
出力: 都道府県別SPM年平均値CSV（3年平均）

データ仕様: README_DATA_STRUCTURE.md参照
- Shift-JISエンコーディング
- カラムインデックス5: 都道府県コード
- カラムインデックス6: 都道府県名
- カラムインデックス14: 測定局区分コード（1=一般局）
- カラムインデックス19: 有効測定日数
- 年平均値(mg/m3): SPM主要指標
"""

import pandas as pd
import zipfile
import io
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
        logging.FileHandler(log_dir / "02b_extract_spm.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# NDB No.10対応年度（令和5年度レセプト → 直近3年の大気データ使用）
TARGET_YEARS = [2021, 2022, 2023]
SPM_CODE = "1000"
MIN_VALID_DAYS = 250  # QCフィルタ: 有効測定日数の閾値


def load_config():
    config_path = POLLEN_PROJECT / "config" / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_spm_file(year, air_pollution_dir):
    """SPMデータファイルを読み込み（ZIP or TXT）"""
    txt_path = air_pollution_dir / f"TD{year}{SPM_CODE}.txt"
    zip_path = air_pollution_dir / f"TD{year}{SPM_CODE}.zip"

    if txt_path.exists():
        logger.info(f"TXTファイル読み込み: {txt_path.name}")
        df = pd.read_csv(txt_path, encoding='shift-jis', header=0)
        return df

    if zip_path.exists():
        logger.info(f"ZIPファイル展開・読み込み: {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as z:
            txt_files = [f for f in z.namelist() if f.endswith('.txt') or f.endswith('.csv')]
            if not txt_files:
                logger.error(f"ZIPにテキストファイルが見つかりません: {zip_path}")
                return None
            with z.open(txt_files[0]) as f:
                df = pd.read_csv(
                    io.TextIOWrapper(f, encoding='shift-jis'),
                    header=0
                )
        return df

    logger.error(f"{year}年のSPMデータが見つかりません")
    return None


def process_spm_year(df, year):
    """1年分のSPMデータを都道府県別に集計"""
    logger.info(f"  元データ: {len(df)}行 × {len(df.columns)}列")

    # カラムインデックスで参照（名前がShift-JISで不安定なため）
    col_pref_code = df.columns[5]    # 都道府県コード
    col_pref_name = df.columns[6]    # 都道府県名
    col_station_type = df.columns[14]  # 測定局区分コード
    col_valid_days = df.columns[19]  # 有効測定日数

    # 年平均値のカラム名を探す（SPMは mg/m3 単位）
    spm_col = None
    for col in df.columns:
        if '年平均値' in str(col) and 'mg' in str(col):
            spm_col = col
            break
    if spm_col is None:
        # カラム名で見つからない場合、インデックス20を使用
        spm_col = df.columns[20]
    logger.info(f"  SPMカラム: '{spm_col}'")

    # フィルタ1: 一般局のみ（区分コード=1）
    df_filtered = df[df[col_station_type] == 1].copy()
    logger.info(f"  一般局フィルタ後: {len(df_filtered)}局")

    # フィルタ2: 有効測定日数 >= MIN_VALID_DAYS
    df_filtered = df_filtered[df_filtered[col_valid_days] >= MIN_VALID_DAYS]
    logger.info(f"  有効日数≥{MIN_VALID_DAYS}フィルタ後: {len(df_filtered)}局")

    # SPM値を数値化
    df_filtered[spm_col] = pd.to_numeric(df_filtered[spm_col], errors='coerce')
    df_filtered = df_filtered.dropna(subset=[spm_col])

    # 都道府県別集計
    agg = df_filtered.groupby([col_pref_code, col_pref_name]).agg(
        spm_mean=(spm_col, 'mean'),
        spm_median=(spm_col, 'median'),
        spm_std=(spm_col, 'std'),
        station_count=(spm_col, 'count')
    ).reset_index()

    agg.columns = ['pref_code', 'pref_name', f'spm_mean_{year}',
                    f'spm_median_{year}', f'spm_std_{year}', f'station_count_{year}']

    logger.info(f"  集計完了: {len(agg)}都道府県")
    logger.info(f"  全国平均: {agg[f'spm_mean_{year}'].mean():.4f} mg/m3")

    return agg


def main():
    logger.info("=" * 60)
    logger.info("Phase 2b: SPMデータ抽出・都道府県集計開始")
    logger.info("=" * 60)

    config = load_config()
    air_dir = PROJECT_ROOT / config["input_paths"]["air_pollution"]
    output_dir = POLLEN_PROJECT / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 各年度のデータを処理
    yearly_results = {}
    for year in TARGET_YEARS:
        logger.info(f"\n--- {year}年度 ---")
        df = read_spm_file(year, air_dir)
        if df is not None:
            result = process_spm_year(df, year)
            yearly_results[year] = result

    if not yearly_results:
        logger.error("SPMデータが1年分も取得できませんでした")
        return

    # 3年間のデータを統合
    logger.info(f"\n--- 3年間データ統合 ---")
    df_merged = yearly_results[TARGET_YEARS[0]][['pref_code', 'pref_name']].copy()

    for year in TARGET_YEARS:
        if year in yearly_results:
            df_merged = df_merged.merge(
                yearly_results[year],
                on=['pref_code', 'pref_name'],
                how='outer'
            )

    # 3年平均を計算
    mean_cols = [f'spm_mean_{y}' for y in TARGET_YEARS if y in yearly_results]
    count_cols = [f'station_count_{y}' for y in TARGET_YEARS if y in yearly_results]

    df_merged['spm_mean_3yr'] = df_merged[mean_cols].mean(axis=1)
    df_merged['station_count_avg'] = df_merged[count_cols].mean(axis=1).round(0).astype(int)

    # 最終出力カラム
    output_cols = ['pref_code', 'pref_name'] + mean_cols + ['spm_mean_3yr', 'station_count_avg']
    df_final = df_merged[output_cols].sort_values('pref_code').reset_index(drop=True)

    # 保存
    out_file = output_dir / "spm_prefecture.csv"
    df_final.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(f"\n保存: {out_file}")

    # 検証
    logger.info(f"\n=== 検証 ===")
    logger.info(f"都道府県数: {len(df_final)}")
    logger.info(f"3年平均 全国平均: {df_final['spm_mean_3yr'].mean():.4f} mg/m3")
    logger.info(f"3年平均 最小: {df_final['spm_mean_3yr'].min():.4f} mg/m3")
    logger.info(f"3年平均 最大: {df_final['spm_mean_3yr'].max():.4f} mg/m3")

    # 上位・下位5都道府県
    df_sorted = df_final.sort_values('spm_mean_3yr', ascending=False)
    logger.info(f"\nSPM 上位5都道府県（高濃度）:")
    for _, row in df_sorted.head().iterrows():
        logger.info(f"  {row['pref_name']}: {row['spm_mean_3yr']:.4f} mg/m3 ({row['station_count_avg']}局)")
    logger.info(f"\nSPM 下位5都道府県（低濃度）:")
    for _, row in df_sorted.tail().iterrows():
        logger.info(f"  {row['pref_name']}: {row['spm_mean_3yr']:.4f} mg/m3 ({row['station_count_avg']}局)")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 2b 完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
