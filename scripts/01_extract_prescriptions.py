#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3: NDB処方薬データ抽出（アレルギー特異的3薬効分類）

入力: NDB処方薬Excel（内服院外/院内、外用）
出力: 薬効分類別の都道府県別処方数量CSV（3ファイル）

重要: NDB処方薬Excelは個別医薬品ごとに1行。薬効分類コード・名称は
各グループの先頭行のみに記載され、2行目以降はNaN。
forward-fill（ffill）で全行に伝播させてからフィルタする。

参照: NDB_XXX_pollen_pm25_spatial/scripts/01_extract_prescriptions.py（ffill修正済み）
"""

import pandas as pd
from pathlib import Path
import yaml
import logging

# プロジェクトルート（NDB_Research_Hub）
PROJECT_ROOT = Path(__file__).resolve().parents[3]
POLLEN_PROJECT = Path(__file__).resolve().parents[1]

# ロガー設定
log_dir = POLLEN_PROJECT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "01_extract_prescriptions.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """config.yamlの読み込み"""
    config_path = POLLEN_PROJECT / "config" / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_extraction_totals(df_result, var_key):
    """抽出結果のバリデーション"""
    total = df_result['quantity'].sum()
    if total <= 0:
        logger.error(f"VALIDATION FAILED [{var_key}]: 総数量={total:,.0f} (>0であるべき)")
        return False
    if len(df_result) != 47:
        logger.warning(f"VALIDATION WARNING [{var_key}]: {len(df_result)}都道府県 (47であるべき)")
    max_share = df_result['quantity'].max() / total
    if max_share > 0.30:
        logger.warning(f"VALIDATION WARNING [{var_key}]: 最大県シェア={max_share:.1%} (>30%)")
    logger.info(f"VALIDATION OK [{var_key}]: total={total:,.0f}, "
                f"min={df_result['quantity'].min():,.0f}, max={df_result['quantity'].max():,.0f}")
    return True


def load_prescription_file(file_path, target_classifications):
    """
    処方薬Excelファイルから指定薬効分類の都道府県別数量を抽出

    NDB Excelは個別医薬品ごとに1行。薬効分類コード・名称は各分類グループの
    先頭行のみに記載され、2行目以降はNaN。forward-fillで全行に伝播させてから
    フィルタ・合算する。
    """
    logger.info(f"ファイル読み込み: {file_path.name}")

    # MultiIndexヘッダーで読み込み
    df = pd.read_excel(file_path, header=[2, 3])

    # 列名を簡素化（Level 0の改行削除、Level 1は都道府県名）
    new_columns = []
    for col in df.columns:
        if 'Unnamed' in str(col[1]):
            col_name = str(col[0]).replace('\n', '').replace(' ', '')
        else:
            col_name = str(col[1])
        new_columns.append(col_name)
    df.columns = new_columns

    # --- CRITICAL: forward-fill ---
    # 薬効分類コード・名称は各グループの先頭行のみに記載。
    # 2行目以降の個別医薬品行はNaN。前方補完で全行に伝播させる。
    col0_name = df.columns[0]  # 薬効分類コード
    col1_name = df.columns[1]  # 薬効分類名称
    df[col0_name] = df[col0_name].ffill()
    df[col1_name] = df[col1_name].ffill()

    # 薬効分類名で全行を抽出（ffill後は全医薬品行にマッチ）
    mask = df[col1_name].isin(target_classifications)
    df_target = df[mask].copy()

    if len(df_target) == 0:
        logger.warning(f"対象薬効分類が見つかりません: {target_classifications}")
        logger.info(f"利用可能な分類: {df[col1_name].dropna().unique()[:10]}...")
        return None

    # 分類別の薬品数を検証ログ出力
    for cls_name in target_classifications:
        n_drugs = (df_target[col1_name] == cls_name).sum()
        logger.info(f"  {cls_name}: {n_drugs}品目")
    logger.info(f"対象薬効分類 合計: {len(df_target)}品目")

    # 都道府県列（列9以降: 北海道, 青森県, ...）
    prefecture_cols = df.columns[9:]

    # 都道府県列を数値化（マスク値'-'、全角数字対応）
    for col in prefecture_cols:
        df_target[col] = pd.to_numeric(
            df_target[col].astype(str).str.strip().replace('-', pd.NA),
            errors='coerce'
        )

    # 全医薬品を都道府県ごとに合算
    df_summed = df_target[prefecture_cols].sum(min_count=1)

    results = []
    for pref in prefecture_cols:
        total = float(df_summed[pref]) if pd.notna(df_summed[pref]) else 0.0
        results.append({"prefecture": pref, "quantity": total})

    df_result = pd.DataFrame(results)

    # 「全国」「総計」行を除外
    df_result = df_result[~df_result['prefecture'].str.contains('全国|総計|合計', na=False)]

    logger.info(f"抽出完了: {len(df_result)}都道府県、総数量={df_result['quantity'].sum():,.0f}")
    return df_result


def extract_oral_prescriptions(base_path, target_classifications):
    """内服（院外＋院内）を合算して抽出"""
    file_external = base_path / "【内服】外来（院外）_都道府県別薬効分類別数量.xlsx"
    file_internal = base_path / "【内服】外来（院内）_都道府県別薬効分類別数量.xlsx"

    df_ext = None
    df_int = None

    if file_external.exists():
        df_ext = load_prescription_file(file_external, target_classifications)
    else:
        logger.error(f"ファイルが見つかりません: {file_external}")

    if file_internal.exists():
        df_int = load_prescription_file(file_internal, target_classifications)
    else:
        logger.error(f"ファイルが見つかりません: {file_internal}")

    # 合算
    if df_ext is not None and df_int is not None:
        df_merged = df_ext.merge(df_int, on="prefecture", how="outer", suffixes=("", "_int"))
        df_merged["quantity"] = df_merged["quantity"].fillna(0) + df_merged["quantity_int"].fillna(0)
        df_merged = df_merged[["prefecture", "quantity"]]
        logger.info(f"院外+院内合算完了: {len(df_merged)}都道府県")
        return df_merged
    elif df_ext is not None:
        return df_ext
    elif df_int is not None:
        return df_int
    else:
        return None


def extract_topical_prescriptions(base_path, target_classifications):
    """外用ファイルから抽出"""
    file_topical = base_path / "【外用】都道府県別薬効分類別数量.xlsx"

    if file_topical.exists():
        return load_prescription_file(file_topical, target_classifications)
    else:
        logger.error(f"ファイルが見つかりません: {file_topical}")
        return None


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 3: NDB処方薬データ抽出開始（アレルギー特異的薬剤）")
    logger.info("=" * 60)

    config = load_config()
    base_path = PROJECT_ROOT / config["input_paths"]["prescription"]
    output_dir = POLLEN_PROJECT / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)

    outcomes = config["outcome_variables"]

    for var_key, var_info in outcomes.items():
        logger.info(f"\n{'─' * 40}")
        logger.info(f"処理中: {var_info['name']} (コード: {var_info['drug_classifications']})")
        logger.info(f"{'─' * 40}")

        classification_names = var_info["classification_names"]
        source_files = var_info["source_files"]

        # 内服 or 外用に応じて抽出
        if "内服院外" in source_files:
            df_result = extract_oral_prescriptions(base_path, classification_names)
        elif "外用" in source_files:
            df_result = extract_topical_prescriptions(base_path, classification_names)
        else:
            logger.error(f"未対応のsource_files: {source_files}")
            continue

        if df_result is None or len(df_result) == 0:
            logger.error(f"{var_key}: データ抽出失敗")
            continue

        # バリデーション（リネーム前に実行）
        validate_extraction_totals(df_result, var_key)

        # 変数名をリネーム
        df_result = df_result.rename(columns={"quantity": var_info["variable_name"]})

        # 保存
        out_file = output_dir / f"prescription_{var_key}.csv"
        df_result.to_csv(out_file, index=False, encoding="utf-8-sig")
        logger.info(f"保存: {out_file}")

        # 記述統計
        var_col = var_info["variable_name"]
        logger.info(f"\n記述統計:")
        logger.info(f"  N = {len(df_result)}")
        logger.info(f"  Mean = {df_result[var_col].mean():,.0f}")
        logger.info(f"  SD   = {df_result[var_col].std():,.0f}")
        logger.info(f"  Min  = {df_result[var_col].min():,.0f}")
        logger.info(f"  Max  = {df_result[var_col].max():,.0f}")

        # 上位・下位5都道府県
        df_sorted = df_result.sort_values(var_col, ascending=False)
        logger.info(f"\n上位5都道府県:")
        for _, row in df_sorted.head().iterrows():
            logger.info(f"  {row['prefecture']}: {row[var_col]:,.0f}")
        logger.info(f"\n下位5都道府県:")
        for _, row in df_sorted.tail().iterrows():
            logger.info(f"  {row['prefecture']}: {row[var_col]:,.0f}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 3 完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
