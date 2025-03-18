import React, { useState, useEffect, useRef, useCallback } from 'react';
import { playNotification, playSuccess, playFailure } from '../../utils/audio';

function BrightnessRound({ data, onPlayerClick }) {
  const [brightness, setBrightness] = useState(50); // Initial brightness
  const [isChanging, setIsChanging] = useState(false);
  const [hasClicked, setHasClicked] = useState(false);
  const startTimeRef = useRef(null);
  const animationRef = useRef(null);
  const targetBrightness = data?.target_brightness || 75;
  const initialPause = (data?.initial_pause || 2) * 1000;
  const brightnessChangeDuration = (data?.brightness_duration || 5) * 1000;
  
  const updateBrightness = useCallback(() => {
    if (!startTimeRef.current) {
      console.log('No start time set');
      return;
    }
    
    const elapsed = Date.now() - startTimeRef.current;
    const progress = Math.min(elapsed / brightnessChangeDuration, 1);
    
    // Linear increase from 0% to 100% brightness
    const newBrightness = Math.floor(progress * 100);
    console.log('Updating brightness:', {
      elapsed,
      progress,
      newBrightness,
      brightnessChangeDuration
    });
    setBrightness(newBrightness);
    
    if (progress < 1 && !hasClicked) {
      animationRef.current = requestAnimationFrame(updateBrightness);
    } else {
      setIsChanging(false);
    }
  }, [brightnessChangeDuration, hasClicked]);
  
  // Initialize the round
  useEffect(() => {
    console.log('Starting round with initial pause:', initialPause);
    // First pause to read instructions
    const timeoutId = setTimeout(() => {
      console.log('Initial pause complete, starting animation');
      setIsChanging(true);
      startTimeRef.current = Date.now();
      playNotification();
      
      // Start the brightness animation
      animationRef.current = requestAnimationFrame(updateBrightness);
    }, initialPause);
    
    return () => {
      clearTimeout(timeoutId);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [initialPause, updateBrightness]);
  
  // Rest of the component remains the same...
  const handleClick = () => {
    if (hasClicked || !isChanging) return;
    
    setHasClicked(true);
    cancelAnimationFrame(animationRef.current);
    
    const clickTime = Date.now() / 1000;
    onPlayerClick(clickTime);
    
    // Calculate how close to target
    const brightnessError = Math.abs(brightness - targetBrightness);
    
    if (brightnessError < 10) {
      playSuccess();
    } else {
      playFailure();
    }
  };
  
  const getBackgroundColor = () => {
    const value = Math.floor(255 * (brightness / 100));
    return `rgb(${value}, ${value}, ${value})`;
  };
  
  const getTextColor = () => {
    return brightness > 50 ? '#000' : '#fff';
  };
  
  return (
    <div className="round-container brightness-round">
      <div className="target-info">
        <span>Target Brightness: {targetBrightness}%</span>
        <div 
          className="target-sample" 
          style={{ 
            backgroundColor: `rgb(${Math.floor(255 * (targetBrightness / 100))}, ${Math.floor(255 * (targetBrightness / 100))}, ${Math.floor(255 * (targetBrightness / 100))})` 
          }}
        ></div>
      </div>
      
      <div
        className="brightness-box"
        style={{
          backgroundColor: getBackgroundColor(),
          color: getTextColor(),
          cursor: isChanging && !hasClicked ? 'pointer' : 'default'
        }}
        onClick={handleClick}
      >
        
        {hasClicked ? ( 
          <span>Clicked at {brightness}%</span>
        ) : isChanging ? (
          <span>Click when brightness matches target!</span>
        ) : (
          <span>Get ready...</span>
        )}
      </div>
      
      <div className="brightness-value">
        Current: {brightness}%
      </div>
    </div>
  );
}

export default BrightnessRound;