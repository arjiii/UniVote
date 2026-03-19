import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services import adviser_service

router = APIRouter()


@router.get("/stream/{election_id}")
async def stream_results(election_id: str):
    """
    SSE endpoint — streams live vote counts to any connected client.
    Pushes a fresh snapshot every 2 seconds. No auth required;
    results are considered public once an election is active.
    """

    async def event_generator():
        try:
            while True:
                data = adviser_service.get_live_results(election_id)
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            # Client disconnected — clean exit
            return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        },
    )
