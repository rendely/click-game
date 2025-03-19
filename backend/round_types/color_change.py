import time
import random
from .base_round import BaseRound

class ColorChangeRound(BaseRound):
    def __init__(self, players):
        super().__init__(players)
        
        # Configure this round type
        self.round_config = {
            'min_delay': 2.0,    # Minimum delay before color change (seconds)
            'max_delay': 7.0,    # Maximum delay before color change (seconds)
            'max_duration': 10.0,  # Maximum round duration (seconds)
            'success_window': 3.0   # Time window for valid clicks after color change (seconds)
        }
        
        # Generate random delay for this instance
        self.color_change_delay = random.uniform(
            self.round_config['min_delay'], 
            self.round_config['max_delay']
        )
        
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        return {
            'type': 'color_change',
            'instructions': 'Click when the box changes color! Don\'t click too early.',
            'max_duration': self.round_config['max_duration'],
            'delay': self.color_change_delay
        }
    
    def execute(self):
        """Execute the round logic on the server"""
        self.start_time = time.time()
        
        # Sleep until the color should change
        time.sleep(self.color_change_delay)
        
        # Record the exact time when the color changed
        self.active_time = time.time()
        
        # Broadcast the color change event
        # This would typically use socketio, but here we just record the time
        
        # Wait for the remaining round time
        remaining_time = self.round_config['max_duration'] - (self.active_time - self.start_time)
        if remaining_time > 0:
            time.sleep(remaining_time)
    
    def process_click(self, player_id, click_time):
        """Process a player's click and return immediate feedback"""
        # Convert client timestamp to server timeline for fair comparison
        # In a real implementation, you might want a more sophisticated sync mechanism
        server_now = time.time()
        client_now = click_time.get('client_now', server_now)
        client_click = click_time.get('client_click', server_now)
        
        # Adjust client click time to server timeline
        time_diff = server_now - client_now
        # adjusted_click_time = client_click + time_diff
        adjusted_click_time = server_now
        
        # Determine if the click was valid
        if self.active_time is None:
            # Color hasn't changed yet - too early!
            result = {
                'success': False,
                'message': 'Too early! The color hasn\'t changed yet.',
                'reaction_time': 10.0  # Penalty value
            }
        else:
            # Color has changed - calculate reaction time
            reaction_time = adjusted_click_time - self.active_time
            
            if reaction_time < 0:
                # Clicked before color change (should be rare with adjusted time)
                result = {
                    'success': False,
                    'message': 'Too early! The color hadn\'t changed yet.',
                    'reaction_time': 10.0  # Penalty value
                }
            elif reaction_time <= self.round_config['success_window']:
                # Valid click within success window
                result = {
                    'success': True,
                    'message': f'Nice! You reacted in {reaction_time:.3f} seconds.',
                    'reaction_time': reaction_time
                }
            else:
                # Too slow (beyond success window)
                result = {
                    'success': False,
                    'message': f'Too slow! You took {reaction_time:.3f} seconds.',
                    'reaction_time': reaction_time
                }
        
        # Store result for this player
        self.player_results[player_id] = result
        
        return result
    
    def should_end(self):
        """Round should end if max duration elapsed or all players have clicked"""
        # Check if base condition is met (max duration)
        if super().should_end():
            return True
            
        # If color has changed and success window has elapsed, we can end early
        if self.active_time and (time.time() - self.active_time) > self.round_config['success_window']:
            return True
        
        # If all players have a result we can end early
        if len(self.player_results) == len(self.players):
            return True
            
        return False