/**
 * useDebounce hook — delays value updates to prevent excessive re-renders.
 * Used for chat input to avoid sending requests on every keystroke.
 */

import { useState, useEffect } from 'react';

/**
 * Debounce a value by the specified delay.
 * @param {any} value - Value to debounce
 * @param {number} delay - Debounce delay in milliseconds
 * @returns {any} Debounced value
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
