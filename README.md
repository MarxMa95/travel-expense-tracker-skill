# Travel Expense Tracker Skill

An open-source travel expense tracking skill for OpenClaw-like agents running in Feishu groups.

它是一个面向 Agent 的 Skill，不是完整的服务端应用。只要宿主 Agent 具备飞书消息接入、HTTP、图片理解、定时任务和少量 KV 存储能力，就可以把这个 Skill 接进去，在飞书群里实现：

- 消费截图识别并自动记账
- 文字记账
- 住宿费用按晚拆分
- 飞书多维表格存储
- 每日日报推送
- 旅行项目状态自动更新

## Features

- Screenshot-to-expense workflow for travel receipts and payment screenshots
- Structured text expense entry from natural-language messages
- Accommodation splitting by stay nights
- Feishu Bitable-backed storage model
- Daily digest generation for active trips
- Agent-oriented tool contracts and runtime assumptions

## Who This Is For

This repository is for people who already have an agent runtime and want to add a reusable travel-expense-tracking skill on top of it.

Typical host environments include:

- OpenClaw-like agents
- Feishu bot agents with tool calling
- LLM agents with HTTP + vision + scheduling capabilities

## What’s Inside

This repository separates GitHub-facing project files from the runtime skill package:

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── examples/
├── scripts/
│   └── package_skill.sh
└── skill/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
```

- `skill/SKILL.md`: the main agent contract and workflow definition
- `skill/references/`: schema, API guidance, business rules, and tool contracts
- `skill/scripts/`: reusable helper scripts for normalization, splitting, and reporting
- `scripts/package_skill.sh`: packages the runtime files into a `.skill` archive

## Runtime Requirements

Your host agent should provide at least these capabilities:

- `http_request`
- `download_file`
- `vision_extract`
- `schedule_job`
- `send_group_message`
- `kv_get` / `kv_set`

See `skill/references/tool_contracts.md` for the exact contract.

## Feishu Requirements

You need:

- a Feishu app with `app_id` and `app_secret`
- a bot identity that can send group messages
- permission to read and write Feishu Bitable
- a target chat/group where the skill will run

## Local Examples

Normalize raw vision output:

```bash
python3 skill/scripts/recognize_expense.py examples/sample_expense_raw.json
```

Split accommodation costs:

```bash
python3 skill/scripts/split_accommodation.py 1500 2026-04-20 2026-04-23
```

Render a daily report:

```bash
python3 skill/scripts/format_report.py "$(cat examples/sample_report.json)"
```

## Package the Skill

```bash
bash scripts/package_skill.sh
```

This creates:

```text
dist/travel-expense-tracker.skill
```

## Open Source Notes

Before publishing, make sure:

- no real tokens, secrets, webhook URLs, chat IDs, or user IDs are committed
- all examples are sanitized
- production environment config stays outside the repository
- the host agent maps the tool contracts in `skill/references/tool_contracts.md`

## Non-Official Project

This is a community-maintained project and is not an official Feishu product.
