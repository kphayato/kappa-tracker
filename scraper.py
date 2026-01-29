#!/usr/bin/env python3
"""
カッパ整体院 全店舗データ収集スクリプト
各店舗のキャンペーン情報（期限・残り人数）を自動収集
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

# 必要なライブラリ
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("必要なライブラリをインストールしてください:")
    print("pip install requests beautifulsoup4")
    exit(1)

# 店舗リスト
STORES = [
    # 茨城県
    {"id": "ushiku", "name": "牛久店", "region": "茨城", "url": "https://kappaseitai.com"},
    {"id": "tsuchiura", "name": "土浦店", "region": "茨城", "url": "https://tsuchiura.kappaseitai.com"},
    {"id": "moriya", "name": "守谷店", "region": "茨城", "url": "https://moriya.kappaseitai.com"},
    {"id": "hitachinaka", "name": "ひたちなか店", "region": "茨城", "url": "https://hitachinaka.kappaseitai.com"},
    {"id": "hitachi", "name": "日立店", "region": "茨城", "url": "https://hitachi.kappaseitai.com"},
    {"id": "tsukuba", "name": "つくば桜店", "region": "茨城", "url": "https://tsukuba.kappaseitai.com"},
    {"id": "koga", "name": "古河店", "region": "茨城", "url": "https://koga.kappaseitai.com"},
    {"id": "mito", "name": "水戸店", "region": "茨城", "url": "https://mito.kappaseitai.com"},
    
    # 北海道
    {"id": "asahikawa", "name": "旭川店", "region": "北海道", "url": "https://asahikawa.kappaseitai.com"},
    {"id": "sapporonishioka", "name": "札幌西岡店", "region": "北海道", "url": "https://sapporonishioka.kappaseitai.com"},
    {"id": "higashikuyakusyo", "name": "東区役所前店", "region": "北海道", "url": "https://higashikuyakusyo.kappaseitai.com"},
    {"id": "obihiro", "name": "帯広店", "region": "北海道", "url": "https://obihiro.kappaseitai.com"},
    
    # 岩手県
    {"id": "morioka", "name": "盛岡店", "region": "岩手", "url": "https://morioka.kappaseitai.com"},
    
    # 宮城県
    {"id": "sendai", "name": "仙台六丁の目店", "region": "宮城", "url": "https://sendai.kappaseitai.com"},
    {"id": "tomiya", "name": "富谷店", "region": "宮城", "url": "https://tomiya.kappaseitai.com"},
    {"id": "dainohara", "name": "台原店", "region": "宮城", "url": "https://dainohara.kappaseitai.com"},
    
    # 福島県
    {"id": "koriyama", "name": "郡山店", "region": "福島", "url": "https://koriyama.kappaseitai.com"},
    {"id": "iwaki", "name": "いわき店", "region": "福島", "url": "https://iwaki.kappaseitai.com"},
    {"id": "fukushima", "name": "福島店", "region": "福島", "url": "https://fukushima.kappaseitai.com"},
    
    # 栃木県
    {"id": "tochigi", "name": "栃木店", "region": "栃木", "url": "https://tochigi.kappaseitai.com"},
    {"id": "utsunomiya", "name": "宇都宮店", "region": "栃木", "url": "https://utsunomiya.kappaseitai.com"},
    {"id": "oyama", "name": "小山店", "region": "栃木", "url": "https://oyama.kappaseitai.com"},
    
    # 千葉県
    {"id": "ichikawa", "name": "市川店", "region": "千葉", "url": "https://ichikawa.kappaseitai.com"},
    {"id": "inzai", "name": "印西店", "region": "千葉", "url": "https://inzai.kappaseitai.com"},
    {"id": "kisarazu", "name": "木更津店", "region": "千葉", "url": "https://kisarazu.kappaseitai.com"},
    {"id": "matsudomabashi", "name": "松戸馬橋店", "region": "千葉", "url": "https://matsudomabashi.kappaseitai.com"},
    
    # 埼玉県
    {"id": "kumagaya", "name": "熊谷店", "region": "埼玉", "url": "https://kumagaya.kappaseitai.com"},
    
    # 東京都
    {"id": "azabu10ban", "name": "PT麻布十番駅前整骨院", "region": "東京", "url": "https://azabu10ban.kappaseitai.com"},
    {"id": "nippori", "name": "日暮里駅前店", "region": "東京", "url": "https://nippori.kappaseitai.com"},
    
    # 神奈川県
    {"id": "ikuta", "name": "川崎生田店", "region": "神奈川", "url": "https://ikuta.kappaseitai.com"},
    {"id": "odawara", "name": "小田原店", "region": "神奈川", "url": "https://odawara.kappaseitai.jp"},
    
    # 長野県
    {"id": "matsumoto", "name": "松本店", "region": "長野", "url": "https://matsumoto.kappaseitai.com"},
    {"id": "nagano", "name": "長野店", "region": "長野", "url": "https://nagano.kappaseitai.com"},
    
    # 富山県
    {"id": "takaoka", "name": "富山高岡店", "region": "富山", "url": "https://takaoka.kappaseitai.com"},
    {"id": "toyama", "name": "富山店", "region": "富山", "url": "https://toyama.kappaseitai.jp"},
    
    # 石川県
    {"id": "nonoichi", "name": "石川野々市店", "region": "石川", "url": "https://nonoichi.kappaseitai.com"},
    {"id": "kanazawa", "name": "金沢店", "region": "石川", "url": "https://kanazawa.kappaseitai.jp"},
    
    # 愛知県
    {"id": "owariasahi", "name": "尾張旭店", "region": "愛知", "url": "https://owariasahi.kappaseitai.com"},
    {"id": "toyohashi", "name": "豊橋店", "region": "愛知", "url": "https://toyohashi.kappaseitai.jp"},
    
    # 滋賀県
    {"id": "kusatsu", "name": "草津店", "region": "滋賀", "url": "https://kusatsu.kappaseitai.com"},
    
    # 大阪府
    {"id": "osakafukushima", "name": "ふくしま駅前店", "region": "大阪", "url": "https://osakafukushima.kappaseitai.com"},
    {"id": "tenjinbashi", "name": "天神橋店", "region": "大阪", "url": "https://tenjinbashi.kappa-seitai.jp"},
    
    # 兵庫県
    {"id": "nishiakashi", "name": "西明石店", "region": "兵庫", "url": "https://nishiakashi.kappaseitai.com"},
    
    # 奈良県
    {"id": "naraoji", "name": "奈良王寺店", "region": "奈良", "url": "https://naraoji.kappaseitai.com"},
    
    # 広島県
    {"id": "hiroshima", "name": "広島光町店", "region": "広島", "url": "https://hiroshima.kappaseitai.com"},
    {"id": "hiroshimaminami", "name": "ゆめタウンみゆき店", "region": "広島", "url": "https://hiroshimaminami.kappaseitai.com"},
    {"id": "kure", "name": "呉駅前店", "region": "広島", "url": "https://kure.kappaseitai.com"},
    {"id": "hiroshimagion", "name": "広島祇園店", "region": "広島", "url": "https://hiroshimagion.kappaseitai.com"},
    {"id": "hatsukaichi", "name": "ゆめタウン廿日市店", "region": "広島", "url": "https://hatsukaichi.kappaseitai.com"},
    
    # 福岡県
    {"id": "otemon", "name": "福岡大手門店", "region": "福岡", "url": "https://otemon.kappaseitai.com"},
    {"id": "kitakyushu", "name": "北九州店", "region": "福岡", "url": "https://kitakyushu.kappaseitai.com"},
    {"id": "kurume", "name": "久留米店", "region": "福岡", "url": "https://kurume.kappaseitai.com"},
    
    # 熊本県
    {"id": "nagamine", "name": "長嶺店", "region": "熊本", "url": "https://nagamine.kappaseitai.com"},
    {"id": "kumamotoshimasaki", "name": "熊本島崎店", "region": "熊本", "url": "https://kumamotoshimasaki.kappaseitai.com"},
    
    # 宮崎県
    {"id": "miyazaki", "name": "宮崎店", "region": "宮崎", "url": "https://miyazaki.kappaseitai.jp"},
    
    # 鹿児島県
    {"id": "kagoshima", "name": "鹿児島店", "region": "鹿児島", "url": "https://kagoshima.kappaseitai.com"},
    
    # 沖縄県
    {"id": "naha", "name": "那覇店", "region": "沖縄", "url": "https://naha.kappaseitai.com"}
]


def extract_campaign_data(html_content: str) -> Optional[Dict]:
    """
    HTMLからキャンペーン情報を抽出
    
    改善版：キャンペーン関連のコンテキスト内でのみデータを抽出
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # キャンペーン関連キーワード
        campaign_keywords = [
            'キャンペーン', 'ご予約の方に限り', '先着', '予約多数',
            '初回限定', '期間限定', 'お得', '特別価格', 'までに'
        ]
        
        # キャンペーンセクションを探す
        campaign_sections = []
        for keyword in campaign_keywords:
            if keyword in text:
                # キーワードの位置を見つける
                index = text.find(keyword)
                # 前後400文字を取得（キャンペーン情報が含まれる範囲）
                start = max(0, index - 200)
                end = min(len(text), index + 400)
                section = text[start:end]
                campaign_sections.append(section)
        
        # キャンペーンセクションが見つからない場合は全体を対象
        if not campaign_sections:
            campaign_sections = [text]
        
        # 全セクションから日付と人数を抽出
        all_dates = []
        all_remaining = []
        
        for section in campaign_sections:
            # 日付を検索（例: 1月31日、1月31日まで、○月○日迄）
            date_pattern = r'(\d+)月(\d+)日(?:まで|迄)?'
            date_matches = re.finditer(date_pattern, section)
            
            for match in date_matches:
                month = int(match.group(1))
                day = int(match.group(2))
                year = datetime.now().year
                
                # 月が過去の場合は来年
                current_month = datetime.now().month
                if month < current_month or (month == current_month and day < datetime.now().day):
                    year += 1
                
                date_obj = datetime(year, month, day)
                all_dates.append(date_obj)
            
            # 残り人数を検索（例: 残り3名、一残り3名、あと3名、→残り3名）
            remaining_pattern = r'[→一ー\s]*(?:残り|あと)[\s]*(\d+)名'
            remaining_matches = re.finditer(remaining_pattern, section)
            
            for match in remaining_matches:
                remaining = int(match.group(1))
                all_remaining.append(remaining)
        
        # 最新の日付を選択
        deadline = None
        if all_dates:
            latest_date = max(all_dates)
            deadline = latest_date.strftime("%Y-%m-%d")
        
        # 残り人数（最初に見つかったものを使用）
        remaining = all_remaining[0] if all_remaining else None
        
        if deadline or remaining is not None:
            return {
                "deadline": deadline,
                "remaining": remaining,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
        
        return None
        
    except Exception as e:
        print(f"データ抽出エラー: {e}")
        return None


def scrape_store(store: Dict) -> Dict:
    """
    1つの店舗をスクレイピング
    """
    print(f"チェック中: {store['name']} ({store['url']})")
    
    try:
        # ウェブサイトにアクセス
        response = requests.get(
            store['url'],
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        response.raise_for_status()
        
        # データ抽出
        campaign_data = extract_campaign_data(response.text)
        
        if campaign_data:
            print(f"  ✓ データ取得成功: 期限={campaign_data['deadline']}, 残り={campaign_data['remaining']}名")
            return {
                **store,
                "data": campaign_data,
                "status": "success"
            }
        else:
            print(f"  ⚠ データが見つかりませんでした")
            return {
                **store,
                "data": None,
                "status": "no_data"
            }
            
    except requests.Timeout:
        print(f"  ✗ タイムアウト")
        return {
            **store,
            "data": None,
            "status": "timeout"
        }
    except Exception as e:
        print(f"  ✗ エラー: {e}")
        return {
            **store,
            "data": None,
            "status": "error",
            "error": str(e)
        }


def scrape_all_stores() -> List[Dict]:
    """
    全店舗をスクレイピング
    """
    results = []
    
    print(f"\n{'='*60}")
    print(f"カッパ整体院 データ収集開始")
    print(f"対象店舗数: {len(STORES)}")
    print(f"{'='*60}\n")
    
    for i, store in enumerate(STORES, 1):
        print(f"[{i}/{len(STORES)}] ", end="")
        result = scrape_store(store)
        results.append(result)
        
        # サーバー負荷軽減のため少し待機
        if i < len(STORES):
            time.sleep(2)
    
    # 統計
    success_count = sum(1 for r in results if r['status'] == 'success')
    no_data_count = sum(1 for r in results if r['status'] == 'no_data')
    error_count = sum(1 for r in results if r['status'] in ['timeout', 'error'])
    
    print(f"\n{'='*60}")
    print(f"収集完了")
    print(f"成功: {success_count} / データなし: {no_data_count} / エラー: {error_count}")
    print(f"{'='*60}\n")
    
    return results


def save_results(results: List[Dict], output_file: str = "campaign_data.json"):
    """
    結果をJSONファイルに保存
    """
    output = {
        "last_updated": datetime.now().isoformat(),
        "total_stores": len(results),
        "successful": sum(1 for r in results if r['status'] == 'success'),
        "stores": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"結果を保存しました: {output_file}")


def main():
    """
    メイン処理
    """
    results = scrape_all_stores()
    save_results(results)
    
    print("\n完了！")


if __name__ == "__main__":
    main()
