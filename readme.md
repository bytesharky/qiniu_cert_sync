# 七牛云CDN域名证书自动更新脚本

👉 这个脚本没有做完善的异常处理机制，也没有做日志，生产环境使用可以自行优化完善，另外建议结合acme.sh自动申请证书

## 📖 使用说明

### 1. 克隆代码 / 下载脚本

将脚本下载到本地，例如目录结构如下：

```txt
project/
│── config.default.py
│── init.py
│── qiniu-cert-sync.py
│── requirements.txt
│── .env.example
```

---

### 2. 安装依赖

请确保你使用的是 **Python 3.8+**。
安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 内容示例：

```txt
requests==2.32.5
cryptography==45.0.6
python-dotenv==1.1.1
```

---

### 3. 配置 `.env`

首先复制示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改为你自己的七牛云密钥：

```ini
QINIU_ACCESS_KEY=你的七牛云AccessKey
QINIU_SECRET_KEY=你的七牛云SecretKey
```

> ⚠️ `.env` 文件不要提交到 Git 仓库，避免泄露密钥。

---

### 4. 配置域名证书

编辑 `config.py`，设置本地证书路径和需要管理的域名：

如果不存在请自行复制 `config.default.py` 为 `config.py`，或首次运行脚本自动复制

```python
# 本地证书存放路径
CERT_PATH = "/certs"

# 域名与证书文件映射
DOMAIN_LIST = {
    "static.example.com": {
        "cert": "example.com.cer",
        "key": "example.com.key",
    }
}
```

确保 `/certs/example.com.cer` 和 `/certs/example.com.key` 文件存在。

---

### 5. 运行脚本

执行：

```bash
python qiniu-cert-sync.py
```

输出示例：

```bash
当前脚本版本: 1.0.0

配置文件版本: 1.0.0

域名列表 ['static.example.com'] 

[static.example.com] 正在查询域名配置 

[static.example.com] 当前绑定证书, certId=abcdef1234567890 

[static.example.com] 线上证书过期时间 2025-10-01 12:00:00 证书未过期 

[static.example.com] 本地证书过期时间 2026-07-01 12:00:00 证书未过期 

[static.example.com] 上传新证书成功, certId=xyz987654321

[static.example.com] 更新域名证书成功, certId=xyz987654321

[static.example.com] 删除过期证书成功, certId=abcdef1234567890
```

---

### 6. 定时任务（可选）

如果你希望定期检查并自动更新证书，可以添加到 **crontab**：

```bash
# 每天凌晨 3 点执行一次。
0 3 * * * /usr/bin/python3 /path/to/project/qiniu-cert-sync.py >> /var/log/qiniu-cert-sync.log 2>&1
```

### 7. Docker部署（可选）

1. 打包镜像

    ```bash
    docker build -t qiniu-cert-sync:latest .
    ```

2. 创建启动容器，映射出`.env`、`config.py`

    ```bash
    # 创建并启动容器
    docker run  -e TZ=Asia/Shanghai -d \
        --privileged=true \
        -v /data/docker/qiniu-cert-sync/certs:/qiniu-cert-sync/certs \
        -v /data/docker/qiniu-cert-sync/logs:/qiniu-cert-sync/logs \
        -v /data/docker/qiniu-cert-sync/config:/qiniu-cert-sync/config/ \
        --name qiniu-cert-sync qiniu-cert-sync:latest;

    # 启动容器
    docker start

    # 重启容器 
    docker restart

    # 停止容器
    docker stop
    ```

### 8. 懒人福利

   ```bash
    # 克隆仓库
    git clone https://gitee.com/bytesharky/qiniu-cert-sync.git
    
    # 为部署脚本添加运行权限
    cd qiniu-cert-sync/deploy
    chmod 755 deploy.sh

    # 运行脚本并根据引导完成部署
    ./deploy.sh

    Select language / 选择语言:
    1) 中文(Chinese)
    2) English
    Enter choice (1/2, default 1): 1
    === Qiniu Cert Sync 部署引导 ===
    请输入持久化目录地址 (默认: /data/docker/qiniu-cert-sync):
    请输入证书存放路径 (默认: /root/.acme.sh/cert):
    请输入容器名称 (默认: qiniu-cert-sync):
    请输入七牛云 AccessKey:**********
    请输入七牛云 SecretKey:**********
    环境变量写入完成:  /data/docker/qiniu-cert-sync/config/.env
    默认 crontab 已写入 /data/docker/qiniu-cert-sync/config/crontab (每天3点执行)
    正在拉取镜像...
    Using default tag: latest
    latest: Pulling from sharky/qiniu-cert-sync
    Digest: sha256:d7bad24cf30c8595fd8bd368705c7472ebafb81175f3dd15c51717a1e2b1a17d
    Status: Image is up to date for ccr.ccs.tencentyun.com/sharky/qiniu-cert-sync:latest
    ccr.ccs.tencentyun.com/sharky/qiniu-cert-sync:latest
    已存在容器，正在删除... qiniu-cert-sync
    qiniu-cert-sync
    正在启动容器...
    efacdfd75f33412b66c1159e0fa18ef19a8bb91050d850f9c7a187db23e02a39

    === 部署完成 ===
    持久化目录:  /data/docker/qiniu-cert-sync
    证书目录:  /root/.acme.sh/cert
    容器名称:  qiniu-cert-sync
    你可以用以下命令查看日志: docker logs -f qiniu-cert-sync

    请记得根据需要修改以下配置文件：
    1) /data/docker/qiniu-cert-sync/config/crontab
    2) /data/docker/qiniu-cert-sync/config/config.py

    # 或者拉取我公开的镜像手动部署
    # docker pull ccr.ccs.tencentyun.com/sharky/qiniu-cert-sync
   ```

---
