import sys
import os
import json
import locale
from time import sleep
from datetime import datetime

# Set locale to avoid C++ crash
try:
    locale.setlocale(locale.LC_ALL, "zh_CN.utf8")
except:
    pass

os.environ["LC_ALL"] = "zh_CN.utf8"
os.environ["LANG"] = "zh_CN.utf8"

def run_account(account_name):
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    account_dir = os.path.join(base_dir, "accounts", account_name)
    if not os.path.exists(account_dir):
        print(f"Error: Account directory {account_dir} does not exist.")
        return
    
    # 核心修复点：在导入 vnpy 之前切换目录，并确保存在 .vntrader 文件夹
    # 这样 vnpy.trader.utility 第一次加载时 Path.cwd() 就是账户目录
    os.makedirs(os.path.join(account_dir, ".vntrader"), exist_ok=True)
    os.chdir(account_dir)
    sys.path.append(base_dir) # Allow importing from parent dir (strategies)

    # 局部导入以确保 os.chdir 生效
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy_ctp import CtpGateway
    from vnpy_ctastrategy import CtaStrategyApp
    from vnpy_ctastrategy.base import EVENT_CTA_LOG
    from vnpy.trader.event import EVENT_LOG

    config_path = os.path.join(account_dir, "connect_ctp.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file {config_path} not found.")
        return

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        ctp_setting = json.load(f)

    # 2. Create engines
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    
    # 3. Add Apps and Gateways
    main_engine.add_gateway(CtpGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    
    # Import and add strategies manually to ensure they are loaded
    from strategies.double_ma_strategy import DoubleMaStrategy
    from strategies.penetration_test_strategy import PenetrationTestStrategy
    cta_engine.classes[DoubleMaStrategy.__name__] = DoubleMaStrategy
    cta_engine.classes[PenetrationTestStrategy.__name__] = PenetrationTestStrategy

    # Log listener
    def process_log_event(event):
        log = event.data
        print(f"{log.time}\t{log.msg}")

    event_engine.register(EVENT_CTA_LOG, process_log_event)
    event_engine.register(EVENT_LOG, process_log_event)

    # 4. Connect to CTP
    main_engine.connect(ctp_setting, "CTP")
    print(f"Connecting to CTP for account: {account_name}...")
    
    # Wait for connection (check if contracts are loaded)
    for i in range(30):
        sleep(1)
        contracts = main_engine.get_all_contracts()
        if contracts:
            print(f"Connected to CTP, received {len(contracts)} contracts.")
            break
    else:
        print("Connection timeout, please check your network or CTP settings.")
    
    # 5. Initialize and Start CTA Strategies
    cta_engine.init_all_strategies()
    sleep(60)  # Wait for initialization (data loading)
    cta_engine.start_all_strategies()
    print("All strategies started.")

    # Keep the process running
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        cta_engine.stop_all_strategies()
        main_engine.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_account.py <account_name>")
    else:
        run_account(sys.argv[1])
