# Q18 — Trace: TranslateRequest Validation

The `TranslateRequest` model validates the `text` and `target_language` fields before creating the request object.

## Case A

```json
{
  "text": "Hello there",
  "target_language": " "
}
```

**Result:** Validation Error

The `text` is valid because it has more than 10 characters.

However, `target_language` contains only a space. The validator calls `strip()`, which turns it into an empty string. Therefore, the validator raises:

```text
Target Language cannot be empty
```

## Case B

```json
{
  "text": "Hi",
  "target_language": "French"
}
```

**Result:** Validation Error

`target_language` is valid because `"French"` is not empty.

However, `text` contains only 2 characters, while the model requires at least 10 characters using `min_length=10`.

Therefore, Pydantic raises a `string_too_short` validation error for the `text` field.

## Case C

```json
{
  "text": "Hi",
  "target_language": "French"
}
```

**Result:** Validation Error

This case has exactly the same input as Case B, so it produces the same result.

The `target_language` is valid, but `"Hi"` has only 2 characters, which is less than the required minimum of 10.

Therefore, the request fails with a `string_too_short` validation error.

## Summary

| Case | Validation Result | Reason                                     |
| ---- | ----------------- | ------------------------------------------ |
| A    | Validation Error  | `target_language` is empty after `strip()` |
| B    | Validation Error  | `text` has only 2 characters               |
| C    | Validation Error  | `text` has only 2 characters               |

Cases B and C are identical, so they have the same validation result.


# Q19 — Debug: String Formatting Bug

## 1. Cause of the Bug

The problem is that the string contains `{max_length}`, but it is not defined as an f-string.

Without the `f` before the string, Python treats `{max_length}` as normal text instead of replacing it with the value of the `max_length` variable.

As a result, the model receives:

```text
{max_length}
```

instead of the actual value, such as `150`.

## 2. Corrected `system_prompt`

The string should be written as an f-string:

```python
system_prompt = (
    f"You are a summarization assistant. "
    f"Summarize the following text concisely "
    f"in maximum {max_length} words."
)
```

Now, if `max_length = 150`, the resulting prompt will contain:

```text
in maximum 150 words.
```

