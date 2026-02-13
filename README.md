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
#### 2.1 Zabbix Agent と Tailscale のインストール
```bash
sudo apt update
sudo apt install zabbix-agent2 jq -y
# Tailscale インストール
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
