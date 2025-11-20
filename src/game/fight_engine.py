import json
import asyncio
from typing import Dict, Any, Generator, Tuple

from src.models.game_state import GameState
from src.models.story import Story
from src.services.api_client import APIClient
from src.services.story_generator import StoryGenerator
from src.services.narrator import Narrator
from src.services.detective import Detective

class FightEngine:
    """
    Orchestrates the Black Stories AI fight mode, managing two independent detective AIs
    against a single narrator.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_client = APIClient(config)
        self.game_state_det1: GameState | None = None
        self.game_state_det2: GameState | None = None
        self.narrator_ai: Narrator | None = None
        self.story: Story | None = None

    async def _initialize_fight(self, narrator_model: str, detective_model_1: str, detective_model_2: str) -> Generator[str, None, None]:
        """
        Initializes the fight by generating a story and setting up AI roles.
        """
        yield json.dumps({"type": "narrator", "content": "Generando una nueva historia de Black Stories para el modo Pelea..."})
        story_generator = StoryGenerator(self.api_client, narrator_model)
        
        retries = 3
        for attempt in range(retries):
            try:
                self.story = story_generator.generate_story("fight_mode") # Use a generic difficulty for story generation
                break
            except Exception as e:
                yield json.dumps({"type": "error", "content": f"Error al generar la historia (intento {attempt + 1}/{retries}): {e}"})
                if attempt + 1 == retries:
                    raise
        
        self.game_state_det1 = GameState(
            narrator_model=narrator_model,
            detective_model=detective_model_1,
            difficulty="fight_mode",
            mystery_situation=self.story.mystery_situation,
            hidden_solution=self.story.hidden_solution,
        )
        self.game_state_det2 = GameState(
            narrator_model=narrator_model,
            detective_model=detective_model_2,
            difficulty="fight_mode",
            mystery_situation=self.story.mystery_situation,
            hidden_solution=self.story.hidden_solution,
        )

        yield json.dumps({"type": "narrator", "content": "============================================================"})
        yield json.dumps({"type": "narrator", "content": "                  BLACK STORIES AI - MODO PELEA"})
        yield json.dumps({"type": "narrator", "content": "============================================================"})
        yield json.dumps({"type": "narrator", "content": f"Narrador: {narrator_model}"})
        yield json.dumps({"type": "narrator", "content": f"Detective 1: {detective_model_1}"})
        yield json.dumps({"type": "narrator", "content": f"Detective 2: {detective_model_2}"})
        yield json.dumps({"type": "narrator", "content": "------------------------------------------------------------"})
        yield json.dumps({"type": "narrator", "content": f"Misterio: {self.story.mystery_situation}"})
        yield json.dumps({"type": "narrator", "content": "============================================================"})

    async def _run_detective_loop(self, detective_id: int, detective_ai: Detective, narrator_ai: Narrator, game_state: GameState, max_questions: int, output_queue: asyncio.Queue):
        """
        Runs the game loop for a single detective.
        """
        detective_ready_to_solve = False
        
        while not game_state.detective_solved:
            current_questions = len(game_state.qa_history)

            if current_questions >= max_questions and not detective_ready_to_solve:
                await output_queue.put(json.dumps({"type": f"detective{detective_id}_question", "content": f"¡Se ha alcanzado el límite de {max_questions} preguntas!"}))
                await output_queue.put(json.dumps({"type": f"detective{detective_id}_question", "content": f"El Detective {detective_id} tiene UNA ÚLTIMA OPORTUNIDAD para dar su solución final."}))
                detective_ready_to_solve = True
            
            if detective_ready_to_solve:
                game_state.detective_solution_attempt = detective_ai.provide_final_solution(game_state.qa_history)
                game_state.detective_solved = True
                break
            
            if not detective_ready_to_solve:
                detective_response = detective_ai.ask_question_or_solve(game_state.qa_history)

                if detective_ai.is_ready_to_solve(detective_response):
                    detective_ready_to_solve = True
                    await output_queue.put(json.dumps({"type": f"detective{detective_id}_question", "content": "¡Estoy listo para resolver!"}))
                    continue

                narrator_answer = await asyncio.to_thread(narrator_ai.answer_question, detective_response, game_state.qa_history) # Run sync in thread
                game_state.qa_history.append((detective_response, narrator_answer))
                
                await output_queue.put(json.dumps({"type": f"detective{detective_id}_question", "content": detective_response}))
                await output_queue.put(json.dumps({"type": f"detective{detective_id}_answer", "content": narrator_answer}))
            
            await asyncio.sleep(1) # Small delay to simulate concurrent thinking

        if not game_state.detective_solved and not game_state.detective_solution_attempt:
            game_state.detective_solved = True


    async def _run_fight_loop(self) -> Generator[str, None, None]:
        """
        Runs the main fight loop where two detectives ask questions concurrently.
        """
        if not self.game_state_det1 or not self.game_state_det2 or not self.story:
            raise RuntimeError("Fight not initialized.")

        self.narrator_ai = Narrator(
            self.api_client,
            self.game_state_det1.narrator_model, # Narrator model is same for both
            self.story,
            self.game_state_det1.difficulty,
        )

        detective1_ai = Detective(
            self.api_client, self.game_state_det1.detective_model, self.game_state_det1.mystery_situation
        )
        detective2_ai = Detective(
            self.api_client, self.game_state_det2.detective_model, self.game_state_det2.mystery_situation
        )

        max_questions = self.config["question_limits"].get(self.game_state_det1.difficulty, 10)

        output_queue = asyncio.Queue()

        task1 = asyncio.create_task(self._run_detective_loop(1, detective1_ai, self.narrator_ai, self.game_state_det1, max_questions, output_queue))
        task2 = asyncio.create_task(self._run_detective_loop(2, detective2_ai, self.narrator_ai, self.game_state_det2, max_questions, output_queue))

        while not task1.done() or not task2.done() or not output_queue.empty():
            try:
                message = await asyncio.wait_for(output_queue.get(), timeout=0.1)
                yield message
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.01) # Yield control to other tasks

        await task1
        await task2


    async def _finalize_fight(self) -> Generator[str, None, None]:
        """
        Finalizes the fight by validating each detective's solution and determining the winner.
        """
        if not self.game_state_det1 or not self.game_state_det2 or not self.narrator_ai:
            raise RuntimeError("Fight not initialized or narrator_ai not set.")

        summary_messages = []
        
        # Finalize Detective 1
        verdict1, analysis1 = "No solution provided", ""
        if self.game_state_det1.detective_solution_attempt:
            verdict1, analysis1 = await asyncio.to_thread(self.narrator_ai.validate_solution, self.game_state_det1.detective_solution_attempt)
        
        # Finalize Detective 2
        verdict2, analysis2 = "No solution provided", ""
        if self.game_state_det2.detective_solution_attempt:
            verdict2, analysis2 = await asyncio.to_thread(self.narrator_ai.validate_solution, self.game_state_det2.detective_solution_attempt)

        # Determine Winner
        winner = None
        winner_rationale = ""

        # Case 1: Both correct
        if verdict1.lower() == "correcto" and verdict2.lower() == "correcto":
            if len(self.game_state_det1.qa_history) <= len(self.game_state_det2.qa_history):
                winner = self.game_state_det1.detective_model
                winner_rationale = f"Ambos Detectives resolvieron correctamente. Detective 1 ({self.game_state_det1.detective_model}) ganó por resolver en menos preguntas ({len(self.game_state_det1.qa_history)} vs {len(self.game_state_det2.qa_history)})."
            else:
                winner = self.game_state_det2.detective_model
                winner_rationale = f"Ambos Detectives resolvieron correctamente. Detective 2 ({self.game_state_det2.detective_model}) ganó por resolver en menos preguntas ({len(self.game_state_det2.qa_history)} vs {len(self.game_state_det1.qa_history)})."
        # Case 2: Only Detective 1 correct
        elif verdict1.lower() == "correcto":
            winner = self.game_state_det1.detective_model
            winner_rationale = f"Detective 1 ({self.game_state_det1.detective_model}) resolvió correctamente. Detective 2 ({self.game_state_det2.detective_model}) no lo hizo."
        # Case 3: Only Detective 2 correct
        elif verdict2.lower() == "correcto":
            winner = self.game_state_det2.detective_model
            winner_rationale = f"Detective 2 ({self.game_state_det2.detective_model}) resolvió correctamente. Detective 1 ({self.game_state_det1.detective_model}) no lo hizo."
        # Case 4: Neither correct, compare closeness (simplified)
        else:
            # For simplicity, if neither is correct, we'll just say no winner, or could implement a more complex closeness metric
            winner = "Ninguno"
            winner_rationale = "Ningún Detective logró resolver la historia correctamente."
            # A more advanced comparison could involve analyzing the "analysis" from the narrator.

        summary_messages.append(f"<h2>Resultados Finales del Modo Pelea</h2>")
        summary_messages.append(f"<p><strong>Historia Original:</strong><br>{self.story.mystery_situation}<br>Solución: {self.story.hidden_solution}</p>")
        
        summary_messages.append(f"<h3>Detective 1: {self.game_state_det1.detective_model}</h3>")
        summary_messages.append(f"<p><strong>Versión:</strong> {self.game_state_det1.detective_model}</p>") # Using model name as version
        summary_messages.append(f"<p><strong>Preguntas realizadas:</strong> {len(self.game_state_det1.qa_history)}</p>")
        summary_messages.append(f"<p><strong>Intento de Solución:</strong> {self.game_state_det1.detective_solution_attempt if self.game_state_det1.detective_solution_attempt else 'No proporcionó solución.'}</p>")
        summary_messages.append(f"<p><strong>Veredicto:</strong> {verdict1}</p>")
        summary_messages.append(f"<p><strong>Análisis:</strong> {analysis1}</p>")

        summary_messages.append(f"<h3>Detective 2: {self.game_state_det2.detective_model}</h3>")
        summary_messages.append(f"<p><strong>Versión:</strong> {self.game_state_det2.detective_model}</p>") # Using model name as version
        summary_messages.append(f"<p><strong>Preguntas realizadas:</strong> {len(self.game_state_det2.qa_history)}</p>")
        summary_messages.append(f"<p><strong>Intento de Solución:</strong> {self.game_state_det2.detective_solution_attempt if self.game_state_det2.detective_solution_attempt else 'No proporcionó solución.'}</p>")
        summary_messages.append(f"<p><strong>Veredicto:</strong> {verdict2}</p>")
        summary_messages.append(f"<p><strong>Análisis:</strong> {analysis2}</p>")
        
        summary_messages.append(f"<h3>GANADOR: {winner}</h3>")
        summary_messages.append(f"<p><strong>Razón:</strong> {winner_rationale}</p>")

        yield json.dumps({"type": "summary", "content": "".join(summary_messages)})

    async def run(self, narrator_model: str, detective_model_1: str, detective_model_2: str) -> Generator[str, None, None]:
        """
        Runs the complete Black Stories AI fight mode.
        """
        try:
            async for msg in self._initialize_fight(narrator_model, detective_model_1, detective_model_2):
                yield msg
            async for msg in self._run_fight_loop():
                yield msg
            async for msg in self._finalize_fight():
                yield msg
        except Exception as e:
            yield json.dumps({"type": "error", "content": f"El modo pelea ha terminado debido a un error crítico: {e}. Asegúrate de que tus claves de API y la URL de Ollama estén configuradas correctamente."})
