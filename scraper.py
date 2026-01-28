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
    
    # 他の店舗も同様に追加...
]


def extract_campaign_data(html_content: str) -> Optional[Dict]:
    """
    HTMLからキャンペーン情報を抽出
    
    パターン:
    - "1月31日まで" または "○月○日まで"
    - "残り○名"
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # 日付を検索（例: 1月31日まで）
        date_pattern = r'(\d+)月(\d+)日'
        date_match = re.search(date_pattern, text)
        
        deadline = None
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = datetime.now().year
            
            # 月が過去の場合は来年
            if month < datetime.now().month:
                year += 1
            
            deadline = f"{year}-{month:02d}-{day:02d}"
        
        # 残り人数を検索（例: 残り3名）
        remaining_pattern = r'残り(\d+)名'
        remaining_match = re.search(remaining_pattern, text)
        
        remaining = None
        if remaining_match:
            remaining = int(remaining_match.group(1))
        
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
