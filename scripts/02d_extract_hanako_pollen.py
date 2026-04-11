#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2d: 環境省はなこさん花粉観測データの都道府県別集計

データソース: 環境省花粉観測システム（はなこさん）2019-2021年
URL: https://www.env.go.jp/page_00209.html
形式: Excel（年月日時 + 観測地点別 花粉飛散数 個/cm2/時）

処理:
1. 観測地点名→都道府県コードのマッピング
2. 負値（-9998/-9997/-9996）はエラーコード→NaN
3. 時間データを日別→シーズン累計に集計
4. 都道府県内の複数地点は平均
5. 3年平均を算出
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import io

# Windows コンソール文字化け対策
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
        logging.FileHandler(log_dir / "02d_extract_hanako.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# 観測地点 → 都道府県コード マッピング
# ============================================================
# 観測地点名に含まれるキーワードで都道府県を判定
# キーワードは名前の一部（部分一致）で判定する
STATION_TO_PREF = {
    # --- 北海道 (1) ---
    '北海道立衛生研究所': 1,
    '北海道渡島総合振興局': 1,
    '北海道上川総合振興局': 1,
    '北海道十勝総合振興局': 1,

    # --- 青森 (2) ---
    '青森市中央卸売市場': 2,
    '弘前大学': 2,

    # --- 岩手 (3) ---
    '岩手県環境保健研究センター': 3,
    '大船渡地区合同庁舎': 3,

    # --- 宮城 (4) ---
    '東北大学医学部': 4,
    '宮城県東部地方振興事務所': 4,

    # --- 秋田 (5) ---
    '秋田県健康環境センター': 5,
    '秋田県平鹿地域振興局': 5,

    # --- 山形 (6) ---
    '山形県衛生研究所': 6,
    '置賜保健所': 6,
    '庄内総合支庁': 6,

    # --- 福島 (7) ---
    '福島県衛生研究所': 7,
    '江東微生物研究所': 7,  # 東北中央研究所（福島県郡山市に所在）

    # --- 茨城 (8) ---
    '水戸石川': 8,
    '国立環境研究所': 8,  # つくば市
    '日立市消防本部': 8,

    # --- 栃木 (9) ---
    '宇都宮市中央生涯学習センター': 9,
    '栃木県庁那須庁舎': 9,
    '日光市役所': 9,

    # --- 群馬 (10) ---
    '群馬県衛生環境研究所': 10,
    '館林保健福祉事務所': 10,

    # --- 埼玉 (11) ---
    'さいたま市役所': 11,
    '飯能市役所': 11,
    '熊谷市保健センター': 11,

    # --- 千葉 (12) ---
    '東邦大学': 12,  # 習志野キャンパス（千葉県）
    '千葉県環境研究センター': 12,
    '印旛健康福祉センター': 12,
    '君津市': 12,

    # --- 東京 (13) ---
    '東京都多摩小平保健所': 13,
    '新宿区役所': 13,

    # --- 神奈川 (14) ---
    '神奈川県庁': 14,
    '川崎生命科学': 14,
    '神奈川県環境科学センター': 14,

    # --- 新潟 (15) ---
    '新潟県保健環境科学研究所': 15,
    '長岡環境センター': 15,
    '上越環境センター': 15,

    # --- 富山 (16) ---
    '富山県庁舎': 16,
    '富山県魚津総合庁舎': 16,

    # --- 石川 (17) ---
    '金沢大学': 17,
    '石川県能登中部': 17,

    # --- 福井 (18) ---
    '福井大気汚染': 18,
    '福井県福井大気汚染': 18,
    '福井市福井大気汚染': 18,
    '二州健康福祉センター': 18,

    # --- 山梨 (19) ---
    '山梨県衛生環境研究所': 19,
    '山梨県身延合同庁舎': 19,

    # --- 長野 (20) ---
    '長野県環境保全研究所': 20,
    '長野県松本合同庁舎': 20,
    '長野県飯田合同庁舎': 20,

    # --- 岐阜 (21) ---
    '大垣市民病院': 21,
    '岐阜県郡上総合庁舎': 21,
    '岐阜県飛騨総合庁舎': 21,

    # --- 静岡 (22) ---
    '静岡県庁本庁舎': 22,
    '静岡県東部総合庁舎': 22,
    '伊東市役所': 22,

    # --- 愛知 (23) ---
    '愛知県環境調査センター': 23,
    '愛知県東三河総合庁舎': 23,

    # --- 三重 (24) ---
    '三重県立総合医療センター': 24,
    '三重県庁': 24,

    # --- 滋賀 (25) ---
    '彦根地方気象台': 25,
    '滋賀県琵琶湖': 25,
    '滋賀県高島合同庁舎': 25,

    # --- 京都 (26) ---
    '京都府立医科大学': 26,
    '舞鶴市': 26,
    '京都市右京区': 26,

    # --- 大阪 (27) ---
    '大阪合同庁舎': 27,
    '豊中市役所': 27,
    '泉大津市役所': 27,

    # --- 兵庫 (28) ---
    '兵庫県立健康': 28,
    '北山緑化植物園': 28,
    '兵庫県篠山庁舎': 28,
    '太子町役場': 28,
    '兵庫県環境研究センター': 28,

    # --- 奈良 (29) ---
    '奈良県産業振興総合センター': 29,
    '奈良県吉野保健所': 29,
    '橿原総合庁舎': 29,

    # --- 和歌山 (30) ---
    '和歌山地方気象台': 30,
    '和歌山県西牟婁振興局': 30,
    '和歌山県東牟婁振興局': 30,

    # --- 鳥取 (31) ---
    '鳥取県庁西町分庁舎': 31,
    '鳥取県中部総合事務所': 31,

    # --- 島根 (32) ---
    '島根県保健環境科学研究所': 32,
    '浜田保健所': 32,

    # --- 岡山 (33) ---
    '岡山県備中県民局': 33,
    '岡山県美作県民局': 33,
    '岡山大学医学部': 33,

    # --- 広島 (34) ---
    '広島県立総合技術研究所': 34,
    '広島県東部建設事務所': 34,

    # --- 山口 (35) ---
    '山口大学医学部': 35,
    '光市立大和総合病院': 35,
    '山口県環境保健センター': 35,

    # --- 徳島 (36) ---
    '徳島県立保健製薬環境センター': 36,
    '徳島県南部総合県民局': 36,
    '南部総合県民局': 36,  # 2020-2021年の表記

    # --- 香川 (37) ---
    '香川県庁本館': 37,
    '善通寺市役所': 37,
    '香川県中讃保健福祉事務所': 37,

    # --- 愛媛 (38) ---
    '新居浜市役所': 38,
    '愛媛大学農学部': 38,
    '宇和島市役所': 38,

    # --- 高知 (39) ---
    '高知県保健衛生総合庁舎': 39,
    '幡多福祉保健所': 39,

    # --- 福岡 (40) ---
    '小倉医師会': 40,
    '福岡県久留米市': 40,
    '田川市立病院': 40,

    # --- 佐賀 (41) ---
    '佐賀県環境センター': 41,
    '唐津市役所': 41,
    '佐賀県武雄総合庁舎': 41,

    # --- 長崎 (42) ---
    '長崎大学病院': 42,
    '諫早総合病院': 42,
    '長崎県': 42,  # 県北振興局

    # --- 熊本 (43) ---
    '熊本市医師会': 43,
    '国立水俣病総合研究センター': 43,
    '休暇村': 43,  # 南阿蘇

    # --- 大分 (44) ---
    '大分県南部振興局': 44,
    '大分大学医学部': 44,
    '大分県農林水産研究': 44,

    # --- 宮崎 (45) ---
    '延岡保健所': 45,
    '宮崎県庁': 45,

    # --- 鹿児島 (46) ---
    '鹿児島県環境保健センター': 46,
    '鹿児島県姶良': 46,
    '鹿児島県大隅': 46,
}


def match_station_to_pref(station_name):
    """観測地点名から都道府県コードを推定"""
    for keyword, pref_code in STATION_TO_PREF.items():
        if keyword in station_name:
            return pref_code
    return None


def process_hanako_file(filepath):
    """はなこさんExcelファイルを読み込み、地点別シーズン累計を算出"""
    df = pd.read_excel(filepath, header=1)

    # 年月日時の列名
    time_cols = ['年', '月', '日', '時']
    existing_time_cols = [c for c in time_cols if c in df.columns]

    # 観測地点列（Unnamed除外、時間列除外）
    station_cols = [
        c for c in df.columns
        if not c.startswith('Unnamed') and c not in time_cols
    ]

    if not station_cols:
        logger.warning(f"  観測地点が見つかりません: {filepath.name}")
        return pd.DataFrame()

    # 負値（エラーコード）をNaNに置換
    df_stations = df[station_cols].copy()
    df_stations = df_stations.apply(pd.to_numeric, errors='coerce')
    df_stations[df_stations < 0] = np.nan

    # 各地点のシーズン累計（時間データの合計）
    results = []
    for col in station_cols:
        pref_code = match_station_to_pref(col)
        if pref_code is None:
            logger.warning(f"  マッピング不明: '{col}'")
            continue

        total = df_stations[col].sum()  # NaNは自動スキップ
        valid_hours = df_stations[col].notna().sum()
        total_hours = len(df_stations)

        results.append({
            'station': col,
            'pref_code': pref_code,
            'seasonal_total': total,
            'valid_hours': valid_hours,
            'total_hours': total_hours,
            'coverage_pct': valid_hours / total_hours * 100 if total_hours > 0 else 0,
        })

    return pd.DataFrame(results)


def main():
    logger.info("=" * 60)
    logger.info("Phase 2d: はなこさん花粉データ抽出")
    logger.info("=" * 60)

    hanako_dir = POLLEN_PROJECT / "data" / "external" / "hanako"
    output_dir = POLLEN_PROJECT / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)

    years = [2019, 2020, 2021]
    regions = ['hokkaido', 'tohoku', 'kanto', 'chubu', 'kansai',
               'chugoku_shikoku', 'kyushu']

    all_station_data = []

    for year in years:
        logger.info(f"\n--- {year}年 ---")
        for region in regions:
            filepath = hanako_dir / f"{year}_{region}.xlsx"
            if not filepath.exists():
                logger.warning(f"  ファイル不在: {filepath.name}")
                continue

            df_result = process_hanako_file(filepath)
            if len(df_result) > 0:
                df_result['year'] = year
                df_result['region'] = region
                all_station_data.append(df_result)
                logger.info(f"  {region}: {len(df_result)}地点")

    # 全データ結合
    df_all = pd.concat(all_station_data, ignore_index=True)
    logger.info(f"\n全データ: {len(df_all)}行")

    # QC: カバレッジが50%未満の地点を除外
    min_coverage = 50.0
    n_before = len(df_all)
    df_all = df_all[df_all['coverage_pct'] >= min_coverage].copy()
    n_after = len(df_all)
    logger.info(f"QC: カバレッジ>={min_coverage}%: {n_before} → {n_after}行")

    # 都道府県×年ごとに平均
    df_pref_year = df_all.groupby(['pref_code', 'year']).agg(
        seasonal_total_mean=('seasonal_total', 'mean'),
        n_stations=('station', 'count'),
    ).reset_index()

    logger.info(f"\n都道府県×年データ: {len(df_pref_year)}行")

    # 3年平均
    df_pref = df_pref_year.groupby('pref_code').agg(
        pollen_count=('seasonal_total_mean', 'mean'),
        n_years=('year', 'count'),
        avg_stations=('n_stations', 'mean'),
    ).reset_index()

    # 都道府県名を付与
    pref_names = {
        1: '北海道', 2: '青森県', 3: '岩手県', 4: '宮城県', 5: '秋田県',
        6: '山形県', 7: '福島県', 8: '茨城県', 9: '栃木県', 10: '群馬県',
        11: '埼玉県', 12: '千葉県', 13: '東京都', 14: '神奈川県', 15: '新潟県',
        16: '富山県', 17: '石川県', 18: '福井県', 19: '山梨県', 20: '長野県',
        21: '岐阜県', 22: '静岡県', 23: '愛知県', 24: '三重県', 25: '滋賀県',
        26: '京都府', 27: '大阪府', 28: '兵庫県', 29: '奈良県', 30: '和歌山県',
        31: '鳥取県', 32: '島根県', 33: '岡山県', 34: '広島県', 35: '山口県',
        36: '徳島県', 37: '香川県', 38: '愛媛県', 39: '高知県', 40: '福岡県',
        41: '佐賀県', 42: '長崎県', 43: '熊本県', 44: '大分県', 45: '宮崎県',
        46: '鹿児島県', 47: '沖縄県',
    }
    df_pref['pref_name'] = df_pref['pref_code'].map(pref_names)

    # 沖縄の処理（はなこさんに観測地点なし）
    if 47 not in df_pref['pref_code'].values:
        logger.warning("沖縄県: 花粉観測地点なし → スギ花粉ほぼ飛散なしとして0を設定")
        okinawa = pd.DataFrame([{
            'pref_code': 47,
            'pollen_count': 0.0,  # スギ・ヒノキ花粉はほぼ飛散しない
            'n_years': 3,
            'avg_stations': 0,
            'pref_name': '沖縄県',
        }])
        df_pref = pd.concat([df_pref, okinawa], ignore_index=True)

    df_pref = df_pref.sort_values('pref_code').reset_index(drop=True)

    # 結果表示
    logger.info(f"\n{'='*60}")
    logger.info(f"都道府県別花粉飛散量（3年平均シーズン累計, 個/cm²）")
    logger.info(f"{'='*60}")
    logger.info(f"都道府県数: {len(df_pref)}")
    logger.info(f"花粉飛散量: 平均={df_pref['pollen_count'].mean():.1f}, "
                f"SD={df_pref['pollen_count'].std():.1f}")
    logger.info(f"  最大: {df_pref.loc[df_pref['pollen_count'].idxmax(), 'pref_name']} "
                f"({df_pref['pollen_count'].max():.1f})")
    logger.info(f"  最小: {df_pref.loc[df_pref['pollen_count'].idxmin(), 'pref_name']} "
                f"({df_pref['pollen_count'].min():.1f})")

    # 欠落都道府県チェック
    missing = set(range(1, 48)) - set(df_pref['pref_code'])
    if missing:
        logger.warning(f"データ欠落都道府県: {[pref_names[c] for c in sorted(missing)]}")

    # CSV出力
    out_cols = ['pref_code', 'pref_name', 'pollen_count', 'n_years', 'avg_stations']
    out_path = output_dir / "pollen_hanako_prefecture.csv"
    df_pref[out_cols].to_csv(out_path, index=False, encoding='utf-8-sig')
    logger.info(f"\n保存: {out_path}")

    # 地点別詳細データも保存
    detail_path = output_dir / "pollen_hanako_station_detail.csv"
    df_all.to_csv(detail_path, index=False, encoding='utf-8-sig')
    logger.info(f"保存（詳細）: {detail_path}")

    # 年別データも保存
    yearly_path = output_dir / "pollen_hanako_yearly.csv"
    df_pref_year.to_csv(yearly_path, index=False, encoding='utf-8-sig')
    logger.info(f"保存（年別）: {yearly_path}")

    logger.info(f"\n{'='*60}")
    logger.info("Phase 2d 完了")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
