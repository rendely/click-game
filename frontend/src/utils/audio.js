
// Audio context for sound effects
let audioContext = null;

// Initialize audio context on first user interaction to comply with autoplay policies
export const initAudio = () => {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
};

/**
 * Play a beep sound effect
 * @param {number} frequency - Beep frequency in Hz
 * @param {number} duration - Beep duration in seconds
 * @param {number} volume - Volume between 0 and 1
 */
export const playBeep = (frequency = 440, duration = 0.2, volume = 0.5) => {
  try {
    const context = initAudio();

    // Create oscillator
    const oscillator = context.createOscillator();
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;

    // Create gain node for volume control
    const gainNode = context.createGain();
    gainNode.gain.value = volume;

    // Connect nodes
    oscillator.connect(gainNode);
    gainNode.connect(context.destination);

    // Start and stop oscillator
    oscillator.start();
    oscillator.stop(context.currentTime + duration);
  } catch (error) {
    console.error("Error playing sound:", error);
  }
};

/**
 * Play a success sound
 */
export const playSuccess = () => {
  playBeep(880, 0.1, 0.3);
  setTimeout(() => playBeep(1318.5, 0.2, 0.3), 100);
};

/**
 * Play a failure sound
 */
export const playFailure = () => {
  playBeep(440, 0.1, 0.3);
  setTimeout(() => playBeep(220, 0.3, 0.3), 100);
};

/**
 * Play a neutral notification sound
 */
export const playNotification = () => {
  playBeep(660, 0.1, 0.2);
};

export const playWelcomeMusic = () => {
  try {
    
    const notes = [
      { freq: 523.25, duration: 0.2 }, // C5
      { freq: 587.33, duration: 0.2 }, // D5
      { freq: 659.25, duration: 0.2 }, // E5
      { freq: 783.99, duration: 0.3 }, // G5
      { freq: 659.25, duration: 0.2 }, // E5
      { freq: 987.77, duration: 0.5 }  // B5
    ];

    let timeOffset = 0;

    notes.forEach(note => {
      setTimeout(() => {
        playBeep(note.freq, note.duration, 0.3);
      }, timeOffset * 1000);
      timeOffset += note.duration + 0.05;
    });
  } catch(error) {
    console.error("Error playing welcome music:", error);
  }
}