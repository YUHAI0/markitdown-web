const hasDocument = typeof document !== "undefined";
const fileInput = hasDocument ? document.querySelector("#file-input") : null;
const dropzone = hasDocument ? document.querySelector("#dropzone") : null;
const convertButton = hasDocument ? document.querySelector("#convert-button") : null;
const copyButton = hasDocument ? document.querySelector("#copy-button") : null;
const downloadButton = hasDocument ? document.querySelector("#download-button") : null;
const statusText = hasDocument ? document.querySelector("#status") : null;
const output = hasDocument ? document.querySelector("#markdown-output") : null;
const preview = hasDocument ? document.querySelector("#markdown-preview") : null;
const rawViewButton = hasDocument ? document.querySelector("#raw-view-button") : null;
const previewViewButton = hasDocument ? document.querySelector("#preview-view-button") : null;
const conversionProgress = hasDocument ? document.querySelector("#conversion-progress") : null;
const copyToast = hasDocument ? document.querySelector("#copy-toast") : null;
const fileMeta = hasDocument ? document.querySelector("#file-meta") : null;
const fileName = hasDocument ? document.querySelector("#file-name") : null;
const fileSize = hasDocument ? document.querySelector("#file-size") : null;
const resultMeta = hasDocument ? document.querySelector("#result-meta") : null;
const themeToggle = hasDocument ? document.querySelector("#theme-toggle") : null;

let selectedFile = null;
let currentMarkdown = "";
let activeView = "raw";
let copyToastTimer = null;

const THEME_KEY = "markitdown-web:theme";

function getStoredTheme() {
  try {
    return localStorage.getItem(THEME_KEY);
  } catch {
    return null;
  }
}

function setStoredTheme(value) {
  try {
    localStorage.setItem(THEME_KEY, value);
  } catch {
    /* storage may be blocked; ignore */
  }
}

function resolveInitialTheme() {
  const stored = getStoredTheme();
  if (stored === "light" || stored === "dark") return stored;
  if (typeof window !== "undefined" && window.matchMedia) {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "light";
}

function applyTheme(theme) {
  if (!hasDocument) return;
  const root = document.documentElement;
  if (theme === "dark") {
    root.setAttribute("data-theme", "dark");
  } else if (theme === "light") {
    root.setAttribute("data-theme", "light");
  } else {
    root.removeAttribute("data-theme");
  }
  if (themeToggle) {
    themeToggle.setAttribute(
      "aria-label",
      theme === "dark" ? "切换到浅色主题" : "切换到深色主题"
    );
  }
}

function markdownDownloadName(filename) {
  const fallback = "converted.md";
  if (!filename) return fallback;

  const lastSlash = Math.max(filename.lastIndexOf("/"), filename.lastIndexOf("\\"));
  const basename = filename.slice(lastSlash + 1).trim();
  if (!basename) return fallback;

  const lastDot = basename.lastIndexOf(".");
  if (lastDot <= 0) return `${basename}.md`;

  return `${basename.slice(0, lastDot)}.md`;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fallbackMarkdownToHtml(markdown) {
  const lines = String(markdown || "").split(/\r?\n/);
  const blocks = [];
  let paragraph = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    const text = paragraph.join(" ");
    blocks.push(`<p>${escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")}</p>`);
    paragraph = [];
  };

  for (const line of lines) {
    if (!line.trim()) {
      flushParagraph();
      continue;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      blocks.push(`<h${heading[1].length}>${escapeHtml(heading[2])}</h${heading[1].length}>`);
      continue;
    }

    paragraph.push(line);
  }

  flushParagraph();
  return blocks.join("\n");
}

function sanitizeHtml(html) {
  if (typeof DOMPurify !== "undefined") {
    return DOMPurify.sanitize(html);
  }

  return String(html)
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/\son\w+="[^"]*"/gi, "")
    .replace(/\son\w+='[^']*'/gi, "")
    .replace(/\s(href|src)=["']javascript:[^"']*["']/gi, "");
}

function renderMarkdownPreview(markdown) {
  const source = String(markdown || "");
  const rendered = typeof marked !== "undefined"
    ? marked.parse(source, { breaks: true, gfm: true })
    : fallbackMarkdownToHtml(source);

  return sanitizeHtml(rendered);
}

function renderPreview() {
  if (!preview) return;

  if (!currentMarkdown) {
    preview.innerHTML = '<p class="preview-placeholder">转换后的 Markdown 会在这里以阅读格式显示。</p>';
    return;
  }

  preview.innerHTML = renderMarkdownPreview(currentMarkdown);
}

function setOutputView(view) {
  activeView = view === "preview" ? "preview" : "raw";

  const isPreview = activeView === "preview";
  rawViewButton.classList.toggle("is-active", !isPreview);
  previewViewButton.classList.toggle("is-active", isPreview);
  rawViewButton.setAttribute("aria-pressed", String(!isPreview));
  previewViewButton.setAttribute("aria-pressed", String(isPreview));
  output.hidden = isPreview;
  preview.hidden = !isPreview;

  if (isPreview) {
    renderPreview();
  }
}

function setStatus(message, type = "idle") {
  statusText.textContent = message;
  statusText.classList.toggle("is-error", type === "error");
  statusText.classList.toggle("is-success", type === "success");
}

function setProgress(isActive) {
  conversionProgress.classList.toggle("is-active", isActive);
  conversionProgress.setAttribute("aria-hidden", String(!isActive));
}

function showCopyToast() {
  if (!copyToast) return;

  window.clearTimeout(copyToastTimer);
  copyToast.classList.add("is-visible");
  copyToast.setAttribute("aria-hidden", "false");
  copyToastTimer = window.setTimeout(() => {
    copyToast.classList.remove("is-visible");
    copyToast.setAttribute("aria-hidden", "true");
  }, 1800);
}

function setSelectedFile(file) {
  selectedFile = file;
  currentMarkdown = "";
  convertButton.disabled = !file;
  copyButton.disabled = true;
  downloadButton.disabled = true;
  output.value = "";
  renderPreview();
  setOutputView("raw");
  resultMeta.textContent = "暂无内容";

  if (!file) {
    fileMeta.hidden = true;
    setStatus("等待上传文件。");
    return;
  }

  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  fileMeta.hidden = false;
  setStatus("文件已选择，可以开始转换。");
}

async function convertSelectedFile() {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile);

  convertButton.disabled = true;
  copyButton.disabled = true;
  downloadButton.disabled = true;
  convertButton.textContent = "转换中…";
  output.value = "";
  resultMeta.textContent = "正在处理";
  setProgress(true);
  setStatus("正在转换文件，较大的 Office、PDF 或音频文件可能需要更久。");

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "转换失败，请换一个文件再试。");
    }

    currentMarkdown = payload.markdown;
    output.value = currentMarkdown;
    renderPreview();
    resultMeta.textContent = `${payload.characters.toLocaleString("zh-CN")} 个字符`;
    copyButton.disabled = false;
    downloadButton.disabled = false;
    setStatus("转换完成。", "success");
  } catch (error) {
    resultMeta.textContent = "转换失败";
    setStatus(error.message, "error");
  } finally {
    setProgress(false);
    convertButton.textContent = "转换为 Markdown";
    convertButton.disabled = !selectedFile;
  }
}

async function copyMarkdown() {
  if (!currentMarkdown) return;

  try {
    await navigator.clipboard.writeText(currentMarkdown);
    setStatus("Markdown 已复制到剪贴板。", "success");
    showCopyToast();
  } catch {
    output.select();
    document.execCommand("copy");
    setStatus("Markdown 已复制。", "success");
    showCopyToast();
  }
}

function downloadMarkdown() {
  if (!currentMarkdown) return;

  const blob = new Blob([currentMarkdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = markdownDownloadName(selectedFile?.name);
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  setStatus(`已准备下载 ${link.download}。`, "success");
}

if (hasDocument) {
  // Theme bootstrap (sync before paint to avoid flash)
  applyTheme(resolveInitialTheme());

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") ||
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      setStoredTheme(next);
    });
  }

  if (window.matchMedia) {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const onSystemThemeChange = (event) => {
      if (getStoredTheme()) return;
      applyTheme(event.matches ? "dark" : "light");
    };
    if (mql.addEventListener) {
      mql.addEventListener("change", onSystemThemeChange);
    } else if (mql.addListener) {
      mql.addListener(onSystemThemeChange);
    }
  }

  fileInput.addEventListener("change", () => {
    setSelectedFile(fileInput.files[0] || null);
  });

  dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("is-dragging");
  });

  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");

    const file = event.dataTransfer.files[0];
    if (file) {
      fileInput.files = event.dataTransfer.files;
      setSelectedFile(file);
    }
  });

  convertButton.addEventListener("click", convertSelectedFile);
  copyButton.addEventListener("click", copyMarkdown);
  downloadButton.addEventListener("click", downloadMarkdown);
  rawViewButton.addEventListener("click", () => setOutputView("raw"));
  previewViewButton.addEventListener("click", () => setOutputView("preview"));
  setOutputView("raw");
}

if (typeof module !== "undefined") {
  module.exports = {
    markdownDownloadName,
    renderMarkdownPreview,
    showCopyToast,
    resolveInitialTheme,
    applyTheme,
  };
}