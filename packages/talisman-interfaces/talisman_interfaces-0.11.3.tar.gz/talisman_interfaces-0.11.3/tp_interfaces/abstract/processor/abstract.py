import asyncio
from functools import partial
from typing import AsyncIterator, Protocol, Sequence, Tuple, Type, TypeVar, runtime_checkable

from tp_interfaces.abstract.model import AsyncModel
from tp_interfaces.abstract.schema import ImmutableBaseModel
from tp_interfaces.helpers.task_execution import async_task_executor
from tp_interfaces.logging.context import with_log_extras

_Config = TypeVar('_Config', bound=ImmutableBaseModel)
_Input = TypeVar('_Input')
_Output = TypeVar('_Output')


@runtime_checkable
class AbstractProcessor(AsyncModel, Protocol[_Config, _Input, _Output]):
    async def process_doc(self, document: _Input, config: _Config) -> _Output:
        pass

    async def process_docs(self, documents: Sequence[_Input], config: _Config) -> Tuple[_Output, ...]:
        log_extras = with_log_extras(doc_id=lambda kwargs: kwargs['document'].id)
        wrapped_processor = log_extras(self.process_doc)
        configured_processor = partial(wrapped_processor, config=config)
        coroutines = map(configured_processor, documents)
        tasks = [asyncio.create_task(coro) for coro in coroutines]
        return await async_task_executor(tasks)

    async def process_stream(
            self,
            documents: AsyncIterator[_Input],
            config: _Config,
            batch_size: int,
            concurrency: int = 1,
            results_queue_max_size: int = 0
    ) -> AsyncIterator[_Output]:
        """
        Asynchronously processes a stream of documents in batches and yields results as they become available.

        This method consumes an asynchronous stream of `_Input` objects, groups them into batches of the specified size,
        and processes the batches concurrently using `process_docs` method. Results are streamed back as they are processed.

        Notes:
        - Output order is **not guaranteed** to match input order due to concurrent batch processing.
        - Exceptions during processing are skipped silently.
        - Processing begins immediately and continues as input documents are streamed in.

        :param documents: asynchronous stream of input documents
        :param config: configuration object for processing (same for all document batches)
        :param batch_size: number of documents per batch
        :param concurrency: number of concurrent workers. Defaults to 1
        :param results_queue_max_size: maximum size of the results queue. Defaults to 0 (unbounded)
        :return: asynchronous iterator over processed documents
        """

        batches_queue: asyncio.Queue[Sequence[_Input]] = asyncio.Queue(maxsize=concurrency)
        results_queue: asyncio.Queue[_Output | Exception | None] = asyncio.Queue(maxsize=results_queue_max_size)

        async def batcher():
            batch = []
            async for doc in documents:
                batch.append(doc)
                if len(batch) >= batch_size:
                    await batches_queue.put(tuple(batch))
                    batch = []
            if batch:
                await batches_queue.put(tuple(batch))

        async def worker():
            while True:
                batch = await batches_queue.get()
                try:
                    result = await self.process_docs(batch, config)
                    for doc in result:
                        await results_queue.put(doc)
                except Exception as e:
                    await results_queue.put(e)
                finally:
                    batches_queue.task_done()  # mark batch processed after adding results in queue

        batcher_task = asyncio.create_task(batcher())
        worker_tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]

        async def finalizer():
            await batcher_task  # no more batches will be added to batches queue
            await batches_queue.join()  # all added tasks are processed
            for worker_task in worker_tasks:
                worker_task.cancel()  # interrupt workers (they are blocked with input_queue.get method)
            await asyncio.gather(*worker_tasks, return_exceptions=True)  # all workers now awaited
            await results_queue.put(None)  # end of results signal

        asyncio.create_task(finalizer())

        while True:
            result = await results_queue.get()
            if result is None:
                break
            if isinstance(result, Exception):
                continue  # TODO: add logging
            yield result

    @property
    def config_type(self) -> Type[_Config]:
        raise NotImplementedError

    @property
    def input_type(self) -> Type[_Input]:
        raise NotImplementedError

    @property
    def output_type(self) -> Type[_Output]:
        raise NotImplementedError
