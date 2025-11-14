import json
from typing import Dict, Any
from src.services.api_client import APIClient
from src.models.story import Story
from src.utils.display import display_error_and_retry

class StoryGenerator:
    """
    Generates Black Stories using an LLM.
    """

    def __init__(self, api_client: APIClient, narrator_model: str):
        self.api_client = api_client
        self.narrator_model = narrator_model

    def _get_story_generation_prompt(self, difficulty: str) -> str:
        """
        Returns the prompt for generating a Black Story based on difficulty.
        """
        difficulty_description = {
            "facil": "con lógica directa, menos elementos rebuscados, causas evidentes.",
            "media": "con una combinación de elementos lógicos y algunos giros inesperados.",
            "dificil": "muy rebuscada, con causas no obvias y múltiples elementos engañosos.",
        }

        return f"""
        Eres un experto creador de Black Stories. Tu tarea es generar una historia de Black Stories
        con el siguiente formato JSON:
        {{
            "situacion_misteriosa": "Una breve descripción de la situación inicial que se presenta al detective.",
            "solucion_oculta": "La explicación completa y detallada de lo que realmente sucedió."
        }}

        La historia debe ser {difficulty_description[difficulty]}.
        Asegúrate de que la "solucion_oculta" sea la verdad completa y que la "situacion_misteriosa"
        sea intrigante pero no revele la solución directamente.
        La historia debe ser concisa y clara.
        """

    def generate_story(self, difficulty: str) -> Story:
        """
        Generates a new Black Story using the Narrator AI.
        Handles connection errors with retry mechanism.
        """
        prompt = self._get_story_generation_prompt(difficulty)
        while True:
            try:
                response_text = self.api_client.generate_text(self.narrator_model, prompt)
                
                # Extract JSON from Markdown code block if present
                if response_text.strip().startswith("```json"):
                    json_start = response_text.find("```json") + len("```json")
                    json_end = response_text.rfind("```")
                    if json_start != -1 and json_end != -1 and json_end > json_start:
                        json_string = response_text[json_start:json_end].strip()
                    else:
                        raise ValueError("Could not extract JSON from Markdown block.")
                else:
                    json_string = response_text.strip()

                story_data = json.loads(json_string)
                return Story(
                    mystery_situation=story_data["situacion_misteriosa"],
                    hidden_solution=story_data["solucion_oculta"]
                )
            except (ConnectionError, ValueError, KeyError, json.JSONDecodeError) as e:
                if not display_error_and_retry(f"Error al generar la historia: {e}"):
                    raise
