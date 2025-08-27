# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import asyncio
from aiohttp import ClientSession, TCPConnector, ClientTimeout


class AsyncIOExecutor:
    MAX_HTTP_REQUESTS = 50

    @classmethod
    def run_in_event_loop(cls, task):
        """Run the given task in async event loop untill complete"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        event_loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(task)
        event_loop.run_until_complete(future)
        event_loop.close()
        return future.result()

    @classmethod
    def execute_http_tasks(cls, max_requests=MAX_HTTP_REQUESTS, *tasks):
        """Get the http tasks future and run in event loop"""
        return cls.run_in_event_loop(cls.__get_http_tasks_future(max_requests, tasks))

    @classmethod
    async def __get_http_tasks_future(cls, max_requests, tasks):
        """Create futures for each http task and return a future aggregating results from them."""
        # Restrict the max no of http requests running at a time in the loop using semaphore
        semaphore = asyncio.Semaphore(max_requests)
        http_tasks = []

        # Timeout for the whole operation set to 30 minutes
        timeout = ClientTimeout(total=30*60)
        async with ClientSession(timeout=timeout, connector=TCPConnector(verify_ssl=False),trust_env=True) as http_client_session:
            for task in tasks:
                http_task = asyncio.ensure_future(
                    cls.__get_bound_task(semaphore, task, http_client_session))
                http_tasks.append(http_task)
            return await asyncio.gather(*http_tasks)

    @classmethod
    async def __get_bound_task(cls, semaphore, task, http_client_session):
        """Acquire the semaphore before executing the task."""
        async with semaphore:
            return await task.execute_async(http_client_session=http_client_session)
