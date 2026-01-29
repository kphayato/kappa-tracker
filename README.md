# カッパ整体院 キャンペーン管理システム

全58店舗のキャンペーン情報を自動収集・一元管理するWebアプリケーション

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://kphayato.github.io/kappa-tracker/)
[![GitHub Actions](https://github.com/kphayato/kappa-tracker/workflows/Campaign%20Scraper/badge.svg)](https://github.com/kphayato/kappa-tracker/actions)

## 🎯 主な機能

### 自動データ収集
- **58店舗の自動スクレイピング**（全国展開）
- **スケジュール実行**: 毎週月・水・金 9:00 JST
- **手動トリガー**: ボタン1つで即時データ更新（約5分）
- **インテリジェント抽出**: キャンペーン情報のみを正確に抽出
  - 除外キーワード対応（オープン日、営業時間など）
  - 「○月○日まで」形式を優先
  - 過去の日付は期限切れとして扱う

### 管理機能
- **ロール別アクセス制御**: Owner / Master / User
- **フィルタリング**: 稼働状態、期限切れ、最近更新、要確認
- **リアルタイム統計**: 稼働中、期限切れ、最新更新の店舗数
- **履歴管理**: 各店舗のキャンペーン変更履歴
- **店舗管理**: 追加・編集・一時停止・削除

### 視覚的インジケーター
- 🔴 **期限切れ**: 赤枠 + 赤バッジ
- 🟠 **最近更新**: オレンジバッジ（7日以内）
- ⚪ **要確認**: グレーバッジ（データなし or 7日以上未更新）

---

## 🏗️ システム構成

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
├─────────────────────────────────────────────────────────┤
│  stores.json          ← 店舗マスターデータ（58店舗）     │
│  scraper.py           ← データ収集スクリプト              │
│  index.html           ← Webアプリケーション               │
│  campaign_data.json   ← 収集結果データ                   │
└─────────────────────────────────────────────────────────┘
           │                        │
           │ GitHub Actions         │ GitHub Pages
           │ (自動実行)             │ (自動デプロイ)
           ↓                        ↓
    ┌──────────────┐        ┌──────────────┐
    │ スケジュール  │        │   Webサイト   │
    │ 月・水・金    │        │  https://... │
    │   9:00 JST   │        │  アクセス可能 │
    └──────────────┘        └──────────────┘
           │
           ↓
    全58店舗をスクレイピング
    campaign_data.json 更新
           │
           ↓
    自動的にGitHub Pagesへ反映
```

---

## 📂 ファイル構成

### **stores.json** - 店舗マスターデータ
全店舗の情報を一元管理。追加・編集はこのファイルを更新するだけ。

```json
[
  {
    "id": "moriya",
    "name": "守谷店",
    "region": "茨城",
    "url": "https://moriya.kappaseitai.com",
    "active": true
  }
]
```

**フィールド:**
- `id`: 店舗の一意ID
- `name`: 店舗名
- `region`: 地域
- `url`: 店舗ウェブサイトURL
- `active`: 稼働状態（true/false、オプション、デフォルトtrue）

### **scraper.py** - データ収集スクリプト

**主な機能:**
- stores.json から店舗リストを読み込み
- 各店舗のウェブサイトをスクレイピング
- キャンペーン情報（期限・残り人数）を抽出
- campaign_data.json に保存

**インテリジェント抽出ロジック:**
```python
# キャンペーン関連キーワードの近くからデータ抽出
campaign_keywords = [
    'キャンペーン', 'ご予約の方に限り', '先着', '予約多数',
    '初回限定', '期間限定', 'お得', '特別価格', 'までに',
    '残り', 'あと', '名様限定'
]

# 除外キーワード（これらの近くの日付は無視）
exclude_keywords = [
    'オープン', '開店', '開業', 'OPEN',
    '営業時間', '定休日', '休診日', '年末年始'
]

# 日付の優先順位
# 1. 未来の日付 > 過去の日付
# 2. 「○月○日まで」 > 「○月○日」
# 3. 日付が近い > 日付が遠い
```

**実行:**
```bash
pip install requests beautifulsoup4 --break-system-packages
python scraper.py
```

### **index.html** - Webアプリケーション

**機能:**
- ログイン認証（ロールベース）
- 店舗一覧表示（カード形式）
- フィルタリング・統計表示
- 手動データ更新トリガー
- 店舗管理（追加・編集・削除）

**データ取得:**
```javascript
// GitHub から最新データを自動取得
const response = await fetch(
  'https://raw.githubusercontent.com/kphayato/kappa-tracker/main/campaign_data.json'
);
```

### **campaign_data.json** - 収集結果データ

```json
{
  "last_updated": "2026-01-29T10:30:00.000000",
  "total_stores": 58,
  "successful": 51,
  "stores": [
    {
      "id": "moriya",
      "name": "守谷店",
      "region": "茨城",
      "url": "https://moriya.kappaseitai.com",
      "data": {
        "deadline": "2026-01-31",
        "remaining": 3,
        "timestamp": "2026-01-29T10:29:21.485575",
        "success": true
      },
      "status": "success"
    }
  ]
}
```

---

## 🚀 セットアップ

### 1. リポジトリの準備

```bash
# クローン
git clone https://github.com/kphayato/kappa-tracker.git
cd kappa-tracker

# 必要なファイルを配置
# - stores.json
# - scraper.py
# - index.html
```

### 2. GitHub Actions の設定

`.github/workflows/scrape.yml` が自動的にスクレイピングを実行します。

**スケジュール:**
```yaml
schedule:
  - cron: '0 0 * * 1,3,5'  # 月・水・金 9:00 JST
```

### 3. GitHub Pages の有効化

1. リポジトリの **Settings** → **Pages**
2. Source: **GitHub Actions**
3. 自動的に `https://kphayato.github.io/kappa-tracker/` でデプロイ

### 4. GitHub Personal Access Token（手動更新用）

手動データ更新機能を使用する場合：

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token (classic)**
3. スコープ: `repo`, `workflow`
4. トークンをコピー
5. アプリの初回使用時に入力

---

## 🎮 使い方

### ログイン

**アカウント:**
- Owner: `owner` / `kappa_owner_2024`
- Master: `master` / `kappa2024`
- User: `user` / `kappa123`

**権限:**
| 機能 | Owner | Master | User |
|------|-------|--------|------|
| 閲覧 | ✅ | ✅ | ✅ |
| フィルター | ✅ | ✅ | ✅ |
| 手動更新 | ✅ | ✅ | ❌ |
| 店舗編集 | ✅ | ✅ | ❌ |
| 店舗削除 | ✅ | ❌ | ❌ |

### 手動データ更新

1. **「🔄 最新データを取得（5分）」** ボタンをクリック
2. GitHub Token を入力（初回のみ）
3. GitHub Actions が実行される
4. 5分後にページをリロード

### フィルター機能

**店舗状態:**
- 全店舗
- 稼働中のみ
- 停止中のみ

**キャンペーン状態:**
- 期限切れ
- 最近更新（7日以内）
- 要確認（データなし or 7日以上未更新）

### 統計カード

クリックでフィルタリング：
- **稼働中**: 稼働している店舗
- **期限切れ**: キャンペーン期限が過ぎた店舗
- **最近更新**: 7日以内に更新された店舗
- **要確認**: データなし or 7日以上未更新

---

## 🔧 カスタマイズ

### 店舗の追加

**stores.json** に追加：

```json
{
  "id": "new_store",
  "name": "新店舗",
  "region": "東京",
  "url": "https://new-store.kappaseitai.com",
  "active": true
}
```

**コミット後、自動的に:**
1. 次回スクレイピングで新店舗も対象に
2. アプリに表示される

### スケジュールの変更

`.github/workflows/scrape.yml` を編集：

```yaml
schedule:
  - cron: '0 0 * * *'  # 毎日 9:00 JST
```

### 抽出ロジックのカスタマイズ

**scraper.py** の `extract_campaign_data()` 関数を編集：

```python
# キーワードを追加
campaign_keywords.append('新しいキーワード')

# 除外キーワードを追加
exclude_keywords.append('除外したいキーワード')
```

---

## 📊 対応店舗（58店舗）

### 関東エリア（28店舗）
**茨城県**: 牛久店、土浦店、守谷店、ひたちなか店、日立店、つくば桜店、古河店、水戸店

**栃木県**: 栃木店、宇都宮店、小山店

**千葉県**: 市川店、印西店、木更津店、松戸馬橋店

**埼玉県**: 熊谷店

**東京都**: PT麻布十番駅前整骨院、日暮里駅前店

**神奈川県**: 川崎生田店、小田原店

### 北海道・東北エリア（10店舗）
**北海道**: 旭川店、札幌西岡店、東区役所前店、帯広店

**岩手県**: 盛岡店

**宮城県**: 仙台六丁の目店、富谷店、台原店

**福島県**: 郡山店、いわき店、福島店

### 中部エリア（8店舗）
**長野県**: 松本店、長野店

**富山県**: 富山高岡店、富山店

**石川県**: 石川野々市店、金沢店

**愛知県**: 尾張旭店、豊橋店

### 近畿エリア（5店舗）
**滋賀県**: 草津店

**大阪府**: ふくしま駅前店、天神橋店

**兵庫県**: 西明石店

**奈良県**: 奈良王寺店

### 中国・四国エリア（5店舗）
**広島県**: 広島光町店、ゆめタウンみゆき店、呉駅前店、広島祇園店、ゆめタウン廿日市店

### 九州・沖縄エリア（7店舗）
**福岡県**: 福岡大手門店、北九州店、久留米店

**熊本県**: 長嶺店、熊本島崎店

**宮崎県**: 宮崎店

**鹿児島県**: 鹿児島店

**沖縄県**: 那覇店

---

## 🐛 トラブルシューティング

### データが更新されない

**原因1: ブラウザキャッシュ**
```
解決策: Command + Shift + R (Mac) または Ctrl + Shift + R (Windows)
```

**原因2: GitHub Actions が失敗**
```
確認: GitHub → Actions → 最新の実行ログを確認
解決策: エラーメッセージに従って修正
```

**原因3: スクレイピング失敗**
```
確認: ログで "データが見つかりませんでした" を確認
解決策: 店舗ウェブサイトの構造が変わった可能性 → scraper.py を調整
```

### 期限切れが表示されない

**確認事項:**
```javascript
// index.html で期限判定
const today = new Date();
const deadline = new Date(latest.deadline);

if (deadline < today) {
  // 期限切れ表示
}
```

**解決策:**
- ページをリロード
- campaign_data.json の deadline を確認

### 店舗追加が反映されない

**チェックリスト:**
1. ✅ stores.json に正しく追加されているか
2. ✅ JSON 形式が正しいか（カンマ、括弧）
3. ✅ `active: true` が設定されているか
4. ✅ GitHub にコミット・プッシュされているか
5. ✅ GitHub Actions が実行されたか

---

## 🔒 セキュリティ

### 認証情報

- ログイン情報は **localStorage** に保存
- 本番環境では適切な認証システムに置き換えることを推奨

### GitHub Token

- **repo** と **workflow** スコープのみ必要
- ブラウザの localStorage に保存
- 定期的なトークンのローテーションを推奨

### データの取り扱い

- スクレイピング対象は公開ウェブサイトのみ
- 個人情報は収集しない
- サーバー負荷軽減のため2秒間隔でリクエスト

---

## 📝 ライセンス

このプロジェクトは個人利用目的で作成されています。

---

## 🤝 貢献

バグ報告や機能リクエストは Issue でお願いします。

---

## 📮 サポート

質問や問題がある場合は、GitHub Issues をご利用ください。

---

## 🎉 更新履歴

### v2.0.0 (2026-01-29)
- ✨ stores.json による店舗管理の一元化
- ✨ インテリジェント抽出ロジック（除外キーワード対応）
- ✨ 年判定の改善（過去の日付を正しく扱う）
- ✨ 「○月○日まで」形式の優先
- 🐛 長野店のオープン日を誤取得する問題を修正
- 🐛 帯広店の年判定エラーを修正

### v1.0.0 (2026-01-28)
- 🎉 初回リリース
- ✨ 58店舗の自動スクレイピング
- ✨ GitHub Actions による自動化
- ✨ ロールベースアクセス制御
- ✨ フィルタリング・統計機能

---

**🌐 Live Demo**: https://kphayato.github.io/kappa-tracker/