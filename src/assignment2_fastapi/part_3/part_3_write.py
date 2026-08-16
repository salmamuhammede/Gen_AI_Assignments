# Standard library
from collections import defaultdict
from datetime import datetime
from http.client import HTTPException
from typing import Dict, List

# Third-party libraries
from fastapi import Depends, Request

# the new added function for question 11
def get_user_id(request: Request) -> str:
    return request.headers.get("X-User-ID", "anonymous")


REQUEST_LIMIT_PER_MINUTE = 10
rate_limit_store: Dict[str, List[datetime]] = defaultdict(list)


async def check_rate_limit(user_id: str = Depends(get_user_id)):
    current_time = datetime.datetime.now()
    cutoff_time = current_time - datetime.timedelta(minutes=1)
    rate_limit_store[user_id] = [
    t for t in rate_limit_store[user_id]
    if t > cutoff_time
    ]
    request_count = len(rate_limit_store[user_id])
    if request_count >= 10:
        raise HTTPException(
            status_code=429,
            detail="Rate Limit exceeded..."
            )
    rate_limit_store[user_id].append(current_time)
    return user_id