# Standard library
import asyncio
import time

# Third-party libraries
from loguru import logger
from pydantic import BaseModel, EmailStr, ValidationError

# Local imports


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


class ConcurrentAPICalls:
    async def fetch_user(self, user_id: int) -> User:
        """Simulate an asynchronous API call and validate the user data."""
        logger.info(f"Fetching user {user_id} has started...")

        await asyncio.sleep(2)

        user_data = {
            "id": user_id,
            "name": f"User_{user_id}",
            "email": f"user_{user_id}@example.com",
        }

        try:
            user = User(**user_data)

        except ValidationError as error:
            logger.error(f"Validation failed for user {user_id}: {error}")
            raise

        logger.success(f"Fetching user {user_id} completed successfully.")

        return user

    async def run_multiple(self) -> None:
        """Fetch multiple users concurrently."""
        logger.info("Running multiple concurrent API calls...")

        start = time.time()

        tasks = [
            asyncio.create_task(self.fetch_user(user_id)) for user_id in range(1, 6)
        ]

        try:
            results = await asyncio.gather(*tasks)

            for user in results:
                print(f"Returned user: {user}")

        except ValidationError as error:
            logger.error(f"User validation failed: {error}")

        end = time.time()

        total_time = end - start

        print(f"Total execution time: {total_time:.2f} seconds")

        logger.success("Multiple concurrent API calls completed successfully.")


async def main():
    logger.info("Testing Question Nine")
    api = ConcurrentAPICalls()
    await api.run_multiple()


if __name__ == "__main__":
    asyncio.run(main())
