import json
import os
from time import sleep
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import OrderType, Direction, Offset
from vnpy.trader.object import OrderRequest
from vnpy_ctp import CtpGateway

class RolloverTool:
    def __init__(self, account_name):
        self.account_name = account_name
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        self.main_engine.add_gateway(CtpGateway)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "accounts", account_name, "connect_ctp.json")
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.ctp_setting = json.load(f)

    def connect(self):
        self.main_engine.connect(self.ctp_setting, "CTP")
        print(f"Connecting to CTP for rollover: {self.account_name}")
        sleep(10)

    def rollover(self, old_symbol, new_symbol, exchange):
        """
        Simple rollover: close old, open new.
        """
        old_vt_symbol = f"{old_symbol}.{exchange.value}"
        new_vt_symbol = f"{new_symbol}.{exchange.value}"
        
        # 1. Get current position
        pos = self.main_engine.get_position(f"{old_vt_symbol}.CTP")
        if not pos or pos.volume == 0:
            print(f"No position found for {old_vt_symbol}")
            return

        volume = pos.volume
        direction = pos.direction
        
        print(f"Rolling over {volume} lots of {old_vt_symbol} to {new_vt_symbol}")

        # 2. Close old position
        close_direction = Direction.SHORT if direction == Direction.LONG else Direction.LONG
        close_req = OrderRequest(
            symbol=old_symbol,
            exchange=exchange,
            direction=close_direction,
            type=OrderType.MARKET,
            volume=volume,
            offset=Offset.CLOSE,
            reference="RolloverClose"
        )
        self.main_engine.send_order(close_req, "CTP")
        
        # 3. Open new position
        open_req = OrderRequest(
            symbol=new_symbol,
            exchange=exchange,
            direction=direction,
            type=OrderType.MARKET,
            volume=volume,
            offset=Offset.OPEN,
            reference="RolloverOpen"
        )
        self.main_engine.send_order(open_req, "CTP")
        
        print("Rollover orders sent.")

    def close(self):
        self.main_engine.close()

if __name__ == "__main__":
    # Example usage
    # tool = RolloverTool("account1")
    # tool.connect()
    # tool.rollover("rb2405", "rb2410", Exchange.SHFE)
    # tool.close()
    pass
