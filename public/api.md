# Conversion API

Use this API to convert one supported file into Markdown.

## Endpoint

`POST /api/convert`

Send a `multipart/form-data` request with one field:

- `file`: the file to convert.

The upload limit is 50MB. Temporary files are removed after conversion.

## Response

Successful requests return JSON:

```json
{
  "filename": "example.pdf",
  "characters": 1234,
  "markdown": "# Converted Markdown"
}
```

Fields:

- `filename`: original uploaded filename.
- `characters`: number of characters in the converted Markdown.
- `markdown`: converted Markdown content.

## Errors

Invalid files, unsupported extensions, oversized uploads, or empty conversion results return `400` with a JSON `detail` message.

## curl Example

```bash
curl -X POST "https://your-domain.example/api/convert" \
  -F "file=@example.pdf"
```

For local development:

```bash
curl -X POST "http://127.0.0.1:8765/api/convert" \
  -F "file=@example.pdf"
```

## JavaScript Example

```js
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("/api/convert", {
  method: "POST",
  body: formData,
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail || "Conversion failed");
}

const result = await response.json();
console.log(result.markdown);
```

## Attribution

This API is powered by markitdown:

https://github.com/microsoft/markitdown
