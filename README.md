# delete_old_installersandboxes

A small utility for inspecting and cleaning stale macOS PackageKit InstallerSandboxes.

macOS の システムデータを謎に圧迫する一因となっている、PackageKit が残した InstallerSandboxes を調査・削除するためのツールです。
InstallerSandboxesは本来作業が終了したら自動削除されるはずのインストーラーの残骸で、これを検索して削除します。

## Features / 主な機能

- Dry-run mode
- Delete by year
- Size estimation
- Verification after deletion
- Log output
- Full Disk Access detection
- Summary before/after cleanup

- ドライラン対応
- 年指定で削除
- 容量推定
- 削除後の検証
- ログ保存
- フルディスクアクセス不足の検出
- 削除前後の容量表示

## Requirements / 動作環境

- macOS
- Python 3.7+
- sudo
管理者権限で実行してください。
- Terminal with Full Disk Access
ターミナルにフルディスクアクセスを許可してください。

## Usage / 使用方法

Preview
下記のコマンドでスキャンのみの実行ができます。初期設定では2023年以前のファイルを対象としたスキャンを行います。
```bash
sudo python3 delete_old_installersandboxes.py
```

Delete everything up to 2023
下記のように--deleteと--yearを追加することで、任意の年以前のファイルを実際に削除できます。
削除前には一旦プログラムがストップして、確認が入ります。DELETEと再度入力して進んでください。
```bash
sudo python3 delete_old_installersandboxes.py --delete --year 2023
```

## Disclaimer / 注意

Use at your own risk.

自己責任で使用してください。

## Link / リンク

https://sssssi.hatenadiary.jp/entry/2026/07/24/231643

## Update history / 更新履歴

2026/07/25 発行
