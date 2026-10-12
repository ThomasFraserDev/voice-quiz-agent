from typing import Any
import re

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
        
        def total_questions(self) -> int: # Method for getting the total amount of questions
            return len(self.questions)
        
        def next_question(self) -> dict[str, Any] | None: # Method for generating the next question
            if self.current_question is not None: # Prevent having two current questions
                raise RuntimeError("Please submit an answer before moving onto the next question.")
            next_index = self.current_index + 1
            
            if next_index >= total_questions(): # If no more questions remaining 
                return None
            
            self.current_index = next_index
            self.current_question = self.questions[next_index]
            
            return {
                "id": self.current_question["id"],
                "topic": self.current_question["topic"],
                "difficulty": self.current_question["difficulty"],
                "question": self.current_question["question"],
                "question_number": self.current_index + 1,
                "total_questions": self.total_questions
            }
            
        @staticmethod
        def normalise_answer(answer: str) -> str: # Normalise an answer, by removing punctuation and any casing differences 
            answer = answer.casefold().strip()
            answer = re.sub(r"[^\w\s]", "", answer) # Replace punctuation with ""
            return " ".join(answer.split())
        
        def submit_answer(self, user_answer: str) -> dict[str, Any]: # Method for submitting and validating a user's answer
            if self.current_question is None:
                raise RuntimeError("There is no active question. Call next_question() first.")
            
            if not isinstance(user_answer, str) or not user_answer.strip(): ## Check that user answer is a string and not just whitespace
                raise ValueError("The user's answer must not be empty.")
            
            question = self.current_question
            self.attempts += 1
            
            accepted_answers = [question["answer"],*question["acceptable_answers"]]
            normalised_accepted = {self.normalise_answer(answer) for answer in accepted_answers} # Create set of normalised accepted answers 
            
            correct = (self.normalise_answer(user_answer) in normalised_accepted) # Check if user answer is correct
            
            if correct: # Update score
                self.score += 1
            else:
                self.failed_questions.append({
                    "id": question["id"],
                    "topic": question["topic"],
                    "user_answer": user_answer,
                })
                
            result = { # Create dictionary of submitted answer info
                "correct": correct,
                "expected_answer": question["answer"],
                "explanation": question["explanation"],
                "score": self.score,
                "attempts": self.attempts,
                "question_number": self.current_index + 1,
                "total_questions": self.total_questions,
            }
            
            self.current_question = None
            return result
        
        def get_summary(self) -> dict[str, Any]: # Method for returning a summary of quiz results
            return {
                "score": self.score,
                "attempts": self.attempts,
                "total_questions": self.total_questions,
                "missed_questions": list(self.missed_questions),
            }