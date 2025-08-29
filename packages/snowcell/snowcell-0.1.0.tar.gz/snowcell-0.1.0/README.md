# Snowcell Python SDK

Python SDK for the **Snowcell** API.

This is a lightweight alternative to the OpenAI SDK that can be integrated into your applications. 

---

## Install

```bash
pip install snowcell
```

---

## Quickstart

```python
import os
from snowcell import Snowcell

client = Snowcell(api_token=os.environ["SNOWCELL_API_TOKEN"])

res = client.chat.create(
    model="Meditron3-8B",
    messages=[{"role": "user", "content": "Say hello."}],
    max_tokens=50,
)
print(res.choices[0].message.content)
```

### Streaming

```python
from snowcell import Snowcell

client = Snowcell(api_token="YOUR_API_TOKEN")

for event in client.chat.stream(
    model="Meditron3-8B",
    messages=[{"role": "user", "content": "Write one short sentence."}],
    max_tokens=40,
):
    # Each `event` is a dict parsed from SSE "data:" lines
    print(event)
```

---

## API

### Client

```python
from snowcell import Snowcell

client = Snowcell(
  api_token="...", # or set SNOWCELL_API_TOKEN env var
)
```

### Chat

```python
res = client.chat.create(
    model="Meditron3-8B",
    messages=[{"role": "user", "content": "Explain attention in one line."}],
    max_tokens=80,
)
print(res.choices[0].message.content)
```

Async:

```python
res = await client.chat.acreate(model="Meditron3-8B", messages=[{"role":"user","content":"Hi"}], max_tokens=80)
```

Streaming:

```python
for evt in client.chat.stream(model="Meditron3-8B", messages=[{"role":"user","content":"Hi"}], max_tokens=80):
    print(evt)
```

### Completions

```python
res = client.completions.create(
    model="Meditron3-8B",
    prompt="Hello world!",
    max_tokens=32,
)
print(res.choices[0].text)
```

Async:

```python
res = await client.completions.acreate(model="Meditron3-8B", prompt="Hello world!", max_tokens=32)
```

---

## Configuration

You can set these environment variables instead of passing args:

- `SNOWCELL_API_TOKEN` – bearer token for authentication
- `SNOWCELL_INFERENCE_BASE_URL` – override the inference origin (e.g., `http://127.0.0.1:11434` for local testing)

The SDK sends `User-Agent: snowcell-python/<version>` and uses timeouts tuned for LLMs: `connect=5s`, `write=30s`, `read=300s`.

---

## Errors

The SDK raises `SnowcellError` for 4xx/5xx responses with server details included. Common cases:

- `401/403` – check your token / project permissions
- `422` – request validation error (inspect the server message)
- `429` – rate limited; retry after the indicated delay
- `5xx`  – transient server error; try again later

---

## Versioning

- Initial public release: **0.1.0** (chat, completions; sync/async; streaming for chat)
- Backwards-compatible fixes → patch bump (`0.1.x`)
- New features/endpoints → minor bump (`0.x.y`)

See [`CHANGELOG.md`](./CHANGELOG.md).

---

## License

MIT – see [`LICENSE`](./LICENSE).
