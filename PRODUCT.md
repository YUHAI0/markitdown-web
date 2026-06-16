# Product

## Register

product

## Users
个人与小团队用户，需要把 PDF / Office / HTML / JSON / ZIP 等"非结构化或半结构化文档"快速整理为干净 Markdown。典型场景：把会议附件喂给 LLM、把论文 / 报告拆给知识库、把网页存档转为可二次编辑文本、把客户发的 docx 转成 git-friendly 文本。

使用环境：白天 / 夜晚都常用；常驻浏览器书签；偶尔作为 API 给脚本 / Agent 调用。

## Product Purpose
把任意"可转文档"蒸馏为干净、可复制、可下载、可被 Agent 调用的 Markdown。后端做活，前端只做交互与呈现 —— 价值在"省掉读杂乱格式的时间"，不在花哨。

成功 = 上传 → 几秒内拿到结构清晰的 Markdown，全程不离开页面，零残留。

## Brand Personality
克制 / 安静 / 工具感 / 不卖弄。
像一本放在桌角的工作手册：纸白、字黑、用得动、用得久。

三词：**安静 · 可靠 · 排版感**。

## Anti-references
- 不做"AI 工具风"：不用渐变 hero / 不用紫蓝主色 / 不用彩虹色卡。
- 不做"轻 SaaS 奶油色"：不用米色 + 嫩绿 + 圆角的"温柔工具"反射色。
- 不做"开发者 IDE 风"：不全等宽、不仿 Vercel/Linear 配色。
- 不做"营销 landing"：本站不卖产品、不写价值主张大字、不堆特征。
- 不引入 SaaS 标志动作：浮动客服气泡、装饰性 3D、装饰性插画、装饰性 emoji 墙。

## Design Principles
1. **白纸优先**：默认只有黑、白、灰。强调色（黄）只在 hover / active / focus 时现身，模仿编辑批注高亮。
2. **信息按距离衰减**：标题 → 元数据 → 辅助文字，靠尺寸 / 重量 / 留白分层，不靠颜色分层。
3. **动作在主舞台**：上传区是默认主角；上传前是产品脸面；上传后是阅读区。动线清晰单向。
4. **少即是结构**：无圆角、无阴影、无装饰边框。1.5px 描边 + 大留白承担所有结构信息。
5. **真材实料**：结果区是阅读区，排版按出版级衬线规格处理（行高、行宽、链接色、引用、代码块）。

## Accessibility & Inclusion
- WCAG 2.2 AA。
- 键盘可达：所有交互可 Tab 进入；focus-visible 用黄环强调。
- 屏幕阅读器：状态用 `aria-live`，结果区 `aria-live="polite"`，视图切换 `aria-pressed`。
- 暗色模式：手动切换 + 跟随系统 `prefers-color-scheme`。
- `prefers-reduced-motion`：所有过渡降到 0ms。
- 中文 / 英文混排：中文走 Noto Sans SC，英文走 Geist；几何节奏一致。