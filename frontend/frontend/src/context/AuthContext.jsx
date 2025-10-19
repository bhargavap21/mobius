import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenExpiredError, setTokenExpiredError] = useState(false);

  // Load user from localStorage on mount and handle email confirmation
  useEffect(() => {
    const handleEmailConfirmation = () => {
      // Check if there are access tokens in the URL hash (from email confirmation)
      const hash = window.location.hash;
      if (hash && hash.includes('access_token=')) {
        try {
          // Parse the hash parameters
          const params = new URLSearchParams(hash.substring(1)); // Remove the # symbol
          const accessToken = params.get('access_token');
          const tokenType = params.get('token_type');
          const expiresIn = params.get('expires_in');
          const refreshToken = params.get('refresh_token');
          
          if (accessToken) {
            // Store the tokens
            localStorage.setItem('access_token', accessToken);
            if (refreshToken) {
              localStorage.setItem('refresh_token', refreshToken);
            }
            
            // Clear the hash from URL
            window.history.replaceState(null, null, window.location.pathname);
            
            // Fetch user data using the access token
            fetch('http://localhost:8000/auth/me', {
              headers: {
                'Authorization': `Bearer ${accessToken}`
              }
            })
            .then(response => response.json())
            .then(userData => {
              localStorage.setItem('user', JSON.stringify(userData));
              setToken(accessToken);
              setUser(userData);
              
              // Redirect to AI dashboard after successful email confirmation
              // This will trigger a page reload to show the AI building interface
              window.location.href = '/';
            })
            .catch(error => {
              console.error('Error fetching user data:', error);
            });
          }
        } catch (error) {
          console.error('Error parsing email confirmation tokens:', error);
        }
      }
    };

    // Handle email confirmation first
    handleEmailConfirmation();

    // Then load from localStorage if no email confirmation tokens
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser && !window.location.hash.includes('access_token=')) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    
    setLoading(false);
  }, []);

  const signup = async (email, password, fullName) => {
    try {
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      // Return the response data (includes email_confirmed status and message)
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  };

  const signin = async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/auth/signin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Sign in failed');
      }

      // Store token and user
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      setToken(data.access_token);
      setUser(data.user);

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  };

  const signout = (showExpiredMessage = false) => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    if (showExpiredMessage) {
      setTokenExpiredError(true);
    }
  };

  const handleTokenExpired = () => {
    console.error('Token expired - signing out user');
    signout(true);
  };

  const clearExpiredError = () => {
    setTokenExpiredError(false);
  };

  const getAuthHeaders = () => {
    if (!token) return {};
    return {
      'Authorization': `Bearer ${token}`,
    };
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    tokenExpiredError,
    signup,
    signin,
    signout,
    handleTokenExpired,
    clearExpiredError,
    getAuthHeaders,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
