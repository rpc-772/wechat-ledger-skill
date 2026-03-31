# WeChat Ledger Skill

最小可用的“微信一句话记账 -> Notion” skill 包。

适合把仓库上传到 GitHub，再交给运行在手机或其他设备上的 ClawBot / skill 导入器使用。

## 目录

- `skills/wechat_ledger/SKILL.md`：skill 规则定义
- `skills/wechat_ledger/agents/openai.yaml`：skill 元数据
- `skills/wechat_ledger/scripts/run.py`：skill 本地入口
- `scripts/wechat_ledger_to_notion.py`：实际解析与 Notion 写入脚本
- `.env.example`：环境变量示例
- `NOTION_TEMPLATE.md`：Notion 字段说明
- `NOTION_API_EXAMPLE.md`：Notion API 示例

## 功能

处理这类短中文记账消息：

- `午饭32微信`
- `打车18支付宝`
- `咖啡26`
- `工资+12000`
- `报销300`

成功写入后只返回一行：

- `已记：{Name} / {金额} / {支付方式或未填}`

## 运行依赖

- Python 3.10+
- 无第三方依赖

## 环境变量

需要以下配置：

- `NOTION_API_KEY`
- `NOTION_DATA_SOURCE_ID`
- `NOTION_VERSION=2025-09-03`
- `LEDGER_API_TOKEN`（可选，给你的 API 加一层 Bearer 鉴权）

注意：

- 当前示例默认对接 `鬆散的開支記錄 DB`
- `NOTION_DATA_SOURCE_ID` 对这个库来说实际填写的是 `database_id`

## 当前默认 Notion 库

- 库名：`鬆散的開支記錄 DB`
- 已验证可访问的数据库 ID 示例：`fcb01619-c5f3-825e-830a-01eeaeff9dad`

## 本地调用

预览解析：

```powershell
python .\skills\wechat_ledger\scripts\run.py --message "午饭32微信"
```

真实写入：

```powershell
python .\skills\wechat_ledger\scripts\run.py --message "午饭32微信" --write
```

## HTTP API 部署

如果 ClawBot 不能执行本地脚本，推荐部署这个最小 API：

- 入口文件：`api/main.py`
- 依赖文件：`requirements.txt`
- Render 一键配置：`render.yaml`

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

启动服务：

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
curl http://127.0.0.1:8000/health
```

记账请求：

```powershell
curl http://127.0.0.1:8000/wechat-ledger ^
  -X POST ^
  -H "Authorization: Bearer your_api_token" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"午饭32微信\"}"
```

返回格式：

```json
{
  "ok": true,
  "reply": "已记：午饭 / 32.0 / 微信",
  "page_id": "..."
}
```

### Render 最短部署

这个仓库已经带了 `render.yaml`，适合直接从 GitHub 部署到 Render。

步骤：

1. 把仓库推到 GitHub
2. 打开 Render 控制台
3. 选择 `Blueprint` 或 `New +` -> `Blueprint`
4. 连接你的 GitHub 仓库
5. Render 会自动识别 `render.yaml`
6. 在环境变量里填真实值：
   - `NOTION_API_KEY`
   - `LEDGER_API_TOKEN`
7. 部署完成后，先访问：
   - `/health`
8. 再用 `POST /wechat-ledger` 测试

## 上传 GitHub 时建议保留

必须保留：

- `api/main.py`
- `skills/wechat_ledger/`
- `scripts/wechat_ledger_to_notion.py`
- `requirements.txt`
- `.env.example`
- `NOTION_TEMPLATE.md`
- `NOTION_API_EXAMPLE.md`
- `README.md`

不要上传：

- `.env`

## 接入说明

如果目标平台支持按仓库导入 skill：

1. 上传本仓库到 GitHub
2. 把仓库链接发给目标平台
3. 目标平台导入 `skills/wechat_ledger/SKILL.md`
4. 在运行环境中配置 `NOTION_API_KEY` 和 `NOTION_DATA_SOURCE_ID`

如果目标平台只支持粘贴 skill 内容：

1. 粘贴 `skills/wechat_ledger/SKILL.md`
2. 同时说明它依赖：
   - `skills/wechat_ledger/scripts/run.py`
   - `scripts/wechat_ledger_to_notion.py`

## 当前限制

当前 `鬆散的開支記錄 DB` 已存在这些字段：

- `項目名稱`
- `金額`
- `購買日期`
- `類別`
- `備忘`

如果库里还没有这些字段：

- `類型`
- `支付方式`
- `原始消息`
- `已確認`

脚本会先把额外信息折叠进 `備忘`，保证最小流程可用。
