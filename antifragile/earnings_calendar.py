#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报披露前瞻模块 (Earnings Disclosure Calendar) —— 前瞻式财报日程

目的
----
将本地研究标的的「财报预约披露日期」提前体现在反脆弱周盘策略报告中。
若某标的在报告日之后 N 天内（默认 7 天 = 下周窗口）披露财报，周报必须
明确列出，使读者在财报落地前就做好仓位与风控准备。

    > 例：7 月 22 日发布财报的标的，必须在 7 月 19 日的周报中写明。

数据来源优先级（遵从 AGENTS.md：不得静默编造 / 不得静默降级为模拟数据）
------------------------------------------------------------------------
  1. 本地 earnings_calendar.json —— 用户维护或自动刷新缓存，作为 source of truth
  2. 实时预约披露接口 best-effort（东方财富 / 巨潮资讯）—— 任一成功即采用，失败降级
  3. 两者皆缺 → 明确标注 ⚠️ 财报日历数据缺失，绝不编造任何日期

earnings_calendar.json 字段说明
--------------------------------
  updated_at     : 日历最后更新日期 YYYY-MM-DD
  source         : 数据来源标注（local_manual / cninfo / eastmoney / mixed）
  horizon_days   : 重点前瞻窗口（天），默认 7（覆盖"下周"）
  extended_days  : 完整前瞻窗口（天），默认 30
  stocks[]:
    code           : 交易所代码，如 600000.SH
    name           : 证券简称
    report_period  : 报告期，如 2026Q2 / 2026H1（可留空，按日期推断）
    report_type    : 报告类型，如 半年度报告 / 第三季度报告（可留空，按日期推断）
    scheduled_date : 预约披露日期 YYYY-MM-DD（null = 待更新）
    source         : 该条来源（cninfo / eastmoney / manual）
    note           : 备注（如「已预告」「待交易所排期」）

仅依赖标准库，便于 run_weekly_report.py 直接 import，无需额外依赖。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# --- Path resolution: this file lives at <root>/antifragile/earnings_calendar.py. ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = _THIS_DIR
PROJECT_ROOT = os.path.dirname(_THIS_DIR)
DEFAULT_CALENDAR_PATH = os.path.join(PROJECT_ROOT, "earnings_calendar.json")

# 中文字段星期
_WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 默认窗口
DEFAULT_HORIZON_DAYS = 7
DEFAULT_EXTENDED_DAYS = 30

# 实时接口（best-effort，失败即降级，不抛异常、不编造）
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


# --------------------------------------------------------------------------- #
# 路径 / 加载 / 保存
# --------------------------------------------------------------------------- #
def project_root() -> str:
    return PROJECT_ROOT


def default_calendar_path() -> str:
    return DEFAULT_CALENDAR_PATH


def load_calendar(path: Optional[str] = None) -> Dict:
    """读取本地财报日历 JSON；文件缺失时返回空骨架（不报错）。"""
    path = path or DEFAULT_CALENDAR_PATH
    if not os.path.exists(path):
        return {
            "updated_at": "",
            "source": "none",
            "horizon_days": DEFAULT_HORIZON_DAYS,
            "extended_days": DEFAULT_EXTENDED_DAYS,
            "stocks": [],
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("horizon_days", DEFAULT_HORIZON_DAYS)
        data.setdefault("extended_days", DEFAULT_EXTENDED_DAYS)
        data.setdefault("stocks", [])
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ⚠️ 财报日历读取失败: {e}，降级为空日历")
        return {
            "updated_at": "",
            "source": "error",
            "horizon_days": DEFAULT_HORIZON_DAYS,
            "extended_days": DEFAULT_EXTENDED_DAYS,
            "stocks": [],
        }


def save_calendar(calendar: Dict, path: Optional[str] = None) -> bool:
    """写回本地财报日历 JSON。"""
    path = path or DEFAULT_CALENDAR_PATH
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(calendar, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"  ⚠️ 财报日历写回失败: {e}")
        return False


# --------------------------------------------------------------------------- #
# 日期推断工具
# --------------------------------------------------------------------------- #
def parse_date(value: Optional[str]):
    """解析 YYYY-MM-DD / YYYYMMDD → datetime.date，失败返回 None。"""
    if not value:
        return None
    s = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _format_report_date_yyyymmdd(report_date: str) -> datetime.date:
    """report_date 可能是 YYYYMMDD（脚本内部）或 YYYY-MM-DD。"""
    d = parse_date(report_date)
    if d is None:
        # 兜底：用今天
        return datetime.now().date()
    return d


def infer_report_period(scheduled_date: str) -> str:
    """按预约披露月份推断报告期。"""
    d = parse_date(scheduled_date)
    if d is None:
        return ""
    m = d.month
    if 1 <= m <= 4:
        return "上一年年报" if m <= 4 else "一季报"
    if m <= 4:
        return "一季报"
    if m <= 8:
        return "半年度报告"
    if m <= 10:
        return "三季报"
    return "年报"


def infer_report_type(scheduled_date: str) -> str:
    """按预约披露月份推断报告类型。"""
    d = parse_date(scheduled_date)
    if d is None:
        return ""
    m = d.month
    if m <= 4:
        return "年度报告" if m == 4 else "第一季度报告"
    if m <= 8:
        return "半年度报告"
    if m <= 10:
        return "第三季度报告"
    return "年度报告"


def _weekday_cn(d) -> str:
    return _WEEKDAY_CN[d.weekday()]


# --------------------------------------------------------------------------- #
# 实时预约披露接口（best-effort）
# --------------------------------------------------------------------------- #
def fetch_live_scheduled_date(code: str) -> Optional[str]:
    """
    尝试从公开接口获取个股最新一期预约披露日期（YYYY-MM-DD）。
    失败（接口不可用 / 无数据）一律返回 None，由调用方降级到本地日历。
    绝不在此编造日期。

    Args:
        code: 带交易所后缀代码，如 600000.SH / 000001.SZ
    Returns:
        预约披露日期字符串，或 None
    """
    raw = code.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    # 候选接口（东方财富 datacenter 预约披露报表；历史 reportName 可能随版本变动）
    candidates = [
        f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_PUBLIC_BS_DATEPRE"
        f"&columns=SECURITY_CODE,SECURITY_NAME_ABBR,PRE_DATE,REPORT_DATE"
        f"&filter=(SECURITY_CODE=%22{raw}%22)&pageSize=5&source=WEB&client=WEB",
    ]
    for url in candidates:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://datacenter.eastmoney.com/",
                    "Accept": "*/*",
                },
            )
            with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as r:
                payload = json.loads(r.read().decode("utf-8"))
            if not payload.get("success"):
                continue
            rows = (payload.get("result") or {}).get("data") or []
            for row in rows:
                pre = row.get("PRE_DATE") or row.get("pre_date")
                if pre:
                    d = parse_date(str(pre))
                    if d:
                        return d.strftime("%Y-%m-%d")
        except Exception:
            # 静默失败 → 尝试下一个候选，最终返回 None
            continue
    return None


def refresh_calendar(calendar: Dict, codes: Optional[List[str]] = None) -> Dict:
    """
    对日历中 scheduled_date 为空的条目尝试实时补全；成功才写入，失败保持原样。
    返回（可能已更新的）calendar。
    """
    stocks = calendar.get("stocks", [])
    if codes:
        target = {c for c in codes}
        stocks = [s for s in stocks if s.get("code") in target]
    refreshed = 0
    for s in stocks:
        if s.get("scheduled_date"):
            continue
        live = fetch_live_scheduled_date(s.get("code", ""))
        if live:
            s["scheduled_date"] = live
            s["source"] = "live_refresh"
            refreshed += 1
    if refreshed:
        calendar["source"] = "mixed" if calendar.get("source") != "none" else "live_refresh"
        calendar["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    return calendar


# --------------------------------------------------------------------------- #
# 前瞻计算
# --------------------------------------------------------------------------- #
def get_upcoming(
    calendar: Dict,
    report_date: str,
    horizon_days: Optional[int] = None,
    extended_days: Optional[int] = None,
) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """
    计算前瞻清单。

    Returns:
        (focus, extended, overdue, pending)
        focus    : 0 <= 距报告日 <= horizon_days（下周重点）
        extended : horizon_days < 距报告日 <= extended_days（30天前瞻）
        overdue  : 距报告日 < 0（已过预约日，本期可能已披露/待核验）
        pending  : scheduled_date 为空（待更新）
    每个元素附带: code,name,report_period,report_type,scheduled_date,
                  days(距报告日),weekday(星期),note,source
    """
    horizon_days = horizon_days or calendar.get("horizon_days", DEFAULT_HORIZON_DAYS)
    extended_days = extended_days or calendar.get("extended_days", DEFAULT_EXTENDED_DAYS)
    base = _format_report_date_yyyymmdd(report_date)

    focus, extended, overdue, pending = [], [], [], []

    for s in calendar.get("stocks", []):
        code = s.get("code", "")
        name = s.get("name", code)
        sd = s.get("scheduled_date")
        if not sd:
            pending.append({
                "code": code, "name": name,
                "report_period": s.get("report_period", ""),
                "report_type": s.get("report_type", ""),
                "scheduled_date": "", "days": None, "weekday": "",
                "note": s.get("note", ""), "source": s.get("source", ""),
            })
            continue
        d = parse_date(sd)
        if d is None:
            pending.append({
                "code": code, "name": name,
                "report_period": s.get("report_period", ""),
                "report_type": s.get("report_type", ""),
                "scheduled_date": sd, "days": None, "weekday": "",
                "note": "日期格式无法解析", "source": s.get("source", ""),
            })
            continue
        days = (d - base).days
        period = s.get("report_period") or infer_report_period(sd)
        rtype = s.get("report_type") or infer_report_type(sd)
        item = {
            "code": code, "name": name,
            "report_period": period, "report_type": rtype,
            "scheduled_date": d.strftime("%Y-%m-%d"),
            "days": days, "weekday": _weekday_cn(d),
            "note": s.get("note", ""), "source": s.get("source", ""),
        }
        if days < 0:
            overdue.append(item)
        elif days <= horizon_days:
            focus.append(item)
        elif days <= extended_days:
            extended.append(item)
        # 超出 extended_days 的远端预约不列出（避免噪声）

    focus.sort(key=lambda x: x["days"])
    extended.sort(key=lambda x: x["days"])
    overdue.sort(key=lambda x: x["days"], reverse=True)
    return focus, extended, overdue, pending


# --------------------------------------------------------------------------- #
# Markdown 渲染
# --------------------------------------------------------------------------- #
_PLACEHOLDER_NOTES = ("待填写", "待更新", "待交易所排期", "示例", "待核实")


def _is_placeholder_note(note: str) -> bool:
    if not note:
        return True
    return any(note.startswith(p) or p in note for p in _PLACEHOLDER_NOTES)


def _row_focus(it: Dict) -> str:
    days = it["days"]
    if days == 0:
        countdown = "**今日披露**"
    elif days == 1:
        countdown = "**明日（1天）**"
    else:
        countdown = f"{days}天（{it.get('weekday','')}）"
    hint = ("披露前 1–2 个交易日降低该标的短线博弈仓位，防范业绩不及预期踩踏；"
            "披露后结合 EarningsMonitor 实际数据重估（详见持仓事件监控 / 塔勒布审计）。")
    note = f"｜{it['note']}" if not _is_placeholder_note(it.get("note", "")) else ""
    return (f"| {it['name']}({it['code']}) | {it.get('report_period','')} | "
            f"{it.get('report_type','')} | {it['scheduled_date']} | {countdown} "
            f"｜ {hint}{note} |")


def _row_simple(it: Dict, with_countdown: bool = True) -> str:
    if with_countdown:
        cd = f"{it['days']}天（{it.get('weekday','')}）" if it["days"] is not None else "—"
        return (f"| {it['name']}({it['code']}) | {it.get('report_period','')} | "
                f"{it['scheduled_date']} | {cd} |")
    return (f"| {it['name']}({it['code']}) | {it.get('report_period','')} | "
            f"{it['scheduled_date']} |")


def generate_section(
    report_date: str,
    calendar: Optional[Dict] = None,
    calendar_path: Optional[str] = None,
    horizon_days: Optional[int] = None,
    extended_days: Optional[int] = None,
) -> str:
    """
    生成「财报披露前瞻」章节 Markdown。

    Args:
        report_date   : 报告日 YYYYMMDD 或 YYYY-MM-DD
        calendar      : 已加载的日历 dict（优先）
        calendar_path : 日历 JSON 路径（calendar 为空时加载）
        horizon_days  : 重点窗口（默认取日历配置/7）
        extended_days : 完整窗口（默认取日历配置/30）
    Returns:
        Markdown 字符串（含 ## 一、 编号由调用方场景决定；本函数输出带子章节）
    """
    cal = calendar or load_calendar(calendar_path)
    horizon_days = horizon_days or cal.get("horizon_days", DEFAULT_HORIZON_DAYS)
    extended_days = extended_days or cal.get("extended_days", DEFAULT_EXTENDED_DAYS)
    base = _format_report_date_yyyymmdd(report_date)

    focus, extended, overdue, pending = get_upcoming(
        cal, report_date, horizon_days, extended_days
    )

    src = cal.get("source", "none")
    updated = cal.get("updated_at", "")
    if src in ("none", "error", ""):
        src_note = ("⚠️ **财报日历数据缺失**：本地 earnings_calendar.json 无有效日程，"
                    "且实时预约披露接口不可用；本报告未编造任何披露日期。"
                    "请在 earnings_calendar.json 填写本地研究标的的预约披露日。")
        live_status = "本地日历缺失 / 实时接口不可用"
    else:
        live_status = "本地日历（source=" + str(src) + ("）" if src else ")")
        if updated:
            live_status += f"，更新于 {updated}"
        src_note = f"数据源：{live_status}｜实时预约披露接口为 best-effort，失败时以本地日历为准。"

    lines = [
        f"## 财报披露前瞻（未来 {horizon_days} 天重点 + 未来 {extended_days} 天清单）",
        "",
        f"> 报告日 {base.strftime('%Y-%m-%d')}（{_weekday_cn(base)}）。"
        f"本模块将持仓股财报预约披露日**提前**列出，使财报落地前的仓位与风控准备可见。",
        f"> {src_note}",
        "",
        f"### 1.1 未来 {horizon_days} 天重点披露（下周财报预告）",
        "",
    ]

    if focus:
        lines.append("| 标的 | 报告期 | 报告类型 | 预约披露日 | 距报告日 | 披露前风控提示 |")
        lines.append("|------|--------|----------|------------|----------|----------------|")
        for it in focus:
            lines.append(_row_focus(it))
        lines.append("")
        lines.append("**📌 重点**：上表标的在未来一周内披露财报，其价格/波动率可能在披露前后放大，"
                     "下周操作决策建议已将其纳入风险控制考量。")
    else:
        lines.append(f"✅ 未来 {horizon_days} 天内无持仓股预约披露（财报空窗周）。")
    lines.append("")

    # 1.2 完整 30 天清单（不含已在重点中的）
    lines.append(f"### 1.2 未来 {extended_days} 天预约披露清单")
    lines.append("")
    combined_ext = focus + extended
    if combined_ext:
        lines.append("| 标的 | 报告期 | 预约披露日 | 倒计时 |")
        lines.append("|------|--------|------------|--------|")
        for it in combined_ext:
            lines.append(_row_simple(it, with_countdown=True))
    else:
        lines.append(f"⏳ 未来 {extended_days} 天内暂无可披露的预约日程（日历未填写或均超出窗口）。")
    lines.append("")

    # 1.3 已过期（可能已披露，待核验）/ 待更新
    lines.append("### 1.3 待更新与已过期")
    lines.append("")
    if overdue:
        lines.append("**已越过预约日（本期可能已披露，需结合 EarningsMonitor 核验实际数据）：**")
        lines.append("")
        lines.append("| 标的 | 报告期 | 预约披露日 | 状态 |")
        lines.append("|------|--------|------------|------|")
        for it in overdue:
            lines.append(f"| {it['name']}({it['code']}) | {it.get('report_period','')} | "
                         f"{it['scheduled_date']} | 已过期 {abs(it['days'])} 天，待核验实际披露 |")
        lines.append("")
    if pending:
        lines.append("**⏳ 待更新（日历中未填写预约披露日）：**")
        lines.append("")
        for it in pending:
            extra = f"（{it['note']}）" if it.get("note") else ""
            lines.append(f"- {it['name']}({it['code']}){extra}")
        lines.append("")
        lines.append("> 维护方式：编辑项目根目录 `earnings_calendar.json`，"
                     "为每只标的填写 `scheduled_date`（YYYY-MM-DD）；"
                     "亦可运行 `python earnings_calendar.py --refresh` 尝试实时补全。")
    if not overdue and not pending:
        lines.append("✅ 全部持仓股预约披露日均已填写且在窗口内或已核验。")
    lines.append("")

    return "\n".join(lines)


def generate_earnings_calendar_section(
    report_date: str,
    calendar_path: Optional[str] = None,
    horizon_days: Optional[int] = None,
    extended_days: Optional[int] = None,
) -> str:
    """
    Weekly_strategy.generate() 的接入函数。
    返回「一、财报披露前瞻」完整编号章节（含 ## 编号与子章节）。
    """
    body = generate_section(
        report_date,
        calendar_path=calendar_path,
        horizon_days=horizon_days,
        extended_days=extended_days,
    )
    # 将首行 "## 财报披露前瞻（...）" 替换为带编号的 "## 一、财报披露前瞻（...）"
    first_newline = body.find("\n")
    head = body[:first_newline]
    rest = body[first_newline:]
    head_numbered = head.replace("## 财报披露前瞻", "## 一、财报披露前瞻", 1)
    return head_numbered + rest


# --------------------------------------------------------------------------- #
# CLI：本地预览 / 刷新
# --------------------------------------------------------------------------- #
def _cli():
    import argparse
    p = argparse.ArgumentParser(description="财报披露前瞻：预览章节 / 刷新日历")
    p.add_argument("--report-date", default=datetime.now().strftime("%Y%m%d"),
                   help="报告日 YYYYMMDD（默认今天）")
    p.add_argument("--calendar", default=DEFAULT_CALENDAR_PATH, help="日历 JSON 路径")
    p.add_argument("--refresh", action="store_true",
                   help="尝试用实时接口补全 scheduled_date 为空的项并写回")
    p.add_argument("--horizon", type=int, default=None, help="重点前瞻窗口（天）")
    p.add_argument("--extended", type=int, default=None, help="完整前瞻窗口（天）")
    args = p.parse_args()

    cal = load_calendar(args.calendar)
    if args.refresh:
        cal = refresh_calendar(cal)
        save_calendar(cal, args.calendar)
        print(f"✅ 刷新完成，source={cal.get('source')}，更新于 {cal.get('updated_at')}")
    print(generate_earnings_calendar_section(
        args.report_date, calendar_path=args.calendar,
        horizon_days=args.horizon, extended_days=args.extended))


if __name__ == "__main__":
    _cli()
