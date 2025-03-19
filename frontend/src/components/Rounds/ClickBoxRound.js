import React, { useState, useEffect, useRef } from 'react';
import { playSuccess, playFailure } from '../../utils/audio';

function ClickBoxRound({ data, onPlayerClick }) {
  const [boxVisible, setBoxVisible] = useState(false);
  const [hasClicked, setHasClicked] = useState(false);
  const [message, setMessage] = useState('Wait for the box to appear...');
  const containerRef = useRef(null);
  const timeoutRef = useRef(null);
  
  // Set up the round when it loads
  useEffect(() => {
    // Set timer to show the box after the delay
    timeoutRef.current = setTimeout(() => {
      setBoxVisible(true);
      setMessage('Click the box now!');
      playSuccess(); // Play a sound when the box appears
    }, data.delay * 1000);
    
    // Clean up on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data.delay]);
  
  // Handle clicks on the box
  const handleBoxClick = (e) => {
    e.stopPropagation(); // Prevent the click from reaching the container
    
    if (hasClicked) return; // Prevent multiple clicks
    
    setHasClicked(true);
    setMessage('Good job!');
    
    // Record the click time
    const clickTime = Date.now() / 1000;
    onPlayerClick(clickTime);
    playSuccess();
  };
  
  // Handle clicks on the container (missed clicks)
  const handleContainerClick = () => {
    if (boxVisible && !hasClicked) {
      setMessage('Try to click the small box!');
      playFailure();
    } else if (!boxVisible && !hasClicked) {
      setMessage('Wait for the box to appear first!');
      playFailure();
    }
  };
  
  return (
    <div className="round-container click-box-round">
      <div 
        ref={containerRef}
        className="click-box-container"
        onClick={handleContainerClick}
        style={{
          position: 'relative',
          width: '100%',
          height: '300px',
          backgroundColor: '#f5f5f5',
          border: '2px solid #ccc',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      >
        {boxVisible && (
          <div
            className="click-target-box"
            onClick={handleBoxClick}
            style={{
              position: 'absolute',
              top: `${data.position.y * 100}%`,
              left: `${data.position.x * 100}%`,
              transform: 'translate(-50%, -50%)',
              width: '50px',
              height: '50px',
              backgroundColor: hasClicked ? '#2ecc71' : '#3498db',
              borderRadius: '4px',
              cursor: hasClicked ? 'default' : 'pointer',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              transition: 'background-color 0.2s ease'
            }}
          />
        )}
        
        <div
          style={{
            position: 'absolute',
            bottom: '10px',
            width: '100%',
            textAlign: 'center',
            color: '#555',
            fontWeight: 'bold'
          }}
        >
          {message}
        </div>
      </div>
    </div>
  );
}

export default ClickBoxRound;