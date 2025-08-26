FROM python:3.9-alpine

# 升级Alpine系统包以修复已知漏洞
RUN apk update && apk upgrade --no-cache

WORKDIR /qiniu_cert_sync

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制任务脚本和配置
COPY .env.example .
COPY config.default.py .
COPY init.py .
COPY qiniu_cert_sync.py .
COPY crontab.txt .
COPY start.sh .

# 设置脚本运行权限
RUN chmod 777 ./start.sh

# 启动脚本：Alpine的cron需要显式指定日志输出
CMD ["./start.sh"]
