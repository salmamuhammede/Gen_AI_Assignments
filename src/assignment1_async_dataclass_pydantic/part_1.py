# Standard library
import asyncio
import time

# Third-party libraries
from loguru import logger

# Local imports


class SynchronousExecution:
    def __init__(self):
        pass

    def task(self, name: str, seconds: float) -> None:
        """This is to test synchronous execution behavior

        Args:
            name (str): name of the task
            seconds (float): time for sleeping
        """
        logger.info("Running single synchronous execution has started ...")
        print(f"{name} has started")
        time.sleep(seconds)
        print(f"{name} has finished")
        logger.success(
            "Running single synchronous execution has completed successfully ..."
        )

    def run_multiple(self, durations: list[float]) -> None:
        """This is to test synchronous execution behavior
        with multiple tasks

        Args:
            durations (List[float]): list of all tasks's duration
        """
        logger.info("Running multiple synchronous execution has started ...")
        start = time.time()
        for i in range(len(durations)):
            self.task(f"Task {i + 1}", durations[i])
        end = time.time()
        total_time = end - start
        print(f"Total time of execution is :{total_time} seconds")
        logger.success(
            "Running multiple synchronous execution has completed successfully ..."
        )


class AsynchronousExecution:
    def __init__(self):
        pass

    async def task(self, name: str, seconds: float) -> None:
        """This is to test asynchronous execution behavior

        Args:
            name (str): name of the task
            seconds (float): time for sleeping
        """
        logger.info("Running single asynchronous execution has started ...")
        print(f"{name} has started")
        await asyncio.sleep(seconds)
        print(f"{name} has finished")
        logger.success(
            "Running single asynchronous execution has completed successfully ..."
        )

    async def run_multiple(self, durations: list[float]) -> None:
        """This is to test asynchronous execution behavior
        with multiple tasks

        Args:
            durations (List[float]): list of all tasks's duration
        """
        logger.info("Running multiple asynchronous execution has started ...")
        start = time.time()
        await asyncio.gather(
            *[self.task(f"Task {i + 1}", durations[i]) for i in range(len(durations))]
        )

        end = time.time()
        total_time = end - start
        print(f"Total time of execution is :{total_time} seconds")
        logger.success(
            "Running multiple asynchronous execution has completed successfully ..."
        )


async def main() -> None:
    tasks_durations = [2, 2, 1]
    # ================= SYNCHRONOUS ================= #
    logger.info("Testing Question one part_1")
    synchronous_executer = SynchronousExecution()
    synchronous_executer.run_multiple(tasks_durations)
    # ================= ASYNCHRONOUS ================= #
    logger.info("Testing Question one part_2")
    asynchronous_executer = AsynchronousExecution()
    await asynchronous_executer.run_multiple(tasks_durations)


if __name__ == "__main__":
    asyncio.run(main())
