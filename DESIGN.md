# Design

## Theme
- 默认浅色（接近纸白）。
- 提供深色模式（手动切换 + 跟随 `prefers-color-scheme`）。
- 暗色场景：夜间浏览 Markdown 渲染；亮色场景：白天处理文档。

## Color Palette

### Light
- `ink` `oklch(18% 0.005 270)` — 文字 / 强描边 / 主按钮
- `paper` `oklch(99% 0.003 90)` — 页面背景
- `paper-2` `oklch(96% 0.008 90)` — 卡片次背景 / 工具栏
- `mute` `oklch(46% 0.005 270)` — 副文
- `line` `oklch(88% 0.005 270)` — 弱描边
- `line-strong` `oklch(72% 0.005 270)` — 强描边
- `accent` `oklch(82% 0.15 95)` — Crayon 黄，仅 hover / active / focus / 拖入态
- `accent-ink` `oklch(18% 0.005 270)` — 黄底上的文字

### Dark
- `ink` `oklch(94% 0.005 90)`
- `paper` `oklch(16% 0.005 270)`
- `paper-2` `oklch(20% 0.005 270)`
- `mute` `oklch(68% 0.005 270)`
- `line` `oklch(28% 0.005 270)`
- `line-strong` `oklch(45% 0.005 270)`
- `accent` `oklch(85% 0.15 95)` — 亮一档的 Crayon 黄
- `accent-ink` `oklch(16% 0.005 270)`

## Typography
- UI / 标题 / 副文：`Geist`（中文 `Noto Sans SC`）
- 等宽（数据 / 代码 / 状态）：`Geist Mono`（中文 `Noto Sans SC`）
- 渲染结果区（Markdown 阅读）：`Geist` 正文 + `Geist Mono` 代码块
- 字号阶梯（rem，桌面）：
  - 标题 H1：clamp(2rem, 2.2vw + 1rem, 2.6rem)
  - H2 / 面板标题：1.25rem
  - 正文：1rem
  - 副文 / 元数据：0.875rem
  - 微文 / chip / 标签：0.75rem
- 行高：UI 1.5；阅读结果 1.72
- 字重对比：500 vs 700（避免 400 / 600 这种看不清的差距）

## Layout
- 单页布局，垂直流。
- 内容最大宽 1180px 居中。
- 关键面板最大宽 920px（在 workspace 内的内容约束）。
- 双栏 `.workspace` 网格：`grid-template-columns: 340px minmax(0, 1fr); gap: 24px;`。
- 留白节奏：8 / 16 / 24 / 32 / 48 / 64。
- 移动端：双栏折叠为单栏。

## Geometry
- 圆角：`0`（除焦点环 `outline`）。
- 描边：`1.5px` 通用；交互态 `1.5px` 保持。
- 阴影：默认无；悬浮卡片用 `1px` hairline 区分。
- 焦点环：`outline: 3px solid var(--accent); outline-offset: 3px;`。
- 动效：`150ms` ease-out，禁止弹性。

## Components
- **TopBar**：左侧 logo + 产品名，右侧 API 链接 + 主题切换。
- **Intro**：eyebrow 小标 + H1 + 一句话副文。垂直堆叠，垂直 24px 间距。
- **DropZone**：dashed 1.5px 边框，hover / drag 黄底。
- **PrimaryButton**：默认黑底白字，hover 黄底黑字。禁用态 opacity 0.4。
- **SecondaryButton**：白底黑边，hover 黄底。
- **ViewToggle**：1.5px 边框容器，激活项反色。
- **OutputPanel**：白底 / paper-2 工具栏，1.5px 边框。
- **CopyToast**：按钮下方 9px 偏移的浮层。
- **ProgressBar**：工具栏底部 1px 高的滑动条，accent 色。
- **ThemeToggle**：单个按钮，`prefers-color-scheme` 检测 + localStorage 记忆。

## Motion
- 进入：fade + 4px 上移，180ms。
- 状态切换：150ms ease-out。
- 进度条：`@keyframes progress-slide`，1.05s 循环。
- `prefers-reduced-motion: reduce` 时所有动效降为 0ms。

## Spacing Tokens
- `--s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 64px;`

## Border Tokens
- `--b-thin: 1.5px; --b-hair: 1px; --b-strong: 2px;`

## Breakpoints
- 移动：`< 720px`（双栏折叠为单栏）。
- 平板：`720–960px`。
- 桌面：`≥ 960px`。