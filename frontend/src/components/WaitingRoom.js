import React, { useEffect } from 'react';
import Leaderboard from './Leaderboard';
import { playNotification, playWelcomeMusic } from '../utils/audio';

function WaitingRoom({ playerCount, username, playerId, onReady, roundResults, leaderboard }) {


  
  // Play notification when results are updated
  useEffect(() => {
    if (roundResults) {
      playNotification();
      playWelcomeMusic()
    }
  }, [roundResults]);

  // Format player result if available
  const formatPlayerResult = () => {
    if (!roundResults || !username) return null;
    
    // Find current player's result
    const myResult = roundResults[playerId];
    
    if (!myResult) return null;
    
    return (
      <div className="player-result">
        <h3>Your Result</h3>
        <p className={myResult.success ? "success-message" : "error-message"}>
          {myResult.message}
        </p>
        <p>Reaction time: {myResult.reaction_time.toFixed(3)}s</p>
      </div>
    );
  };

  return (
    <div className="waiting-room">
      <h2>Waiting for Next Round</h2>
      <p>Players online: {playerCount}</p>
      
      {/* Show round results if available */}
      {roundResults && (
        <div className="round-results">
          <h3>Last Round Results</h3>
          {formatPlayerResult()}
        </div>
      )}
      
      {/* Show leaderboard */}
      {leaderboard && leaderboard.length > 0 && (
        <Leaderboard leaderboard={leaderboard} currentUsername={username} />
      )}
      
      <div className="ready-section">
        <p>The next round will start automatically when all players are ready.</p>
        <button 
          className="primary-button"
          onClick={onReady}
        >
          I'm Ready!
        </button>
      </div>
    </div>
  );
}

export default WaitingRoom;