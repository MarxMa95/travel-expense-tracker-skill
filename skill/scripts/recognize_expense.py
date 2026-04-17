#!/usr/bin/env python3
"""
标准化视觉模型输出的旅行消费识别结果。

Usage:
    python recognize_expense.py '<raw_json>'
    python recognize_expense.py /path/to/raw.json

The agent should first use its own vision capability to extract a JSON object,
then pass that JSON into this script for normalization and validation.
"""

import json
import os
import sys
from datetime import datetime

VALID_CATEGORIES = {"餐饮", "交通", "住宿", "门票", "购物", "娱乐", "其他"}
VALID_EXPENSE_TYPES = {"公共 AA", "个人消费"}
IGNORED_STATUSES = {"交易关闭", "已取消", "已退款", "未支付"}


def load_payload(value: str) -> dict:
    if os.path.exists(value):
        with open(value, "r", encoding="utf-8") as file:
            return json.load(file)
    return json.loads(value)


def normalize_datetime(value):
    if not value:
        return None
    text = str(value).strip().replace("T", " ")
    text = text.replace("/", "-")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            if fmt == "%Y-%m-%d":
                return parsed.strftime("%Y-%m-%d 00:00")
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return text


def normalize_date(value):
    if not value:
        return None
    text = str(value).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def normalize_amount(value):
    if value is None or value == "":
        return None
    text = str(value).strip().replace("¥", "").replace(",", "")
    return round(float(text), 2)


def normalize_category(value):
    if not value:
        return None
    text = str(value).strip()
    if text in VALID_CATEGORIES:
        return text
    fuzzy_map = {
        "餐费": "餐饮",
        "吃饭": "餐饮",
        "打车": "交通",
        "酒店": "住宿",
        "机票": "交通",
        "景点": "门票",
    }
    return fuzzy_map.get(text, text)


def normalize_expense_type(value):
    if not value:
        return "公共 AA"
    text = str(value).strip()
    if text in VALID_EXPENSE_TYPES:
        return text
    if text in {"AA", "公共", "公共AA"}:
        return "公共 AA"
    if text in {"个人", "个人付款", "个人消费"}:
        return "个人消费"
    return text


def normalize_status(value):
    if not value:
        return None
    return str(value).strip()


def standardize(payload: dict) -> dict:
    warnings = []
    missing_fields = []

    normalized = {
        "amount": normalize_amount(payload.get("amount")),
        "currency": str(payload.get("currency") or "CNY").strip().upper(),
        "merchant": (str(payload.get("merchant")).strip() if payload.get("merchant") else None),
        "expense_time": normalize_datetime(payload.get("expense_time")),
        "category": normalize_category(payload.get("category")),
        "transaction_status": normalize_status(payload.get("transaction_status")),
        "expense_type": normalize_expense_type(payload.get("expense_type")),
        "check_in": normalize_date(payload.get("check_in")),
        "check_out": normalize_date(payload.get("check_out")),
        "notes": (str(payload.get("notes")).strip() if payload.get("notes") else None),
    }

    for field in ("amount", "merchant", "expense_time", "category"):
        if normalized[field] in (None, ""):
            missing_fields.append(field)

    amount = normalized["amount"]
    if amount is not None and amount <= 0:
        warnings.append("amount_must_be_positive")

    if normalized["category"] and normalized["category"] not in VALID_CATEGORIES:
        warnings.append("unknown_category")

    if normalized["expense_type"] not in VALID_EXPENSE_TYPES:
        warnings.append("unknown_expense_type")

    status = normalized["transaction_status"]
    if status in IGNORED_STATUSES:
        warnings.append("ignored_transaction_status")

    if normalized["category"] == "住宿":
        if not normalized["check_in"]:
            missing_fields.append("check_in")
        if not normalized["check_out"]:
            missing_fields.append("check_out")

    return {
        "ok": len([item for item in warnings if item in {"amount_must_be_positive", "unknown_category"}]) == 0,
        "normalized": normalized,
        "missing_fields": sorted(set(missing_fields)),
        "warnings": warnings,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recognize_expense.py '<raw_json>'", file=sys.stderr)
        sys.exit(1)

    raw = load_payload(sys.argv[1])
    result = standardize(raw)
    print(json.dumps(result, ensure_ascii=False, indent=2))
