#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import asyncio
import resource
from asyncio.queues import Queue

TERMINATOR = object()

QUEUE_SIZE_PER_WORKER = 256


class TaskPool(object):
    def queue_size(self):
        soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
        qs = min(self.num_workers * QUEUE_SIZE_PER_WORKER, soft)
        if self.debug:
            print(f"TaskPool queue size : {qs}")
        return qs

    def __init__(self, num_workers: int, debug=False):
        if num_workers <= 0:
            raise RuntimeError("number of worker is zero")
        self.debug = debug
        self.num_workers = num_workers
        self.tasks = Queue(maxsize=self.queue_size())
        self.workers = []
        for _ in range(num_workers):
            worker = asyncio.ensure_future(self.worker())
            self.workers.append(worker)

    async def worker(self):
        while True:
            future, task = await self.tasks.get()
            if task is TERMINATOR:
                break
            result = await asyncio.wait_for(task, None)
            future.set_result(result)

    async def submit(self, task):
        future = asyncio.Future()
        await self.tasks.put((future, task))
        return future

    async def join(self):
        for _ in self.workers:
            await self.tasks.put((None, TERMINATOR))
        await asyncio.gather(*self.workers)
