#!/bin/bash
set -e

# ===== Language selection =====
echo "Select language / 选择语言:"
echo "1) 中文(Chinese)"
echo "2) English"
read -p "Enter choice (1/2, default 1): " LANG_CHOICE
LANG_CHOICE=${LANG_CHOICE:-1}

if [ "$LANG_CHOICE" = "1" ]; then
  source "$(dirname "$0")/lang/zh.sh"
else
  source "$(dirname "$0")/lang/en.sh"
fi

echo "$MSG_TITLE"

# ===== persistent dir =====
read -p "$MSG_PERSISTENT" DATA_DIR
DATA_DIR=${DATA_DIR:-/data/docker/qiniu_cert_sync}

# ===== cert dir =====
if [ -L "$DATA_DIR/certs" ]; then
    CERT_DEFAULT_DIR=$(readlink "$DATA_DIR/certs")
else
    CERT_DEFAULT_DIR="/root/.acme.sh/cert"
fi

read -p "$MSG_CERT [$CERT_DEFAULT_DIR]: " CERT_DIR
CERT_DIR=${CERT_DIR:=$CERT_DEFAULT_DIR}

# ===== container name =====
read -p "$MSG_CONTAINER" CONTAINER_NAME
CONTAINER_NAME=${CONTAINER_NAME:-qiniu_cert_sync}

# ===== create directories =====
mkdir -p "$DATA_DIR" "$DATA_DIR/config" "$DATA_DIR/logs"
if [ -d "$DATA_DIR/certs" ] || [ -f "$DATA_DIR/certs" ]; then
    rm -rf "$DATA_DIR/certs"
fi
ln -s "$CERT_DIR" "$DATA_DIR/certs"

# ===== .env file check =====
ENV_FILE="$DATA_DIR/config/.env"

if [[ -f "$ENV_FILE" ]]; then
    read -p "$MSG_ENV_EXISTS" OVERWRITE_ENV
    OVERWRITE_ENV=${OVERWRITE_ENV:-N}
else
    OVERWRITE_ENV=Y
fi

if [[ "$OVERWRITE_ENV" =~ ^[Yy]$ ]]; then
    read -p "$MSG_AK" QINIU_ACCESS_KEY
    read -s -p "$MSG_SK" QINIU_SECRET_KEY
    echo ""
    cat > "$ENV_FILE" <<EOF
QINIU_ACCESS_KEY=$QINIU_ACCESS_KEY
QINIU_SECRET_KEY=$QINIU_SECRET_KEY
EOF
    echo "$MSG_ENV $ENV_FILE"
fi

# ===== write default crontab =====
CRONTAB_FILE="$DATA_DIR/config/crontab"
if [ -f "$CRONTAB_FILE" ]; then
    read -p "$MSG_CRON_EXISTS" OVERWRITE_CRON
    OVERWRITE_CRON=${OVERWRITE_CRON:-N}
else
    OVERWRITE_CRON=Y
fi

if [[ "$OVERWRITE_CRON" =~ ^[Yy]$ ]]; then
    cat > "$CRONTAB_FILE" <<EOF
# Default crontab for Qiniu Cert Sync
0 3 * * * python /qiniu_cert_sync/qiniu_cert_sync.py >> /qiniu_cert_sync/logs/qiniu_cert_sync.log 2>&1
EOF
    printf "$MSG_CRON_WRITTEN\n" "$CRONTAB_FILE"
fi

# ===== pull image =====
echo "$MSG_PULL"
docker pull ccr.ccs.tencentyun.com/sharky/qiniu_cert_sync

# ===== remove old container =====
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
  echo "$MSG_EXIST $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME"
fi

# ===== run container =====
echo "$MSG_START"
docker run -d \
    -e TZ=Asia/Shanghai \
    --privileged=true \
    -v "$DATA_DIR/certs:/qiniu_cert_sync/certs" \
    -v "$DATA_DIR/logs:/qiniu_cert_sync/logs" \
    -v "$DATA_DIR/config:/qiniu_cert_sync/config" \
    --name "$CONTAINER_NAME" \
    ccr.ccs.tencentyun.com/sharky/qiniu_cert_sync

# ===== summary =====
echo ""
echo "$MSG_DONE"
echo "$MSG_SUMMARY_PERSISTENT $DATA_DIR"
echo "$MSG_SUMMARY_CERT $CERT_DIR"
echo "$MSG_SUMMARY_CONTAINER $CONTAINER_NAME"
echo "$MSG_LOGS $CONTAINER_NAME"

# ===== reminder to edit config files =====
echo ""
echo "$MSG_REMIND_CONFIG"
printf "$MSG_REMIND_CRONTAB\n" "$DATA_DIR"
printf "$MSG_REMIND_CONFIGPY\n" "$DATA_DIR"
echo ""
