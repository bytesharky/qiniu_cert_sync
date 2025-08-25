# config.py
import os
from dotenv import load_dotenv

# 读取 .env 文件
load_dotenv()

# 从环境变量读取七牛云密钥
ACCESS_KEY = os.getenv("QINIU_ACCESS_KEY", "")
SECRET_KEY = os.getenv("QINIU_SECRET_KEY", "")

# 配置文件版本
VER = "1.0.0"

# 强制更新
FORCE = False

# 删除过期证书
DEL_EXP = True

# 七牛云 API 地址
QINIU_API = "https://api.qiniu.com"

# 证书存放路径
CERT_PATH = "/certs"
DOMAIN_LIST = {
    "static.example.com":{
        "cert":"example.com.cer",
        "key":"example.com.key",
    }
}
