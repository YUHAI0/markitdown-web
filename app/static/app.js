const hasDocument = typeof document !== "undefined";
const fileInput = hasDocument ? document.querySelector("#file-input") : null;
const dropzone = hasDocument ? document.querySelector("#dropzone") : null;
const convertButton = hasDocument ? document.querySelector("#convert-button") : null;
const copyButton = hasDocument ? document.querySelector("#copy-button") : null;
const downloadButton = hasDocument ? document.querySelector("#download-button") : null;
const statusText = hasDocument ? document.querySelector("#status") : null;
const output = hasDocument ? document.querySelector("#markdown-output") : null;
const fileMeta = hasDocument ? document.querySelector("#file-meta") : null;
const fileName = hasDocument ? document.querySelector("#file-name") : null;
const fileSize = hasDocument ? document.querySelector("#file-size") : null;
const resultMeta = hasDocument ? document.querySelector("#result-meta") : null;

let selectedFile = null;

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

function setStatus(message, type = "idle") {
  statusText.textContent = message;
  statusText.classList.toggle("is-error", type === "error");
  statusText.classList.toggle("is-success", type === "success");
}

function setSelectedFile(file) {
  selectedFile = file;
  convertButton.disabled = !file;
  copyButton.disabled = true;
  downloadButton.disabled = true;
  output.value = "";
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
  convertButton.textContent = "转换中...";
  output.value = "";
  resultMeta.textContent = "正在处理";
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

    output.value = payload.markdown;
    resultMeta.textContent = `${payload.characters.toLocaleString("zh-CN")} 个字符`;
    copyButton.disabled = false;
    downloadButton.disabled = false;
    setStatus("转换完成。", "success");
  } catch (error) {
    resultMeta.textContent = "转换失败";
    setStatus(error.message, "error");
  } finally {
    convertButton.textContent = "转换为 Markdown";
    convertButton.disabled = !selectedFile;
  }
}

async function copyMarkdown() {
  if (!output.value) return;

  try {
    await navigator.clipboard.writeText(output.value);
    setStatus("Markdown 已复制到剪贴板。", "success");
  } catch {
    output.select();
    document.execCommand("copy");
    setStatus("Markdown 已复制。", "success");
  }
}

function downloadMarkdown() {
  if (!output.value) return;

  const blob = new Blob([output.value], { type: "text/markdown;charset=utf-8" });
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
}

if (typeof module !== "undefined") {
  module.exports = { markdownDownloadName };
}
