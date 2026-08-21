# Standard library
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Third-party libraries
from fastapi import FastAPI, HTTPException, Depends, Security
from pydantic import BaseModel, Field, validator
from fastapi.security import APIKeyHeader
from openai import OpenAI
import time
import uvicorn
from loguru import logger
from collections import defaultdict
from datetime import datetime, timedelta
import os

# Configs
ALLOWED_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
REQUEST_LIMIT_PER_MINUTE = 10
VALID_API_KEYS = {"dev-key-1": "ahmed", "dev-key-2": "omar", "dev-key-3": "ayman"}
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

app = FastAPI(title="ML API with Validation + Logging + Rate Limiting + Auth")


async def call_openai_model(
    text: str,
    model: str,
    temperature: float,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
        temperature=temperature,
        max_tokens=150,
    )

    return response.choices[0].message.content


##############################################################


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid api key attempt:{api_key}")
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing Api Key. use X-API-KEY header with a valid api key",
        )
    username = VALID_API_KEYS[api_key]
    logger.info(f"Authenticated user:{username}")
    return username


rate_limit_store: dict[str, list[datetime]] = defaultdict(list)


async def check_rate_limit(user_id: str = Depends(verify_api_key)):

    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=1)

    rate_limit_store[user_id] = [
        req_time for req_time in rate_limit_store[user_id] if req_time > cutoff_time
    ]

    request_count = len(rate_limit_store[user_id])
    if request_count >= 10:
        logger.warning(
            f"Rate Limit exceeded for user : {user_id} ({request_count}/{REQUEST_LIMIT_PER_MINUTE})"
        )
        raise HTTPException(
            status_code=429,
            detail=f"Rate Limit exceeded, Maximum {REQUEST_LIMIT_PER_MINUTE} requests per minute Try Again later!",
        )

    rate_limit_store[user_id].append(current_time)
    logger.info(
        f"Rate limit check passed for {user_id}:{request_count + 1}/{REQUEST_LIMIT_PER_MINUTE}"
    )
    return user_id


class Model_Request(BaseModel):
    """
    Request model with Pydantic validation.
    - text: Must be 1-5000 characters and not empty after strip
    - model: Must be in ALLOWED_MODELS whitelist
    - temperature: Must be between 0.0 and 2.0
    """

    text: str = Field(
        ..., min_length=1, max_length=5000, description="Input text (1-5000 characters)"
    )
    model: str = Field(
        default="gpt-3.5-turbo", description="Model to use for inference"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,  # greater than or equal to 0.0
        le=2.0,  # less than or equal to 2.0
        description="Temperature for generation (0.0-2.0)",
    )

    @validator("model")
    def validate_model(cls, v):
        """Validate model is in whitelist"""
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {ALLOWED_MODELS}")
        return v

    @validator("text")
    def validate_text_content(cls, v):
        """Additional text validation - no empty strings after strip"""
        if not v.strip():
            raise ValueError("Text cannot be empty or only whitespace")
        return v.strip()


class Model_Response(BaseModel):
    input_text: str
    output_text: str
    model_used: str
    processing_time: float
    success: bool
    username: str  # added to show which user made the request


# assuming we have model response and request
@app.post("/predict", response_model=Model_Response)
async def predict(request: Model_Request, user_id: str = Depends(check_rate_limit)):

    logger.info(
        f"Received Prediction request- Model {request.model}, text length {len(request.text)}"
    )
    start_time = time.time()
    try:
        result = await call_openai_model(
            request.text, request.model, request.temperature
        )
        processing_time = time.time() - start_time
        logger.info(
            f"{user_id} Prediction success,Processing time {processing_time:.2f}s"
        )
        return Model_Response(
            input_text=request.text,
            output_text=result,
            model_used=request.model,
            processing_time=processing_time,
            success=True,
            username=user_id,
        )
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"{user_id} prediction fail error {e!s} Processing time {processing_time:.2f}s"
        )
        return Model_Response(
            input_text=request.text,
            output_text=f"Error : {e!s}",
            model_used=request.model,
            processing_time=processing_time,
            success=False,
            username=user_id,
        )
