#!/usr/bin/env python3
"""
カッパ整体院 全店舗データ収集スクリプト
各店舗のキャンペーン情報（期限・残り人数）を自動収集

改善版:
- stores.json から店舗リストを読み込み
- 過去の日付は期限切れとして扱う（来年にしない）
- オープン日などの除外
- 「まで」付き日付を優先
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time
import os

# 必要なライブラリ
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("必要なライブラリをインストールしてください:")
    print("pip install requests beautifulsoup4")
    exit(1)


def load_stores() -> List[Dict]:
    """
    stores.json から店舗リストを読み込む
    """
    stores_file = 'stores.json'
    
    # ファイルが存在するか確認
    if not os.path.exists(stores_file):
        print(f"エラー: {stores_file} が見つかりません")
        print("stores.json を作成してください")
        exit(1)
    
    try:
        with open(stores_file, 'r', encoding='utf-8') as f:
            stores = json.load(f)
        
        # active フラグを追加（デフォルトは True）
        for store in stores:
            if 'active' not in store:
                store['active'] = True
        
        # アクティブな店舗のみ返す
        active_stores = [s for s in stores if s.get('active', True)]
        
        print(f"店舗リスト読み込み完了: 全{len(stores)}店舗 / アクティブ{len(active_stores)}店舗")
        return active_stores
        
    except json.JSONDecodeError as e:
        print(f"エラー: stores.json の形式が正しくありません: {e}")
        exit(1)
    except Exception as e:
        print(f"エラー: stores.json の読み込みに失敗しました: {e}")
        exit(1)


def extract_campaign_data(html_content: str) -> Optional[Dict]:
    """
    HTMLからキャンペーン情報を抽出
    
    改善版：キャンペーン関連のコンテキスト内でのみデータを抽出
    除外キーワード（オープン、営業時間など）の近くの日付は無視
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # 除外キーワード（これらの近くの日付は無視）
        exclude_keywords = [
            'オープン', '開店', '開業', 'OPEN', 'Open', 
            '営業時間', '定休日', '休診日', '年末年始',
            '開院', 'グランドオープン'
        ]
        
        # キャンペーン関連キーワード
        campaign_keywords = [
            'キャンペーン', 'ご予約の方に限り', '先着', '予約多数',
            '初回限定', '期間限定', 'お得', '特別価格', 'までに',
            '残り', 'あと', '名様限定', 'お問い合わせの方'
        ]
        
        # キャンペーンセクションを探す
        campaign_sections = []
        for keyword in campaign_keywords:
            if keyword in text:
                # キーワードの位置を見つける（全て）
                start_pos = 0
                while True:
                    index = text.find(keyword, start_pos)
                    if index == -1:
                        break
                    
                    # 前後400文字を取得（キャンペーン情報が含まれる範囲）
                    section_start = max(0, index - 200)
                    section_end = min(len(text), index + 400)
                    section = text[section_start:section_end]
                    
                    # 除外キーワードが含まれていないことを確認
                    has_exclude = any(excl in section for excl in exclude_keywords)
                    if not has_exclude:
                        campaign_sections.append(section)
                    
                    start_pos = index + 1
        
        # キャンペーンセクションが見つからない場合は全体を対象
        if not campaign_sections:
            campaign_sections = [text]
        
        # 全セクションから日付と人数を抽出
        all_dates = []
        all_remaining = []
        
        for section in campaign_sections:
            # 日付を検索
            # 優先順位: 「○月○日まで」 > 「○月○日」
            date_pattern_with_made = r'(\d+)月(\d+)日(?:まで|迄)'
            date_pattern_plain = r'(\d+)月(\d+)日'
            
            # まず「まで」付きの日付を探す
            date_matches = list(re.finditer(date_pattern_with_made, section))
            
            # なければ普通の日付を探す
            if not date_matches:
                date_matches = list(re.finditer(date_pattern_plain, section))
            
            for match in date_matches:
                month = int(match.group(1))
                day = int(match.group(2))
                year = datetime.now().year
                
                # 今年の日付として作成
                try:
                    date_obj = datetime(year, month, day)
                except ValueError:
                    # 無効な日付（例: 2月30日）はスキップ
                    continue
                
                # 日付の前後50文字をチェックして除外キーワードが近くにないか確認
                match_start = max(0, match.start() - 50)
                match_end = min(len(section), match.end() + 50)
                context = section[match_start:match_end]
                
                has_exclude_nearby = any(excl in context for excl in exclude_keywords)
                if not has_exclude_nearby:
                    all_dates.append(date_obj)
                    print(f"    [DEBUG] 見つかった日付: {year}-{month:02d}-{day:02d}")
                else:
                    print(f"    [DEBUG] 除外した日付: {year}-{month:02d}-{day:02d} (除外キーワード近接)")
            
            # 残り人数を検索（例: 残り3名、一残り3名、あと3名、→残り3名）
            remaining_pattern = r'[→一ー\s]*(?:残り|あと)[\s]*(\d+)名'
            remaining_matches = re.finditer(remaining_pattern, section)
            
            for match in remaining_matches:
                remaining = int(match.group(1))
                all_remaining.append(remaining)
                print(f"    [DEBUG] 見つかった人数: {remaining}名")
        
        # 最新の日付を選択（未来の日付を優先、なければ最も新しい過去の日付）
        deadline = None
        if all_dates:
            now = datetime.now()
            future_dates = [d for d in all_dates if d >= now]
            
            if future_dates:
                # 未来の日付がある場合は最も近い未来の日付を選択
                latest_date = min(future_dates)
            else:
                # 全て過去の日付の場合は最も新しい日付を選択
                latest_date = max(all_dates)
            
            deadline = latest_date.strftime("%Y-%m-%d")
            print(f"    [DEBUG] 採用した日付: {deadline} (全{len(all_dates)}件から選択)")
        
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
    # stores.json から店舗リストを読み込む
    stores = load_stores()
    
    results = []
    
    print(f"\n{'='*60}")
    print(f"カッパ整体院 データ収集開始")
    print(f"対象店舗数: {len(stores)}")
    print(f"{'='*60}\n")
    
    for i, store in enumerate(stores, 1):
        print(f"[{i}/{len(stores)}] ", end="")
        result = scrape_store(store)
        results.append(result)
        
        # サーバー負荷軽減のため少し待機
        if i < len(stores):
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