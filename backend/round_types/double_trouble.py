import time
import random
from .base_round import BaseRound

class DoubleTroubleRound(BaseRound):
    def __init__(self, players):
        super().__init__(players)
        
        # Configure this round type
        self.round_config = {
            'delay': 3.0,         # Delay before boxes appear (seconds)
            'max_duration': 10.0, # Maximum round duration (seconds)
            'success_window': 7.0  # Time window for valid clicks after boxes appear (seconds)
        }
        
        # Generate random positions for both boxes
        # Make sure they don't overlap
        self.good_position = {
            'x': random.uniform(0.1, 0.9),  # Relative position (0-1) within container
            'y': random.uniform(0.1, 0.9)   # Relative position (0-1) within container
        }
        
        # Generate position for the bad box, ensuring some minimum distance
        while True:
            bad_x = random.uniform(0.1, 0.9)
            bad_y = random.uniform(0.1, 0.9)
            
            # Calculate distance between the two boxes
            distance = ((bad_x - self.good_position['x'])**2 + 
                       (bad_y - self.good_position['y'])**2)**0.5
            
            # If the distance is sufficient, use this position
            if distance > 0.2:  # 20% of the container width/height as minimum distance
                break
        
        self.bad_position = {
            'x': bad_x,
            'y': bad_y
        }
        
        # Randomize which box will be green and which will be red
        self.good_color = "#4CAF50"  # Green
        self.bad_color = "#FF5252"   # Red
        
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        return {
            'type': 'double_trouble',
            'instructions': 'Two colored boxes will appear. Click the GREEN box as fast as you can, avoid the RED box!',
            'max_duration': self.round_config['max_duration'],
            'delay': self.round_config['delay'],
            'good_position': self.good_position,
            'bad_position': self.bad_position,
            'good_color': self.good_color,
            'bad_color': self.bad_color
        }
    
    def execute(self):
        """Execute the round logic on the server"""
        self.start_time = time.time()
        
        # Sleep until the boxes should appear
        time.sleep(self.round_config['delay'])
        
        # Record the exact time when the boxes appeared
        self.active_time = time.time()
        
        # Wait for the remaining round time
        remaining_time = self.round_config['max_duration'] - (self.active_time - self.start_time)
        if remaining_time > 0:
            time.sleep(remaining_time)
    
    def process_click(self, player_id, data):
        """Process a player's click and return immediate feedback"""
        # Convert client timestamp to server timeline for fair comparison
        server_now = time.time()
        client_now = data.get('client_now', server_now)
        client_click =  data.get('client_click', server_now)
        click_position = data.get('position', None)
        
        # Adjust client click time to server timeline
        time_diff = server_now - client_now
        adjusted_click_time = server_now
        
        # Determine if the click was valid
        if self.active_time is None:
            # Boxes haven't appeared yet - too early!
            result = {
                'success': False,
                'message': 'Too early! The boxes haven\'t appeared yet.',
                'reaction_time': 10.0  # Penalty value
            }
        elif click_position is None:
            # No position data
            result = {
                'success': False,
                'message': 'Invalid click detected.',
                'reaction_time': 10.0  # Penalty value
            }
        else:
            # Boxes have appeared - calculate reaction time
            reaction_time = adjusted_click_time - self.active_time
            
            if reaction_time < 0:
                # Clicked before boxes appeared (should be rare with adjusted time)
                result = {
                    'success': False,
                    'message': 'Too early! The boxes hadn\'t appeared yet.',
                    'reaction_time': 10.0  # Penalty value
                }
            elif reaction_time <= self.round_config['success_window']:
                # Check if the click is closest to the good box or the bad box
                dist_to_good = ((click_position['x'] - self.good_position['x'])**2 + 
                               (click_position['y'] - self.good_position['y'])**2)**0.5
                
                dist_to_bad = ((click_position['x'] - self.bad_position['x'])**2 + 
                              (click_position['y'] - self.bad_position['y'])**2)**0.5
                
                if dist_to_good < dist_to_bad:
                    # Clicked closer to the good box
                    result = {
                        'success': True,
                        'message': f'Nice! You clicked the correct box in {reaction_time:.3f} seconds.',
                        'reaction_time': reaction_time
                    }
                else:
                    # Clicked closer to the bad box
                    result = {
                        'success': False,
                        'message': 'Oops! You clicked the wrong box!',
                        'reaction_time': 10.0  # Penalty for clicking the wrong box
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
            
        # If boxes have appeared and success window has elapsed, we can end early
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
                    'message': 'You didn\'t click any box during this round.',
                    'reaction_time': 10.0  # Penalty value for not clicking
                }                
        return results