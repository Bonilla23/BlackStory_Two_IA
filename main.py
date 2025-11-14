from src.utils.config import Config
from src.game.game_engine import GameEngine

def main():
    """
    Main entry point for the Black Stories AI game.
    Initializes configuration and starts the game engine.
    """
    config_loader = Config()
    game_config = config_loader.get_config()

    game_engine = GameEngine(game_config)
    game_engine.run()

if __name__ == "__main__":
    main()
