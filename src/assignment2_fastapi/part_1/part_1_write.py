# Standard library

# Third-party libraries
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator

# Local imports


ALLOWED_MODELS = {"gpt-4", "gpt-3.5-turbo"}


class Model_Request(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(..., ge=10, le=500)

    @field_validator("model")
    @classmethod
    def normalize_model(cls, v):
        model_cleaned = v.strip().lower()

        if not model_cleaned:
            raise ValueError("Model cannot be empty or only whitespace")

        return model_cleaned

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {ALLOWED_MODELS}")

        return v

    @field_validator("text")
    @classmethod
    def validate_text_content(cls, v):
        if not v.strip():
            raise ValueError("model cannot be empty or only whitespace")

        return v.strip()


def main():
    logger.info("Testing part 1 q3: write")
    cases = {
        "Case 1": {
            "text": " ",
            "model": "gpt-4",
        },
        "Case 2": {
            "text": " Hello World ",
            "model": "gpt-4",
            "temperature": 2.5,
        },
        "Case 3": {
            "text": "Hi",
            "model": "claude-3",
        },
        "Case 4": {"text": "Hi", "max_tokens": 100},
        "Case 5": {
            "text": " Hello World 3333 ",
            "model": "  GPT-4",
            "temperature": 1.5,
            "max_tokens": 12,
        },
    }

    for case_name, data in cases.items():
        print(f"\n{'=' * 40}")
        print(case_name)
        print(f"Input: {data}")

        try:
            request = Model_Request(**data)

            print("Result: SUCCESS")
            print(f"Created model: {request}")

        except ValidationError as error:
            print("Result: VALIDATION ERROR")
            logger.error(f"{error}")


if __name__ == "__main__":
    main()
