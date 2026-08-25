# Admin 转换统计页

日期：2026-08-25  
项目：markitdown-web  
状态：已确认，待实现

## 背景

站点是 FastAPI + 静态页的文档转 Markdown 工具。公开入口只有上传与 `POST /api/convert`。需要一个密码保护的 `/admin` 页，查看：

- 使用过转换功能的人数
- 成功转换的文档数

站点也部署在 Vercel Serverless 上，但本功能明确选择本地 JSON 持久化：适合长期运行的本机 `uvicorn`；Vercel 上文件可能被清空，数字可能归零。这是已知取舍，不在本规格内引入 Redis / KV。

## 目标

- 转换成功时累计「人数」和「文档数」。
- `/admin` 用单一密码登录后，以双卡大数字展示这两项。
- 首页和其他公开页面不放 admin 入口。

## 非目标

- 趋势图、按日拆分、文件类型分布
- 改密码界面、多管理员账号
- Vercel 上的可靠持久化
- 对失败转换、仅打开首页未转换的访问计数

## 计数口径

只在 `POST /api/convert` **成功返回 Markdown** 时记账。校验失败、不支持的类型、转换抛错、空内容：两个数字都不动，现有错误响应不变。

| 指标 | 规则 |
| --- | --- |
| 文档数 `documents` | 每次成功转换 +1 |
| 人数 `unique_users` | 请求没有有效访客 cookie 时 +1，并种下长期访客 cookie |

访客 cookie：

- 名称：`mdw_vid`
- 值：UUID v4
- 属性：`HttpOnly`、`SameSite=Lax`、`Path=/`、`Max-Age=31536000`（365 天）
- 有效：非空、能解析为 UUID

同一浏览器多次转换只算 1 人。用户清除 cookie 或换浏览器算新人。

脚本直接调 API 且不带回 cookie：每次成功都算 1 个新人，响应里带上 `Set-Cookie`。调用方之后带上该 cookie，则只加文档数。

不持久化访客 ID 列表。cookie 是唯一性来源；JSON 只存两个整数。

## 存储

文件：`data/stats.json`（相对项目根目录）

```json
{
  "unique_users": 0,
  "documents": 0
}
```

- 写入时使用文件锁，避免并发转换丢计数。
- 文件不存在、无法解析、缺字段：按 `0/0` 重建后再写，不让转换接口因此 500。
- 写文件失败：转换接口仍返回成功；计数失败只记服务端日志。用户不能因为统计写失败而转不了文档。
- `data/stats.json` 加入 `.gitignore`。`data/.gitkeep` 可以入库，保证目录存在。
- `.superpowers/` 加入 `.gitignore`（brainstorm 会话文件不进仓库）。

## 认证

单一密码，无用户名。密码：`holmes@d920167`。

| 路径 | 行为 |
| --- | --- |
| `GET /admin` | 返回 `admin.html`。页面自己根据 session 显示登录框或统计卡。 |
| `POST /admin/login` | JSON `{ "password": "..." }`。正确则种 session cookie 并返回 `{ "ok": true }`；错误返回 401 `{ "detail": "密码错误" }`。 |
| `POST /admin/logout` | 清除 session cookie，返回 `{ "ok": true }`。 |
| `GET /api/admin/stats` | 需有效 session。成功返回 `{ "unique_users": N, "documents": M }`。无 session 返回 401。 |

密码比较使用恒定时间比较（`hmac.compare_digest`），避免计时侧信道。

Session：

- Cookie 名：`mdw_admin`
- HttpOnly、SameSite=Lax、Path=/
- 有效期 7 天
- 值为 `expiry.hmac`：`expiry` 是 Unix 秒；`hmac` 是 HMAC-SHA256（密钥由管理密码派生）。不把会话存在内存。服务重启后 cookie 未过期仍视为已登录。
- 不引入额外环境变量，保持本机零配置。

未登录访问 `/api/admin/stats` 返回 401；前端回到密码框。`GET /admin` 本身始终 200，避免把「有没有这个页面」和登录态绑在 HTTP 状态上。

不做登录速率限制（本机小工具，YAGNI）。

## 界面

视觉跟随现有 `PRODUCT.md` / `DESIGN.md`：纸白、无圆角、1.5px 描边、Crayon 黄仅用于 hover / focus。沿用 Geist + Noto Sans SC、现有 spacing / 颜色 token。支持现有主题切换。

**登录态（未登录）**

- 顶栏：左侧 `¶ markitdown` 链回首页，右侧文案「管理」，无公开导航堆砌。
- 中间窄栏：eyebrow「Admin」、标题「查看使用统计」、一句说明、密码输入、主按钮「进入」。
- 密码错误：按钮下方一行红字「密码错误」。

页面加载时请求 `GET /api/admin/stats`：401 显示登录框；200 显示统计卡。登录成功后同一页切换到统计卡，不必整页刷新。退出后回到密码框。

**登录态（已登录）**

- 顶栏右侧「退出」。
- 标题「转换使用情况」。
- 两个并排卡片（移动端折叠为单列）：
  - 使用人数 → `unique_users`，等宽大数字
  - 转换文档 → `documents`，等宽大数字
- 数字用 `zh-CN` 千分位。

首页 `index.html` 不增加任何 admin 链接。

## 后端模块边界

- `app/stats.py`：JSON 读写、文件锁、`record_conversion(visitor_id) -> (stats, should_set_cookie, visitor_id)`。不关心 HTTP。
- `app/admin_auth.py`：密码校验、签发 / 校验 / 清除 session cookie。不关心统计数字。
- `app/main.py`：接线。转换成功后调用 `record_conversion`；挂 admin 路由。

访客 cookie 的读取和 `Set-Cookie` 放在 `main.py` 的 convert / 相关依赖里，`stats.py` 只根据「有没有有效 id」决定是否 `unique_users += 1`。

## 测试

用现有 `python -m unittest`，不引入新测试框架，不编译项目。

覆盖：

1. 无访客 cookie 的成功转换：`unique_users` 和 `documents` 都 +1，响应 Set-Cookie `mdw_vid`。
2. 同一 `mdw_vid` 再次成功转换：仅 `documents` +1。
3. 转换失败（不支持类型或空内容）：两个数字不变。
4. 错误密码：401，不种 `mdw_admin`。
5. 正确密码：种下 `mdw_admin`；随后 `GET /api/admin/stats` 返回当前数字。
6. 无 session 访问 `GET /api/admin/stats`：401。

`stats.py` 的文件路径可注入（测试传入临时目录），避免污染开发数据。

## 实现时要改的文件

新增：

- `app/stats.py`
- `app/admin_auth.py`
- `app/static/admin.html`
- `app/static/admin.js`
- `data/.gitkeep`
- `tests/test_admin_stats.py`

修改：

- `app/main.py`
- `app/static/styles.css`
- `.gitignore`
- `tests/test_static_assets.py`（若现有测试会枚举静态页，补上 admin 页存在性即可；不要为统计页加首页入口断言）
