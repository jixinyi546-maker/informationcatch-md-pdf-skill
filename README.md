# jixinyi-catch-md-pdf-skill

一个一体化 Skill：
1. 把 URL 抓取为 Markdown
2. 按需把 Markdown 转成 PDF

适用于你希望通过一个入口统一处理“抓取网页 / YouTube / 远程 PDF”并输出 `md` 或 `pdf` 的场景。

---

## 功能特性

- 统一入口：一个命令同时支持抓取与导出
- 输出格式可选：`md` / `pdf` / `auto`
- 自动判断输出：`--format auto` + `--intent`
- 多路由抓取：
  - YouTube（`yt-dlp` 元数据路线）
  - 远程 PDF
  - 通用网页（`r.jina.ai` -> `defuddle.md` 回退）
- 内置 PDF 排版引擎（`scripts/md2pdf.py`）

---

## 目录结构

```text
jixinyi-catch-md-pdf-skill/
├─ SKILL.md
├─ README.md
├─ requirements.txt
├─ .gitignore
└─ scripts/
   ├─ fetch_and_convert.py
   └─ md2pdf.py
```

---

## 环境要求

- Python 3.8+
- 依赖见 `requirements.txt`

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 快速开始

### 1) 自动判断输出为 PDF

```bash
python scripts/fetch_and_convert.py \
  --url "https://example.com/article" \
  --format auto \
  --intent "export pdf"
```

### 2) 自动判断输出为 Markdown

```bash
python scripts/fetch_and_convert.py \
  --url "https://example.com/article" \
  --format auto \
  --intent "save as markdown"
```

### 3) 显式指定输出格式

```bash
python scripts/fetch_and_convert.py --url "https://example.com/article" --format md
python scripts/fetch_and_convert.py --url "https://example.com/article" --format pdf
```

---

## 命令参数

`fetch_and_convert.py` 支持：

- `--url` (必填): 目标链接
- `--format`: `md` / `pdf` / `auto`，默认 `auto`
- `--intent`: 当 `--format auto` 时用于推断输出格式
- `--output`: 自定义输出路径
- `--theme`: PDF 主题（默认 `warm-academic`）
- `--watermark`: PDF 水印文本（默认空）

示例：

```bash
python scripts/fetch_and_convert.py \
  --url "https://youtu.be/xxxxxxxx" \
  --format auto \
  --intent "export pdf with watermark" \
  --theme warm-academic \
  --watermark "internal"
```

---

## 路由规则

- `youtube.com` / `youtu.be`
  - 走 YouTube 路由（`yt-dlp` 提取标题、章节、描述等）
- URL 以 `.pdf` 结尾
  - 走远程 PDF 路由
- 其他 URL
  - 先尝试 `https://r.jina.ai/<url>`
  - 失败后回退 `https://defuddle.md/<url>`

---

## 输出规则

- 默认输出目录：`~/Downloads`
- 生成 PDF 时会保留中间 Markdown 文件
- 文件名基于抓取标题清洗后生成

---

## 常见问题（FAQ）

### 1) `auto` 是如何判断 `md` 还是 `pdf`？

通过 `--intent` 关键词判断。
命中 `pdf` 关键词输出 PDF；命中 `markdown/md` 关键词输出 Markdown；都不命中时默认输出 Markdown。

### 2) YouTube 报错怎么办？

先确认：

1. `yt-dlp` 已安装（`pip install yt-dlp`）
2. 网络可访问 YouTube
3. Python 版本与依赖正常

### 3) PDF 转换失败怎么办？

先确认：

1. `reportlab` 已安装
2. `scripts/md2pdf.py` 文件存在
3. 输入 Markdown 不是空内容

---

## 在 GitHub 发布

1. 新建仓库（例如 `jixinyi-catch-md-pdf-skill`）
2. 将本目录全部文件上传
3. 可选：添加 release tag（如 `v1.0.0`）
4. 在仓库首页引用本 README 的“快速开始”命令

---

## 免责声明

- 抓取内容的完整性取决于目标站点是否依赖登录、反爬策略与前端动态渲染。
- 请遵守目标网站的使用条款与版权规范。

---
##致谢
致谢
r.jina.ai — Jina AI 提供的免费 URL 转 Markdown 代理
defuddle.md — 干净的文章提取服务
agent-fetch — 本地 URL 内容提取工具
Playwright — 微信公众号抓取的浏览器自动化
飞书开放平台 — 飞书文档 API
向阳乔木joeseesun - URL抓取信息赚Markdown工具

