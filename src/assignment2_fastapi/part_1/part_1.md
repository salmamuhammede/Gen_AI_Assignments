# Part 1 — Input Validation

## Q1 — Trace

### Case 1

**Result:** Validation Error

**Reason:**  
The `text` value is only whitespace. The `validate_text_content` validator
calls `strip()`, resulting in an empty string, so it raises a `ValueError`.

**Validation Error:**

`Text cannot be empty or only whitespace`

---

### Case 2

**Result:** Validation Error

**Reason:**  
The `temperature` value is `2.5`, but the allowed maximum is `2.0`.
Therefore, the `Field(ge=0.0, le=2.0)` constraint raises a validation error.

**Validation Error:**

`Input should be less than or equal to 2`

---

### Case 3

**Result:** Validation Error

**Reason:**  
The model `"claude-3"` is not included in `ALLOWED_MODELS`.
The allowed models are `"gpt-4"` and `"gpt-3.5-turbo"`.

**Validation Error:**

`Model must be one of: {'gpt-4', 'gpt-3.5-turbo'}`

---

### Case 4

**Result:** Successfully created

**Reason:**  
Only `text` is provided. The `model` and `temperature` fields use their
default values.

**Final Values:**

```text
text = "Hi"
model = "gpt-3.5-turbo"
temperature = 0.7
```

---

## Q2 — Debug

### 1. Missing line in `validate_model`

The missing line is:

```python
return v
```

This returns the validated model value after checking that it exists in
`ALLOWED_MODELS`.

---

### 2. Missing line in `validate_text_content`

The missing line is:

```python
return v.strip()
```

This returns the validated text after removing leading and trailing
whitespace.

---

### 3. Runtime impact of the missing lines

If `return v` is missing from `validate_model`, the validator implicitly
returns `None` after successful validation. Therefore, the `model` field
will not receive the validated model value.

If `return v.strip()` is missing from `validate_text_content`, the
validator also implicitly returns `None` after successful validation.
Therefore, the `text` field will not receive the validated text value.

---

### 4. Complete corrected model

```python
class Model_Request(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    @field_validator("model")
    @classmethod  # this was missing
    def validate_model(cls, v):
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {ALLOWED_MODELS}")

        return v  # this was missing too

    @field_validator("text")
    @classmethod  # this was missing
    def validate_text_content(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or only whitespace")

        return v.strip()  # this was missing too
```