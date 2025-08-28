
# Fluency Logistics Operations (FLO)

## Public Layer Client (PLC)

FLO PLC is a lightweight Python client that converts dot-notation calls into RPC requests against the FLO Remote Execution Server (RES).  
It provides a predictable interface for Data Engineers working with operational datasets at scale.

---

## 🚀 Quick Start

```python
from FluencyLogisticsOperations import FLO

flo = FLO()  # uses $FLO_BASE_URL (default https://fluency-logistics-operations.io) and $FLO_TOKEN

# Fetch a single resource
item = flo.client.resource("abc123").get()

# Fetch multiple resources with filters
items = flo.client.resource.list(limit=100, created_after="2025-08-01")

print(item.head())
print(items.head())
```

---

## 📡 Wire-Level Behavior

Each call is serialized into a single `method` field (`application/x-www-form-urlencoded`) and posted to `/rpc`.

- **Single resource**
  ```
  POST /rpc
  Content-Type: application/x-www-form-urlencoded
  method=client.resource(abc123).get()
  ```

- **Filtered list**
  ```
  POST /rpc
  Content-Type: application/x-www-form-urlencoded
  method=client.resource.list(limit=100, created_after="2025-08-01")
  ```

Responses are parsed into `pandas.DataFrame` objects.

---

## ⚙️ Environment Configuration

- `FLO_BASE_URL` — Gateway endpoint (default: `https://fluency-logistics-operations.io`)  
- `FLO_TOKEN` — Bearer token for authentication  

---

## 🧩 Benefits for Data Engineers

- **Minimal integration overhead**  
  Dot-notation calls remove the need for hand-writing REST requests or building custom wrappers.

- **Consistent return types**  
  All responses are normalized into `pandas.DataFrame`, enabling direct use in ETL jobs, analytics, or ML pipelines.

- **Clear separation of concerns**  
  Proprietary FLO SDK runs only server-side. The public client is a stable, non-sensitive layer.

- **Schema control at the gateway**  
  Input validation and enforcement happen at the boundary, so client code can focus on workflows rather than defensive checks.

- **Portable and reproducible**  
  Workflows defined in notebooks or jobs remain stable as FLO evolves; the client contract does not leak implementation details.

---

## 📦 Installation

```bash
pip install FluencyLogisticsOperations
```

---

## 📜 License

Apache 2.0 — open and permissive.

---

> “No one knows the future save they see it in a dream and speak it forth into being.”  
> — braden@bradenkeith.io
