import time
import random
from .base_round import BaseRound

class ClickBoxRound(BaseRound):
    def __init__(self, players):
        super().__init__(players)
        
        # Configure this round type
        self.round_config = {
            'delay': 3.0,         # Delay before box appears (seconds)
            'max_duration': 10.0, # Maximum round duration (seconds)
            'success_window': 7.0  # Time window for valid clicks after box appears (seconds)
        }
        
        # Generate random position for the small box
        self.position = {
            'x': random.uniform(0.1, 0.9),  # Relative position (0-1) within container
            'y': random.uniform(0.1, 0.9)   # Relative position (0-1) within container
        }
        
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        return {
            'type': 'click_box',
            'instructions': 'A small box will appear after 3 seconds. Click it as fast as you can!',
            'max_duration': self.round_config['max_duration'],
            'delay': self.round_config['delay'],
            'position': self.position  # Random position for the box
        }
    
    def execute(self):
        """Execute the round logic on the server"""
        self.start_time = time.time()
        
        # Sleep until the box should appear
        time.sleep(self.round_config['delay'])
        
        # Record the exact time when the box appeared
        self.active_time = time.time()
        
        # Wait for the remaining round time
        remaining_time = self.round_config['max_duration'] - (self.active_time - self.start_time)
        if remaining_time > 0:
            time.sleep(remaining_time)
    
    def process_click(self, player_id, click_time):
        """Process a player's click and return immediate feedback"""
        # Convert client timestamp to server timeline for fair comparison
        server_now = time.time()
        client_now = click_time.get('client_now', server_now)
        client_click = click_time.get('client_click', server_now)
        
        # Adjust client click time to server timeline
        time_diff = server_now - client_now
        # adjusted_click_time = client_click + time_diff
        adjusted_click_time = server_now
        
        # Determine if the click was valid
        if self.active_time is None:
            # Box hasn't appeared yet - too early!
            result = {
                'success': False,
                'message': 'Too early! The box hasn\'t appeared yet.',
                'reaction_time': 10.0  # Penalty value
            }
        else:
            # Box has appeared - calculate reaction time
            reaction_time = adjusted_click_time - self.active_time
            
            if reaction_time < 0:
                # Clicked before box appeared (should be rare with adjusted time)
                result = {
                    'success': False,
                    'message': 'Too early! The box hadn\'t appeared yet.',
                    'reaction_time': 10.0  # Penalty value
                }
            elif reaction_time <= self.round_config['success_window']:
                # Valid click within success window
                result = {
                    'success': True,
                    'message': f'Nice! You clicked in {reaction_time:.3f} seconds.',
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
            
        # If box has appeared and success window has elapsed, we can end early
        if self.active_time and (time.time() - self.active_time) > self.round_config['success_window']:
            return True
        
        # If all players have a result we can end early
        if len(self.player_results) == len(self.players):
            return True
            
        return False
        
    def get_results(self):
        """Get the final results for all players in this round, including those who didn't click"""
        # Get the default results for players who did click
        results = super().get_results()
        
        # Add default "no click" results for players who didn't click
        for player_id in self.players:
            if player_id not in results:
                results[player_id] = {
                    'success': False,
                    'message': 'You didn\'t click the box during this round.',
                    'reaction_time': 10.0  # Penalty value for not clicking
                }                
        return results