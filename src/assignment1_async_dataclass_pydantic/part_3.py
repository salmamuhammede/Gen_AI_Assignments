# Standard library
from dataclasses import dataclass, field

# Third-party libraries
from loguru import logger

# Local imports


@dataclass
class Product:
    name: str
    price: float
    quantity: int
    discount: float = 0.0

    def total_price(self) -> float:
        """a method to calculate the total price of the product
        according to its info (quantity, discount,price)

        Returns:
            total_price (float): this is the final price of the product
        """
        logger.info(f"Calculating the total price for {self.name} is starting")
        total_price = self.price * self.quantity * (1 - self.discount)
        logger.success(
            f"Calculating the total price for {self.name} has completed successfully | total price is: {total_price}"
        )
        return total_price


@dataclass
class Student:
    name: str
    age: int
    courses: list = field(default_factory=list)

    def __post_init__(self) -> None:
        """This is like a custom validation for age because dataclasses doesn't have validation by default"""
        logger.info("Validating age is starting ...")
        if self.age < 18:
            raise ValueError("Student age must be at least 18.")

        logger.success(f"Age for {self.name} is valid.")


def main():
    logger.info("Testing Question four")
    product_1 = Product(name="Washing Machine", price=20000, quantity=2, discount=0.20)
    product_2 = Product(name="Laptop", price=10000, quantity=1, discount=0.10)
    print(f"The total price for {product_1.name} is :{product_1.total_price()}")
    print(f"The total price for {product_2.name} is :{product_2.total_price()}")
    ##########################################
    logger.info("Testing Question five")
    student_1 = Student(name="Salma", age=23)
    student_2 = Student(name="Mariam", age=21)

    student_1.courses.append("Python")

    print(f"{student_1.name} courses: {student_1.courses}")
    print(f"{student_2.name} courses: {student_2.courses}")


if __name__ == "__main__":
    main()
