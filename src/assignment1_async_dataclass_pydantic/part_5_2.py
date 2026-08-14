# Standard library
import asyncio
import time
from dataclasses import dataclass, field
from typing import ClassVar

# Third-party libraries
from loguru import logger
from pydantic import BaseModel, EmailStr, Field, field_validator

# Local imports


database = {}


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=18, le=90)

    @field_validator("name")
    @classmethod
    def check_name(cls, name: str) -> str:
        """Validate that the user name contains at least 3 characters."""
        logger.info("Validating user name...")

        if len(name) < 3:
            raise ValueError("User name must contain at least 3 characters.")

        logger.success("User name is valid.")

        return name


@dataclass
class User:
    name: str
    email: str
    age: int
    id: int = field(init=False)

    _next_id: ClassVar[int] = 1

    def __post_init__(self) -> None:
        """Generate a unique ID automatically."""
        self.id = User._next_id
        User._next_id += 1


class ConcurrentAPICalls:
    async def save_user(self, user: UserCreate) -> User:
        """Simulate saving a user to an asynchronous database."""
        logger.info(f"Saving user {user.name}...")

        await asyncio.sleep(1)

        saved_user = User(
            name=user.name,
            email=str(user.email),
            age=user.age,
        )

        database[saved_user.id] = saved_user

        logger.success(
            f"User {saved_user.name} saved successfully with ID {saved_user.id}."
        )

        return saved_user

    async def find_user(self, user_id: int) -> User:
        """Retrieve a user from the database by ID."""
        logger.info(f"Searching for user {user_id}...")

        try:
            user = database[user_id]

        except KeyError:
            logger.error(f"User with ID {user_id} does not exist.")
            raise

        logger.success(f"User {user_id} found successfully.")

        return user

    async def run_multiple(
        self,
        users: list[UserCreate],
    ) -> None:
        """Save multiple users concurrently."""
        logger.info("Running multiple concurrent API calls...")

        start = time.time()

        tasks = [asyncio.create_task(self.save_user(user)) for user in users]

        results = await asyncio.gather(*tasks)

        for user in results:
            print("User created successfully:")
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Age: {user.age}")
            print("*" * 30)

        total_time = time.time() - start

        print(f"Total execution time: {total_time:.2f} seconds")

        logger.success("Multiple concurrent API calls completed successfully.")


async def main():
    logger.info("Testing Question Ten")

    api = ConcurrentAPICalls()

    users = [
        UserCreate(
            name="Amr",
            email="amr@example.com",
            age=25,
        ),
        UserCreate(
            name="Ahmed",
            email="ahmed@example.com",
            age=30,
        ),
        UserCreate(
            name="Mohamed",
            email="mohamed@example.com",
            age=28,
        ),
        UserCreate(
            name="Omar",
            email="omar@example.com",
            age=24,
        ),
        UserCreate(
            name="Ali",
            email="ali@example.com",
            age=27,
        ),
    ]

    await api.run_multiple(users)

    # Bonus: find a user
    user = await api.find_user(1)

    print("\nFound user:")
    print(user)


if __name__ == "__main__":
    asyncio.run(main())
