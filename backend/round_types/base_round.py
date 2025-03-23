import time
from abc import ABC, abstractmethod

class BaseRound(ABC):
    def __init__(self, players):
        self.start_time = None
        self.active_time = None  # When the actual interaction should happen
        self.player_results = {}  # player_id -> result data
        self.round_config = {}    # Configuration for this round
        self.players = players
        
    @abstractmethod
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        pass
    
    @abstractmethod
    def execute(self):
        """Execute the round logic on the server"""
        pass
    
    @abstractmethod
    def process_click(self, player_id, data):
        """Process a player's click and return immediate feedback"""
        pass
    
    def should_end(self):
        """Determine if the round should end based on current state"""
        # Default implementation: round ends after max_duration
        if self.start_time is None:
            return False
            
        elapsed = time.time() - self.start_time
        return elapsed > self.round_config.get('max_duration', 15)  # Default 15s timeout
    
    def get_results(self):
        """Get the final results for all players in this round"""
        return self.player_results