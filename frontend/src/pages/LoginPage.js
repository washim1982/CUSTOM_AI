// frontend/src/pages/LoginPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { registerUser, loginUser } from '../services/api';

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);
  
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    setError('');
    setStatus('');
    setIsLoading(true);

    if (isRegistering) {
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        setIsLoading(false);
        return;
      }
      registerUser({ email, password })
        .then(response => {
          setStatus('Registration successful! Please log in.');
          setIsRegistering(false);
        })
        .catch(err => {
          setError(err.response?.data?.detail || 'Registration failed.');
        })
        .finally(() => {
          setIsLoading(false);
        });
      
    } else {
      loginUser(email, password)
        .then(response => {
          login(email, response.data.access_token);
          navigate('/models');
        })
        .catch(err => {
          setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setError('');
    setStatus('');
  };

  return (
    <div className="page-content" style={{ maxWidth: '500px' }}>
      <h2>{isRegistering ? 'Register' : 'Login'}</h2>
      <form onSubmit={handleSubmit} className="form-layout">
        
        {isRegistering && (
          <>
            <input
              type="text"
              placeholder="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
              className="form-input"
            />
            <input
              type="text"
              placeholder="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
              className="form-input"
            />
          </>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="form-input"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="form-input"
        />
        
        {isRegistering && (
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="form-input"
          />
        )}
        
        {error && <p className="status-message status-error">{error}</p>}
        {status && <p className="status-message status-success">{status}</p>}

        <button type="submit" disabled={isLoading} className="btn btn-primary">
          {isLoading ? 'Processing...' : (isRegistering ? 'Register' : 'Login')}
        </button>
      </form>

      <div onClick={toggleMode} style={{ color: 'var(--link-color)', cursor: 'pointer', textAlign: 'center' }}>
        {isRegistering ? 'Already have an account? Login!' : "Don't have an account? Create one for free!"}
      </div>
    </div>
  );
}

export default LoginPage;