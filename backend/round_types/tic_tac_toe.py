import time
import random
from .base_round import BaseRound

class TicTacToeRound(BaseRound):
    def __init__(self, players):
        super().__init__(players)
        
        # Configure this round type
        self.round_config = {
            'delay': 3.0,         # Delay before the board appears (seconds)
            'max_duration': 10.0, # Maximum round duration (seconds)
            'success_window': 7.0  # Time window for valid clicks after board appears (seconds)
        }
        
        # Generate a random mid-game tic-tac-toe board with a winning move
        self.board, self.winning_move = self._generate_board()
        
    def _generate_board(self):
        """Generate a mid-game tic-tac-toe board with a winning move.
        Return the board and the winning move position."""
        
        # Create possible board configurations with one winning move for X
        board_configs = [
            # Horizontal win setups
            [['X', 'X', None], ['O', 'O', None], [None, None, None]],  # Top row win
            [[None, None, None], ['X', 'X', None], ['O', 'O', None]],  # Middle row win
            [[None, 'O', None], [None, 'O', None], ['X', 'X', None]],  # Bottom row win
            
            # Vertical win setups
            [['X', 'O', None], ['X', 'O', None], [None, None, None]],  # Left column win
            [[None, 'X', 'O'], [None, 'X', None], [None, None, 'O']],  # Middle column win
            [['O', None, 'X'], [None, None, 'X'], [None, 'O', None]],  # Right column win
            
            # Diagonal win setups
            [['X', None, 'O'], [None, 'X', 'O'], [None, None, None]],  # Main diagonal win
            [['O', None, None], ['O', 'X', None], [None, None, 'X']],  # Anti-diagonal win
            
            # More complex setups
            [['X', 'O', None], [None, 'X', 'O'], [None, None, None]],  # Diagonal with distraction
            [['O', 'X', None], ['X', 'O', None], [None, None, None]],  # Complex setup
            [[None, 'O', 'X'], [None, 'X', 'O'], [None, None, None]],  # Another complex setup
        ]
        
        # Choose a random board configuration
        board = random.choice(board_configs)
        
        # Find the winning move position (None position that completes three X's)
        winning_position = None
        
        # Check rows
        for i in range(3):
            if board[i].count('X') == 2 and None in board[i]:
                row, col = i, board[i].index(None)
                # Verify this is a winning move
                board[row][col] = 'X'  # Temporarily place X
                if self._check_win(board, 'X'):
                    winning_position = (row, col)
                board[row][col] = None  # Reset the position
                if winning_position:
                    break
        
        # Check columns if no winning move found yet
        if not winning_position:
            for j in range(3):
                column = [board[i][j] for i in range(3)]
                if column.count('X') == 2 and None in column:
                    col = j
                    row = [board[i][j] for i in range(3)].index(None)
                    # Verify this is a winning move
                    board[row][col] = 'X'  # Temporarily place X
                    if self._check_win(board, 'X'):
                        winning_position = (row, col)
                    board[row][col] = None  # Reset the position
                    if winning_position:
                        break
        
        # Check diagonals if no winning move found yet
        if not winning_position:
            # Main diagonal
            diag = [board[i][i] for i in range(3)]
            if diag.count('X') == 2 and None in diag:
                idx = diag.index(None)
                board[idx][idx] = 'X'  # Temporarily place X
                if self._check_win(board, 'X'):
                    winning_position = (idx, idx)
                board[idx][idx] = None  # Reset the position
                
        if not winning_position:
            # Anti-diagonal
            anti_diag = [board[i][2-i] for i in range(3)]
            if anti_diag.count('X') == 2 and None in anti_diag:
                idx = anti_diag.index(None)
                board[idx][2-idx] = 'X'  # Temporarily place X
                if self._check_win(board, 'X'):
                    winning_position = (idx, 2-idx)
                board[idx][2-idx] = None  # Reset the position
        
        return board, winning_position
    
    def _check_win(self, board, player):
        """Check if a player has won on the given board."""
        # Check rows
        for i in range(3):
            if board[i].count(player) == 3:
                return True
                
        # Check columns
        for j in range(3):
            if [board[i][j] for i in range(3)].count(player) == 3:
                return True
                
        # Check main diagonal
        if [board[i][i] for i in range(3)].count(player) == 3:
            return True
            
        # Check anti-diagonal
        if [board[i][2-i] for i in range(3)].count(player) == 3:
            return True
            
        return False
        
    def get_client_data(self):
        """Return round data to send to clients for initialization"""
        return {
            'type': 'tic_tac_toe',
            'instructions': 'Find and click on the winning move for X as fast as you can!',
            'max_duration': self.round_config['max_duration'],
            'delay': self.round_config['delay'],
            'board': self.board,
            'winning_move': None  # We don't send the winning move to the client
        }
    
    def execute(self):
        """Execute the round logic on the server"""
        self.start_time = time.time()
        
        # Sleep until the board should appear
        time.sleep(self.round_config['delay'])
        
        # Record the exact time when the board appeared
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
        client_delta = server_now - client_now
        
        # Get the click position from data
        if 'position' not in data:
            return {'status': 'error', 'message': 'Missing position data'}
            
        click_row = data['position']['row']
        click_col = data['position']['col']
        
        # Initialize response
        result = {'status': 'error', 'message': 'Invalid click'}
        
        # If the round hasn't started yet
        if self.active_time is None:
            result = {'status': 'too_early', 'message': 'Board not active yet'}
            
        # If player already has a result, no need to process again
        elif player_id in self.player_results:
            existing_result = self.player_results[player_id]
            result = {
                'status': existing_result['status'],
                'message': 'You already clicked',
                'reaction_time': existing_result.get('reaction_time')
            }
            
        # Check if the click is within the allowed time window
        elif self.active_time and server_now - self.active_time <= self.round_config['success_window']:
            # Calculate reaction time (adjusted for client-server time difference)
            reaction_time = (client_now + client_delta) - self.active_time
            
            # Check if the click is on the winning move
            if (click_row, click_col) == self.winning_move:
                self.player_results[player_id] = {
                    'status': 'success',
                    'reaction_time': reaction_time,
                    'position': {'row': click_row, 'col': click_col}
                }
                result = {
                    'status': 'success',
                    'message': 'Correct move!',
                    'reaction_time': round(reaction_time, 3)
                }
            else:
                self.player_results[player_id] = {
                    'status': 'wrong_move',
                    'reaction_time': None,
                    'position': {'row': click_row, 'col': click_col}
                }
                result = {
                    'status': 'wrong_move',
                    'message': 'Incorrect move!',
                }
        else:
            # Click was too late
            self.player_results[player_id] = {
                'status': 'too_late',
                'reaction_time': None
            }
            result = {'status': 'too_late', 'message': 'Too late!'}
            
        return result
        
    def should_end(self):
        """Determine if the round should end based on current state"""
        # If all players have clicked or the max time has elapsed
        if self.start_time is None:
            return False
            
        all_players_clicked = all(player_id in self.player_results for player_id in self.players)
        elapsed = time.time() - self.start_time
        
        return all_players_clicked or elapsed > self.round_config['max_duration']
        
    def get_results(self):
        """Get the final results for all players in this round"""
        final_results = {}
        
        for player_id, player_data in self.players.items():
            if player_id in self.player_results:
                result = self.player_results[player_id]
                final_results[player_id] = {
                    'username': player_data['username'],
                    'status': result['status'],
                    'reaction_time': result.get('reaction_time'),
                    'score': self._calculate_score(result)
                }
            else:
                # Player didn't click
                final_results[player_id] = {
                    'username': player_data['username'],
                    'status': 'no_click',
                    'reaction_time': None,
                    'score': 0
                }
                
        # Add the winning move to the results
        final_results['winning_move'] = {'row': self.winning_move[0], 'col': self.winning_move[1]}
                
        return final_results
        
    def _calculate_score(self, result):
        """Calculate a score for the player based on performance"""
        if result['status'] == 'success':
            # Faster reaction time = higher score
            # Max score is 100, min score is 50 for correct answers
            reaction_time = result['reaction_time']
            max_time = self.round_config['success_window']
            
            # Linear scoring: 100 points for immediate click, 50 points for slowest valid click
            score = max(50, 100 - (reaction_time / max_time) * 50)
            return round(score)
        else:
            # Wrong click or no click
            return 0 