# Agent 工具契约

本文件定义的是 skill 对宿主 Agent 的最低能力要求。

## 最小工具集

### `http_request`

用于调用飞书开放平台 API。

输入至少包含：

- `method`
- `url` 或 `path`
- `headers`
- `json` / `body`

输出至少包含：

- `status_code`
- `body`
- `headers`

### `download_file`

从飞书消息附件 URL 下载图片到临时路径。

输出必须提供：

- `local_path`
- `content_type`

### `vision_extract`

对消费截图执行视觉理解，输出一个 JSON 对象。必须尽量贴近如下 schema：

```json
{
  "amount": 128.0,
  "currency": "CNY",
  "merchant": "海底捞",
  "expense_time": "2026-04-17 18:30",
  "category": "餐饮",
  "transaction_status": "交易成功",
  "expense_type": "公共 AA",
  "check_in": null,
  "check_out": null,
  "notes": "可选备注"
}
```

要求：

- `amount` 可转成正数
- `category` 只能是 `餐饮/交通/住宿/门票/购物/娱乐/其他`
- `expense_type` 只能是 `公共 AA/个人消费`
- 住宿类尽量抽取 `check_in` 和 `check_out`

### `schedule_job`

用于创建定时任务：

- `0 22 * * *`：发送日报
- `0 0 * * *`：更新项目状态

### `send_group_message`

向飞书群发送普通文本消息或带 `@` 的提示。

### `kv_get` / `kv_set`

用于保存：

- 项目管理表位置
- 群聊与项目绑定关系
- 已创建的定时任务 ID

## 标准化脚本约定

### `scripts/recognize_expense.py`

输入：视觉模型的原始 JSON 字符串。

输出：

```json
{
  "ok": true,
  "normalized": {
    "amount": 128.0,
    "currency": "CNY",
    "merchant": "海底捞",
    "expense_time": "2026-04-17 18:30",
    "category": "餐饮",
    "transaction_status": "交易成功",
    "expense_type": "公共 AA",
    "check_in": null,
    "check_out": null,
    "notes": null
  },
  "missing_fields": [],
  "warnings": []
}
```

如果字段缺失或非法，`ok` 仍可为 `true`，但必须在 `missing_fields` 或 `warnings` 中明确指出，便于 Agent 决定是否追问。
