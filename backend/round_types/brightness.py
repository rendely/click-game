import time
import random
from .base_round import BaseRound

class BrightnessRound(BaseRound):
    def __init__(self, players):
        super().__init__(players)
        
        # Configure this round type
        self.round_config = {
            'initial_pause': 2.0,     # Initial pause to read instructions (seconds)
            'brightness_duration': 5.0, # How long brightness changes take (seconds)
            'max_duration': 10.0,     # Maximum round duration (seconds)
            'target_brightness': random.randint(30, 80)  # Target brightness (0-100)
        }
        
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        return {
            'type': 'brightness',
            'instructions': f'Click when the brightness matches the target of {self.round_config["target_brightness"]}%',
            'target_brightness': self.round_config['target_brightness'],
            'initial_pause': self.round_config['initial_pause'],
            'brightness_duration': self.round_config['brightness_duration'],
            'max_duration': self.round_config['max_duration']
        }
    
    def execute(self):
        """Execute the round logic on the server"""
        self.start_time = time.time()
        
        # Wait for the initial pause
        time.sleep(self.round_config['initial_pause'])
        
        # Record when brightness starts changing
        self.active_time = time.time()
        print('done executing')
        
        # Wait for the remaining round time
        remaining_time = self.round_config['max_duration'] - self.round_config['initial_pause']
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
        adjusted_click_time = client_click + time_diff
        
        # Determine if the click timing was valid
        if self.active_time is None or adjusted_click_time < self.active_time:
            # Clicked before brightness starts changing
            result = {
                'success': False,
                'message': 'Too early! The brightness hasn\'t started changing yet.',
                'reaction_time': 10.0,  # Penalty
                'brightness_error': 100  # Maximum error
            }
        else:
            # Calculate how far into the brightness change the click occurred
            time_into_brightness = adjusted_click_time - self.active_time
            
            if time_into_brightness > self.round_config['brightness_duration']:
                # Clicked after brightness change completed
                result = {
                    'success': False,
                    'message': 'Too late! The brightness change has completed.',
                    'reaction_time': time_into_brightness,
                    'brightness_error': 100  # Maximum error
                }
            else:
                # Calculate current brightness at click time
                # Assuming linear brightness increase from 0% to 100% over the duration
                current_brightness = (time_into_brightness / self.round_config['brightness_duration']) * 100
                
                # Calculate how close to target
                target = self.round_config['target_brightness']
                brightness_error = abs(current_brightness - target)
                
                # Scale reaction time based on accuracy (lower error = better score)
                adjusted_reaction_time = time_into_brightness * (1 + brightness_error / 100)
                
                # Provide feedback based on accuracy
                if brightness_error < 5:
                    result = {
                        'success': True,
                        'message': f'Perfect! You were only {brightness_error:.1f}% off the target.',
                        'reaction_time': adjusted_reaction_time,
                        'brightness_error': brightness_error
                    }
                elif brightness_error < 15:
                    result = {
                        'success': True,
                        'message': f'Good! You were {brightness_error:.1f}% off the target.',
                        'reaction_time': adjusted_reaction_time,
                        'brightness_error': brightness_error
                    }
                else:
                    result = {
                        'success': False,
                        'message': f'Off target! You were {brightness_error:.1f}% off.',
                        'reaction_time': adjusted_reaction_time,
                        'brightness_error': brightness_error
                    }
        
        # Store result for this player
        self.player_results[player_id] = result
        
        return result
    
    def should_end(self):
        """Round should end if max duration elapsed"""
        # Check if base condition is met (max duration)
        if super().should_end():
            return True
            
        # If active time has passed and brightness duration is complete, we can end
        if (self.active_time and 
            (time.time() - self.active_time) > self.round_config['brightness_duration']):
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
                    'message': 'You didn\'t click during this round.',
                    'reaction_time': 10.0,
                    'brightness_error': 100  # Maximum error
                }          
        return results