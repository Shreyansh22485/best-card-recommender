import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = ({ onLogout }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gmailConnected, setGmailConnected] = useState(false);
  const [statement, setStatement] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [authUrl, setAuthUrl] = useState('');

  // For spend form
  const [spends, setSpends] = useState([
    { category: 'Dining', amount: 250 },
    { category: 'Grocery', amount: 350 },
  ]);
  const [formLoading, setFormLoading] = useState(false);

  // Available spending categories
  const categories = [
    'Dining', 'Grocery', 'Travel', 'Entertainment', 
    'Shopping', 'Gas', 'Utilities', 'Healthcare', 'Other'
  ];
  // Setup axios interceptor for auth header
  useEffect(() => {
    axios.interceptors.request.use(
      config => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );

    // Check if Gmail was just connected (from AuthSuccess)
    const gmailConnectedFlag = localStorage.getItem('gmailConnected');
    if (gmailConnectedFlag === 'true') {
      setGmailConnected(true);
      // Clear the flag after using it
      localStorage.removeItem('gmailConnected');
    }
  }, []);
  // Load user profile
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get('/api/auth/me');
        setUser(response.data);
        // After loading user profile, check if Gmail is connected
        checkGmailConnection();
      } catch (err) {
        console.error('Error fetching user profile:', err);
        if (err.response?.status === 401) {
          onLogout();
        }
        setError('Failed to load user profile');
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [onLogout]);

  // Check if Gmail is connected
  const checkGmailConnection = async () => {
    try {
      // Try to parse a statement - if successful, Gmail is connected
      // If not connected, it will return 400 with "Gmail not connected"
      const response = await axios.get('/api/gmail/parse-statement');
      setGmailConnected(true);
      setStatement(response.data);
      
      // Update spends based on the statement data if available
      if (response.data.spending_analysis) {
        const newSpends = Object.entries(response.data.spending_analysis).map(
          ([category, amount]) => ({ category, amount })
        );
        setSpends(newSpends);
      }
    } catch (err) {
      // If error is "Gmail not connected", we know Gmail is not connected
      // Otherwise, it might be some other error
      if (err.response?.status === 400 && err.response?.data?.detail === 'Gmail not connected') {
        setGmailConnected(false);
      } else {
        console.error('Error checking Gmail connection:', err);
      }
    }
  };

  // Handle Gmail connection
  const handleConnectGmail = async () => {
    try {
      const response = await axios.get('/api/gmail/auth');
      setAuthUrl(response.data.auth_url);
      window.location.href = response.data.auth_url;
    } catch (err) {
      setError('Failed to initiate Gmail authorization');
      console.error(err);
    }
  };
  // Handle parsing statement
  const handleParseStatement = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/api/gmail/parse-statement');
      
      // If no statements found, show friendly message
      if (response.data.message === 'No statement emails found') {
        setError('No statement emails found in your Gmail account. Make sure you have credit card statements in your inbox.');
      } else {
        setStatement(response.data);
        setGmailConnected(true);
        
        // Update spends based on the statement data
        if (response.data.spending_analysis) {
          const newSpends = Object.entries(response.data.spending_analysis).map(
            ([category, amount]) => ({ category, amount })
          );
          setSpends(newSpends);
        }
      }
    } catch (err) {
      if (err.response?.status === 400 && err.response?.data?.detail === 'Gmail not connected') {
        handleConnectGmail();
      } else {
        setError('Failed to parse statement: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle adding a new spend
  const handleAddSpend = () => {
    setSpends([...spends, { category: 'Other', amount: 0 }]);
  };

  // Handle removing a spend
  const handleRemoveSpend = (index) => {
    setSpends(spends.filter((_, i) => i !== index));
  };

  // Handle spend change
  const handleSpendChange = (index, field, value) => {
    const newSpends = [...spends];
    newSpends[index][field] = field === 'amount' ? parseFloat(value) || 0 : value;
    setSpends(newSpends);
  };

  // Handle recommendation form submit
  const handleGetRecommendation = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/api/recommend', { spends });
      setRecommendation(response.data);
    } catch (err) {
      setError('Failed to get recommendation: ' + (err.response?.data?.detail || err.message));
    } finally {
      setFormLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="header">
        <h1 className="header-title">Best Card Recommender</h1>
        <button className="form-button button-secondary" onClick={onLogout}>Logout</button>
      </div>
      
      {error && <div className="message error">{error}</div>}
      
      <div className="flex-container">
        <div className="flex-item">
          <div className="card">            <h2 className="card-title">Welcome, {user?.email}</h2>
            <div className="connect-gmail">
              <p>
                {gmailConnected 
                  ? "Your Gmail account is connected! You can parse your statements." 
                  : "Connect your Gmail account to import e-statements automatically."}
              </p>
              {!gmailConnected ? (
                <button 
                  className="form-button"
                  onClick={handleConnectGmail}
                >
                  Connect Gmail
                </button>
              ) : (
                <button 
                  className="form-button"
                  onClick={handleParseStatement}
                >
                  Parse Recent Statement
                </button>
              )}            </div>
            
            {gmailConnected && !statement && (
              <div className="message success">
                <p>Your Gmail account is connected! Click "Parse Recent Statement" to analyze your spending.</p>
              </div>
            )}
            
            {statement && (
              <div className="statement-info">
                <h3>Statement Information</h3>
                <p>Subject: {statement.email_subject}</p>
                <p>Transactions: {statement.transaction_count}</p>
                <h4>Spending Analysis</h4>
                <ul>
                  {Object.entries(statement.spending_analysis).map(([category, amount]) => (
                    <li key={category}>{category}: ${amount.toFixed(2)}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex-item">
          <div className="card">
            <h2 className="card-title">Get Card Recommendation</h2>
            <form className="spend-form" onSubmit={handleGetRecommendation}>
              <h3>Your Spending</h3>
              {spends.map((spend, index) => (
                <div key={index} className="spend-item">
                  <div className="form-group" style={{ flex: 2 }}>
                    <select
                      className="form-input"
                      value={spend.category}
                      onChange={(e) => handleSpendChange(index, 'category', e.target.value)}
                    >
                      {categories.map((cat) => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <input
                      type="number"
                      className="form-input"
                      value={spend.amount}
                      onChange={(e) => handleSpendChange(index, 'amount', e.target.value)}
                      placeholder="Amount"
                      step="0.01"
                      min="0"
                    />
                  </div>
                  <button
                    type="button"
                    className="form-button button-remove"
                    onClick={() => handleRemoveSpend(index)}
                    disabled={spends.length <= 1}
                  >
                    -
                  </button>
                </div>
              ))}
              
              <div className="form-group">
                <button
                  type="button"
                  className="form-button button-add"
                  onClick={handleAddSpend}
                >
                  Add Spend Category
                </button>
              </div>
              
              <div className="form-group">
                <button
                  type="submit"
                  className="form-button"
                  disabled={formLoading}
                >
                  {formLoading ? 'Loading...' : 'Get Recommendation'}
                </button>
              </div>
            </form>
            
            {recommendation && (
              <div className="recommendation-result">
                <h3>Your Best Card</h3>
                <div className="card-option best-card">
                  <h4>{recommendation.recommended_card}</h4>
                  <p>Annual Reward Value: ${recommendation.score.toFixed(2)}</p>
                </div>
                
                <h3>Comparison</h3>
                <div className="card-comparison">
                  {Object.entries(recommendation.comparison).map(([card, score]) => (
                    <div 
                      key={card} 
                      className={`card-option ${card === recommendation.recommended_card ? 'best-card' : ''}`}
                    >
                      <h4>{card}</h4>
                      <p>${score.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
