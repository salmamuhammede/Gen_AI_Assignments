# Standard library
import asyncio
import time

# Third-party libraries
from loguru import logger

# Local imports


class Concurrent_API_Calls:
    def __init__(self):
        pass

    async def fetch_data(self, api_name: str, delay: float) -> str:
        """this is the single function that each api try to mock data fetching process
        Args:
            api_name (str): the name of each api
            delay (float): the duration of it

        Returns:
            result (str): the final result of data fetching operation
        """

        logger.info("Running single asynchronous api call has started ...")
        print(f"{api_name} has started")
        await asyncio.sleep(delay)
        result = f"{api_name} has fetched the data"
        print(f"{api_name} has finished")
        logger.success(
            "Running single asynchronous api call has completed successfully ..."
        )
        return result

    async def run_multiple(self, durations: list[float]) -> None:
        """This is to test asynchronous execution behavior
        with multiple api calls

        Args:
            durations (List[float]): list of all tasks's duration
        """
        logger.info("Running multiple concurrent api calls has started ...")
        start = time.time()
        apis = [
            asyncio.create_task(self.fetch_data(f"API {i + 1}", durations[i]))
            for i in range(len(durations))
        ]
        results = await asyncio.gather(*apis)
        for i, result in enumerate(results):
            print(f"Api {i + 1} result's is : {result}")

        end = time.time()
        total_time = end - start
        print(f"Total time of execution is :{total_time} seconds")
        logger.success(
            "Running multiple concurrent api calls has completed successfully ..."
        )


class Async_Exception_Handling:
    def __init__(self):
        pass

    async def divide(self, a: float, b: float) -> float:
        """Apply division operation asynchronously.

        Args:
            a: The numerator.
            b: The denominator.

        Returns:
            The result of the division.

        Raises:
            ZeroDivisionError: If the denominator is zero.
        """

        try:
            logger.info("Running division has started ...")

            print(f"Numerator is: {a} and denominator is: {b}")

            result = a / b

            logger.success("Division operation has completed successfully ...")

            return result

        except ZeroDivisionError as e:
            logger.error("Zero Division error has occurred")
            print(f"Error: {e}")

            raise

    async def run_multiple(self, pairs: list[tuple[float, float]]) -> None:
        """Run multiple division operations concurrently.

        Args:
            pairs: List of numerator and denominator pairs.
        """

        logger.info(
            "Running multiple division operations with exception handling "
            "has started ..."
        )

        # Create tasks
        operations = [
            asyncio.create_task(self.divide(pair[0], pair[1])) for pair in pairs
        ]

        # Wait for all tasks without stopping when one fails
        results = await asyncio.gather(*operations, return_exceptions=True)

        # Handle results and exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Operation {i + 1} failed: {result}")

            else:
                print(f"Operation {i + 1} successful: {result}")

        logger.success(
            "Running multiple division operations with exception "
            "handling has completed successfully ..."
        )


async def main():
    logger.info("Testing Question two")
    api_executor = Concurrent_API_Calls()
    durations = [2, 1, 3, 2, 1]
    await api_executor.run_multiple(durations)
    ##########################################
    logger.info("Testing Question three")
    executor = Async_Exception_Handling()
    pairs = [(10, 2), (20, 4), (5, 0), (30, 5)]
    await executor.run_multiple(pairs)


if __name__ == "__main__":
    asyncio.run(main())
