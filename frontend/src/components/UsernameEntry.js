import React, { useState, useEffect } from 'react';

function UsernameEntry({ onSubmit }) {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate username
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }
    
    if (username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }
    
    if (username.length > 20) {
      setError('Username must be at most 20 characters');
      return;
    }
    
    // Submit username
    onSubmit(username);
  };
  
  return (
    <div className="username-entry">
      <h2>Enter Your Username</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            placeholder="Your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="username-input"
            autoFocus
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" className="primary-button">
          Join Game
        </button>
      </form>
    </div>
  );
}

export default UsernameEntry;