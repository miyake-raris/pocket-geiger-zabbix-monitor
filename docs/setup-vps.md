# VPS サーバーセットアップガイド

Zabbix Server を VPS にセットアップする手順です。

## 前提条件

- VPS サーバー（2GB RAM以上）
- Debian 11/12
- root または sudo 権限

## セットアップ手順

### 1. システム更新

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. IPv6 無効化

```bash
sudo nano /etc/sysctl.conf
```

以下を追加：

```
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
```

適用：
```bash
sudo sysctl -p
```

### 3. Zabbix インストール

```bash
# リポジトリ追加（Debian 12）
wget https://repo.zabbix.com/zabbix/7.0/debian/pool/main/z/zabbix-release/zabbix-release_7.0-2+debian12_all.deb
sudo dpkg -i zabbix-release_7.0-2+debian12_all.deb
sudo apt update

# インストール
sudo apt install -y zabbix-server-pgsql zabbix-frontend-php php8.2-pgsql zabbix-nginx-conf zabbix-sql-scripts postgresql
```

### 4. データベース作成

