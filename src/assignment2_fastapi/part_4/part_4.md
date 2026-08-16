## Q13 — Trace

The valid API keys are:

```python id="2i4t9c"
VALID_API_KEYS = {
    "dev-key-1": "ahmed",
    "dev-key-2": "omar",
    "dev-key-3": "ayman",
}
```

The `verify_api_key()` function checks whether the API key exists in `VALID_API_KEYS`.

### Case A — `X-API-KEY: dev-key-2`

`dev-key-2` exists in `VALID_API_KEYS` and is associated with the username `"omar"`.

**Result:**

```text id="4v0q4r"
omar
```

The function returns the username **`omar`**.

---

### Case B — `X-API-KEY: dev-key-9`

`dev-key-9` does not exist in `VALID_API_KEYS`.

Therefore, the function raises an HTTP exception.

**Result:**

```text id="r4xxka"
HTTP 403
Detail: "Invalid or missing Api Key..."
```

---

### Case C — `X-API-KEY` Header Is Missing

The `APIKeyHeader` is configured with:

```python id="y2cb8r"
auto_error=True
```

This means FastAPI automatically raises an HTTP exception when the `X-API-KEY` header is missing, so `verify_api_key()` is not executed.

**Result:**

```text id="t9ebgq"
HTTP 403
Detail: "Not authenticated"
```

### Final Answers

| Case  | Result                                       |
| ----- | -------------------------------------------- |
| **A** | Returns `"omar"`                             |
| **B** | HTTP 403 — `"Invalid or missing Api Key..."` |
| **C** | HTTP 403 — `"Not authenticated"`             |


## Q14 — Debug

### 1. Input That Causes the Bug

An input such as:

```text
X-API-KEY: DEV-KEY-2
```

causes the bug.

### 2. Exact Reason for the Bug

The condition converts the API key to lowercase:

```python
if api_key.lower() not in VALID_API_KEYS:
```

So `"DEV-KEY-2"` becomes `"dev-key-2"`, which exists in `VALID_API_KEYS`. Therefore, the condition passes.

However, the return statement uses the original API key without conversion :

```python
return VALID_API_KEYS[api_key]
```

It tries to access:

```python
VALID_API_KEYS["DEV-KEY-2"]
```

But the dictionary only contains the lowercase key `"dev-key-2"`.

As a result, a **KeyError** is raised.

### 3. Corrected Line

The corrected return statement is:

```python
return VALID_API_KEYS[api_key.lower()]
```

This makes the lookup consistent with the check:

```python
if api_key.lower() not in VALID_API_KEYS:
    raise HTTPException(
        status_code=403,
        detail="Invalid or missing Api Key..."
    )

return VALID_API_KEYS[api_key.lower()]
```

So both the validation and dictionary lookup use the same lowercase API key.
