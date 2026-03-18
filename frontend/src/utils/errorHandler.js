/**
 * Parse API error responses into user-friendly messages
 * Handles FastAPI validation errors and other error formats
 */
export const parseApiError = (error) => {
  // Default error message
  let errorMessage = 'An error occurred';

  try {
    if (error.response?.data) {
      const data = error.response.data;

      // Handle FastAPI validation errors (array of error objects)
      if (data.detail && Array.isArray(data.detail)) {
        errorMessage = data.detail
          .map((err) => {
            // Extract field name from location array
            const field = err.loc?.[err.loc.length - 1] || 'field';
            // Get error message
            const msg = err.msg || 'Invalid value';
            return `${field}: ${msg}`;
          })
          .join(', ');
      }
      // Handle string detail
      else if (data.detail && typeof data.detail === 'string') {
        errorMessage = data.detail;
      }
      // Handle message field
      else if (data.message && typeof data.message === 'string') {
        errorMessage = data.message;
      }
      // Handle error field
      else if (data.error && typeof data.error === 'string') {
        errorMessage = data.error;
      }
      // If data itself is a string
      else if (typeof data === 'string') {
        errorMessage = data;
      }
    }
    // Handle error message
    else if (error.message && typeof error.message === 'string') {
      errorMessage = error.message;
    }
  } catch (parseError) {
    console.error('Error parsing API error:', parseError);
    errorMessage = 'An unexpected error occurred';
  }

  // Ensure we always return a string
  return String(errorMessage);
};
