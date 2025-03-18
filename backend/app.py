from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
from game_manager import GameManager

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize game manager
game_manager = GameManager()
game_manager.set_socketio(socketio)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Simple status endpoint to verify server is running"""
    return jsonify({
        "status": "online",
        "active_players": game_manager.get_player_count(),
        "current_round": game_manager.get_current_round_info()
    })

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    game_manager.remove_player(request.sid)
    emit('player_count', {"count": game_manager.get_player_count()}, broadcast=True)

@socketio.on('register_player')
def handle_register_player(data):
    username = data.get('username')
    player_id = request.sid

    # Check if username already exists
    existing_id = game_manager.username_to_id.get(username)
    if existing_id:
        # Remove the old connection
        game_manager.remove_player(existing_id)

    # Register the player with the game manager
    success = game_manager.add_player(player_id, username)

    # Join the waiting room
    join_room('waiting_room')

    # Notify the client about registration status
    emit('registration_status', {
        'success': success,
        'player_id': player_id,
        'username': username,
        'game_state': game_manager.get_game_state(),
        'round_in_progress': game_manager.is_round_in_progress()
    })

    # Broadcast updated player count
    emit('player_count', {"count": game_manager.get_player_count()}, broadcast=True)

@socketio.on('player_click')
def handle_player_click(data):
    player_id = request.sid
    click_time = data.get('click_time')

    # Process the player's click in the current round
    result = game_manager.process_player_click(player_id, click_time)

    # Send back the immediate result to the player
    emit('click_result', result)

    # If all players have clicked or the round timeout is reached,
    # the game manager will trigger the round end automatically

@socketio.on('join_waiting_room')
def handle_join_waiting_room():
    player_id = request.sid
    join_room('waiting_room')
    game_manager.set_player_ready(player_id)

    # Check if all registered players are ready and if we should start the next round
    if game_manager.should_start_next_round():
        game_manager.start_next_round()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)