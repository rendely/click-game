import React, { useState, useEffect, useRef } from 'react';
import { playSuccess, playFailure } from '../../utils/audio';

function ColorChangeRound({ data, onPlayerClick }) {
  const [boxColor, setBoxColor] = useState('#e0e0e0'); // Start with gray
  const [isActive, setIsActive] = useState(false);
  const [hasClicked, setHasClicked] = useState(false);
  const [timer, setTimer] = useState(null);
  const timeoutRef = useRef(null);
  
  // Set up the round when it loads
  useEffect(() => {
    // Wait a random amount of time before changing color
    const changeColorDelay = Math.random() * (7000 - 2000) + 2000; // 2-7 seconds
    
    timeoutRef.current = setTimeout(() => {
      setBoxColor('#4a90e2'); // Change to blue
      setIsActive(true);
      playSuccess(); // Play a sound when color changes
    }, changeColorDelay);
    
    // Clean up on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  // Handle clicks on the box
  const handleClick = () => {
    if (hasClicked) return; // Prevent multiple clicks
    
    setHasClicked(true);
    
    if (!isActive) {
      // Clicked too early
      setBoxColor('#e74c3c'); // Red for error
      playFailure();
    } else {
      // Valid click
      const clickTime = Date.now() / 1000;
      onPlayerClick(clickTime);
      playSuccess();
    }
  };
  
  return (
    <div className="round-container color-change-round">
      <div
        className="color-box"
        style={{
          backgroundColor: boxColor,
          cursor: hasClicked ? 'default' : 'pointer'
        }}
        onClick={handleClick}
      >
        {hasClicked ? (
          isActive ? 'Good!' : 'Too Early!'
        ) : (
          <span>Wait for color change...</span>
        )}
      </div>
    </div>
  );
}

export default ColorChangeRound;