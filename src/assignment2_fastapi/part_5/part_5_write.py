"""
Feature 5: adding multiple model endpoints
- /summarize endpoint for text summarization
- /translate endpoint for text translation
- each endpoint has specialized validation
- different system prompts will be given for each task
"""
# imports 
from fastapi import FastAPI, HTTPException, Depends , Security
from pydantic import BaseModel, Field, validator
from fastapi.security import APIKeyHeader
from openai import OpenAI
import time
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict 
from datetime import datetime,timedelta
from typing import Dict,List , Optional
from dotenv import load_dotenv
import os 

load_dotenv()
# initialize of api
app = FastAPI(title="ML API with Validation + Logging + Rate Limiting + Auth + Multiple end Points")


# Setup Logging all requests and responses
logging.basicConfig(level=logging.INFO,
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    handlers = [
                        RotatingFileHandler("api-logs.log",maxBytes=10485760,backupCount=5),
                        logging.StreamHandler(), # Also log to console
                    ])

logger = logging.getLogger(__name__)
logger.info("="*60)
logger.info("Application Starting - Logging Enabled")
logger.info("="*60)

# ==================== CONFIGURATION ====================
# Allowed models whitelist for validation
ALLOWED_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
REQUEST_LIMIT_PER_MINUTE = 10

VALID_API_KEYS = {"dev-key-1":"ahmed","dev-key-2":"omar","dev-key-3":"ayman"}
## authentication part
api_key_header = APIKeyHeader(name="X-API-KEY",auto_error=True)
# "X-API-KEY":"dev-key-1"
async def verify_api_key(api_key:str=Security(api_key_header))->str:
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid api key attempt:{api_key}")
        raise HTTPException(
            status_code=  403,detail="Invalid or missing Api Key. use X-API-KEY header with a valid api key"
        )
    username = VALID_API_KEYS[api_key]
    logger.info(f"Authenticated user:{username}")
    return username
# ==================== PYDANTIC MODELS WITH VALIDATION ====================
# Rate Limiting
rate_limit_store :Dict[str,List[datetime]] = defaultdict(list)
# def get_user_id()->str:
#     return "default"
async def check_rate_limit(user_id:str=Depends(verify_api_key)):
    """check if user has exceeded rate limit Implement sliding window rate
    How it works
    1. Remove timestamps older than 1 minute
    2. check if remaining request >=Limit
    3. if exceeded , raise status code : 429
    4. otherwise, add current timestamp
    """
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=1)
    
    #remove old requests outside the time window
    rate_limit_store[user_id] = [req_time for req_time in rate_limit_store[user_id] if req_time > cutoff_time ]
    # check if user exceeded limit :
    request_count = len(rate_limit_store[user_id])
    if request_count>=10:
        logger.warning(f"Rate Limit exceeded for user : {user_id} ({request_count}/{REQUEST_LIMIT_PER_MINUTE})")
        raise HTTPException(
            status_code=429,
            detail=f"Rate Limit exceeded, Maximum {REQUEST_LIMIT_PER_MINUTE} requests per minute Try Again later!"
        )
    # add current request timestamp
    rate_limit_store[user_id].append(current_time)
    logger.info(f"Rate limit check passed for {user_id}:{request_count+1}/{REQUEST_LIMIT_PER_MINUTE}")
    return user_id

class Model_Request(BaseModel):
    """
    Request model with Pydantic validation.
    - text: Must be 1-5000 characters and not empty after strip
    - model: Must be in ALLOWED_MODELS whitelist
    - temperature: Must be between 0.0 and 2.0
    """

    text: str = Field(..., min_length=1, max_length=5000, description="Input text (1-5000 characters)")
    model: str = Field(default="gpt-3.5-turbo", description="Model to use for inference")
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

class SummarizeRequest(BaseModel):
    text:str = Field(...,min_length=50,max_length=10000,description="Text to be summarized (min 50 chars)")
    max_length:int = Field(default=150,ge=50,le=500,description="Max Length Summary words")
    
class TranslateRequest(BaseModel):
    text:str = Field(...,min_length=50,max_length=10000,description="Text to be translated (min 50 chars)")
    target_language:str = Field(...,description="Target Language ex: Spanish , French , German")
    source_language:str = Field(...,description="Source Language ex: Arabic , English")
    @validator("source_language")
    def validate_language(cls,v):
        if not v.strip():
            raise ValueError("Source Language cannot be empty")
        return v.strip()
    
    @validator("target_language")
    def validate_language(cls,v):
        if not v.strip():
            raise ValueError("Target Language cannot be empty")
        return v.strip()
    
    
    

class Model_Response(BaseModel):
    input_text: str
    output_text: str
    model_used: str
    processing_time: float
    success: bool
    username:str # added to show which user made the request
    endpoint:str = "predict" # track which endpoint was used


# ==================== ML INFERENCE ====================


async def call_openai_model(text: str, model: str, temperature: float,system_prompt:Optional[str]=None) -> str:
    """Call OpenAi Api"""
    logger.info(f"Calling OpenAI API - Model {model} temp {temperature} , text length {len(text)}")
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        message = []
        if system_prompt:
            message.append({"role":"system","content":system_prompt})
        message.append({"role":"user","content":text})
        response = client.chat.completions.create(
            model=model, messages=message, temperature=temperature, max_tokens=150
        )
        result = response.choices[0].message.content
        logger.info(f"openapi call succesful - response length {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Openai API error {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

async def summarize_text(text:str,max_length:int=150)->str:
    system_prompt = (f"You are a summarization assistant. Summarize the following text concisely in maximum {max_length} words.")
    return await call_openai_model(text,"gpt-3.5-turbo",.3,system_prompt)

async def translate_text(text:str,source_language:str, target_language: str) -> str:
    system_prompt = (f"You are a translation assistant. Translate the following text concisley from source language {source_language} into target language {target_language} maintain the original meaning and tone.")
    return await call_openai_model(text,"gpt-3.5-turbo",.3,system_prompt)
    
# ==================== API ENDPOINTS ====================


@app.post("/predict", response_model=Model_Response)
async def predict(request: Model_Request,user_id:str=Depends(check_rate_limit)):
    """
    Call AI model with input validation.

    The request will be automatically validated:
    - Text length must be 1-5000 characters
    - Model must be in whitelist
    - Temperature must be 0.0-2.0
    - test keys : dev-key-1/2/3
    """
    logger.info(f"Received Prediction request- Model {request.model}, text length {len(request.text)}")
    start_time = time.time()
    try:
        result = await call_openai_model(request.text, request.model, request.temperature)
        processing_time = time.time() - start_time
        logger.info(f"{user_id} Predicition success,Processing time {processing_time:.2f}s")
        return Model_Response(
            input_text=request.text,
            output_text=result,
            model_used=request.model,
            processing_time=processing_time,
            success=True,
            username=user_id,
            endpoint="predict"
        )
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"{user_id} prediction fail error {str(e)} Processing time {processing_time:.2f}s")
        return Model_Response(
            input_text=request.text,
            output_text=f"Error : {str(e)}",
            model_used=request.model,
            processing_time=processing_time,
            success=False,
            username=user_id,
            endpoint="predict"
        )
@app.post("/summarize", response_model=Model_Response)
async def summarize(request: SummarizeRequest,user_id:str=Depends(check_rate_limit)):
    """
    Call AI model with input validation.

    The request will be automatically validated:
    - Text length must be 1-5000 characters
    - Model must be in whitelist
    - Temperature must be 0.0-2.0
    - test keys : dev-key-1/2/3
    """
    logger.info(f"Received Summarization request- Model {request.model}, text length {len(request.text)}")
    start_time = time.time()
    try:
        result = await summarize_text(request.text, request.max_length)
        processing_time = time.time() - start_time
        logger.info(f"{user_id} Summarization success,Processing time {processing_time:.2f}s")
        return Model_Response(
            input_text=request.text,
            output_text=result,
            model_used="gpt-3.5-turbo",
            processing_time=processing_time,
            success=True,
            username=user_id,
            endpoint="summarize"
        )
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"{user_id} Summary fail error {str(e)} Processing time {processing_time:.2f}s")
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/translate", response_model=Model_Response)
async def translate(request: TranslateRequest,user_id:str=Depends(check_rate_limit)):
    """
    Call AI model with input validation.

    The request will be automatically validated:
    - Text length must be 1-5000 characters
    - Model must be in whitelist
    - Temperature must be 0.0-2.0
    - test keys : dev-key-1/2/3
    """
    logger.info(f"Received Prediction request- Model {request.model}, text length {len(request.text)}")
    start_time = time.time()
    try:
        result = await translate_text(request.text, request.source_language,request.target_language)
        processing_time = time.time() - start_time
        logger.info(f"{user_id} Translating success,Processing time {processing_time:.2f}s")
        return Model_Response(
            input_text=request.text,
            output_text=result,
            model_used="gpt-3.5-turbo",
            processing_time=processing_time,
            success=True,
            username=user_id,
            endpoint="translate"
        )
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"{user_id} Translation fail error {str(e)} Processing time {processing_time:.2f}s")
        raise HTTPException(status_code=500,detail=str(e))
    

    

@app.get("/rate-limit-status")
async def rate_limit_status(user_id:str=Depends(verify_api_key)):
    
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=1)
    
    # count requests in last minute
    recent_requests = [req for req in rate_limit_store[user_id] if req >cutoff_time]
    remaining = max(0,REQUEST_LIMIT_PER_MINUTE-len(recent_requests))
    return {
    "user_id":user_id,
    "requests_in_last_minute":len(recent_requests),
    "rate_limit":REQUEST_LIMIT_PER_MINUTE,
    "remaining":remaining,
    "Limit_resets_in":"60 seconds"
}
@app.get("/health")
async def health():
    logger.info(f"Health check requested")
    return {"status": "healthy", "features": ["Input Validation","Logging","Rate limiting","Api Key auth"]}


@app.get("/")
async def root():
    logger.info(f"Root endpoint accessed")
    return {
        "message": "ML API with Input Validation",
        "version": "1.0 - Validation + Logging + Rate Limit",
        "features": {
            "validation": {
                "text_length": "1-5000 characters",
                "allowed_models": ALLOWED_MODELS,
                "temperature_range": "0.0-2.0",
                "whitespace_check": "Text cannot be empty or only whitespace",
            },
            "Rate Limit":{
                "limit" :"requests per user 10 requests per minute",
                "Sliding" :"window rate limiting ",
                "per user": "tracking ",
                "Returns 429": "status code when limit exceeded"
            },
            "Api Key Auth":{
                            "method" :"API KEY in header x api key",
                            "test keys" :"dev-key 1/2/3 ",
                            "per user": "tracking ",
                            "example": "Api-key-based with user mapping"
                        }
        },
        "endpoints": {
            "/predict": "POST - Text generation with validation",
            "/summarize": "POST - Text summarization with validation",
            "/translate": "POST - Text translation with validation",
            "/predict": "POST - Text generation with validation",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation",
            "/rate-limit-status":"Get - Rate Remaining for user id"
        },
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ML API v4: Authentication")
    print("=" * 60)
    print("✅ Feature 1: Pydantic validation with length & whitelists")
    print("✅ Feature 2 : Logging for errors or warning or information")
    print("✅ Feature 3: Rate limiting to protect my api")
    print("✅ Feature 4: Api key Authentication")
    print("   - Text: 1-5000 characters")
    print(f"   - Models: {ALLOWED_MODELS}")
    print("   - Temperature: 0.0-2.0")
    print("=" * 60)
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
