import sys
import os
import json
from flask import Flask, render_template, request, Response
from src.utils.config import Config

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from src.game.game_engine import GameEngine
from src.game.fight_engine import FightEngine # Import FightEngine

app = Flask(__name__, template_folder='templates', static_folder='static')
game_engine_instance = None # For single player game
fight_engine_instance = None # For fight mode

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    global game_engine_instance
    data = request.json
    difficulty = data.get('difficulty')
    narrator_model = data.get('narrator_model')
    detective_model = data.get('detective_model')

    def generate():
        global game_engine_instance
        try:
            config_loader = Config(parse_cli=False)
            config = config_loader.get_config()
            game_engine_instance = GameEngine(config)
            for line in game_engine_instance.run(difficulty, narrator_model, detective_model):
                print(f"DEBUG: Yielding line: {line}") # Added for debugging
                yield line + '\n'
        except Exception as e:
            print(f"ERROR: An exception occurred in generate: {e}") # Added for debugging
            yield json.dumps({"type": "error", "content": f"An error occurred: {e}"})

    return Response(generate(), mimetype='application/x-ndjson')

@app.route('/start_fight', methods=['POST'])
async def start_fight():
    global fight_engine_instance
    data = request.json
    # Use the narrator model from the main game form as the default for fight mode
    # If the main form's narrator model is not provided, default to 'gpt-4'
    narrator_model = data.get('narrator_model', 'gpt-4') 
    detective_model_1 = data.get('detective_model_1')
    detective_model_2 = data.get('detective_model_2')

    async def generate_fight_stream():
        global fight_engine_instance
        try:
            config_loader = Config(parse_cli=False)
            config = config_loader.get_config()
            fight_engine_instance = FightEngine(config)
            async for line in fight_engine_instance.run(narrator_model, detective_model_1, detective_model_2):
                print(f"DEBUG: Yielding fight line: {line}") # Added for debugging
                yield line + '\n'
        except Exception as e:
            print(f"ERROR: An exception occurred in generate_fight_stream: {e}") # Added for debugging
            yield json.dumps({"type": "error", "content": f"An error occurred in fight mode: {e}"}) + '\n'
            
    return Response(generate_fight_stream(), mimetype='application/x-ndjson')

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    global game_engine_instance
    # In fight mode, we don't save individual conversations in the same way, 
    # but the Narrator might have its own save mechanism if needed.
    # For now, this route is mainly for the single-player game.
    if game_engine_instance:
        game_engine_instance.save_conversation()
        return {"status": "success"}, 200
    return {"status": "error", "message": "Game not started"}, 400


if __name__ == '__main__':
    app.run(debug=True)
