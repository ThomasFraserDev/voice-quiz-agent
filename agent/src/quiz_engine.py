from typing import Any

class QuizEngine:
    
    def __init__(self, questions: list[dict[str, Any]]):
        if not questions:
            raise ValueError("The quiz needs at least one question.")

        self.questions = questions # Question list
        self.current_index = -1 # Index of current question
        self.current_question = None # Actual current question

        self.score = 0 # Current score for questions answered correctly
        self.attempts = 0 # Amount of attempts on current question
        self.failed_questions = [] # List of failed questions