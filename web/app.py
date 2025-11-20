import sys
import os
import json
from flask import Flask, render_template, request, Response
from src.utils.config import Config

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.game_engine import GameEngine

app = Flask(__name__, template_folder='templates', static_folder='static')
game_engine_instance = None

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
                yield json.dumps({"type": "event", "content": line}) + '\n'
        except Exception as e:
            print(f"ERROR: An exception occurred in generate: {e}") # Added for debugging
            yield json.dumps({"type": "error", "content": f"An error occurred: {e}"})

    return Response(generate(), mimetype='application/x-ndjson')

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    global game_engine_instance
    if game_engine_instance:
        game_engine_instance.save_conversation()
        return {"status": "success"}, 200
    return {"status": "error", "message": "Game not started"}, 400


if __name__ == '__main__':
    app.run(debug=True)
