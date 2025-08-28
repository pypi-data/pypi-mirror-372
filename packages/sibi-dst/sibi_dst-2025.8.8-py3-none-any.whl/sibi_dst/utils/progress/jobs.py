# jobs.py
import asyncio, json, uuid
import contextlib
import os

import redis.asyncio as redis
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
host = os.getenv("REDIS_HOST", "0.0.0.0")
port = int(os.getenv("REDIS_PORT", 6379))
db = int(os.getenv("REDIS_DB", 0))
router = APIRouter(prefix="/jobs", tags=["Jobs"])
r = redis.Redis(host=host, port=port, db=db, decode_responses=True)  # strings for pubsub

CHANNEL = lambda job_id: f"job:{job_id}:events"
KEY_STATUS = lambda job_id: f"job:{job_id}:status"   # JSON blob with state/progress
KEY_RESULT = lambda job_id: f"job:{job_id}:result"   # final payload

async def publish(job_id: str, event: str, data: dict):
    msg = json.dumps({"event": event, "data": data})
    await r.publish(CHANNEL(job_id), msg)
    # store last status
    await r.set(KEY_STATUS(job_id), json.dumps({"event": event, "data": data}))

# ---- Worker entry (can live in a separate process) ----
async def run_job(job_id: str):
    try:
        await publish(job_id, "progress", {"message": "Initializing..."})
        # ... do actual work, emit more progress
        await asyncio.sleep(0.2)
        # compute result
        result = [{"id": 1, "ok": True}]
        await r.set(KEY_RESULT(job_id), json.dumps(result), ex=3600)
        await publish(job_id, "complete", {"records": len(result)})
    except Exception as e:
        await publish(job_id, "error", {"detail": str(e)})

# ---- API ----
@router.post("/start")
async def start_job():
    job_id = str(uuid.uuid4())
    # enqueue: prefer Celery/RQ/etc. For demo we detach a task.
    asyncio.create_task(run_job(job_id))
    return {"job_id": job_id}

@router.get("/{job_id}/stream")
async def stream(job_id: str):
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL(job_id))

    async def gen():
        try:
            # emit latest known status immediately, if any
            if (s := await r.get(KEY_STATUS(job_id))):
                yield {"event": "progress", "data": s}
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30.0)
                if msg and msg["type"] == "message":
                    payload = msg["data"]  # already a JSON string
                    yield {"event": "message", "data": payload}
                await asyncio.sleep(0.01)
        finally:
            with contextlib.suppress(Exception):
                await pubsub.unsubscribe(CHANNEL(job_id))
                await pubsub.close()

    return EventSourceResponse(
        gen(),
        ping=15,
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )

@router.get("/{job_id}/status")
async def status(job_id: str):
    s = await r.get(KEY_STATUS(job_id))
    done = await r.exists(KEY_RESULT(job_id))
    return {"job_id": job_id, "status": json.loads(s) if s else None, "done": bool(done)}

@router.get("/{job_id}/result")
async def result(job_id: str):
    data = await r.get(KEY_RESULT(job_id))
    return {"job_id": job_id, "result": json.loads(data) if data else None}