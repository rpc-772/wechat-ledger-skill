# Notion Ledger Template

用于 `skills/wechat_ledger/SKILL.md` 的 Notion 接入说明。

当前优先方案：复用现成模板中的 `鬆散的開支記錄 DB`。

## 1. 环境变量

- `NOTION_API_KEY`
- `NOTION_DATA_SOURCE_ID`
- `NOTION_VERSION`，建议 `2025-09-03`

注意：

- 环境变量名仍使用 `NOTION_DATA_SOURCE_ID`
- 但对于当前已验证的 `鬆散的開支記錄 DB`，这里实际填写的是它的 `database_id`

当前已确认可访问的数据库 ID：

- `fcb01619-c5f3-825e-830a-01eeaeff9dad`

实际请求结构可参考 `NOTION_API_EXAMPLE.md:1`。

## 2. 优先方案：`鬆散的開支記錄 DB`

建议把 `NOTION_DATA_SOURCE_ID` 直接设为 `鬆散的開支記錄 DB` 的 `database_id`。

### 建议字段映射

| 记账字段 | Notion 字段 |
| --- | --- |
| `Name` | 标题列 |
| `金额` | `金額` |
| `时间` | `購買日期` |
| `分类` | `類別` |
| `备注` | `備忘` |

### 建议最小补充字段

| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| `類型` | Select | `支出` / `收入` |
| `支付方式` | Select | `微信` / `支付寶` / `銀行卡` / `現金` |
| `原始消息` | Rich text | 保存用户原始微信消息 |
| `已確認` | Checkbox | 成功写入后设为 `true` |

## 3. 备用方案：最小自建模板

如果你不复用现成模板，可新建一个表格数据库，并创建以下属性：

| 属性名 | 类型 |
| --- | --- |
| `Name` | Title |
| `金额` | Number |
| `类型` | Select |
| `分类` | Select |
| `支付方式` | Select |
| `时间` | Date |
| `备注` | Rich text |
| `原始消息` | Rich text |
| `已确认` | Checkbox |

## 4. 最小接入约定

- 缺少 `NOTION_API_KEY`：返回 `记账失败：未配置 NOTION_API_KEY`
- 缺少 `NOTION_DATA_SOURCE_ID`：返回 `记账失败：未配置 NOTION_DATA_SOURCE_ID`
- 没有可用的 Notion 写入能力：返回 `记账失败：当前环境没有可用的 Notion 写入能力`
- 字段不兼容：返回 `记账失败：Notion 字段与当前记账映射不兼容`
- 成功写入后只返回：`已记：{Name} / {金额} / {支付方式或未填}`
