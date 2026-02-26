# 期货交易项目 (基于 vn.py)

## 项目结构
- `accounts/`: 包含每个账户的子目录。
  - `account_name/connect_ctp.json`: 账户的 CTP 连接设置。
- `strategies/`: 自定义 CTA 策略。
- `run_account.py`: 在独立进程中运行特定账户的主脚本。
- `rollover_tool.py`: 手动或自动合约展期的工具。
- `logs/`: 集中日志 (可选，每个账户在其目录下有自己的日志)。

## 账户隔离
运行多个账户时，启动独立的进程：
```bash
python3 run_account.py account1
python3 run_account.py account2
```
每个账户将在其目录下拥有自己的 `vt_setting.json`、`cta_strategy_data.json` 和日志文件，确保完全隔离。

## 穿透测试
要通过穿透测试 (例如广发期货)：
1.  **配置**: 在 `connect_ctp.json` 中填写 `产品名称` (AppID)、`授权码` (AuthCode) 和 `产品信息`。
2.  **终端 ID**: `vnpy_ctp` 会自动收集并向经纪商发送所需的终端信息 (IP、MAC 等)。
3.  **测试流程**:
    - 连接到经纪商的模拟环境。
    - 使用 `PenetrationTestStrategy` 执行基本操作：买入、卖出、撤单。
    - 经纪商将验证终端信息是否被正确报告。
4.  **日志**: 确保 `temp` 目录可写。日志对于调试和合规至关重要。

## 展期
使用 `rollover_tool.py` 将持仓从到期合约转移到新合约。
示例：
```python
from rollover_tool import RolloverTool
from vnpy.trader.constant import Exchange

tool = RolloverTool("my_account")
tool.connect()
tool.rollover("rb2405", "rb2410", Exchange.SHFE)
tool.close()
```

## 安装
确保你已安装 `vnpy` 和 `vnpy_ctp`：
```bash
pip3 install vnpy vnpy_ctp vnpy_ctastrategy
