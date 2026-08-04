<p align="center">
  <img src="https://www.zotero.org/support/_media/icons/zotero_icon.png" width="96" alt="Zotero 图标"/>
</p>

<h1 align="center">Zotero Literature Workflow</h1>

<p align="center">
  基于 <a href="https://www.zotero.org/support/dev/web_api/v3/start">Zotero Web API v3</a> 的只读文献工具，为 <a href="https://opencode.ai">OpenCode</a> 提供以证据为先的文献综述能力。
</p>

<p align="center">
  <a href="#安装"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/></a>
  <a href="https://github.com/thovet55/zotero-literature-workflow/actions"><img src="https://img.shields.io/github/actions/workflow/status/thovet55/zotero-literature-workflow/test.yml" alt="CI 状态"/></a>
</p>

<p align="center">
  <a href="./README.md">English</a> | <strong>简体中文</strong>
</p>

无需 Zotero 桌面客户端、本地数据库或手动上传 PDF。只需一个只读 API key——客户端直接对接 Zotero Web API，key 永远不会泄露。

## 特性

- **只读设计**——仅暴露 `search_items`、`get_item`、`get_children`、`get_fulltext` 和 `get_pdf_text`，不存在任何写入工具。
- **PDF 文本提取**——下载已同步的 PDF 附件，通过 [pypdf](https://github.com/py-pdf/pypdf) 提取正文文本。
- **默认安全**——API key 通过 `Zotero-API-Key` 请求头传递，绝不进入 URL；密钥存放于本地 `.env`（已被 git 忽略、永不提交）。
- **MCP 就绪**——以 [MCP](https://modelcontextprotocol.io) 服务器形式发布，OpenCode 智能体可直接查询你的文献库。
- **懒加载配置**——即使没有凭据，服务器也能正常启动；仅在实际调用工具时才报清晰的 `ZOTERO_API_KEY is required` 错误。
- **证据优先工作流**——配套 `literature-review` 技能，强制提供引文上下文证据，并对仅基于元数据的结论进行降级标注。

## 安装

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,mcp,pdf]'
cp .env.example .env
chmod 600 .env
```

### 获取 API key

1. 登录 [zotero.org](https://www.zotero.org)，打开 **Settings → Security → API Keys**（[直达链接](https://www.zotero.org/settings/keys)）。
2. 点击 **Create new private key**，只授予目标库的**只读**权限。
3. 复制 key，并记下**数字 UserID**（同页面显示 "Your userID for use in API calls is …"）。

填写 `.env`：

```text
ZOTERO_API_KEY=你的-key
ZOTERO_LIBRARY_ID=你的数字用户ID
ZOTERO_LIBRARY_TYPE=user
```

切勿把 key 发到聊天、日志或 issue 中。若泄露，请到 Zotero Settings 吊销并重新创建。

## 验证

```bash
zotero-workflow check          # 读取 1 条，仅打印脱敏后的 key
zotero-workflow search "moire" # 搜索你的文献库
```

`check` 输出 `{"ok": true, ...}` 即代表凭据可用。

## OpenCode MCP 接入

在 OpenCode 配置（`~/.config/opencode/opencode.json` 或项目级 `opencode.json`）中添加本地 MCP 服务器。结构见 [`opencode.example.jsonc`](./opencode.example.jsonc)：

```jsonc
{
  "mcp": {
    "zotero-literature": {
      "type": "local",
      "command": ["/绝对路径/zotero-literature-workflow/.venv/bin/zotero-workflow-mcp"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "ZOTERO_DOTENV": "/绝对路径/zotero-literature-workflow/.env",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    }
  }
}
```

MCP 进程通过 `ZOTERO_DOTENV` 环境变量（绝对路径）读取 `.env`，不依赖 OpenCode 的工作目录。修改配置后重启 OpenCode；每次会话都会启动全新的只读 MCP 进程。

### 工具列表

| 工具 | 说明 |
| --- | --- |
| `search_items` | 搜索文献库（支持关键词、条数、偏移量） |
| `get_item` | 获取单条条目的元数据与摘要 |
| `get_children` | 获取子条目（PDF、笔记、批注） |
| `get_fulltext` | 从 Zotero 检索索引读取全文 |
| `get_pdf_text` | 下载已同步的 PDF 附件并提取文本 |

## 文献综述技能

[`skills/literature-review/SKILL.md`](./skills/literature-review/SKILL.md) 定义了证据优先的综述协议：每条引用必须给出上下文证据，记录文本来源（Zotero 索引或已同步 PDF），并将仅基于元数据的结论标注为低置信度。

## 开发

```bash
pytest -q
python -m compileall -q src
```

## 限制

- 有附件记录不代表 PDF 已同步到 Zotero Storage。
- 即使文件接口对已同步附件可用，全文索引也可能不完整。
- PDF 批注/高亮需按条目确认，并非所有 Web API 响应都保证包含。
- 本项目不绕过付费墙、不寻找未授权副本，并且刻意不实现任何写入 API。

## 安全

完整策略见 [SECURITY.md](./SECURITY.md)。

## 许可证

[MIT](./LICENSE) © 2026
