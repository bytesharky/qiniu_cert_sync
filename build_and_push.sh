#!/bin/sh
set -e

if [ -z "$1" ]; then
  echo "用法: $0 <TAG>"
  exit 1
fi

TAG=$1
IMAGE_NAME=sharky/qiniu-cert-sync
REGISTRY=ccr.ccs.tencentyun.com

echo ">>> 构建镜像: $IMAGE_NAME:$TAG"
docker build -t $IMAGE_NAME:$TAG .

echo ">>> 打标签..."
docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:$TAG
docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:latest

echo ">>> 推送镜像..."
docker push $REGISTRY/$IMAGE_NAME:$TAG
docker push $REGISTRY/$IMAGE_NAME:latest

echo ">>> 完成"
