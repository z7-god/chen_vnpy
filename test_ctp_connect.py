import os
import json
from time import sleep
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp import CtpGateway
from vnpy.trader.event import EVENT_LOG

def test_connect():
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)

    def process_log_event(event):
        log = event.data
        print(f"LOG: {log.msg}")

    event_engine.register(EVENT_LOG, process_log_event)

    with open("/root/project/chen_vnpy/accounts/simnow_std/connect_ctp.json", "r") as f:
        setting = json.load(f)

    main_engine.connect(setting, "CTP")
    print("Connecting...")
    
    for i in range(30):
        sleep(1)
        # Check if connected
        # main_engine.get_gateway("CTP") ...
    
    main_engine.close()

if __name__ == "__main__":
    test_connect()
