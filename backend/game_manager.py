import time
import random
import threading
from round_types.color_change import ColorChangeRound
from round_types.brightness import BrightnessRound

class GameManager:
    def __init__(self):
         # Add a mapping of username to player_id
        self.username_to_id = {}  # username -> player_id
        # Player tracking
        self.players = {}  # player_id -> {'username': str, 'score': float, 'ready': bool}
        self.current_round = None
        self.round_in_progress = False
        # self.round_types = [ColorChangeRound, BrightnessRound]
        self.round_types = [ColorChangeRound]
        self.round_history = []
        self.socketio = None  # Will be set by the Flask-SocketIO instance
        
    def set_socketio(self, socketio_instance):
        """Set the Flask-SocketIO instance for broadcasts"""
        self.socketio = socketio_instance
        
    def add_player(self, player_id, username):
        """Add a new player to the game"""
         # If username already exists, remove the old connection
        if username in self.username_to_id:
            old_player_id = self.username_to_id[username]
            if old_player_id in self.players:
                del self.players[old_player_id]
            
        # Update username to player_id mapping
        self.username_to_id[username] = player_id
            
        self.players[player_id] = {
            'username': username,
            'score': 0,
            'rounds_played': 0,
            'ready': True,
            'avg_time': 0
        }
        return True
        
    def remove_player(self, player_id):
        """Remove a player from the game"""
        if player_id in self.players:
            username = self.players[player_id]['username']
            # Clean up username mapping
            if username in self.username_to_id:
                del self.username_to_id[username]
            del self.players[player_id]
            return True
        return False
    
    def get_player_count(self):
        """Get the current number of active players"""
        return len(self.players)
    
    def get_current_round_info(self):
        """Get information about the current round"""
        if self.current_round is None:
            return {"status": "waiting"}
        
        return {
            "type": self.current_round.__class__.__name__,
            "in_progress": self.round_in_progress
        }
    
    def get_game_state(self):
        """Get the current game state for a newly connected player"""
        state = {
            "status": "waiting" if not self.round_in_progress else "in_progress",
            "leaderboard": self._get_leaderboard()  # Add this line
        }
        if self.current_round is not None and self.round_in_progress:
            state.update({
                "round_type": self.current_round.__class__.__name__,
                "round_data": self.current_round.get_client_data()
            })

        return state

    def is_round_in_progress(self):
        """Check if a round is currently in progress"""
        return self.round_in_progress
    
    def set_player_ready(self, player_id):
        """Mark a player as ready for the next round"""
        if player_id in self.players:
            self.players[player_id]['ready'] = True
            return True
        return False
    
    def should_start_next_round(self):
        """Check if all conditions are met to start the next round"""
        # Don't start if a round is already in progress
        if self.round_in_progress:
            return False
            
        # Only start if we have at least one player
        if not self.players:
            return False
            
        # Check if all players are ready
        return all(player['ready'] for player in self.players.values())
    
    def start_next_round(self):
        """Start the next round"""
        if self.round_in_progress:
            return False
            
        # Reset player ready status
        for player_id in self.players:
            self.players[player_id]['ready'] = False
            
        # Select a random round type
        RoundClass = random.choice(self.round_types)
        self.current_round = RoundClass(players=self.players)
        self.round_in_progress = True
        
        # Get round initialization data
        round_data = self.current_round.get_client_data()
        
        # Broadcast round start to all clients
        if self.socketio:
            self.socketio.emit('round_start', {
                'round_type': self.current_round.__class__.__name__,
                'round_data': round_data
            }, room='waiting_room')
            
        # Start round execution thread
        thread = threading.Thread(target=self._execute_round)
        thread.daemon = True
        thread.start()
        
        return True
    
    def _execute_round(self):
        """Execute the current round logic in a separate thread"""
        # Let the round run its course
        self.current_round.execute()
        
        # When round is complete, calculate and update scores
        if self.round_in_progress:
            self._end_round()
    
    def _end_round(self):
        """End the current round and update scores"""
        self.round_in_progress = False
        
        # Get round results
        results = self.current_round.get_results()
        
        # Update player scores
        self._update_player_scores(results)
        
        # Get leaderboard
        leaderboard = self._get_leaderboard()
        
        # Broadcast round end and results
        if self.socketio:
            self.socketio.emit('round_end', {
                'results': results,
                'leaderboard': leaderboard
            }, room='waiting_room')
            
        # Add a delay before allowing the next round to start
        # time.sleep(5)  # 5 second delay between rounds
        
        # Mark all connected players as ready for the next round
        # for player_id in self.players:
        #     self.players[player_id]['ready'] = True
            
        # Check if we should auto-start the next round
        if self.should_start_next_round():
            self.start_next_round()
    
    def process_player_click(self, player_id, click_time):
        """Process a player's click during a round"""
        if not self.round_in_progress or self.current_round is None:
            return {"success": False, "message": "No round in progress"}
            
        if player_id not in self.players:
            return {"success": False, "message": "Player not registered"}
            
        # Let the current round handle the click logic
        result = self.current_round.process_click(player_id, click_time)
        
        # Check if the round should end (all players clicked or timeout)
        if self.current_round.should_end():
            # Signal round end in a non-blocking way
            thread = threading.Thread(target=self._end_round)
            thread.daemon = True
            thread.start()
            
        return result
    
    def _update_player_scores(self, results):
        """Update player scores based on round results"""
        for player_id, result in results.items():
            if player_id in self.players:
                player = self.players[player_id]
                
                # Get the reaction time or use a penalty value if invalid click
                reaction_time = result.get('reaction_time', 10.0)  # 10 seconds is penalty
                
                # Update player's total score and rounds played
                current_total = player['avg_time'] * player['rounds_played']
                player['rounds_played'] += 1
                player['avg_time'] = (current_total + reaction_time) / player['rounds_played']
    
    def _get_leaderboard(self):
        """Generate a leaderboard sorted by average reaction time (lower is better)"""
        leaderboard = []
        
        for player_id, player_data in self.players.items():
            if player_data['rounds_played'] > 0:
                leaderboard.append({
                    'username': player_data['username'],
                    'avg_time': player_data['avg_time'],
                    'rounds_played': player_data['rounds_played'],
                    'player_id': player_id
                })
        
        # Sort by average time (lower is better)
        leaderboard.sort(key=lambda x: x['avg_time'])
        
        # Return top 20 players
        return leaderboard[:20]