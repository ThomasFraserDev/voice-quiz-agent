import json
import logging
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
    function_tool,
    inference,
)

from quiz_engine import QuizEngine

load_dotenv(".env.local")

logger = logging.getLogger("agent")

QUESTIONS_FILE = Path(__file__).parent / "questions.json"  # Path for questions json

REQUIRED_FIELDS = {
    "id",
    "topic",
    "difficulty",
    "question",
    "answer",
    "acceptable_answers",
    "explanation",
}


def load_questions(
    file_path: str | Path = QUESTIONS_FILE,
) -> list[dict[str, Any]]:  # Load questions from json
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:  # Read json file
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError(  # Raise error if questions not in a json format
            "Questions must be a JSON array"
        )

    seen_ids = set()

    for index, question in enumerate(questions):
        label = f"Question at index {index}"

        if not isinstance(question, dict):
            raise ValueError(f"{label} must be a JSON object.")

        missing = REQUIRED_FIELDS - question.keys()
        if missing:
            raise ValueError(f"{label} is missing fields: {', '.join(sorted(missing))}")

        for field in REQUIRED_FIELDS - {"acceptable_answers", "difficulty"}:
            if not isinstance(question[field], str) or not question[field].strip():
                raise ValueError(f"{label}: '{field}' must be a non-empty string.")

        answers = question["acceptable_answers"]
        if not isinstance(answers, list) or not all(
            isinstance(answer, str) for answer in answers
        ):
            raise ValueError(
                f"{label}: 'acceptable_answers' must be a list of strings."
            )

        question_id = question["id"]
        if question_id in seen_ids:
            raise ValueError(f"{label} has duplicate ID: {question_id!r}")

        seen_ids.add(question_id)

    return questions


class Assistant(Agent):
    def __init__(self, questions: list[dict[str, Any]]):
        self.quiz = QuizEngine(questions)

        super().__init__(
            llm=inference.LLM(model="google/gemma-4-31b-it"),
            instructions="""
                You are a friendly voice quiz tutor.

                Start by greeting the learner and asking the first
                question using get_next_question.

                Rules:
                - Only ask questions returned by get_next_question.
                - Ask one question at a time.
                - Listen to the learner's answer before moving on.
                - Submit each answer using submit_answer.
                - Use the tool result to explain whether the answer
                  was correct and give the explanation provided.
                - Do not decide correctness yourself.
                - Do not reveal the expected answer before the
                  learner has answered.
                - After giving feedback, ask the next question
                  using get_next_question.
                - If no more questions remain, use get_quiz_summary
                  and tell the learner their final score.
                - Keep your speech concise and conversational.
            """,
        )

    @function_tool()
    async def get_next_question(self) -> str:  # Method for getting next question

        question = self.quiz.next_question()

        if question is None:  # If no more questions remain, denote the quiz as finished
            return json.dumps(
                {
                    "finished": True,
                    "message": "The quiz is finished. No more questions remain.",
                }
            )

        return json.dumps(
            {
                "finished": False,
                "question": question,
            }
        )

    @function_tool()
    async def submit_answer(
        self, user_answer: str
    ) -> str:  # Method for submitting and checking user answer

        try:  # Try submit the user answer
            result = self.quiz.submit_answer(user_answer)
        except (RuntimeError, ValueError) as exc:
            return json.dumps({"error": str(exc)})

        return json.dumps(result)

    @function_tool()
    async def get_quiz_summary(self) -> str:  # Method for getting a summary of the quiz

        return json.dumps(self.quiz.get_summary())


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

    questions = load_questions()
    assistant = Assistant(questions)

    await session.start(
        agent=assistant,
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
