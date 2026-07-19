<div align="center">

# A-Share Antifragile Trading Loop

### 隐私优先的 A 股周度市场快照工具

先核验数据，再删除无依据叙事，让下一步判断可复核。

[English](../README.md) | [Español](README.es.md) | [简体中文](README.zh-CN.md)

<img src="../assets/readme/hero.png" alt="A-Share Antifragile Trading Loop 工作流" width="100%" />

</div>

> [!IMPORTANT]
> 本项目仅用于学习和量化研究，不自动下单，也不构成投资建议。

## 项目价值

常见周复盘容易混入陈旧新闻和主观判断。本项目先建立一个更小、更安全的闭环：

1. 运行时获取公开行情。
2. 明确标注统计时间窗口。
3. 数据缺失时直接显示不可用，不模拟价格。
4. 加入反脆弱研究约束。
5. 生成可复核、可扩展的 Markdown 快照。

## 核心能力

| 能力 | 行为 |
|---|---|
| A 股市场环境 | 上证综指、深证成指、科创 50 |
| 海外参考环境 | SPY、QQQ、VIX |
| 可配置股票列表 | 只读取 WATCH_TICKERS |
| 周度统计口径 | 最新交易周首日开盘至末日收盘 |
| 显式降级 | 数据不可用时不生成模拟值 |
| 本地输出 | 生成一份 Markdown 报告 |

## 隐私设计

- 仓库不包含默认股票列表。
- 不需要持仓数量、买入成本、账户或邮箱。
- 本地环境文件、个人配置、报告、图表、日志和导出物均由 Git 忽略。
- 生成的研究报告默认只保存在本机。

## 快速开始

~~~bash
git clone https://github.com/marqosjiang-gif/A-Share-Antifragile-Trading-Loop.git
cd A-Share-Antifragile-Trading-Loop

python3 -m venv .venv
source .venv/bin/activate
python3 run_weekly_report.py
~~~

未配置股票代码时，只生成指数环境快照。

研究自己的股票代码：

~~~bash
export WATCH_TICKERS="<六位股票代码>.SS,<六位股票代码>.SZ"
python3 run_weekly_report.py
~~~

上海市场使用 .SS，深圳市场使用 .SZ。

## 输出文件

~~~text
antifragile_weekly_YYYYMMDD.md
~~~

报告包含 A 股指数、海外参考环境、可选股票周涨跌、数据可用性和反脆弱研究约束。

## 运行逻辑

~~~mermaid
flowchart TD
    A["可选 WATCH_TICKERS"] --> B["公开实时行情接口"]
    B --> C["校验代码与时间窗口"]
    C --> D{"数据可用？"}
    D -- 否 --> E["明确标注不可用"]
    D -- 是 --> F["计算首日开盘至末日收盘"]
    E --> G["Markdown 快照"]
    F --> G
    G --> H["复核、删除无依据叙事、判断"]
~~~

## 配置

| 环境变量 | 作用 | 必需 |
|---|---|---|
| WATCH_TICKERS | 逗号分隔的 A 股代码 | 否 |
| TA_VENV | 可选 TradingAgents Python 路径 | 否 |
| TA_RUN_WEBUI_TOOLS | 可选 TradingAgents 适配器 | 否 |
| TA_CWD | 可选 TradingAgents 工作目录 | 否 |

公开核心只使用 Python 标准库。

## 验证

~~~bash
python3 -m py_compile run_weekly_report.py
python3 -m unittest test_public_snapshot -v
~~~

## 扩展原则

可以扩展 BOLL、资金流、事件核验和决策日志，但股票代码应通过配置传入，并始终保留数据来源、统计日期和降级状态。

## 开源许可

本项目使用 [MIT License](../LICENSE)。

## 免责声明

行情可能延迟、缺失或不可用。本项目不保证信号准确性、交易效果或未来收益，使用者应自行完成研究并承担决策责任。
