# Homemade-MCP

**Homemade-MCP** is a tiny Python library that gives you **one standard input/output format** for multiple AI providers (OpenAI GPT, Google Gemini, Mistral OCR).

✨ Features:

- Unified request/response schema (no more provider-specific formats).
- **LLM & OCR support**: text, text+image, and documents.
- **Structured outputs**: enforce JSON schema across models.
- **Thinking control** (reasoning budget / effort) when supported.
- **Search grounding** (Gemini’s Google Search integration).
- **Batch processing**:

  - “Concurrent” mode → fast async fan-out.
  - “Native” batch (OpenAI & Gemini) → cheaper large jobs with JSONL.

---

## Why?

Each provider (OpenAI, Gemini, Mistral) exposes different SDKs, request shapes, and batch/structured-output quirks.
**Homemade-MCP** acts as a “universal socket”: one entry point, one output format.
Swap providers or models without rewriting your code.

---

## Installation

```bash
pip install -e .
```

---

## Quick start

```python
from homemade_mcp.client import LLMClient
from homemade_mcp.schemas import StdRequest, LLMInput, PDFDoc

client = LLMClient({
  "openai": {"api_key": "..."},
  "gemini": {"api_key": "..."},
  "mistral_ocr": {"api_key": "..."},
})

req = StdRequest(
    provider="openai",
    model="gpt-5",
    task="llm",
    input=LLMInput(
        blocks=["Extract title & price: Widget X costs 12.99"],
        json_schema={"type":"object","properties":{"title":{"type":"string"},"price":{"type":"number"}},"required":["title","price"]},
        thinking="low"
    )
)

resp = await client.run(req)
print(resp.content)  # {'title': 'Widget X', 'price': 12.99}
```

---

## Roadmap

- [x] Add batch job polling helpers (OpenAI & Gemini).
- [ ] Extend OCR adapter (PDFs, multi-page).
- [ ] PDF rasterization helper (images for LLM vision) [optional extra dep].
- [ ] Add more providers (Anthropic, Cohere, Claude OCR).
- [ ] CLI tool for quick testing.

---

## Contributing

Pull requests and issues welcome!

- Keep code simple (no heavy abstractions).
- Follow PEP8.
- Add examples if you add features.

---
