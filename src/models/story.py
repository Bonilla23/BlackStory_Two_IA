from dataclasses import dataclass

@dataclass
class Story:
    """
    Represents a Black Story with a mysterious situation and its hidden solution.
    """
    mystery_situation: str
    hidden_solution: str
