# Standard library


# Third-party libraries
from loguru import logger
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator

# Local imports


class User(BaseModel):
    id: int
    name: str
    email: str
    age: int


class Student(BaseModel):
    name: str
    age: int = Field(ge=18, le=60)
    grade: float = Field(ge=0, le=100)

    @field_validator("name")
    @classmethod
    def check_name(cls, name) -> str:
        """This is like a custom validation for age because dataclasses doesn't have validation by default"""
        logger.info("Validating age is starting ...")
        if len(name) < 3:
            raise ValueError("Student name length must be with minimum 3 characters.")

        logger.success("Student name is valid.")
        return name


class Address(BaseModel):
    city: str
    country: str


class User2(BaseModel):
    name: str
    email: EmailStr
    address: Address


def main():
    logger.info("Testing Question Six")

    user = User(
        id="101",
        name="Amr",
        email="amr@example.com",
        age="25",
    )

    print(f"The created user info is: {user}")
    print(f"The data type of user id is: {type(user.id)}")
    print(f"The data type of user age is: {type(user.age)}")
    print(
        "Note: Pydantic automatically converts the numeric strings 101 and 25 into integers because the model fields are declared as int"
    )
    ##########################################
    logger.info("Testing Question Seven")

    # 1. Valid data
    try:
        student = Student(
            name="Amr",
            age=25,
            grade=90,
        )
        print(f"Valid student: {student}")

    except ValidationError as error:
        logger.error(f"Validation error:\n{error}")

    # 2. Invalid name
    try:
        Student(
            name="Am",
            age=25,
            grade=90,
        )

    except ValidationError as error:
        logger.error(f"Invalid name:\n{error}")

    # 3. Invalid age
    try:
        Student(
            name="Amr",
            age=17,
            grade=90,
        )

    except ValidationError as error:
        logger.error(f"Invalid age:\n{error}")

    # 4. Invalid grade
    try:
        Student(
            name="Amr",
            age=25,
            grade=105,
        )

    except ValidationError as error:
        logger.error(f"Invalid grade:\n{error}")
    ###########################################################
    logger.info("Testing Question Eight")

    # Valid user
    try:
        user = User2(
            name="Amr",
            email="amr@example.com",
            address={
                "city": "Sadat",
                "country": "Egypt",
            },
        )

        # 1. Print user's city
        print(f"User's city: {user.address.city}")

        # 2. Convert model to dictionary
        user_dict = user.model_dump()
        print(f"User as dictionary: {user_dict}")

    except ValidationError as error:
        logger.error(f"User validation failed: {error}")

    # Invalid email
    try:
        _ = User2(
            name="Amr",
            email="invalid-email",
            address={
                "city": "Sadat",
                "country": "Egypt",
            },
        )

    except ValidationError as error:
        logger.error(f"Invalid email: {error}")


if __name__ == "__main__":
    main()
