import React, { useState, useEffect } from 'react';
import ColorChangeRound from './Rounds/ColorChangeRound';
import BrightnessRound from './Rounds/BrightnessRound';
import ClickBoxRound from './Rounds/ClickBoxRound';
import DoubleTroubleRound from './Rounds/DoubleTroubleRound';
import TicTacToeRound from './Rounds/TicTacToeRound';
import { playNotification } from '../utils/audio';

function Game({ roundData, onPlayerClick, username }) {
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  
  // Play notification when round starts
  useEffect(() => {
    if (roundData) {
      playNotification();
    }
  }, [roundData]);

  // Render the appropriate round component based on round type
  const renderRound = () => {
    if (!roundData) return <div>Loading...</div>;
    
    switch (roundData.round_type) {
      case 'ColorChangeRound':
        return (
          <ColorChangeRound 
            data={roundData.round_data} 
            onPlayerClick={handlePlayerClick}
          />
        );
      case 'BrightnessRound':
        return (
          <BrightnessRound
            data={roundData.round_data}
            onPlayerClick={handlePlayerClick}
          />
        );
      case 'ClickBoxRound':
        return (
          <ClickBoxRound
            data={roundData.round_data}
            onPlayerClick={handlePlayerClick}
          />
        );
      case 'DoubleTroubleRound':
        return (
          <DoubleTroubleRound
            data={roundData.round_data}
            onPlayerClick={handlePlayerClick}
          />
        );
      case 'TicTacToeRound':
        return (
          <TicTacToeRound
            data={roundData.round_data}
            onPlayerClick={handlePlayerClick}
          />
        );
      default:
        return (
          <div className="unknown-round">
            <h3>Unknown Round Type</h3>
            <p>Waiting for next round...</p>
          </div>
        );
    }
  };

  // Handle player click with feedback
  const handlePlayerClick = (clickTime) => {
    onPlayerClick(clickTime);
  };

  return (
    <div className="game-round">
      <div className="round-info">
        <h2>Round in Progress</h2>
        {roundData && roundData.round_data && (
          <p className="instructions">{roundData.round_data.instructions}</p>
        )}
      </div>
      
      <div className="round-content">
        {renderRound()}
      </div>
    </div>
  );
}

export default Game;