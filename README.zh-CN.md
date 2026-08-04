# Zotero Literature Workflow

<p align="center">
  <a href="./README.md">English</a> | 简体中文
</p>

Zotero Literature Workflow 把 [Zotero](https://www.zotero.org) 文献库接入 [OpenCode](https://opencode.ai) 里的 AI 助手。用大白话问文献、直接读 PDF 正文和网页快照、还能看图表公式——不用打开 Zotero 桌面端，也不用手动导出任何东西。

## 特性

* **搜索** — 用自然语言在文献库里找论文，AI 返回的不只是标题，而是带引文上下文的匹配结果。
* **阅读** — 自动提取已同步 PDF 的正文，网页快照（保存的网页）也能自动抽文字。
* **看图** — 把 PDF 任意一页渲染成图片，多模态模型可以直接读图表、表格、公式和扫描版页面。
* **证据优先** — 每条回答都绑定引文上下文，并标明文字来源，区分"原文有的"和"AI 总结的"。
* **上手快** — 不需要 Zotero 桌面端、本地数据库或手动上传 PDF。装好、填一个 key，就能用。

## 快速开始

```bash
python -m venv .venv
. .venv/bin/activate
pip install "zotero-literature-workflow[mcp,pdf] @ git+https://github.com/thovet55/zotero-literature-workflow.git"
```

在磁盘任意位置创建一个 `.env`（例如 `~/.config/zotero-workflow/.env`），填入你的 key：

```text
ZOTERO_API_KEY=你的-key
ZOTERO_LIBRARY_ID=你的数字用户ID
ZOTERO_LIBRARY_TYPE=user
```

去 **Zotero → Settings → Security → API Keys**（[直达链接](https://www.zotero.org/settings/keys)）申请。创建带**只读**权限的 private key，同页会显示你的数字 UserID。

验证是否一切正常：

```console
$ zotero-workflow check
{"ok": true, "library": "1234567", "items_read": 1, "key": "abc...xyz"}
```

搜索你的文献库：

```console
$ zotero-workflow search "moire"
[
  {
    "key": "ABC123DE",
    "data": {
      "itemType": "journalArticle",
      "title": "Fractional quantum anomalous Hall effect in twisted MoTe2",
      ...
```

## 在 OpenCode 里用

接好 MCP 服务器后（见下方 [OpenCode MCP 接入](#opencode-mcp-接入)），你只需要直接问：

> "帮我在文献库里搜 moiré 相关的论文，列出标题、年份和期刊。"

> "把这篇关于分数量子反常霍尔效应的论文 PDF 正文提取出来。"

> "把那个 PDF 的第 3 页渲染成图片，帮我描述一下 Figure 2。"

> "找找我的批注里哪些提到了 'Chern number'。"

AI 会自动挑选合适的工具，从你的文献库里取来证据，并告诉你它到底读了什么。

## OpenCode MCP 接入

在 OpenCode 配置（`~/.config/opencode/opencode.json` 或项目级 `opencode.json`）中添加本地 MCP 服务器。完整结构见 [`opencode.example.jsonc`](./opencode.example.jsonc)：

```jsonc
{
  "mcp": {
    "zotero-literature": {
      "type": "local",
      "command": ["/你的虚拟环境路径/bin/zotero-workflow-mcp"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "ZOTERO_DOTENV": "/你的/.env路径",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    }
  }
}
```

把路径替换成你虚拟环境里的 `zotero-workflow-mcp` 可执行文件和 `.env` 路径。`ZOTERO_DOTENV` 用绝对路径指向 `.env`，因此不依赖 OpenCode 的工作目录。改完配置重启 OpenCode；每次会话都会启动全新的只读 MCP 进程。

服务器没有凭据也能正常启动——只有真正调用工具时，才会提示清晰的 `ZOTERO_API_KEY is required` 错误。

### 工具列表

| 工具 | 说明 |
| --- | --- |
| `search_items` | 搜索文献库（支持关键词、条数、偏移量） |
| `get_item` | 获取单条条目的元数据与摘要 |
| `get_children` | 获取子条目（PDF、笔记、批注） |
| `get_fulltext` | 从 Zotero 检索索引读取全文 |
| `get_pdf_text` | 下载已同步的 PDF 附件并提取文本 |
| `get_attachment_text` | 下载附件并按实际内容类型提取文本（PDF 或网页快照） |
| `get_pdf_pages` | 将一页或多页 PDF 渲染为 PNG 图片供多模态模型查看（`pages` 支持 `"1"`、`"1-3"`、`"1,3,5"`；省略则渲染全部） |

**视觉分析。** `get_pdf_pages` 返回的是图片而非文本——消费它们的模型必须是多模态的。只请求需要的页：单页渲染约 750 KB base64，一次渲染整篇容易撑爆上下文窗口。文字密集的段落优先用 `get_pdf_text`，图表、表格、公式或扫描版页面再退回渲染。

## 文献综述技能

[`skills/literature-review/SKILL.md`](./skills/literature-review/SKILL.md) 定义了证据优先的综述协议：每条引用必须有引文上下文，记录文字来源（Zotero 索引或已同步 PDF），并将仅基于元数据的结论标注为低置信度。

## 开发

```bash
pytest -q
python -m compileall -q src
```

## 限制

* 有附件记录不代表 PDF 已同步到 Zotero Storage。
* 即使文件接口对已同步附件可用，全文索引也可能不完整。
* PDF 批注/高亮需按条目确认，并非所有 Web API 响应都保证包含。
* 本项目不绕过付费墙、不寻找未授权副本，并且刻意不实现任何写入 API。

## 安全

API key 通过 `Zotero-API-Key` 请求头传递，绝不进入 URL。密钥存放于本地 `.env`（已被 git 忽略、永不提交）——切勿把 key 发到聊天、日志或 issue 中；若泄露，请到 Zotero Settings 吊销并重新创建。完整策略见 [SECURITY.md](./SECURITY.md)。

## 许可证

[MIT](./LICENSE) © 2026
