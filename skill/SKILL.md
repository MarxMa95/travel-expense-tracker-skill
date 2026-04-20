---
name: travel-expense-tracker
description: >
  给具备飞书消息、HTTP、图片理解和定时任务能力的 Agent 使用的旅行记账 skill。
  Use when: (1) 需要在飞书群中管理旅行项目和消费记录, (2) 需要把截图或文字消费写入飞书多维表格,
  (3) 需要按业务规则拆分住宿费用, (4) 需要生成并发送旅行记账日报,
  (5) 需要把 OpenClaw 类 agent 接到飞书 Bot + 多维表格上作为开箱即用能力。
---

# 旅行记账 Agent Skill

把这个 skill 视为一个 **面向 Agent 的运行契约**，而不是产品说明书。它假设 Agent 已经具备以下能力：

- 能接收飞书群消息、附件和成员信息
- 能发起 HTTP 请求并保存少量配置
- 能读取图片并用视觉模型输出结构化 JSON
- 能创建定时任务
- 能向飞书群回消息

如果当前 Agent 缺少上述任一能力，不要假装可用；先告知用户缺失项。

## 何时使用

在以下场景触发本 skill：

- 用户说“记一笔旅行消费”“发票/支付截图帮我记账”
- 用户要创建或切换旅行项目
- 用户要求发送旅行记账日报
- 用户要修改今天或最近一笔旅行消费记录
- 用户要求把群聊消费自动同步到飞书多维表格

## 运行前提

在真正执行写入前，Agent 必须确认这 5 个前提：

1. 已有飞书 Bot 凭证，且可调用飞书开放平台 API
2. 已有项目管理表，或用户允许创建项目管理表
3. 当前群聊已有一个进行中项目，或用户愿意创建/指定项目
4. Bot 对目标多维表具有读写权限
5. Agent 时区固定使用 `Asia/Shanghai`

缺任何一项时，先补配置，不要直接进入记账流程。

## 必需工具映射

把下列能力映射到你所在 Agent 平台的实际工具名；如果平台工具名不同也没关系，但语义必须一致。

- 表格与飞书 API：见 [references/api_guide.md](references/api_guide.md)
- 数据结构：见 [references/schema.md](references/schema.md)
- 业务规则：见 [references/business_rules.md](references/business_rules.md)
- 工具契约：见 [references/tool_contracts.md](references/tool_contracts.md)

最小必需能力：

- `http_request`：调用飞书开放平台 API
- `download_file`：下载飞书消息里的图片到本地临时路径
- `vision_extract`：从消费截图抽取结构化 JSON
- `schedule_job`：创建 22:00 日报和 00:00 项目状态更新任务
- `send_group_message`：向飞书群发送确认、追问和日报
- `kv_get` / `kv_set`：保存 app token、table id、群与项目映射等轻量配置

## 输出规范

### 截图识别输出

视觉模型必须输出 `ExpenseExtraction` 结构，字段见 [references/tool_contracts.md](references/tool_contracts.md)。

然后运行：

```bash
python scripts/recognize_expense.py '<raw_json>'
```

该脚本只做 **标准化和校验**，不负责真正 OCR。Agent 必须先用自己的视觉能力得到 JSON，再交给脚本处理。

### 住宿拆分输出

```bash
python scripts/split_accommodation.py <total_amount> <check_in> <check_out>
```

### 日报格式化输出

```bash
python scripts/format_report.py '<json_data>'
```

## 主流程

### 流程 1：初始化项目与表结构

当用户首次启用旅行记账时：

1. 创建或确认“项目管理表”存在
2. 创建消费明细表，并按 [references/schema.md](references/schema.md) 建字段
3. 为目标群成员开启 `full_access`
4. 保存 `group_chat_id -> project_record_id -> app_token/table_id` 映射
5. 创建两个定时任务：22:00 日报、00:00 状态刷新

如果表已存在，只校验字段，不重复创建。

### 流程 2：处理消费截图

1. 下载图片
2. 用视觉模型提取 JSON
3. 用 `scripts/recognize_expense.py` 标准化结果
4. 如果状态是“交易关闭 / 已取消 / 已退款 / 未支付”，直接回消息说明不入账
5. 根据群聊和日期确定当前项目
6. 如果是住宿，走“流程 4：住宿拆分”
7. 如果有缺失字段，向发图者追问，拿到补充信息后再写入
8. 写入消费明细表
9. 在群里返回确认消息

### 流程 3：处理文字记账

支持这三类输入：

- `商户 金额`
- `类别 金额 商户`
- 带时间描述的自由文本，例如“昨天午饭 128 海底捞”

Agent 需要把文字解析成与截图同一份标准结构，然后复用截图流程后半段。

### 流程 4：住宿拆分

满足任一条件时判定为住宿：

- 类别明确为“住宿”
- 截图里出现入住 / 离店 / 酒店 / 民宿 / 晚数等强信号

处理规则：

1. 必须拿到入住日期和离店日期
2. 调用 `scripts/split_accommodation.py`
3. 为每晚各写一条“住宿”记录
4. 每条记录的消费时间固定为当天 `00:00`
5. 若入住/离店缺失，先 `@` 用户追问，不落表

### 流程 5：修改记录

当用户说“时间改为 19:20”“金额改为 88”“上一笔改成个人消费”时：

1. 优先定位当前群、当前项目、最近一笔相关记录
2. 如果歧义超过 1 条，列出候选让用户选
3. 只更新用户明确指定的字段
4. 更新后回发变更摘要

### 流程 6：发送日报

每天 22:00 对所有“进行中”项目执行：

1. 查询今日记录
2. 计算今日总额、类别分布、付款人分布、累计统计
3. 组装 `format_report.py` 所需 JSON
4. 运行脚本生成日报文本
5. 发回对应群聊

### 流程 7：项目状态刷新

每天 00:00：

1. 读取项目管理表全部项目
2. 按以下原则判断项目状态：
   - `开始时间 <= 当前时间 <= 结束时间`：项目状态 = `进行中`
   - `当前时间 < 开始时间`：项目状态 = `未开始`
   - `当前时间 > 结束时间`：项目状态 = `已结束`
3. 仅在状态变化时写回

## 决策规则

- 没有进行中项目：先提示用户创建或指定项目
- 同时存在多个进行中项目：优先使用当前群绑定项目；若仍冲突，向用户确认
- 无明确消费时间：使用消息发送时间
- 无明确币种：默认 `CNY`
- 无明确消费类型：默认 `公共 AA`
- 识别结果缺 2 个以上核心字段：不要写表，改为追问
- 金额无法解析为正数：拒绝入账并说明原因

## 追问策略

以下情况必须追问，而不是猜测：

- 无法确定商户
- 无法确定金额
- 住宿缺入住或离店日期
- 无法确定记录应属于哪个项目
- 用户要求修改记录，但匹配到多条候选

追问要尽量一次问全，例如：

- `@用户 这笔看起来是住宿消费，请补充入住日期和离店日期。`
- `@用户 当前有两个进行中的旅行项目：日本游、首尔游。这笔要记到哪个项目？`

## 实施要求

- 所有飞书写操作都必须走 Bot 身份
- 所有写表前都先做字段级校验
- 所有时间戳都按 `Asia/Shanghai` 转成毫秒时间戳
- 所有失败都返回用户可理解的消息，不只返回异常堆栈
- 不要把真实 Token、Webhook、群 ID 写进 skill 文件

## 读取哪些引用文件

- 实际创建/更新多维表时，读取 [references/api_guide.md](references/api_guide.md)
- 判断字段和表结构时，读取 [references/schema.md](references/schema.md)
- 判断是否应追问、过滤或拆分时，读取 [references/business_rules.md](references/business_rules.md)
- 需要对接 Agent 工具层时，读取 [references/tool_contracts.md](references/tool_contracts.md)
