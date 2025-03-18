import React from 'react';

function Leaderboard({ leaderboard, currentUsername }) {
  // Find the current user's position in the leaderboard
  const userPosition = leaderboard.findIndex(
    player => player.username === currentUsername
  );
  
  return (
    <div className="leaderboard">
      <h3>Leaderboard</h3>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Avg. Time</th>
            <th>Rounds</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((player, index) => (
            <tr 
              key={player.player_id || index} 
              className={player.username === currentUsername ? 'current-player' : ''}
            >
              <td>{index + 1}</td>
              <td>{player.username}</td>
              <td>{player.avg_time.toFixed(3)}s</td>
              <td>{player.rounds_played}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {userPosition === -1 && currentUsername && (
        <p className="not-on-leaderboard">
          Play a round to appear on the leaderboard!
        </p>
      )}
    </div>
  );
}

export default Leaderboard;