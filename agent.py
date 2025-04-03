from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)

from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import TutorFnc
from prompts import INSTRUCTIONS, WELCOME_MESSAGE
import os

load_dotenv()

# connects to a livekit room and subsribes to all the tracks in that room
# aka in our case hears all audio in that room
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant() # waits for a participant to join a room

    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS,
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"]
    )
    tutor_fnc = TutorFnc()
    tutor = MultimodalAgent(model=model, fnc_ctx=tutor_fnc)
    tutor.start(ctx.room)

    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="tutor",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
