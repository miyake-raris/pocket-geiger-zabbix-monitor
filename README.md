# Pocket Geiger Type-6 Zabbix Monitor

Pocket Geiger Type-6 を Raspberry Pi に接続し、Zabbix で放射線量をモニタリングするシステムです。

## 🌟 特徴

- **リアルタイムモニタリング**: 1秒、3秒、10秒、30秒の移動平均でCPM値を取得
- **ノイズ補正**: Single/Random/True counts を分離して記録
- **Tailscale VPN**: プライベートネットワーク経由で安全にデータ収集
- **systemd サービス**: 自動起動・自動再起動に対応

## 📊 測定データ

- **Counts Single**: 放射線+ノイズ
- **Counts Random**: ノイズのみ
- **Counts True**: 実際の放射線 (Single - Random)

各カウントは1秒、3秒、10秒、30秒の移動平均で記録されます。

## 🛠️ システム構成

### クライアント側 (Raspberry Pi)
- **Pocket Geiger Type-6**: USB接続で放射線を検出
- **pocketgeiger_service.py**: シリアルデータを読み取り `/var/lib/pocketgeiger/data.json` に出力
- **Zabbix Agent 2**: JSON ファイルを読み取り、VPS に送信
- **Tailscale**: プライベート VPN で VPS と接続

### サーバー側 (VPS)
- **Zabbix Server**: Raspberry Pi からデータを受信・保存
- **Nginx**: Zabbix Web UI を提供
- **PostgreSQL**: データベース
- **Tailscale**: プライベート VPN でクライアントと接続

### 通信フロー
Pocket Geiger → (USB) → Raspberry Pi → (Tailscale VPN) → VPS → Zabbix Web UI

## 📋 必要なもの

### ハードウェア
- Pocket Geiger Type-6 (Radiation Watch)
- Raspberry Pi (2以降推奨)
- VPS サーバー (Debian推奨)

### ソフトウェア
- Debian 11/12 (VPS)
- Raspberry Pi OS (Client)
- Zabbix Server 7.0+
- Zabbix Agent 2
- Tailscale
- Python 3.7+

## 🚀 セットアップ

### 1. VPS サーバー

詳細は [docs/setup-vps.md](docs/setup-vps.md) を参照してください。

### 2. クライアント (Raspberry Pi)

詳細は [docs/setup-client.md](docs/setup-client.md) を参照してください。

#### クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/あなたのユーザー名/pocket-geiger-zabbix-monitor.git
cd pocket-geiger-zabbix-monitor

# インストールスクリプトを実行
sudo bash scripts/install-client.sh
```

### 3. Zabbix Template のインポート

1. Zabbix Web UI にログイン
2. **Configuration** → **Templates** → **Import**
3. \`zabbix/pocketgeiger_templates.yaml\` をアップロード
4. ホストに "Pocket Geiger Type6" テンプレートをリンク

## 📈 グラフの見方

- **緑線 (Random)**: ノイズ成分
- **青線 (Single)**: 全カウント
- **赤線 (True)**: 実際の放射線 (Single - Random)

## 🔧 トラブルシューティング

### データが取得できない

```bash
sudo systemctl status pocketgeiger.service
sudo journalctl -u pocketgeiger.service -f
ls -l /dev/ttyPG
```

### Zabbix で値が 0 になる

```bash
zabbix_agent2 -t pocketgeiger.signal[signal_1s]
ls -l /var/lib/pocketgeiger/data.json
```

## 📄 ライセンス

MIT License

## 👤 作者

miyake@lns.tohoku.ac.jp

## 🙏 謝辞

- [Radiation Watch](https://www.radiation-watch.co.jp/) - Pocket Geiger Type-6
- [Zabbix](https://www.zabbix.com/)
- [Tailscale](https://tailscale.com/)
