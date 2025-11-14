import os

def clear_screen() -> None:
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_initial_screen(
    title: str,
    narrator_model: str,
    detective_model: str,
    difficulty: str,
    mystery_situation: str
) -> None:
    """
    Displays the initial game screen with title, models, difficulty, and mystery situation.
    """
    clear_screen()
    print("════════════════════════════════════════════")
    print(f"        {title.upper()}        ")
    print("════════════════════════════════════════════")
    print(f"\nModelos de IA:")
    print(f"  Narrador: {narrator_model}")
    print(f"  Detective: {detective_model}")
    print(f"Dificultad: {difficulty.capitalize()}")
    print("\nSITUACIÓN MISTERIOSA INICIAL:")
    print(mystery_situation)
    print("\nPresiona ENTER para comenzar el interrogatorio...")
    input()

def display_qa_pair(question: str, answer: str) -> None:
    """
    Displays a question from the detective and the narrator's answer.
    """
    print("\n─────────────────────────────")
    print(f"Detective: {question}")
    print(f"Narrador: {answer}")
    print("─────────────────────────────")
    print("Presiona ENTER para continuar...")
    input()

def display_final_screen(
    result: str,
    original_story: str,
    detective_solution: str,
    verdict: str,
    analysis: str
) -> None:
    """
    Displays the final game screen with the result, original story, detective's solution,
    verdict, and a detailed analysis.
    """
    clear_screen()
    print("════════════════════════════════════════════")
    print(f"RESULTADO: {result.upper()}")
    print("════════════════════════════════════════════")
    print("\nHISTORIA ORIGINAL:")
    print(original_story)
    print("\nSOLUCIÓN DEL DETECTIVE:")
    print(detective_solution)
    print("\nVEREDICTO:")
    print(verdict)
    print("\nANÁLISIS DETALLADO:")
    print(analysis)
    print("════════════════════════════════════════════")
    print("\nFin del juego. Presiona ENTER para salir.")
    input()

def display_error_and_retry(message: str) -> bool:
    """
    Displays an error message and asks the user if they want to retry.
    Returns True if the user wants to retry, False otherwise.
    """
    print(f"\nError: {message}")
    while True:
        response = input("¿Desea reintentar? (s/n): ").lower().strip()
        if response in ["s", "si"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Respuesta inválida. Por favor, ingrese 's' o 'n'.")
