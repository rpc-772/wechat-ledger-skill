# Notion API Example

用于 `skills/wechat_ledger/SKILL.md` 的最小写入示例。

当前 `鬆散的開支記錄 DB` 已验证可通过 `database_id` 访问，因此这里使用 `database_id` 写法。

## 1. 运行前准备

在运行环境里配置：

- `NOTION_API_KEY`
- `NOTION_DATA_SOURCE_ID`
- `NOTION_VERSION`，建议 `2025-09-03`

注意：

- 环境变量名仍保留 `NOTION_DATA_SOURCE_ID`
- 但如果目标是 `鬆散的開支記錄 DB`，它的值实际填写的是 `database_id`

## 2. 字段映射

| 记账字段 | Notion 字段 |
| --- | --- |
| `Name` | 标题列 |
| `金额` | `金額` |
| `时间` | `購買日期` |
| `分类` | `類別` |
| `备注` | `備忘` |
| `类型` | `類型` |
| `支付方式` | `支付方式` |
| `原始消息` | `原始消息` |
| `已确认` | `已確認` |

如果 `鬆散的開支記錄 DB` 还没补 `類型`、`支付方式`、`原始消息`、`已確認`，就不要把这些属性放进请求体。

## 3. 最小 `curl` 示例

把 `TITLE_PROPERTY_NAME` 替换成你数据库里的标题列属性名。

```bash
curl https://api.notion.com/v1/pages \
  -X POST \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: ${NOTION_VERSION:-2025-09-03}" \
  --data '{
    "parent": {
      "type": "database_id",
      "database_id": "'"$NOTION_DATA_SOURCE_ID"'"
    },
    "properties": {
      "TITLE_PROPERTY_NAME": {
        "title": [
          {
            "text": {
              "content": "午饭"
            }
          }
        ]
      },
      "金額": {
        "number": 32
      },
      "購買日期": {
        "date": {
          "start": "2026-03-31T12:30:00+08:00"
        }
      },
      "類別": {
        "select": {
          "name": "餐飲"
        }
      },
      "備忘": {
        "rich_text": [
          {
            "text": {
              "content": ""
            }
          }
        ]
      },
      "類型": {
        "select": {
          "name": "支出"
        }
      },
      "支付方式": {
        "select": {
          "name": "微信"
        }
      },
      "原始消息": {
        "rich_text": [
          {
            "text": {
              "content": "午饭32微信"
            }
          }
        ]
      },
      "已確認": {
        "checkbox": true
      }
    }
  }'
```

## 4. 最小 JSON Payload 示例

```json
{
  "parent": {
    "type": "database_id",
    "database_id": "${NOTION_DATA_SOURCE_ID}"
  },
  "properties": {
    "TITLE_PROPERTY_NAME": {
      "title": [
        {
          "text": {
            "content": "午饭"
          }
        }
      ]
    },
    "金額": {
      "number": 32
    },
    "購買日期": {
      "date": {
        "start": "2026-03-31T12:30:00+08:00"
      }
    },
    "類別": {
      "select": {
        "name": "餐飲"
      }
    },
    "備忘": {
      "rich_text": [
        {
          "text": {
            "content": ""
          }
        }
      ]
    },
    "類型": {
      "select": {
        "name": "支出"
      }
    },
    "支付方式": {
      "select": {
        "name": "微信"
      }
    },
    "原始消息": {
      "rich_text": [
        {
          "text": {
            "content": "午饭32微信"
          }
        }
      ]
    },
    "已確認": {
      "checkbox": true
    }
  }
}
```

## 5. 失败处理建议

- `记账失败：未配置 NOTION_API_KEY`
- `记账失败：未配置 NOTION_DATA_SOURCE_ID`
- `记账失败：Notion 字段与当前记账映射不兼容`
- `记账失败：Notion API 调用失败`

## 6. 本地脚本

已提供最小 Python 脚本：`scripts/wechat_ledger_to_notion.py:1`

只做预览：

```powershell
python .\scripts\wechat_ledger_to_notion.py --message "午饭32微信"
```

真实写入：

```powershell
python .\scripts\wechat_ledger_to_notion.py --message "午饭32微信" --write
```

脚本行为：

- 自动从当前进程环境变量或 `.env` 读取 `NOTION_API_KEY`、`NOTION_DATA_SOURCE_ID`
- 自动读取 `鬆散的開支記錄 DB` 的真实属性名
- 当前库缺少 `類型`、`支付方式`、`原始消息`、`已確認` 时，会把这些额外信息折叠进 `備忘`
