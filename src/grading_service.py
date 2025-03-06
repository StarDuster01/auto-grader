from openai import OpenAI
import pandas as pd
import re
from typing import Tuple

class GradingService:
    def __init__(self, api_key: str, model: str, temperature: float):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
    
    def grade_discussion(self, 
                        message: str, 
                        post_type: str,
                        post_points: float,
                        reply_points: float,
                        system_prompt: str) -> Tuple[float, str]:
        """Grade a single discussion post/reply"""
        max_points = post_points if post_type == 'post' else reply_points
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\nIMPORTANT GRADING RULES:\n1. Always provide grades as whole numbers or decimals (not fractions)\n2. Grades must be between 0 and {max_points}\n3. Your response must strictly follow this format: [NUMBER];[EXPLANATION]\n4. Be objective and consistent in grading"},
                {"role": "user", "content": self._create_grading_prompt(
                    message, post_type, max_points)}
            ],
            temperature=self.temperature,
            model=self.model
        )
        
        return self._parse_grade_response(response.choices[0].message.content)
    
    @staticmethod
    def _create_grading_prompt(message: str, post_type: str, max_points: float) -> str:
        return (f"Grade this {post_type}. Provide a single number between 0 and {max_points} "
                f"(use decimals, not fractions) followed by a semicolon and brief explanation.\n\n"
                f"The {post_type} to grade: \"{message}\"")
    
    @staticmethod
    def _parse_grade_response(response: str) -> Tuple[float, str]:
        """Parse grading response into numeric grade and feedback"""
        match = re.match(r"(\d+(?:\.\d+)?);(.*)", response.strip())
        if match:
            try:
                grade = float(match.group(1))
                feedback = match.group(2).strip()
                return grade, feedback
            except ValueError:
                return 0.0, "Error parsing grade value"
        return 0.0, response 