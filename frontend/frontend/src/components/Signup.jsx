import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Signup = ({ onClose, onSwitchToLogin, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup, signin } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    const result = await signup(email, password, fullName);

    if (result.success) {
      if (result.data.email_confirmed) {
        setSuccess('Account created successfully! Signing you in...');
        // Auto-login after successful signup
        const loginResult = await signin(email, password);
        if (loginResult.success) {
          setTimeout(() => {
            onClose();
            if (onSuccess) {
              onSuccess();
            }
          }, 1000);
        } else {
          setTimeout(() => {
            onSwitchToLogin();
          }, 2000);
        }
      } else {
        setSuccess(result.data.message || 'Account created! Please check your email to confirm your account.');
      }
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Sign Up</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900 bg-opacity-50 rounded text-red-200 text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-900 bg-opacity-50 rounded text-green-200 text-sm">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="John Doe"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="••••••••"
              required
              minLength={6}
            />
            <p className="text-gray-400 text-xs mt-1">Minimum 6 characters</p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-800 to-purple-700 hover:from-purple-900 hover:to-purple-800 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded transition-all"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-gray-400 text-sm">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-accent hover:text-accent-light"
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
