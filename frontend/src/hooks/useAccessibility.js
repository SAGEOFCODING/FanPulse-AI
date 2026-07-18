/**
 * useAccessibility hook — manages high-contrast and large-text modes.
 * Persists preferences in localStorage and applies data attributes to <html>.
 */

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY_CONTRAST = 'fanpulse-high-contrast';
const STORAGE_KEY_LARGE_TEXT = 'fanpulse-large-text';

/**
 * @returns {object} Accessibility state and toggle functions
 */
export function useAccessibility() {
  const [highContrast, setHighContrast] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY_CONTRAST) === 'true';
    } catch {
      return false;
    }
  });

  const [largeText, setLargeText] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY_LARGE_TEXT) === 'true';
    } catch {
      return false;
    }
  });

  // Apply data attributes to <html> element
  useEffect(() => {
    document.documentElement.setAttribute('data-high-contrast', String(highContrast));
    try {
      localStorage.setItem(STORAGE_KEY_CONTRAST, String(highContrast));
    } catch {
      /* localStorage not available */
    }
  }, [highContrast]);

  useEffect(() => {
    document.documentElement.setAttribute('data-large-text', String(largeText));
    try {
      localStorage.setItem(STORAGE_KEY_LARGE_TEXT, String(largeText));
    } catch {
      /* localStorage not available */
    }
  }, [largeText]);

  const toggleHighContrast = useCallback(() => {
    setHighContrast((prev) => !prev);
  }, []);

  const toggleLargeText = useCallback(() => {
    setLargeText((prev) => !prev);
  }, []);

  return {
    highContrast,
    largeText,
    toggleHighContrast,
    toggleLargeText,
    accessibilityMode: highContrast || largeText,
  };
}
