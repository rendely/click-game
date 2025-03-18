import { useState, useEffect } from 'react';

/**
 * Custom hook for persistent state with localStorage
 * @param {string} key - localStorage key
 * @param {any} initialValue - Initial value if key doesn't exist in localStorage
 * @returns {[any, Function]} - Current value and setter function
 */
function useLocalStorage(key, initialValue) {
  // Get initial value from localStorage or use provided initialValue
  const [value, setValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      return initialValue;
    }
  });

  // Update localStorage when value changes
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error("Error writing to localStorage:", error);
    }
  }, [key, value]);

  return [value, setValue];
}

export default useLocalStorage;