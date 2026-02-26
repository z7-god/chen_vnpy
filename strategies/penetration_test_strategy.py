from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
)

class PenetrationTestStrategy(CtaTemplate):
    """
    Strategy for passing broker penetration testing.
    Performs basic operations: Buy, Sell, Cancel.
    Includes monitoring for order/cancel counts and thresholds.
    """
    author = "Chen"

    order_count_threshold = 5
    cancel_count_threshold = 3

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.test_step = 0
        self.order_count = 0
        self.cancel_count = 0

    def on_init(self):
        self.write_log("Test Strategy Init - 检查合约代码和配置")

    def on_start(self):
        self.write_log("Test Strategy Started - 连通性测试通过")
        # 步骤 1: 发送一个远端价格单用于测试撤单 (基础交易 - 撤单)
        self.send_cancel_test_order()

    def send_cancel_test_order(self):
        if self.order_count >= self.order_count_threshold:
            self.write_log(f"警告：报单总笔数 {self.order_count} 达到阈值 {self.order_count_threshold}")
            return
        
        price = 1000.0  # 远低于市场价
        self.buy(price, 1)
        self.order_count += 1
        self.test_step = 1
        self.write_log(f"基础交易 - 发送撤单测试单，价格: {price}，当前报单总数: {self.order_count}")

    def on_tick(self, tick: TickData):
        # 如果需要基于最新行情发单，可以在这里处理
        pass

    def on_order(self, order: OrderData):
        self.write_log(f"日志记录 - 报单更新: {order.vt_orderid} 状态: {order.status.value}")
        
        # 步骤 1 的撤单
        if self.test_step == 1 and order.status.value == "提交中":
            self.cancel_order(order.vt_orderid)
            self.write_log("基础交易 - 发送撤单指令")
        
        if order.status.value == "已撤销":
            self.cancel_count += 1
            self.write_log(f"异常监测 - 撤单成功，当前撤单总数: {self.cancel_count}")
            
            # 步骤 2: 发送一个立即成交单 (基础交易 - 开仓)
            if self.test_step == 1:
                self.test_step = 2
                self.send_trade_test_order()

    def send_trade_test_order(self):
        # 发送一个大概率成交的买单
        self.buy(99999.0, 1) # 高价买入确保成交
        self.order_count += 1
        self.write_log(f"基础交易 - 发送开仓成交单，当前报单总数: {self.order_count}")

    def on_trade(self, trade: TradeData):
        self.write_log(f"基础交易 - 成交更新: {trade.vt_tradeid}")
        
        # 步骤 3: 成交后立即平仓 (基础交易 - 平仓)
        if self.test_step == 2:
            self.test_step = 3
            self.sell(1000.0, 1) # 低价平仓确保成交
            self.order_count += 1
            self.write_log(f"基础交易 - 发送平仓单，当前报单总数: {self.order_count}")
        elif self.test_step == 3:
            # 步骤 4: 触发错误提示 (错误防范 - 无持仓平仓)
            self.test_step = 4
            self.sell(1000.0, 100) # 超量平仓或无仓平仓
            self.write_log("错误防范 - 尝试超量平仓以触发系统错误提示")

    def on_stop(self):
        self.write_log("应急处置 - 暂停交易功能（系统停止）")
