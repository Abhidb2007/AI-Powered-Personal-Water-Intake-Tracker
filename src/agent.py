import os

from dotenv import load_dotenv
from openai import APIError,OpenAI

load_dotenv()


class WaterIntakeAgent:
    def __init__(self):
        self.history = []
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_intake(self, intake_ml):
        if self.client is None:
            return self.local_analysis(intake_ml)

        prompt = f"""
        You are a hydration assistant. The user has consumed {intake_ml} ml of water today.
        Provide a hydration status and suggest whether they need to drink more water.
        """
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )
            return response.output_text
        except APIError:
            return self.local_analysis(intake_ml)

    @staticmethod
    def local_analysis(intake_ml):
        if intake_ml < 1000:
            return "Your intake is currently low. Consider drinking more water throughout the day."
        if intake_ml < 2000:
            return "Your intake is progressing well. Continue drinking water regularly."
        return "Your intake is strong for today. Continue listening to your body's thirst signals."


if __name__ == "__main__":
    agent = WaterIntakeAgent()
    intake = 1600
    feedback = agent.analyze_intake(intake)
    print(f"Hydration Analysis: {feedback}")
