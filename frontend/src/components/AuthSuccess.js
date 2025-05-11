import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Set a localStorage flag indicating Gmail was connected
    localStorage.setItem('gmailConnected', 'true');
    
    // Redirect to dashboard after a short delay
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="form-container">
      <h2>Authentication Successful</h2>
      <div className="message success">
        Your Gmail account has been successfully connected! You will be redirected to the dashboard shortly.
      </div>
      <button 
        className="form-button"
        onClick={() => navigate('/dashboard')}
      >
        Go to Dashboard
      </button>
    </div>
  );
};

export default AuthSuccess;
