# A股中低频量化研究循环

面向 A 股周度复盘的证据优先研究工作流：先量化一周数据，再排除不可靠信息，最后只在规则一致时形成条件式决策。

[English](../README.md) | [Español](README.es.md) | [简体中文](README.zh-CN.md)

> 仅用于量化研究和决策辅助，不接券商、不下单，不构成投资建议。

## 它解决什么问题

日内噪声、陈旧新闻和事后回测很容易把周度决策带偏。本项目把中低频研究固化为可检查的顺序：

1. 以本周首个实际开盘到最后实际收盘计算周度表现。
2. 先核对价格、成交量、时间戳和信源一致性。
3. 硬门槛通过后，历史 BOLL 证据优先，再看量价、5/10/20日资金、公司披露和宏观环境。
4. 没有日期与可复核来源的叙事，不能成为交易理由。
5. 复盘只能使用报告 `evidence_cutoff` 前公开的信息；之后披露的是新事件，不得倒灌为原报告失误。

## 快速开始

```bash
git clone https://github.com/marqosjiang-gif/A-Share-Antifragile-Trading-Loop.git
cd A-Share-Antifragile-Trading-Loop
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

cp watchlist.example.json watchlist.local.json
python3 quant_loop.py --watchlist watchlist.local.json
```

请只在 `watchlist.local.json` 中配置自己的研究代码和显示名。该文件已被 Git 忽略；不要填写持仓数量、成本、账户或密钥。

## 公开版包含什么

- 周度时间口径与可执行回测边界
- BOLL、量价、资金流、公告和宏观信息的证据优先级
- `Via Negativa` 去除未验证叙事
- `report_generated_at`、`evidence_cutoff`、下周验证窗口的审计字段
- 只沉淀跨周复现规则的进化闭环

详细规则见 [`PUBLIC_PROTOCOL.md`](../PUBLIC_PROTOCOL.md)。

## 边界

生成的周度文件只是一份研究脚手架，默认状态是 `research_only`。真实交易判断必须由使用者补充当期、可验证的数据和自身风险约束。请勿向公开仓库提交个人自选股、持仓、成本、报告、缓存、邮箱、令牌或 API Key。

## 许可

[MIT License](../LICENSE)
