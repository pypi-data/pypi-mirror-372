from __future__ import annotations
import asyncio, contextlib, inspect, json
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
from sibi_dst.utils import Logger

Payload = Union[str, bytes, dict, list, None]
Task2 = Callable[[asyncio.Queue, str], Awaitable[Payload]]
Task3 = Callable[[asyncio.Queue, str, Dict[str, Any]], Awaitable[Payload]]
TaskFn = Union[Task2, Task3]

def _as_sse_msg(event: str, data: Any) -> dict:
    return {"event": event, "data": json.dumps(data) if not isinstance(data, (str, bytes)) else data}

class SSERunner:
    def __init__(self, *, task: TaskFn, logger: Logger, ping: int = 15,
                 headers: Optional[dict] = None, auto_complete: bool = True) -> None:
        self.task = task
        self.logger = logger
        self.ping = ping
        self.headers = headers or {"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"}
        self.auto_complete = auto_complete
        self._expects_ctx = len(inspect.signature(task).parameters) >= 3

    async def _call_task(self, queue: asyncio.Queue, task_id: str, ctx: Dict[str, Any]) -> Payload:
        if self._expects_ctx:
            return await self.task(queue, task_id, ctx)  # type: ignore[misc]
        return await self.task(queue, task_id)           # type: ignore[misc]

    async def _worker(self, queue: asyncio.Queue, task_id: str, ctx: Dict[str, Any]) -> None:
        self.logger.info(f"SSE {task_id}: start")
        try:
            await queue.put(_as_sse_msg("progress", {"message": "Task started"}))
            payload = await self._call_task(queue, task_id, ctx)
            if self.auto_complete:
                final = payload if payload is not None else {"status": "complete"}
                await queue.put(_as_sse_msg("complete", final))
            self.logger.info(f"SSE {task_id}: complete")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"SSE {task_id} failed: {e}", exc_info=True)
            await queue.put(_as_sse_msg("error", {"detail": str(e)}))
        finally:
            await queue.put(None)

    def endpoint(self):
        async def handler(request: Request):  # <-- only Request
            queue: asyncio.Queue = asyncio.Queue()
            task_id = str(asyncio.get_running_loop().time()).replace(".", "")

            ctx: Dict[str, Any] = {
                "path": dict(request.path_params),          # <-- pull path params here
                "query": dict(request.query_params),
                "method": request.method,
            }
            if request.headers.get("content-type", "").startswith("application/json"):
                try:
                    ctx["body"] = await request.json()
                except Exception:
                    ctx["body"] = None

            worker = asyncio.create_task(self._worker(queue, task_id, ctx))

            async def gen():
                try:
                    while True:
                        msg = await queue.get()
                        if msg is None:
                            break
                        yield msg
                finally:
                    if not worker.done():
                        worker.cancel()
                        with contextlib.suppress(Exception):
                            await worker

            return EventSourceResponse(gen(), ping=self.ping, headers=self.headers)
        return handler

__all__ = ["SSERunner", "_as_sse_msg"]