#!/usr/bin/env python3
"""
格式化旅行记账日报。

Usage:
    python format_report.py <json_data>

Input JSON:
{
    "project_name": str,
    "start_date": str,
    "end_date": str,
    "destination": str,
    "today": str,
    "today_total": float,
    "today_count": int,
    "payer_distribution": {"付款人": 金额, ...},
    "expense_type_distribution": {"公共AA": 金额, "个人消费": 金额},
    "category_distribution": {"类别": {"amount": 金额, "percentage": 百分比}, ...},
    "today_records": [{"merchant": str, "amount": float, "category": str, "expense_type": str, "payer": str}, ...],
    "project_total": float,
    "days_passed": int,
    "days_remaining": int,
    "daily_avg": float,
    "payer_stats": {"付款人": {"amount": 金额, "percentage": 百分比}, ...},
    "table_url": str
}

Returns formatted text report.
"""

import sys
import json

def format_currency(amount: float) -> str:
    return f"¥{amount:,.2f}"

def format_report(data: dict) -> str:
    """
    生成格式化的日报文本。
    """
    lines = [
        f"📊 **旅行记账日报 - {data['project_name']}** （{data['today']}）",
        "",
        "**📅 项目周期**",
        f"• 开始日期：{data['start_date']}",
        f"• 结束日期：{data['end_date']}",
        f"• 旅行目的地：{data['destination']}",
        "• 项目状态：进行中 ✅",
        "",
        "**📅 今日消费总览**",
        f"• 消费日期：{data['today']}",
        f"• 总消费：**{format_currency(data['today_total'])}**",
        f"• 消费笔数：{data['today_count']}",
    ]

    # 付款人分布
    payer_dist = data.get('payer_distribution', {})
    if payer_dist:
        payer_str = ", ".join([f"{k}:{format_currency(v)}" for k, v in payer_dist.items()])
        lines.append(f"• 付款人分布：{payer_str}")

    # 消费类型分布
    type_dist = data.get('expense_type_distribution', {})
    if type_dist:
        type_str = " / ".join([f"{k}:{format_currency(v)}" for k, v in type_dist.items()])
        lines.append(f"• 消费类型分布：{type_str}")

    lines.append("")
    lines.append("**📂 今日类别分布**")

    # 类别分布
    cat_dist = data.get('category_distribution', {})
    for cat, info in cat_dist.items():
        lines.append(f"• {cat}: {format_currency(info['amount'])} ({info['percentage']}%)")

    if not cat_dist:
        lines.append("• 今日无消费记录")

    lines.append("")
    lines.append("**📝 今日消费明细**")

    # 消费明细
    records = data.get('today_records', [])
    if records:
        for i, r in enumerate(records, 1):
            lines.append(f"{i}. {r['merchant']} {format_currency(r['amount'])} {r['category']} {r['expense_type']} {r['payer']}")
    else:
        lines.append("（今日无消费记录）")

    lines.append("")
    lines.append("**📊 项目累计统计**")
    lines.append(f"• 项目总花费：{format_currency(data['project_total'])}")
    lines.append(f"• 项目已过天数：{data['days_passed']}天")
    lines.append(f"• 项目剩余天数：{data['days_remaining']}天")
    lines.append(f"• 项目日均花费：{format_currency(data['daily_avg'])}/天")

    lines.append("")
    lines.append("**💰 各付款人付款明细（项目累计）**")

    # 累计付款人统计
    payer_stats = data.get('payer_stats', {})
    for payer, info in payer_stats.items():
        lines.append(f"• {payer}：{format_currency(info['amount'])}（占比 {info['percentage']}%）")

    lines.append("")
    lines.append(f"**📒 项目账本：** {data['table_url']}")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python format_report.py '<json_data>'", file=sys.stderr)
        sys.exit(1)

    data = json.loads(sys.argv[1])
    report = format_report(data)
    print(report)
