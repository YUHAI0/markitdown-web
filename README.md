# 文档转 Markdown

本地网页工具：上传 markitdown 支持的文件，自动转换为 Markdown，并在页面中一键复制。

## 支持类型

首版按 markitdown README 的能力开放常见文件类型：PDF、Word、PowerPoint、Excel、图片、音频、HTML、CSV、JSON、XML、ZIP、EPub 和文本文件。

## 运行

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

打开：

```text
http://127.0.0.1:8765
```

## 测试

```powershell
python -m unittest discover -s tests -v
```

## 安全边界

工具默认面向本地使用。后端限制单文件最大 50MB，只接受常见 markitdown 文件扩展名，转换后删除临时文件。

## Vercel

项目包含 `vercel.json` 和 `api/index.py`，可用 Vercel Python Serverless Function 部署。受 Vercel 函数体积、执行时间和临时目录限制影响，较大的 Office、PDF、音频或需要额外系统依赖的转换可能不适合线上 serverless 环境。
