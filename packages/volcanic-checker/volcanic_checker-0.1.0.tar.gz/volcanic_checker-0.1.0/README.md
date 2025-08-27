# Volcano Checker

火山の噴火警戒レベルをチェックするための Python モジュールです。

現在はシンプルな実装で、指定した火山名またはURLに対応する警戒レベルを取得することができます。将来的にはより機能を充実させてライブラリとして利用できる形を目指しています。

## 特徴

* 火山名から警戒レベルを取得
* URLから直接警戒レベルを取得
* BeautifulSoup を使った HTML パース
* 警戒レベルが見つからない場合は `0` を返す安全設計

## 使用方法

### 1. 必要なファイルの準備

`volcanolist.json` を用意してください。

```json
{
    "富士山": "https://www.example.com/fuji",
    "桜島": "https://www.example.com/sakurajima"
}
```

### 2. スクリプトとして実行

```bash
python volcano_checker.py
```

実行後、火山名の入力を求められます。

### 3. コード内で利用

```python
from volcano_checker import VolcanoAlertChecker

checker = VolcanoAlertChecker("./volcanolist.json")
level = checker.get_alert_level_by_name("富士山")
print(level)
```

## インストール

まだPyPIには公開していないため、ローカルで直接使用してください。将来的には以下のように pip でインストールできることを目指しています：

```bash
pip install volcano-checker
```

## 依存ライブラリ

* requests
* beautifulsoup4

インストール例：

```bash
pip install requests beautifulsoup4
```

## ライセンス

現在は開発段階のためライセンス未定。

## 今後の予定（TODO）

* 警戒レベルの国際対応（他国の火山サイト対応）
* ログ機能の追加
* エラー処理の強化と例外クラスの導入
* PyPI への公開準備
* CI/CD 対応

---

開発や改善に協力したい方は、ぜひフィードバックやプルリクエストをお寄せください。
