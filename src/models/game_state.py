from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class GameState:
    """
    Represents the current state of the Black Stories game.
    """
    narrator_model: str
    detective_model: str
    difficulty: str
    mystery_situation: str
    hidden_solution: str
    qa_history: List[Tuple[str, str]] = field(default_factory=list)
    detective_solved: bool = False
    detective_solution_attempt: str | None = None
