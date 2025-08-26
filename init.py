import os
import shutil

def init_config():
    # 获取脚本所在目录的绝对路径
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
    DEFAULT_CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.default.py")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.py")
    INIT_FILE = os.path.join(CONFIG_DIR, "__init__.py")

    if not os.path.exists(INIT_FILE):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(INIT_FILE, "w") as f:
            f.write("# This package contains configuration\n")

    # 如果本地 config.py 不存在，则自动生成
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(DEFAULT_CONFIG_FILE):
            shutil.copy(DEFAULT_CONFIG_FILE, CONFIG_FILE)
            print(f"生成 {CONFIG_FILE} 成功", "\n")
        else:
            raise FileNotFoundError(f"{DEFAULT_CONFIG_FILE} 不存在")
