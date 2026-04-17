#!/usr/bin/env python3
"""
住宿消费拆分计算。

Usage:
    python split_accommodation.py <total_amount> <check_in> <check_out>

Args:
    total_amount: 住宿总金额
    check_in: 入住日期 (YYYY-MM-DD)
    check_out: 离店日期 (YYYY-MM-DD)

Returns JSON:
{
    "nights": int,
    "per_night": float,
    "records": [
        {"date": "YYYY-MM-DD", "amount": float},
        ...
    ]
}
"""

import sys
import json
from datetime import datetime, timedelta

def split_accommodation(total_amount: float, check_in: str, check_out: str) -> dict:
    """
    按入住天数拆分住宿费用。
    """
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

    nights = (check_out_date - check_in_date).days
    if nights <= 0:
        raise ValueError("离店日期必须晚于入住日期")

    per_night = round(total_amount / nights, 2)

    records = []
    allocated = 0.0
    for i in range(nights):
        night_date = check_in_date + timedelta(days=i)
        amount = per_night if i < nights - 1 else round(total_amount - allocated, 2)
        allocated += amount
        records.append({
            "date": night_date.strftime("%Y-%m-%d"),
            "amount": amount
        })

    return {
        "nights": nights,
        "per_night": per_night,
        "records": records
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python split_accommodation.py <total_amount> <check_in> <check_out>", file=sys.stderr)
        sys.exit(1)

    total_amount = float(sys.argv[1])
    check_in = sys.argv[2]
    check_out = sys.argv[3]

    result = split_accommodation(total_amount, check_in, check_out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
