import logging
import json
from pathlib import Path
from typing import Any
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

QUESTIONS_FILE = Path(__file__).parent / "questions.json" # Path for questions json

REQUIRED_FIELDS = {
    "id",
    "topic",
    "difficulty",
    "question",
    "answer",
    "acceptable_answers",
    "explanation",
}

def load_questions(file_path: str | Path = QUESTIONS_FILE) -> list[dict[str, Any]]: # Load questions from json
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file: # Read json file
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError( # Raise error if questions not in a json format
            "Questions must be a JSON array"
        )

    seen_ids = set()

    for index, question in enumerate(questions):
        label = f"Question at index {index}"

        if not isinstance(question, dict):
            raise ValueError(f"{label} must be a JSON object.")

        missing = REQUIRED_FIELDS - question.keys()
        if missing:
            raise ValueError(
                f"{label} is missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        for field in REQUIRED_FIELDS - {"acceptable_answers", "difficulty"}:
            if not isinstance(question[field], str) or not question[field].strip():
                raise ValueError(
                    f"{label}: '{field}' must be a non-empty string."
                )

        answers = question["acceptable_answers"]
        if not isinstance(answers, list) or not all(
            isinstance(answer, str) for answer in answers
        ):
            raise ValueError(
                f"{label}: 'acceptable_answers' must be a list of strings."
            )

        question_id = question["id"]
        if question_id in seen_ids:
            raise ValueError(
                f"{label} has duplicate ID: {question_id!r}"
            )

        seen_ids.add(question_id)

    return questions
    
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
    questions = load_questions()
    cli.run_app(server)