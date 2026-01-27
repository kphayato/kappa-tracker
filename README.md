# カッパ整体院 全店舗管理システム

全国58店舗のキャンペーン情報を自動収集・管理するシステム

## 🏗️ システム構成

```
GitHub Actions (週3回自動実行)
    ↓
Pythonスクレイパー (scraper.py)
    ↓
各店舗サイトから自動収集
    ↓
campaign_data.json に保存
    ↓
フロントエンド (index.html) で表示
```

## 🚀 セットアップ手順

### 1. GitHubリポジトリ作成

```bash
# 新規リポジトリを作成
mkdir kappa-tracker
cd kappa-tracker
git init

# ファイルをコピー
# - index.html (フロントエンド)
# - scraper.py (スクレイパー)
# - requirements.txt (Python依存関係)
# - .github/workflows/scrape.yml (自動実行設定)

git add .
git commit -m "初回コミット"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kappa-tracker.git
git push -u origin main
```

### 2. GitHub Actionsを有効化

1. リポジトリの「Actions」タブに移動
2. 「I understand my workflows, go ahead and enable them」をクリック
3. 自動的に週3回（月・水・金の9:00）実行されます

### 3. 手動でテスト実行

1. 「Actions」タブ → 「データ自動収集」
2. 「Run workflow」をクリック
3. 数分後に `campaign_data.json` が更新される

### 4. フロントエンドをデプロイ

#### Netlifyの場合:
```bash
# index.htmlとcampaign_data.jsonを同じディレクトリに配置
netlify deploy --prod
```

#### Vercelの場合:
```bash
vercel --prod
```

## 📁 ファイル構成

```
kappa-tracker/
├── index.html              # フロントエンド（管理画面）
├── scraper.py              # データ収集スクリプト
├── requirements.txt        # Python依存関係
├── campaign_data.json      # 収集したデータ（自動生成）
├── .github/
│   └── workflows/
│       └── scrape.yml      # 自動実行設定
└── README.md               # このファイル
```

## ⏰ 自動実行スケジュール

- **月曜日 9:00 JST**
- **水曜日 9:00 JST**
- **金曜日 9:00 JST**

手動実行も可能：GitHub Actions → Run workflow

## 🔧 カスタマイズ

### スケジュール変更

`.github/workflows/scrape.yml` の `cron` を編集:

```yaml
# 毎日12:00に実行
- cron: '0 3 * * *'  # UTC 3:00 = JST 12:00

# 月〜金の18:00に実行
- cron: '0 9 * * 1-5'  # UTC 9:00 = JST 18:00
```

### 店舗追加

`scraper.py` の `STORES` リストに追加:

```python
STORES = [
    {"id": "new_store", "name": "新店舗", "region": "東京", "url": "https://..."},
    # ...
]
```

## 🔐 認証情報

### デフォルトアカウント

**Owner（最高権限）:**
- ID: `owner`
- PW: `kappa_owner_2024`

**Master（管理者）:**
- ID: `master`
- PW: `kappa2024`

## 📊 データ形式

`campaign_data.json`:

```json
{
  "last_updated": "2026-01-27T12:00:00",
  "total_stores": 58,
  "successful": 45,
  "stores": [
    {
      "id": "moriya",
      "name": "守谷店",
      "region": "茨城",
      "url": "https://moriya.kappaseitai.com",
      "data": {
        "deadline": "2026-01-31",
        "remaining": 3,
        "timestamp": "2026-01-27T12:00:00",
        "success": true
      },
      "status": "success"
    }
  ]
}
```

## 🐛 トラブルシューティング

### データが取得できない場合

1. `scraper.py` の正規表現パターンを確認
2. 対象サイトのHTML構造が変わっている可能性
3. 手動で確認: `python scraper.py`

### GitHub Actionsが実行されない

1. リポジトリ設定 → Actions → 有効化を確認
2. `.github/workflows/scrape.yml` の配置を確認
3. ブランチ名が `main` であることを確認

## 📞 サポート

問題が発生した場合は、GitHub Issuesで報告してください。
