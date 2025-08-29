import asyncio


async def async_task_executor(tasks) -> tuple:
    if not tasks:
        return tuple()
    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    for task in pending:
        task.cancel()
    res = []
    for task in tasks:
        if task.exception():
            raise task.exception()
        else:
            res.append(task.result())
    return tuple(res)
