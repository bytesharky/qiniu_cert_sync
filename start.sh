#!/bin/sh
set -e

# 创建目录，存在就忽略
mkdir -p /qiniu_cert_sync/config
mkdir -p /qiniu_cert_sync/logs

# 复制文件，如果目标不存在才复制
ENV_TARGET=/qiniu_cert_sync/config/.env
CONFIG_TARGET=/qiniu_cert_sync/config/config.py
CRONTAB_TARGET=/qiniu_cert_sync/config/crontab
[ ! -f "$ENV_TARGET" ] && cp /qiniu_cert_sync/.env.example "$ENV_TARGET"
[ ! -f "$CONFIG_TARGET" ] && cp /qiniu_cert_sync/config.default.py "$CONFIG_TARGET"
[ ! -f "$CRONTAB_TARGET" ] && cp /qiniu_cert_sync/crontab.txt "$CRONTAB_TARGET"

# 创建软链接 /etc/crontabs/root 指向 CRONTAB_TARGET
ln -sf "$CRONTAB_TARGET" /etc/crontabs/root

# 启动 crond 前台运行
exec crond -f -l 2
