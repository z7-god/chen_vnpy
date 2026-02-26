import os
import sys
import shutil

def init_account(account_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    account_dir = os.path.join(base_dir, "accounts", account_name)
    
    if os.path.exists(account_dir):
        print(f"Account {account_name} already exists.")
        return

    os.makedirs(account_dir)
    
    # 核心：创建 .vntrader 标记文件，使 vn.py 识别该目录为配置根目录
    os.makedirs(os.path.join(account_dir, ".vntrader"), exist_ok=True)
    
    # Copy CTP config template
    template_path = os.path.join(base_dir, "accounts", "connect_ctp_template.json")
    target_path = os.path.join(account_dir, "connect_ctp.json")
    shutil.copy(template_path, target_path)
    
    # Copy Strategy config template
    strategy_template_path = os.path.join(base_dir, "accounts", "cta_strategy_setting_template.json")
    strategy_target_path = os.path.join(account_dir, "cta_strategy_setting.json")
    shutil.copy(strategy_template_path, strategy_target_path)

    print(f"Account {account_name} initialized at {account_dir}")
    print(f"Please edit {target_path} and {strategy_target_path} with your settings.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init_account.py <account_name>")
    else:
        init_account(sys.argv[1])
