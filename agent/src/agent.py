
import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)

load_dotenv(".env.local")

logger = logging.getLogger("agent")


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            llm=inference.LLM(model="google/gemma-4-31b-it"),
            instructions="""
                You are a voice assistant.
                Keep responses concise and conversational.
                Ask one question at a time.
            """,
        )


server = AgentServer()


@server.rtc_session()
async def my_agent(ctx: JobContext):
    logger.info("Starting agent in room %s", ctx.room.name)

    session = AgentSession(
        stt=inference.STT(
            model="assemblyai/universal-3-6-pro",
            language="en",
        ),
        tts=inference.TTS(
            model="fishaudio/s2.1-pro",
            voice="fa4c9eb3dccc4806b382b40d61c6b10a",
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            interruption={"mode": "adaptive"},
        ),
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)