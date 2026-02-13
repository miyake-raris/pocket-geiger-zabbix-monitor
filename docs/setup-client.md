
markdown

# クライアント（Raspberry Pi）セットアップガイド

Pocket Geiger Type-6 を接続した Raspberry Pi のセットアップ手順です。

## 前提条件

- Raspberry Pi 2以降
- Raspberry Pi OS（64-bit推奨）
- Pocket Geiger Type-6
- インターネット接続

## セットアップ手順

### 1. OS インストール

Raspberry Pi Imager でOSをインストール。

- OS: Raspberry Pi OS (64-bit)
- ホスト名: `radipi`
- SSH有効化

### 2. システム更新

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. パッケージインストール

```bash
sudo apt install -y zabbix-agent2 jq python3-serial minicom git
```

### 4. Tailscale セットアップ

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

認証URLをブラウザで開いて認証。

Tailscale IP確認：

```bash
tailscale ip -4
```

### 5. USB デバイス固定

Pocket Geiger を接続して確認：

```bash
lsusb
ID 04d8:f46f Microchip Technology, Inc. PocketGeiger Type-6 CDC が表示されることを確認。
```

udev ルール作成：

```bash
sudo nano /etc/udev/rules.d/99-usb-pgeiger.rules
```

以下を記述：

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="f46f", SYMLINK+="ttyPG"
```

保存して適用：

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -l /dev/ttyPG
```

### 6. 動作テスト

```bash
minicom -D /dev/ttyPG -b 38400
```

S キーで測定開始
データ表示を確認（例: >123,45）
E キーで停止
Ctrl+A → X で終了

### 7. リポジトリクローン

```bash
cd ~
git clone https://github.com/miyake-raris/pocket-geiger-zabbix-monitor.git
cd pocket-geiger-zabbix-monitor
```

### 8. Pocket Geiger サービスインストール

```bash
sudo cp client/pocketgeiger_service.py /usr/local/bin/
sudo chmod +x /usr/local/bin/pocketgeiger_service.py
sudo cp client/pocketgeiger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pocketgeiger.service
sudo systemctl start pocketgeiger.service
```

状態確認：

```bash
sudo systemctl status pocketgeiger.service
9. データ確認

```bash
cat /var/lib/pocketgeiger/data.json
```

JSON形式でデータが表示されればOK：

```json
{"timestamp": 1234567890, "samples": 300, "signal_30s": 0.12, ...}
```

### 10. Zabbix Agent 2 設定

```bash
sudo cp client/pocketgeiger.conf /etc/zabbix/zabbix_agent2.d/
sudo nano /etc/zabbix/zabbix_agent2.conf
```

以下を設定（VPSのTailscale IPに変更）：

```
Server=100.x.x.x
ServerActive=100.x.x.x
Hostname=radipi
```

保存して再起動：

```bash
sudo systemctl restart zabbix-agent2
sudo systemctl enable zabbix-agent2
```

### 11. 動作確認
```bash
zabbix_agent2 -t pocketgeiger.signal[signal_1s]
zabbix_agent2 -t pocketgeiger.signal[signal_30s]
zabbix_agent2 -t pocketgeiger.uptime
```

値が返ってくればOK。

### 12. Zabbix Server 側の設定

Zabbix Web UI で：

```
Configuration → Hosts → Create host
Host name: radipi
Groups: Linux servers
Interfaces: Agent, IP: 100.x.x.x（RaspberryPiのTailscale IP）, Port: 10050
```

Templates タブで Pocket Geiger Type6 をリンク
数分後、Monitoring → Hosts で radipi の Availability が緑色（ZBX）になることを確認。

### トラブルシューティング

サービスが起動しない
```bash
sudo journalctl -u pocketgeiger.service -n 50
ls -l /dev/ttyPG
```

データが取得できない
bash
sudo systemctl restart pocketgeiger.service
sudo journalctl -u pocketgeiger.service -f
```

Zabbix Agent が接続できない
```bash
sudo tail -f /var/log/zabbix/zabbix_agent2.log
telnet 100.x.x.x 10051
```

値が 0 になる
```bash
ls -l /var/lib/pocketgeiger/data.json
jq -r '.signal_30s // 0' /var/lib/pocketgeiger/data.json
zabbix_agent2 -t pocketgeiger.signal[signal_1s]
```

### 便利なコマンド
```bash
# サービス状態
sudo systemctl status pocketgeiger.service

# データ表示
cat /var/lib/pocketgeiger/data.json | jq

# ログリアルタイム
sudo journalctl -u pocketgeiger.service -f

# Tailscale 状態
tailscale status
```

### 設定更新
```bash
cd ~/pocket-geiger-zabbix-monitor
git pull origin main
sudo cp client/pocketgeiger_service.py /usr/local/bin/
sudo systemctl restart pocketgeiger.service
```
