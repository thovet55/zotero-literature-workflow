# 构建 Zotero 文献读取与分析工作流

请在当前 OpenCode session 中完成一个可持久使用的 Zotero 文献研究工作流。我的机器上**没有 Zotero Desktop**，因此不要依赖 Zotero 本地 API、`zotero.sqlite`、本地 Zotero 插件或必须运行 Zotero 的方案。

## 目标

通过 Zotero Web API 访问我已经加入并同步到 Zotero 云端的文献，避免我在每个新 session 中重复粘贴 API key，也避免我手动逐篇上传 PDF。

最终我希望在任意新 OpenCode session 中直接提出类似请求：

> 查找我 Zotero 中关于 single-photon absorption 的文献，读取已同步的 PDF，分析正文引用了哪些关键文献，并推荐值得阅读的被引文献。

工作流至少应支持：

- 搜索 Zotero library 中的条目
- 获取题目、作者、年份、期刊、DOI、摘要、标签和 collection
- 获取条目的 children，识别 PDF attachment
- 读取 Zotero Web API 提供的全文索引
- 在全文索引不足时下载已同步的 PDF，并提取 PDF 文本
- 读取 Zotero notes、PDF annotations 和 highlights（API 能力允许时）
- 获取参考文献列表或从 PDF 文本提取参考文献
- 定位正文中引用某篇参考文献的上下文
- 判断被引文献的引用作用：理论基础、方法来源、关键结论、历史背景、对照结果、争议或研究空白等
- 为值得阅读的被引文献给出推荐等级、推荐原因、DOI/URL 和与当前研究主题的关系

## 非目标

- 不绕过出版社付费墙
- 不抓取或下载没有合法访问权限的全文
- 不把 Zotero API key 写入 Git 仓库、公开文件、聊天消息或最终报告
- 不默认修改 Zotero 条目、collection、标签或 notes
- 不默认启用写权限
- 不要求在本机安装 Zotero Desktop

## 推荐技术路线

优先研究并采用以下方案；如果与当前 OpenCode 版本不兼容，再选择等价方案：

1. 使用成熟的 Zotero MCP/Web API 适配器，例如 `54yyyu/zotero-mcp` 的当前稳定版本。
2. 使用 Zotero Web API，而不是 local API。
3. 将 `ZOTERO_API_KEY`、`ZOTERO_LIBRARY_ID` 和 `ZOTERO_LIBRARY_TYPE=user` 存在本机的安全环境变量或权限受限的 secrets 文件中。
4. 在 OpenCode 的持久化 MCP 配置中注册 Zotero MCP，使所有新 session 自动发现该服务。
5. 默认只暴露或启用读取工具；如果适配器无法细粒度禁用写工具，必须在配置和操作规范中明确禁止写入。
6. 不要把 API key 硬编码在 MCP JSON、项目文件或 shell 命令中。优先使用环境变量引用、受限 `.env` 文件或 OpenCode 支持的 secrets 机制。
7. 如果使用语义检索，优先选择本地 embedding/Ollama；不要未经确认把 PDF 全文发送给 OpenAI、Gemini 或其他外部 embedding 服务。

## 重要的 Zotero Web API 事实

请先核对当前官方 Zotero Web API v3 文档，不要凭记忆假设 endpoint。需要重点验证：

- 用户 library 与 group library 的 endpoint 差异
- API key 的读取权限和 library scope
- 条目、children、attachment file 和 fulltext content 的 endpoint
- PDF 文件是否必须已经同步到 Zotero Storage
- Web API 是否能直接返回 PDF 全文、全文索引或 annotations
- 大文件下载、分页、速率限制和错误响应
- API key 应使用 header 还是 query parameter；优先使用 header，避免 key 出现在 URL、日志和 shell history 中

明确区分以下状态并在验证报告中说明：

- Zotero 中只有元数据，没有附件
- 有附件记录但 PDF 未同步到 Zotero Storage
- PDF 已同步，可以下载
- 有全文索引，可以直接读取
- 只有 notes/annotations，没有可用 PDF

## API key 配置流程

新 session 必须指导我在本机完成一次配置，但绝不能要求我把 key 发到聊天中：

1. 登录 Zotero，进入 `Settings → Security → API Keys`。
2. 创建 Personal API Key。
3. 只授权目标个人 library 的读取权限；默认不要开启 write 权限或不必要的 group library 权限。
4. 找到 numeric User ID。
5. 让用户在本机输入或保存 key，不要让用户在聊天中粘贴 key。
6. 设置安全文件权限，例如 secrets 文件只能由当前用户读取。
7. 使用脱敏测试确认 key 有效，输出中不得打印完整 key。

如果当前 OpenCode 的 MCP 配置需要明文环境变量值，而不能引用外部 secrets 文件，必须先说明风险并优先寻找安全替代方式。禁止把真实 key 写入本仓库。

## 执行前的检查

开始修改前必须：

- 读取当前工作区和 OpenCode 配置方式，确认本次修改的实际目标文件
- 检查是否已经存在 Zotero MCP、相关 MCP server、`.env`、secrets 或同名配置
- 检查 OpenCode 当前支持的 MCP transport 和全局配置位置
- 检查 `uv`/`uvx`、Python、Node.js 等可用运行时
- 检查是否有用户未提交的相关修改；不要覆盖或回滚它们
- 读取第三方项目 README、发行版本、许可证和配置示例
- 只使用官方 Zotero 文档、项目仓库和可核验的发行渠道

如果需要编辑 OpenCode 自身配置，先使用 `customize-opencode` skill，并遵守其安全规则。不要把 Zotero API key 写入 skill 文件、prompt 文件或仓库。

## 实现要求

### A. 持久化 MCP 连接

配置一个跨 session 可用的 Zotero MCP server。优先使用无需手动启动的命令形式，例如 `uvx` 或稳定的已安装命令；不要未经必要性使用 Docker。

配置必须清楚说明：

- server 名称
- command/args
- transport
- 环境变量来源
- 读取模式
- 如何启动、停止、更新和检查状态
- 如何撤销 API key

### B. 文献读取能力

确认 MCP 工具确实能够完成以下最小测试：

1. 列出/搜索 library 中的条目
2. 获取一条条目的完整 metadata
3. 获取 children 并识别 PDF attachment
4. 获取 fulltext 或下载 PDF
5. 读取一条 note/annotation（如果库中存在）
6. 返回清晰的“无附件、未同步、无全文或权限不足”错误

不要只根据 README 宣称判断可用性；使用非敏感的实际请求或 MCP Inspector/等价诊断验证工具能力。

### C. 固定的文献分析工作流

新增一个简短、可复用的 literature-review skill 或 workflow（如果已有同类 skill，优先改进现有内容而不是重复创建）。它应要求：

1. 先搜索 Zotero library，确认目标条目和 item key。
2. 获取 metadata、abstract、children、fulltext、notes 和 annotations。
3. 记录全文来源：Zotero fulltext endpoint、PDF 下载、HTML、摘要或其他来源。
4. 读取参考文献表。
5. 对每个重要引用搜索正文上下文，不能仅凭参考文献标题推测引用原因。
6. 将引用按功能分类。
7. 推荐被引文献时优先考虑：
   - 在多处或关键段落被引用
   - 支撑核心实验/理论/方法
   - 是该主题的奠基性或转折性工作
   - 能解释当前论文与先前工作的关系
   - 对当前研究问题具有直接可迁移性
8. 对无法获得全文的被引文献明确标记“仅根据 metadata/abstract/引用上下文判断”。
9. 不把“引用次数高”直接等同于“值得阅读”。
10. 最终报告提供文献标题、作者、年份、DOI/稳定 URL、原文引用位置、引用作用、推荐理由和优先级。

### D. 只读安全边界

默认只允许读取：

- search/list/get metadata
- collection/tag 查询
- children/attachment 查询
- fulltext/PDF 读取
- notes/annotations 读取

禁止默认执行：

- add/import item
- update metadata
- create/delete note
- create/delete collection
- 修改 tags
- 删除 item
- 上传或替换附件

如果 MCP server 自动注册了写工具，必须在可行时用 toolset、权限或配置禁用；否则在 skill 中加入硬性规则：未经用户明确确认，不调用任何写工具。

## 验证计划

完成配置后运行并记录结果：

1. MCP server 能启动且不会把 API key 打到 stdout/stderr。
2. 新进程可以读取环境变量或 secrets 文件。
3. Zotero API 返回 library/item，而不是 401、403 或 404。
4. 分页读取至少一页条目。
5. 对一个有 PDF 且已同步的条目验证 attachment 和 fulltext/file。
6. 对一个没有 PDF 的条目验证错误信息准确。
7. 验证 PDF 文本提取后能找到 `References`/`Bibliography` 部分。
8. 验证可以返回一条正文引用上下文，而不是只返回参考文献条目。
9. 启动新的 OpenCode session 或等价新 MCP client 进程，确认无需重新输入 key 即可发现 server。
10. 确认没有在仓库、配置示例、日志和测试输出中留下完整 key。

如果真实 API key 尚未配置，先完成不涉及秘密的安装和配置，再明确告诉我下一步只需在本机设置什么变量；不要索要或回显 key。可以用占位符、脱敏输出和模拟请求验证其余部分。

## 交付物

完成后请报告：

- 修改/新增了哪些文件
- Zotero MCP 的项目、版本、许可证和选择理由
- API key 的持久化位置（只报告路径/变量名，不报告值）
- MCP server 的配置方式
- literature-review skill/workflow 的位置和调用方法
- 已验证的 API 能力
- 尚未验证或受 Zotero Storage/权限/付费墙限制的能力
- 如何撤销 key、关闭 server 和恢复只读安全配置
- 下一步如何让我在新 session 中请求“读取 Zotero 文献并分析引用关系”

不要声称“完成”或“可读取 PDF”，除非验证结果确实证明了该能力。 
