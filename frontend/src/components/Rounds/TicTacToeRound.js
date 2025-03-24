import React, { useState, useEffect } from 'react';
import { playSuccess, playFailure } from '../../utils/audio';
import '../../styles/ticTacToe.css';

function TicTacToeRound({ data, onPlayerClick }) {
  const [boardVisible, setBoardVisible] = useState(false);
  const [boardState, setBoardState] = useState(data.board || Array(3).fill(Array(3).fill(null)));
  const [hasClicked, setHasClicked] = useState(false);
  const [clickedCell, setClickedCell] = useState(null);
  const [message, setMessage] = useState('Tic-Tac-Toe board will appear soon...');
  const [feedback, setFeedback] = useState(null);

  // Set up the round when it loads
  useEffect(() => {
    // Set timer to show the board after the delay
    const timer = setTimeout(() => {
      setBoardVisible(true);
      setMessage('Find and click on the winning move for X!');
      playSuccess(); // Play a sound when the board appears
    }, data.delay * 1000);
    
    return () => clearTimeout(timer);
  }, [data.delay]);

  const handleCellClick = (row, col) => {
    if (!boardVisible || hasClicked || boardState[row][col] !== null) {
      return;
    }
    
    setHasClicked(true);
    setClickedCell({ row, col });
    
    // Record the click time and position
    const clickTime = Date.now() / 1000;
    onPlayerClick({
      client_now: clickTime,
      position: { row, col }
    });
  };

  // Function to render a cell
  const renderCell = (value, row, col) => {
    let cellClass = 'cell';
    
    // Add highlighting for the cell that was clicked
    if (hasClicked && clickedCell && clickedCell.row === row && clickedCell.col === col) {
      cellClass += ' clicked-cell';
    }
    
    return (
      <div 
        key={`${row}-${col}`}
        className={cellClass}
        onClick={() => handleCellClick(row, col)}
      >
        {value === 'X' && <span className="x-mark">X</span>}
        {value === 'O' && <span className="o-mark">O</span>}
      </div>
    );
  };

  // Function to render the board
  const renderBoard = () => {
    return (
      <div className="tic-tac-toe-board">
        {boardState.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row">
            {row.map((cell, colIndex) => renderCell(cell, rowIndex, colIndex))}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="round-container tic-tac-toe-round">
      <div className="game-instructions">
        {message}
      </div>
      
      <div className="board-container" style={{ opacity: boardVisible ? 1 : 0.3 }}>
        {renderBoard()}
      </div>
      
      {feedback && (
        <div className={`feedback ${feedback.status}`}>
          {feedback.message}
          {feedback.reaction_time && (
            <span className="reaction-time">Time: {feedback.reaction_time}s</span>
          )}
        </div>
      )}
    </div>
  );
}

export default TicTacToeRound; 