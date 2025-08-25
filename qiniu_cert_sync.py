import os
import os
import shutil

CONFIG_FILE = "config.py"
DEFAULT_CONFIG_FILE = "config.default.py"

# 如果本地 config.py 不存在，则自动生成
if not os.path.exists(CONFIG_FILE):
    if os.path.exists(DEFAULT_CONFIG_FILE):
        shutil.copy(DEFAULT_CONFIG_FILE, CONFIG_FILE)
        print(f"生成 {CONFIG_FILE} 成功", "\n")
    else:
        raise FileNotFoundError(f"{DEFAULT_CONFIG_FILE} 不存在")

import time
import hmac
import requests
import config
from hashlib import sha1
from datetime import datetime
from datetime import timezone
from cryptography import x509
from base64 import urlsafe_b64encode
from cryptography.hazmat.backends import default_backend

# ----------------- 工具函数 -----------------

def utf8(data):
    if isinstance(data, str):
        return data.encode('utf-8')
    return data

def qiniu_sign(path):
    """
    生成 QBox AccessToken
    """
    secret_key = utf8(config.SECRET_KEY)
    path = utf8(''.join([path,'\n']))
    hashed = hmac.new(secret_key, path, sha1)
    token = urlsafe_b64encode(hashed.digest())
    decoded = token.decode('utf-8')
    return f"QBox {config.ACCESS_KEY}:{decoded}"


def get_local_cert_expiry(cert_path: str) -> datetime:
    """
    解析本地证书过期时间 (PEM 格式)
    """
    with open(cert_path, "rb") as f:
        cert_data = f.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    expiry_time = getattr(cert, "not_valid_after_utc", None)
    if expiry_time is None:
        expiry_time = cert.not_valid_after.replace(tzinfo=timezone.utc)
    return int(expiry_time.timestamp())


def qiniu_request(method, path, data=None):
    """
    封装七牛 API 请求
    """
    url = config.QINIU_API + path
    headers = {
        "Content-Type": "application/json",
        "Authorization": qiniu_sign(path)
    }
    resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code >= 300:
        print(f"Qiniu API Error: {resp.status_code}, {resp.text}", "\n")
        
    return resp.json() if resp.text else {}

def timestamp_to_readable(timestamp):
    """
    将时间戳转换为可读的日期时间格式
    """
    if not timestamp:
        return ""
    try:
        local_time = time.localtime(int(timestamp))
        return time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    except (ValueError, TypeError):
        return str(timestamp)
    
# ----------------- 七牛证书操作 -----------------


def list_domain():
    """
    获取域名列表
    """
    path = "/domain"
    return qiniu_request("GET", path)

def list_cert():
    """
    获取证书列表
    """
    path = "/sslcert"
    return qiniu_request("GET", path)

def get_domain_conf(domain: str):
    """
    获取域名绑定的配置 (包括 certId)
    """
    path = f"/domain/{domain}"
    return qiniu_request("GET", path)


def get_cert(cert_id: str):
    """
    获取证书
    """
    path = f"/sslcert/{cert_id}"
    return qiniu_request("GET", path)


def upload_cert(domain: str, cert_pem_path: str, key_pem_path: str):
    """
    上传证书
    需要七牛账号开通「证书托管」功能
    """
    with open(cert_pem_path, "r") as f:
        cert_pem = f.read()
    with open(key_pem_path, "r") as f:
        key_pem = f.read()
                
    path = "/sslcert"
    data = {
        "name": f"{domain}-{datetime.now().strftime('%Y%m%d')}",
        'common_name': domain,
        "pri": key_pem,
        "ca": cert_pem
    }
    return qiniu_request("POST", path, data)


def delete_cert(cert_id: str):
    """
    删除证书
    """
    path = f"/sslcert/{cert_id}"
    return qiniu_request("DELETE", path)


def update_domain_cert(domain: str, cert_id: str):
    """
    修改域名证书配置
    """
    path = f"/domain/{domain}/httpsconf"
    data = {
        "certId": cert_id,
        "forceHttps": True,
        "http2Enable": True
    }
    return qiniu_request("PUT", path, data)


# ----------------- 主逻辑 -----------------

def sync_cert():

    # 1.获取域名列表
    print("开始查询","\n")
    
    domain_data = list_domain()
    domains = []
    for index, domain in enumerate(domain_data['domains'], start=1):
        # 提取所需字段，处理可能的缺失值
        domain = domain.get('name', '')
        if domain:
            domains.append(domain)

    print("域名列表", domains,"\n")
        
    for domain in domains:

        print(f"[{domain}] 正在查询域名配置","\n")

        # 2.获取域名绑定的证书ID
        domain_conf = get_domain_conf(domain)
        https_conf = domain_conf.get("https")
        cert_id = https_conf.get("certId")
        print(f"[{domain}] 当前绑定证书, certId={cert_id}","\n")

        # 3.获取远程证书的过期时间
        cert_info = get_cert(cert_id)
        cert_info = cert_info.get('cert')
        not_after = cert_info.get('not_after')
        current_time = time.time()
        is_expire = current_time >= not_after
        status = "证书已经过期" if is_expire else "证书未过期"
        print(f"[{domain}] 线上证书过期时间", timestamp_to_readable(not_after), status, "\n")
        
        # 4.获取本地证书的过期时间
        if domain in config.DOMAIN_LIST:
            local_cert = config.DOMAIN_LIST.get(domain)
            cert_pem = local_cert.get("cert")
            key_pem = local_cert.get("key")
            cert_pem_full = os.path.join(config.CERT_PATH, cert_pem)
            cert_key_full = os.path.join(config.CERT_PATH, key_pem)
            if os.path.isfile(cert_pem_full):
                local_not_after = get_local_cert_expiry(cert_pem_full)
                local_is_expire = current_time >= local_not_after
                local_status = "证书已过期" if local_is_expire else "证书未过期"
                print(f"[{domain}] 本地证书过期时间", timestamp_to_readable(local_not_after), local_status, "\n")
            else:
                print(f"[{domain}] 本地证书文件不存在", "\n")
                continue
        else:
            print(f"[{domain}] 未发现本地证书", "\n")
            continue
        
        # 5.上传本地证书到七牛云
        if not local_is_expire:
            if (local_not_after > not_after) or config.FORCE:
                uploaded = upload_cert(domain, cert_pem_full, cert_key_full)
                new_cert_id = uploaded.get('certID')
                print(f"[{domain}] 上传新证书成功, certId={new_cert_id}", "\n")
            else:
                print(f"[{domain}] 不需要更新证书", "\n")
                continue
        else:
            print(f"[{domain}] 本地证书已经过期", "\n")
            continue
        
        # 6.更新域名绑定证书
        updateed = update_domain_cert(domain, new_cert_id)
        succeed = updateed.get("code") == 200
        if succeed:
            print(f"[{domain}] 更新域名证书成功, certId={new_cert_id}", "\n")
        else:
            print(f"[{domain}] 更新域名证书失败", updateed.get("error"), "\n")
        
    # 7.删除过期的证书
    if config.DEL_EXP:
        certs = list_cert()
        certs = certs.get("certs", [])
        for cert in certs:
            cert_id = cert.get("certid")
            domain = cert.get("common_name")
            not_after = cert_info.get('not_after')
            current_time = time.time()
            is_expire = current_time >= not_after
            if is_expire:
                deleteed = delete_cert(cert_id)
                if deleteed.get("code") == 200:
                    print(f"[{domain}] 删除过期证书成功, certId={cert_id}", "\n")
                else:
                    print(f"[{domain}] 删除过期证书失败, certId={cert_id}", deleteed.get("error"), "\n")
            else:
                print(f"[{domain}] 证书未过期, certId={cert_id}", "\n")
# ----------------- 示例运行 -----------------

if __name__ == "__main__":
    VER = "1.0.0"
    CFGS = ["1.0.0"]
    print(f"当前脚本版本: {VER}", "\n")
    print(f"配置文件版本: {config.VER}", "\n")
    if config.VER not in CFGS:
        print(f"当前配置文件版本不兼容，兼容的配置文件版本: {CFGS}", "\n")
        exit(1)

    sync_cert()
    print("已退出")
