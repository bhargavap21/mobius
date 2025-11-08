import { API_URL } from '../config'
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

const EmailConfirmation = () => {
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('Verifying your email...');
  const { signin } = useAuth();

  useEffect(() => {
    handleEmailConfirmation();
  }, []);

  const handleEmailConfirmation = async () => {
    try {
      // Get the hash fragment from URL
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      const accessToken = hashParams.get('access_token');
      const refreshToken = hashParams.get('refresh_token');
      const error = hashParams.get('error');
      const errorDescription = hashParams.get('error_description');

      if (error) {
        setStatus('error');
        setMessage(errorDescription || 'Email confirmation failed. The link may have expired.');
        return;
      }

      if (accessToken && refreshToken) {
        // Store tokens
        localStorage.setItem('access_token', accessToken);

        // Fetch user data
        const response = await fetch(`${API_URL}/auth/me', {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          localStorage.setItem('user', JSON.stringify(userData));

          setStatus('success');
          setMessage('Email confirmed successfully! Redirecting...');

          // Redirect to home after 2 seconds
          setTimeout(() => {
            window.location.href = '/';
          }, 2000);
        } else {
          throw new Error('Failed to fetch user data');
        }
      } else {
        setStatus('error');
        setMessage('Invalid confirmation link');
      }
    } catch (err) {
      console.error('Email confirmation error:', err);
      setStatus('error');
      setMessage('An error occurred during confirmation. Please try signing in.');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center">
      <div className="bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4 text-center">
        {status === 'verifying' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <h2 className="text-xl font-bold text-white mb-2">Verifying Email</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <h2 className="text-xl font-bold text-white mb-2">Email Confirmed!</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <h2 className="text-xl font-bold text-white mb-2">Confirmation Failed</h2>
            <p className="text-gray-400 mb-4">{message}</p>
            <a
              href="/"
              className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              Go to Home
            </a>
          </>
        )}
      </div>
    </div>
  );
};

export default EmailConfirmation;
