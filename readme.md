# 七牛云CDN域名证书自动更新脚本

👉 这个脚本没有做完善的异常处理机制，也没有做日志，生产环境使用可以自行优化完善，另外建议结合acme.sh自动申请证书

## 📖 使用说明

### 1. 克隆代码 / 下载脚本

将脚本下载到本地，例如目录结构如下：

```txt
project/
│── config.default.py
│── qiniu_cert_sync.py
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
requests
cryptography
python-dotenv
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
python qiniu_cert_sync.py
```

输出示例：

```bash
当前脚本版本: 1.0.0

配置文件版本: 1.0.0

开始查询 

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
0 3 * * * /usr/bin/python3 /path/to/project/qiniu_cert_sync.py >> /var/log/qiniu_cert_sync.log 2>&1
```

每天凌晨 3 点执行一次。

---
