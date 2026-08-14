# Standard library

# Third-party libraries
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator

# Local imports


ALLOWED_MODELS = {"gpt-4", "gpt-3.5-turbo"}


class ModelRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {ALLOWED_MODELS}")

        return value

    @field_validator("text")
    @classmethod
    def validate_text_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot be empty or only whitespace")

        return value.strip()


def main():
    logger.info("Testing part 1 q1: trace")
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
        "Case 4": {
            "text": "Hi",
        },
    }

    for case_name, data in cases.items():
        print(f"\n{'=' * 40}")
        print(case_name)
        print(f"Input: {data}")

        try:
            request = ModelRequest(**data)

            print("Result: SUCCESS")
            print(f"Created model: {request}")

        except ValidationError as error:
            print("Result: VALIDATION ERROR")
            logger.error(f"{error}")


if __name__ == "__main__":
    main()
