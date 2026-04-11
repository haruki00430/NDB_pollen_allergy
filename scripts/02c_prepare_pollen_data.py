#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2c: 花粉飛散データの準備

ウェザーニューズの花粉飛散観測データ（CSV）を都道府県別に集計する。

データ取得方法:
  1. https://wxtech.weathernews.com/pollen/index.html にアクセス
  2. 各都道府県の県庁所在地を選択
  3. 期間: 2月〜7月（花粉シーズン）で各年のCSVをダウンロード
  4. data/external/ に配置（例: pollen_北海道_2023.csv）

CSVフォーマット:
  - citycode: 市区町村コード
  - date: 日時（ISO8601）
  - pollen: 花粉飛散数（個/cm²）

出力: data/interim/pollen_count_prefecture.csv

代替データソース:
  - 環境省「花粉観測システム（はなこさん）」
  - 都道府県衛生研究所の公表データ
"""

import pandas as pd
from pathlib import Path
import yaml
import logging
import glob

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
        logging.FileHandler(log_dir / "02c_prepare_pollen_data.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 都道府県コード → 県庁所在地の市区町村コード（総務省コード、5桁）
CAPITAL_CITY_CODES = {
    1: ("北海道", "01100"),    2: ("青森県", "02201"),    3: ("岩手県", "03201"),
    4: ("宮城県", "04100"),    5: ("秋田県", "05201"),    6: ("山形県", "06201"),
    7: ("福島県", "07201"),    8: ("茨城県", "08201"),    9: ("栃木県", "09201"),
    10: ("群馬県", "10201"),   11: ("埼玉県", "11100"),   12: ("千葉県", "12100"),
    13: ("東京都", "13101"),   14: ("神奈川県", "14100"), 15: ("新潟県", "15100"),
    16: ("富山県", "16201"),   17: ("石川県", "17201"),   18: ("福井県", "18201"),
    19: ("山梨県", "19201"),   20: ("長野県", "20201"),   21: ("岐阜県", "21201"),
    22: ("静岡県", "22100"),   23: ("愛知県", "23100"),   24: ("三重県", "24201"),
    25: ("滋賀県", "25201"),   26: ("京都府", "26100"),   27: ("大阪府", "27100"),
    28: ("兵庫県", "28100"),   29: ("奈良県", "29201"),   30: ("和歌山県", "30201"),
    31: ("鳥取県", "31201"),   32: ("島根県", "32201"),   33: ("岡山県", "33100"),
    34: ("広島県", "34100"),   35: ("山口県", "35203"),   36: ("徳島県", "36201"),
    37: ("香川県", "37201"),   38: ("愛媛県", "38201"),   39: ("高知県", "39201"),
    40: ("福岡県", "40130"),   41: ("佐賀県", "41201"),   42: ("長崎県", "42201"),
    43: ("熊本県", "43100"),   44: ("大分県", "44201"),   45: ("宮崎県", "45201"),
    46: ("鹿児島県", "46201"), 47: ("沖縄県", "47201"),
}


def load_config():
    config_path = POLLEN_PROJECT / "config" / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def process_weathernews_csvs(external_dir):
    """ウェザーニューズCSVファイルを都道府県別に集計"""
    csv_files = list(external_dir.glob("pollen_*.csv"))

    if not csv_files:
        logger.warning(f"花粉CSVファイルが見つかりません: {external_dir}")
        logger.info("代替: 環境省「はなこさん」データまたは手動入力を使用してください")
        return None

    logger.info(f"花粉CSVファイル数: {len(csv_files)}")

    all_data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8")
            if 'pollen' in df.columns and 'citycode' in df.columns:
                all_data.append(df)
                logger.info(f"  読み込み: {csv_file.name} ({len(df)}行)")
        except Exception as e:
            logger.warning(f"  読み込みエラー: {csv_file.name}: {e}")

    if not all_data:
        return None

    df_all = pd.concat(all_data, ignore_index=True)

    # 市区町村コードから都道府県コードを抽出（先頭2桁）
    df_all['pref_code'] = df_all['citycode'].astype(str).str.zfill(5).str[:2].astype(int)

    # 都道府県別のシーズン累積花粉飛散数を算出
    df_pref = df_all.groupby('pref_code').agg(
        pollen_count=('pollen', 'sum'),
        n_days=('pollen', 'count')
    ).reset_index()

    # 都道府県名を付与
    df_pref['pref_name'] = df_pref['pref_code'].map(
        {k: v[0] for k, v in CAPITAL_CITY_CODES.items()}
    )

    return df_pref[['pref_code', 'pref_name', 'pollen_count']]


def create_manual_pollen_data():
    """
    手動入力の花粉飛散データ（文献値ベース）

    環境省花粉観測データ、都道府県別飛散量のおおよその相対値。
    実測データが入手できるまでのプレースホルダー。

    出典: 日本アレルギー学会・環境省花粉情報サイトの都道府県別飛散量
    スケール: 相対値（東京=100とした場合の各県の相対花粉飛散量）

    注意: この値は参考値であり、正確な解析には実測値の使用を推奨する。
    """
    logger.info("手動入力の花粉飛散相対データを使用（プレースホルダー）")
    logger.warning("注意: 実測花粉データの入手を推奨。この値は文献ベースの概算値です。")

    # 都道府県別花粉飛散量の相対指標
    # 北海道・沖縄はスギが少なく低い、関東・東海は非常に高い
    pollen_relative = {
        1: 5,    # 北海道（スギほぼ無し、シラカバが主）
        2: 40,   3: 55,   4: 65,   5: 35,   6: 50,   7: 70,
        8: 85,   9: 90,  10: 95,  11: 100, 12: 95,  13: 100,
        14: 105, 15: 45,  16: 40,  17: 35,  18: 50,  19: 80,
        20: 60,  21: 75,  22: 90,  23: 85,  24: 80,  25: 70,
        26: 65,  27: 75,  28: 70,  29: 85,  30: 80,  31: 30,
        32: 35,  33: 60,  34: 55,  35: 50,  36: 55,  37: 50,
        38: 55,  39: 60,  40: 65,  41: 55,  42: 50,  43: 60,
        44: 55,  45: 60,  46: 50,  47: 3,   # 沖縄（スギ無し）
    }

    rows = []
    for pref_code, (pref_name, _) in CAPITAL_CITY_CODES.items():
        rows.append({
            'pref_code': pref_code,
            'pref_name': pref_name,
            'pollen_count': pollen_relative[pref_code]
        })

    df = pd.DataFrame(rows)
    logger.info(f"相対花粉飛散データ: {len(df)}都道府県")
    logger.info(f"  最大: {df['pollen_count'].max()} (関東)")
    logger.info(f"  最小: {df['pollen_count'].min()} (沖縄)")

    return df


def main():
    logger.info("=" * 60)
    logger.info("Phase 2c: 花粉飛散データ準備")
    logger.info("=" * 60)

    config = load_config()
    external_dir = POLLEN_PROJECT / "data" / "external"
    output_dir = POLLEN_PROJECT / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: ウェザーニューズCSVの処理を試みる
    df_pollen = process_weathernews_csvs(external_dir)

    # Step 2: CSVが無い場合は手動入力データを使用
    if df_pollen is None:
        logger.info("\nウェザーニューズCSVが未取得のため、プレースホルダーデータを使用")
        df_pollen = create_manual_pollen_data()

    # 保存
    out_file = output_dir / "pollen_count_prefecture.csv"
    df_pollen.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(f"\n保存: {out_file}")

    # 検証
    logger.info(f"\n=== 検証 ===")
    logger.info(f"都道府県数: {len(df_pollen)}")
    logger.info(f"花粉飛散数: mean={df_pollen['pollen_count'].mean():.1f}, "
                f"min={df_pollen['pollen_count'].min():.1f}, "
                f"max={df_pollen['pollen_count'].max():.1f}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 2c 完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
