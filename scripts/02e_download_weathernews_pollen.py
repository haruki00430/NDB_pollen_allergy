#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2e: ウェザーニューズ花粉飛散数データのAPI取得（2023年シーズン）

API: https://wxtech.weathernews.com/products/data/services/opendata-pollen/
エンドポイント: GET /opendata/v1/pollen?citycode=XXXXX&start=YYYYMMDD&end=YYYYMMDD
制約: 1リクエスト31日以内、過度なアクセス制限あり

47都道府県の県庁所在地について、2023年花粉シーズン（2月〜7月）のデータを取得し、
都道府県別シーズン累計を算出する。
"""

import pandas as pd
import numpy as np
import requests
import time
from pathlib import Path
import logging
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

POLLEN_PROJECT = Path(__file__).resolve().parents[1]

# ロガー設定
log_dir = POLLEN_PROJECT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "02e_weathernews_pollen.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API設定
API_BASE = "https://wxtech.weathernews.com/opendata/v1/pollen"
RATE_LIMIT_SEC = 2.0  # リクエスト間隔（秒）

# 47都道府県 県庁所在地コード
PREFECTURE_CAPITALS = {
    1: ("北海道", "01101"),     # 札幌市中央区
    2: ("青森県", "02201"),     # 青森市
    3: ("岩手県", "03201"),     # 盛岡市
    4: ("宮城県", "04101"),     # 仙台市青葉区
    5: ("秋田県", "05201"),     # 秋田市
    6: ("山形県", "06201"),     # 山形市
    7: ("福島県", "07201"),     # 福島市
    8: ("茨城県", "08201"),     # 水戸市
    9: ("栃木県", "09201"),     # 宇都宮市
    10: ("群馬県", "10201"),    # 前橋市
    11: ("埼玉県", "11101"),    # さいたま市西区
    12: ("千葉県", "12101"),    # 千葉市中央区
    13: ("東京都", "13101"),    # 千代田区
    14: ("神奈川県", "14101"),  # 横浜市鶴見区
    15: ("新潟県", "15101"),    # 新潟市北区
    16: ("富山県", "16201"),    # 富山市
    17: ("石川県", "17201"),    # 金沢市
    18: ("福井県", "18201"),    # 福井市
    19: ("山梨県", "19201"),    # 甲府市
    20: ("長野県", "20201"),    # 長野市
    21: ("岐阜県", "21201"),    # 岐阜市
    22: ("静岡県", "22101"),    # 静岡市葵区
    23: ("愛知県", "23101"),    # 名古屋市千種区
    24: ("三重県", "24201"),    # 津市
    25: ("滋賀県", "25201"),    # 大津市
    26: ("京都府", "26101"),    # 京都市北区
    27: ("大阪府", "27102"),    # 大阪市都島区
    28: ("兵庫県", "28101"),    # 神戸市東灘区
    29: ("奈良県", "29201"),    # 奈良市
    30: ("和歌山県", "30201"),  # 和歌山市
    31: ("鳥取県", "31201"),    # 鳥取市
    32: ("島根県", "32201"),    # 松江市
    33: ("岡山県", "33101"),    # 岡山市北区
    34: ("広島県", "34101"),    # 広島市中区
    35: ("山口県", "35203"),    # 山口市
    36: ("徳島県", "36201"),    # 徳島市
    37: ("香川県", "37201"),    # 高松市
    38: ("愛媛県", "38201"),    # 松山市
    39: ("高知県", "39201"),    # 高知市
    40: ("福岡県", "40131"),    # 福岡市東区
    41: ("佐賀県", "41201"),    # 佐賀市
    42: ("長崎県", "42201"),    # 長崎市
    43: ("熊本県", "43101"),    # 熊本市中央区
    44: ("大分県", "44201"),    # 大分市
    45: ("宮崎県", "45201"),    # 宮崎市
    46: ("鹿児島県", "46201"),  # 鹿児島市
    47: ("沖縄県", "47201"),    # 那覇市
}

# 2023年花粉シーズンの期間（31日ずつ分割）
DATE_RANGES_2023 = [
    ("20230207", "20230309"),  # 2月7日〜3月9日
    ("20230310", "20230409"),  # 3月10日〜4月9日
    ("20230410", "20230510"),  # 4月10日〜5月10日
    ("20230511", "20230610"),  # 5月11日〜6月10日
    ("20230611", "20230711"),  # 6月11日〜7月11日
    ("20230712", "20230730"),  # 7月12日〜7月30日
]


def fetch_pollen_csv(citycode, start, end):
    """APIから花粉CSVデータを取得"""
    params = {
        "citycode": citycode,
        "start": start,
        "end": end,
    }
    try:
        resp = requests.get(API_BASE, params=params, timeout=30)
        if resp.status_code == 200:
            lines = resp.text.strip().split('\n')
            if len(lines) > 1:
                from io import StringIO
                df = pd.read_csv(StringIO(resp.text))
                return df
            else:
                return pd.DataFrame()
        else:
            logger.warning(f"  HTTP {resp.status_code} for {citycode} ({start}-{end})")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"  エラー: {citycode} ({start}-{end}): {e}")
        return pd.DataFrame()


def main():
    logger.info("=" * 60)
    logger.info("Phase 2e: ウェザーニューズ花粉データ取得（2023年）")
    logger.info("=" * 60)

    output_dir = POLLEN_PROJECT / "data" / "external" / "weathernews"
    output_dir.mkdir(parents=True, exist_ok=True)
    interim_dir = POLLEN_PROJECT / "data" / "interim"
    interim_dir.mkdir(parents=True, exist_ok=True)

    results = []
    total_prefs = len(PREFECTURE_CAPITALS)

    for idx, (pref_code, (pref_name, citycode)) in enumerate(PREFECTURE_CAPITALS.items(), 1):
        logger.info(f"\n[{idx}/{total_prefs}] {pref_name} (code={citycode})")

        all_data = []
        for start, end in DATE_RANGES_2023:
            df = fetch_pollen_csv(citycode, start, end)
            if len(df) > 0:
                all_data.append(df)
            time.sleep(RATE_LIMIT_SEC)

        if all_data:
            df_pref = pd.concat(all_data, ignore_index=True)

            # 花粉カラム名を確認（'pollen'が標準）
            pollen_col = None
            for col in df_pref.columns:
                if 'pollen' in col.lower():
                    pollen_col = col
                    break

            if pollen_col:
                # 負値やNaN除外
                valid = df_pref[pollen_col].apply(pd.to_numeric, errors='coerce')
                valid = valid[valid >= 0]
                seasonal_total = valid.sum()
                valid_days = valid[valid > 0].count()
                logger.info(f"  累計: {seasonal_total:.1f} 個/cm², データ日数: {len(valid)}, 飛散日数: {valid_days}")
            else:
                seasonal_total = 0
                valid_days = 0
                logger.warning(f"  pollenカラムが見つかりません: {df_pref.columns.tolist()}")

            # 個別CSV保存
            csv_path = output_dir / f"pollen_2023_{pref_code:02d}_{pref_name}.csv"
            df_pref.to_csv(csv_path, index=False, encoding='utf-8-sig')
        else:
            seasonal_total = 0
            valid_days = 0
            logger.warning(f"  データ取得失敗")

        results.append({
            'pref_code': pref_code,
            'pref_name': pref_name,
            'citycode': citycode,
            'pollen_count': seasonal_total,
            'pollen_days': valid_days,
        })

    # 都道府県別集計
    df_result = pd.DataFrame(results)

    logger.info(f"\n{'='*60}")
    logger.info(f"ウェザーニューズ 2023年花粉データ集計結果")
    logger.info(f"{'='*60}")
    logger.info(f"都道府県数: {len(df_result)}")
    logger.info(f"データあり: {(df_result['pollen_count'] > 0).sum()}県")
    logger.info(f"花粉飛散量: mean={df_result['pollen_count'].mean():.1f}, "
                f"SD={df_result['pollen_count'].std():.1f}")
    if df_result['pollen_count'].max() > 0:
        logger.info(f"  最大: {df_result.loc[df_result['pollen_count'].idxmax(), 'pref_name']} "
                    f"({df_result['pollen_count'].max():.1f})")
    nonzero = df_result[df_result['pollen_count'] > 0]
    if len(nonzero) > 0:
        logger.info(f"  最小(>0): {nonzero.loc[nonzero['pollen_count'].idxmin(), 'pref_name']} "
                    f"({nonzero['pollen_count'].min():.1f})")

    # CSV出力
    out_path = interim_dir / "pollen_weathernews_2023.csv"
    df_result.to_csv(out_path, index=False, encoding='utf-8-sig')
    logger.info(f"\n保存: {out_path}")

    logger.info(f"\n{'='*60}")
    logger.info("Phase 2e 完了")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
