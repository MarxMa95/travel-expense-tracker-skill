# 飞书多维表格 API 调用指南

## 使用方式

本文件描述的是 **Agent 需要达到的 HTTP 行为**，不是某个特定 SDK 的绑定方式。

Agent 至少需要支持：

- 获取 Tenant Access Token
- 创建多维表 App / Table / Field
- 查询、创建、更新记录
- 为群成员授予多维表权限

如果当前平台已经内置了飞书工具，可直接映射；如果没有，就用通用 HTTP 工具访问飞书开放平台。

## 必需配置

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_BOT_OPEN_ID` 或可唯一标识 Bot 的身份字段
- 群聊 ID / Open Chat ID
- 项目管理表的 `app_token` 与 `table_id`

## 常用接口

### 1. 获取 Tenant Access Token

- Method: `POST`
- Path: `/open-apis/auth/v3/tenant_access_token/internal`

请求体：

```json
{
  "app_id": "${FEISHU_APP_ID}",
  "app_secret": "${FEISHU_APP_SECRET}"
}
```

### 2. 创建多维表记录

- Method: `POST`
- Path: `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`

字段必须符合 [schema.md](schema.md) 的定义。

### 3. 查询多维表记录

- Method: `GET`
- Path: `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- 用 filter 过滤 `消费日期`、`状态`、`付款人` 等字段

### 4. 更新多维表记录

- Method: `PUT`
- Path: `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`

### 5. 创建字段

- Method: `POST`
- Path: `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields`

`类别` 和 `状态` 应创建为单选字段，并按 [schema.md](schema.md) 中的颜色值配置选项。

### 6. 添加成员权限

- Method: `POST`
- Path: `/open-apis/drive/v1/permissions/{app_token}/members?type=bitable`

请求体示例：

```json
{
  "member_type": "openid",
  "member_id": "ou_xxx",
  "perm": "full_access"
}
```

## 记录写入约束

每次写入消费记录时至少包含：

- `商户`
- `金额`
- `币种`
- `消费时间`
- `消费日期`
- `类别`
- `付款人`
- `消费类型`

## 时间处理

- 所有时间统一视为 `Asia/Shanghai`
- `消费时间` 存毫秒时间戳
- `消费日期` 存 `yyyy/MM/dd`
- 无明确时间时，用消息发送时间
- 住宿拆分记录统一写当日 `00:00`

## 错误处理

遇到以下情况不要静默失败：

- Token 获取失败
- 权限不足
- 字段不存在或字段类型不匹配
- 记录写入成功但回查失败

每次失败都要：

1. 记录接口名和错误码
2. 回用户一个可理解的中文说明
3. 如果是可修复问题，给出下一步建议
