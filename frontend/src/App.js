import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import useLocalStorage from './hooks/useLocalStorage';
import Game from './components/Game';
import UsernameEntry from './components/UsernameEntry';
import WaitingRoom from './components/WaitingRoom';
import './styles/main.css';

const BACKEND_URL = 'http://localhost:5000';

function App() {
  // Game state
  const [gameState, setGameState] = useState('username'); // 'username', 'waiting', 'playing'
  const [socket, setSocket] = useState(null);
  const [username, setUsername] = useLocalStorage('reaction-game-username', '');
  const [playerId, setPlayerId] = useState(null);
  const [playerCount, setPlayerCount] = useState(0);
  const [currentRound, setCurrentRound] = useState(null);
  const [roundResults, setRoundResults] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [connected, setConnected] = useState(false);


  // Initialize socket connection
  useEffect(() => {
    if (socket) {
      socket.disconnect();
    }

    const newSocket = io(BACKEND_URL);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
      setSocket(newSocket);

      // If we already have a username, register with the server
      if (username) {
        newSocket.emit('register_player', { username });
      }
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
      setGameState('username');
    });

    // Clean up on unmount
    return () => {
      newSocket.disconnect();
    };
  }, []);

  // Listen for game events once socket is established
  useEffect(() => {
    if (!socket) return;

    socket.on('registration_status', (data) => {
      if (data.success) {
        setPlayerId(data.player_id);

        // Determine if we should join a game in progress or wait
        if (data.round_in_progress) {
          setGameState('playing');
          setCurrentRound(data.game_state);
        } else {
          setGameState('waiting');
        }
      } else {
        // Handle registration failure
        alert('Failed to join game. Please try again.');
        setGameState('username');
      }
    });

    socket.on('player_count', (data) => {
      setPlayerCount(data.count);
    });

    socket.on('round_start', (data) => {
      console.log('Round starting:', data);
      setGameState('playing');
      setCurrentRound(data);
      setRoundResults(null);
    });

    socket.on('round_end', (data) => {
      console.log('Round ended:', data);
      setRoundResults(data.results);
      setLeaderboard(data.leaderboard);
      setGameState('waiting');

    });

    socket.on('click_result', (data) => {
      console.log('Click result:', data);
      // This could be used to show immediate feedback
    });

  }, [socket]);

  // Handle username submission
  const handleUsernameSubmit = (name) => {
    setUsername(name);

    if (socket && connected) {
      socket.emit('register_player', { username: name });
    }
  };

  // Handle player ready for next round
  const handleReadyForNextRound = () => {
    if (socket) {
      socket.emit('join_waiting_room');
    }
  };

  // Handle player click during a round
  const handlePlayerClick = (data) => {
    if (socket && gameState === 'playing') {
      socket.emit('player_click', {
          ...data,
          client_now: Date.now() / 1000        
      });
    }
  };

  // Render the appropriate screen based on game state
  const renderGameState = () => {
    switch (gameState) {
      case 'username':
        return <UsernameEntry onSubmit={handleUsernameSubmit} />;

      case 'waiting':
        return (
          <WaitingRoom
            playerCount={playerCount}
            username={username}
            playerId={playerId}
            onReady={handleReadyForNextRound}
            roundResults={roundResults}
            leaderboard={leaderboard}
          />
        );

      case 'playing':
        return (
          <Game
            roundData={currentRound}
            onPlayerClick={handlePlayerClick}
            username={username}
          />
        );

      default:
        return <div>Loading...</div>;
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Reaction Time Game</h1>
        {connected ?
          <span className="connection-status connected">Connected</span> :
          <span className="connection-status disconnected">Disconnected</span>
        }
      </header>

      <main className="game-container">
        {renderGameState()}
      </main>

      <footer className="app-footer">
        <p>Players online: {playerCount}</p>
      </footer>
    </div>
  );
}

export default App;