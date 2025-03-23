import React, { useState, useEffect, useRef } from 'react';
import { playSuccess, playFailure } from '../../utils/audio';

function DoubleTroubleRound({ data, onPlayerClick }) {
  const [boxesVisible, setBoxesVisible] = useState(false);
  const [hasClicked, setHasClicked] = useState(false);
  const [message, setMessage] = useState('Wait for the boxes to appear...');
  const containerRef = useRef(null);
  const timeoutRef = useRef(null);
  
  // Set up the round when it loads
  useEffect(() => {
    // Set timer to show the boxes after the delay
    timeoutRef.current = setTimeout(() => {
      setBoxesVisible(true);
      setMessage('Click the GREEN box! Avoid the RED box!');
      playSuccess(); // Play a sound when the boxes appear
    }, data.delay * 1000);
    
    // Clean up on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data.delay]);
  
  // Handle clicks on the good box
  const handleGoodBoxClick = (e) => {
    e.stopPropagation(); // Prevent the click from reaching the container
    
    if (hasClicked) return; // Prevent multiple clicks
    
    setHasClicked(true);
    setMessage('Good job! You clicked the correct box!');
    
    // Get the click coordinates relative to the container
    const rect = containerRef.current.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) / rect.width;
    const clickY = (e.clientY - rect.top) / rect.height;
    
    // Record the click time and position
    const clickTime = Date.now() / 1000;
    onPlayerClick({
      client_click: clickTime,
      client_now: clickTime,
      position: { x: clickX, y: clickY }
    });
    playSuccess();
  };
  
  // Handle clicks on the bad box
  const handleBadBoxClick = (e) => {
    e.stopPropagation(); // Prevent the click from reaching the container
    
    if (hasClicked) return; // Prevent multiple clicks
    
    setHasClicked(true);
    setMessage('Oops! You clicked the wrong box!');
    
    // Get the click coordinates relative to the container
    const rect = containerRef.current.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) / rect.width;
    const clickY = (e.clientY - rect.top) / rect.height;
    
    // Record the click time and position
    const clickTime = Date.now() / 1000;
    onPlayerClick({
      client_click: clickTime,
      client_now: clickTime,
      position: { x: clickX, y: clickY }
    });
    playFailure();
  };
  
  // Handle clicks on the container (missed clicks)
  const handleContainerClick = (e) => {
    // If boxes are visible and player hasn't clicked yet
    if (boxesVisible && !hasClicked) {
      // Get the click coordinates relative to the container
      const rect = containerRef.current.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) / rect.width;
      const clickY = (e.clientY - rect.top) / rect.height;
      
      setHasClicked(true);
      setMessage('You missed both boxes!');
      
      // Record the click time and position
      const clickTime = Date.now() / 1000;
      onPlayerClick({
        client_click: clickTime,
        client_now: clickTime,
        position: { x: clickX, y: clickY }
      });
      playFailure();
    } else if (!boxesVisible && !hasClicked) {
      setMessage('Wait for the boxes to appear first!');
      playFailure();
    }
  };
  
  return (
    <div className="round-container double-trouble-round">
      <div 
        ref={containerRef}
        className="double-trouble-container"
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
        {boxesVisible && (
          <>
            <div
              className="good-box"
              onClick={handleGoodBoxClick}
              style={{
                position: 'absolute',
                top: `${data.good_position.y * 100}%`,
                left: `${data.good_position.x * 100}%`,
                transform: 'translate(-50%, -50%)',
                width: '50px',
                height: '50px',
                backgroundColor: data.good_color,
                borderRadius: '4px',
                cursor: hasClicked ? 'default' : 'pointer',
                boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
                transition: 'background-color 0.2s ease'
              }}
            />
            
            <div
              className="bad-box"
              onClick={handleBadBoxClick}
              style={{
                position: 'absolute',
                top: `${data.bad_position.y * 100}%`,
                left: `${data.bad_position.x * 100}%`,
                transform: 'translate(-50%, -50%)',
                width: '50px',
                height: '50px',
                backgroundColor: data.bad_color,
                borderRadius: '4px',
                cursor: hasClicked ? 'default' : 'pointer',
                boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
                transition: 'background-color 0.2s ease'
              }}
            />
          </>
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

export default DoubleTroubleRound;