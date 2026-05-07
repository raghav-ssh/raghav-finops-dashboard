import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const BudgetsView = ({ onBudgetUpdate }) => {
  const [budgets, setBudgets] = useState({});
  const [editedBudgets, setEditedBudgets] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [budgetPeriod, setBudgetPeriod] = useState('monthly'); // 'daily', 'weekly', 'monthly'

  // Fetch budgets on mount
  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/budgets`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch budgets`);
      }
      
      const data = await response.json();
      
      // Normalize budget data to new format
      const normalized = {};
      Object.entries(data).forEach(([env, budget]) => {
        if (typeof budget === 'number') {
          // Convert old format to new format
          normalized[env] = {
            daily: Math.round(budget / 30),
            weekly: Math.round(budget / 30 * 7),
            monthly: budget
          };
        } else {
          normalized[env] = budget;
        }
      });
      
      setBudgets(normalized);
      setEditedBudgets(normalized);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBudgetChange = (env, period, value) => {
    setEditedBudgets(prev => ({
      ...prev,
      [env]: {
        ...prev[env],
        [period]: parseFloat(value) || 0
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/budgets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ budgets: editedBudgets })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to update budgets`);
      }
      
      const data = await response.json();
      setBudgets(data.budgets);
      setEditedBudgets(data.budgets);
      setSuccess(true);
      setIsEditing(false);
      
      // Trigger dashboard refresh
      if (onBudgetUpdate) {
        console.log('Triggering dashboard refresh after budget update...');
        onBudgetUpdate();
      }
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Save error:', err);
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedBudgets(budgets);
    setIsEditing(false);
    setError(null);
  };

  const envLabels = {
    'prod': { name: 'Production', icon: '🏭', color: '#ef4444' },
    'uat': { name: 'UAT', icon: '🧪', color: '#f59e0b' },
    'dev': { name: 'Development', icon: '💻', color: '#10b981' },
    'UNLABELED': { name: 'Unlabeled', icon: '🏷️', color: '#6b7280' }
  };

  const periodLabels = {
    'daily': { name: 'Daily', icon: '📅' },
    'weekly': { name: 'Weekly', icon: '📊' },
    'monthly': { name: 'Monthly', icon: '📆' }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="text-gradient loading-text">
          Loading Budgets...
        </div>
      </div>
    );
  }

  return (
    <div className="budgets-view">
      <header className="header animate-fade-in">
        <div className="header-info">
          <h1 className="header-title">
            <span className="text-gradient">Budget Management</span>
          </h1>
          <p className="header-subtitle">Configure daily, weekly, and monthly budgets for each environment</p>
        </div>
        <div className="header-controls">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              style={{
                background: 'var(--accent-gradient)',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              ✏️ Edit Budgets
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                onClick={handleSave}
                disabled={saving}
                style={{
                  background: 'var(--success)',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  opacity: saving ? 0.6 : 1
                }}
              >
                {saving ? '💾 Saving...' : '💾 Save Changes'}
              </button>
              <button 
                onClick={handleCancel}
                disabled={saving}
                style={{
                  background: 'var(--bg-elevated)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.1)',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  opacity: saving ? 0.6 : 1
                }}
              >
                ❌ Cancel
              </button>
            </div>
          )}
        </div>
      </header>

      {error && (
        <div className="card animate-fade-in" style={{ 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid rgba(239, 68, 68, 0.3)',
          marginBottom: '20px'
        }}>
          <div style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {success && (
        <div className="card animate-fade-in" style={{ 
          background: 'rgba(16, 185, 129, 0.1)', 
          border: '1px solid rgba(16, 185, 129, 0.3)',
          marginBottom: '20px'
        }}>
          <div style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>✅</span>
            <span>Budgets updated successfully! Reports will use the new budgets.</span>
          </div>
        </div>
      )}

      {/* Budget Period Selector */}
      {!isEditing && (
        <div className="card animate-fade-in" style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ marginBottom: '8px' }}>View Budget Period</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>
                Select which budget period to display
              </p>
            </div>
            <div className="period-selector">
              {Object.entries(periodLabels).map(([period, info]) => (
                <button 
                  key={period}
                  onClick={() => setBudgetPeriod(period)}
                  className={`period-button ${budgetPeriod === period ? 'active' : ''}`}
                >
                  {info.icon} {info.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="budgets-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '20px',
        marginBottom: '20px'
      }}>
        {Object.entries(editedBudgets).map(([env, envBudget]) => {
          const envInfo = envLabels[env] || { name: env, icon: '📊', color: '#6366f1' };
          
          return (
            <div key={env} className="card animate-fade-in" style={{
              borderLeft: `4px solid ${envInfo.color}`
            }}>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '12px',
                  marginBottom: '8px'
                }}>
                  <span style={{ fontSize: '32px' }}>{envInfo.icon}</span>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '18px' }}>{envInfo.name}</h3>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '12px', 
                      color: 'var(--text-secondary)',
                      textTransform: 'uppercase'
                    }}>
                      {env}
                    </p>
                  </div>
                </div>
              </div>

              {isEditing ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Daily Budget */}
                  <div>
                    <label style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '8px',
                      fontSize: '13px',
                      color: 'var(--text-secondary)'
                    }}>
                      📅 Daily Budget (₹)
                    </label>
                    <input
                      type="number"
                      value={envBudget.daily || 0}
                      onChange={(e) => handleBudgetChange(env, 'daily', e.target.value)}
                      style={{
                        width: '100%',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        padding: '10px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontFamily: 'monospace'
                      }}
                      step="100"
                      min="0"
                    />
                    <div style={{ 
                      marginTop: '4px',
                      fontSize: '12px',
                      color: 'var(--text-secondary)'
                    }}>
                      {formatCurrency(envBudget.daily || 0)}
                    </div>
                  </div>

                  {/* Weekly Budget */}
                  <div>
                    <label style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '8px',
                      fontSize: '13px',
                      color: 'var(--text-secondary)'
                    }}>
                      📊 Weekly Budget (₹)
                    </label>
                    <input
                      type="number"
                      value={envBudget.weekly || 0}
                      onChange={(e) => handleBudgetChange(env, 'weekly', e.target.value)}
                      style={{
                        width: '100%',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        padding: '10px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontFamily: 'monospace'
                      }}
                      step="500"
                      min="0"
                    />
                    <div style={{ 
                      marginTop: '4px',
                      fontSize: '12px',
                      color: 'var(--text-secondary)'
                    }}>
                      {formatCurrency(envBudget.weekly || 0)}
                    </div>
                  </div>

                  {/* Monthly Budget */}
                  <div>
                    <label style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '8px',
                      fontSize: '13px',
                      color: 'var(--text-secondary)'
                    }}>
                      📆 Monthly Budget (₹)
                    </label>
                    <input
                      type="number"
                      value={envBudget.monthly || 0}
                      onChange={(e) => handleBudgetChange(env, 'monthly', e.target.value)}
                      style={{
                        width: '100%',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        padding: '10px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontFamily: 'monospace'
                      }}
                      step="1000"
                      min="0"
                    />
                    <div style={{ 
                      marginTop: '4px',
                      fontSize: '12px',
                      color: 'var(--text-secondary)'
                    }}>
                      {formatCurrency(envBudget.monthly || 0)}
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ 
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    marginBottom: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    {periodLabels[budgetPeriod].icon} {periodLabels[budgetPeriod].name} Budget
                  </div>
                  <div style={{ 
                    fontSize: '28px',
                    fontWeight: '600',
                    fontFamily: 'monospace',
                    color: envInfo.color
                  }}>
                    {formatCurrency(envBudget[budgetPeriod] || 0)}
                  </div>
                  
                  {/* Show all budgets in small text */}
                  <div style={{ 
                    marginTop: '12px',
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(255,255,255,0.1)',
                    fontSize: '12px',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}>
                    <div>📅 Daily: {formatCurrency(envBudget.daily || 0)}</div>
                    <div>📊 Weekly: {formatCurrency(envBudget.weekly || 0)}</div>
                    <div>📆 Monthly: {formatCurrency(envBudget.monthly || 0)}</div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="card animate-fade-in">
        <h3 style={{ marginBottom: '16px' }}>Budget Overview</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Environment</th>
              <th>Daily Budget</th>
              <th>Weekly Budget</th>
              <th>Monthly Budget</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(editedBudgets).map(([env, envBudget]) => {
              const envInfo = envLabels[env] || { name: env, icon: '📊', color: '#6366f1' };
              const hasAnyBudget = (envBudget.daily || 0) > 0 || (envBudget.weekly || 0) > 0 || (envBudget.monthly || 0) > 0;
              
              return (
                <tr key={env}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{envInfo.icon}</span>
                      <span style={{ fontWeight: '600' }}>{envInfo.name}</span>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '14px' }}>
                    {formatCurrency(envBudget.daily || 0)}
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '14px' }}>
                    {formatCurrency(envBudget.weekly || 0)}
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '14px' }}>
                    {formatCurrency(envBudget.monthly || 0)}
                  </td>
                  <td>
                    {hasAnyBudget ? (
                      <span className="badge badge-success">Active</span>
                    ) : (
                      <span className="badge badge-warning">Not Set</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="card animate-fade-in" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '12px' }}>💡 Budget Tips</h3>
        <ul style={{ 
          color: 'var(--text-secondary)', 
          fontSize: '14px',
          lineHeight: '1.8',
          paddingLeft: '20px'
        }}>
          <li><strong>Daily Budgets:</strong> Used for daily report tracking and alerts</li>
          <li><strong>Weekly Budgets:</strong> Used for weekly report tracking (typically 7x daily budget)</li>
          <li><strong>Monthly Budgets:</strong> Used for monthly projections and forecasting</li>
          <li>Set realistic budgets based on historical spending patterns</li>
          <li>Production environments typically require higher budgets than dev/UAT</li>
          <li>Budget alerts will trigger when spending exceeds 75% and 90% thresholds</li>
          <li>PDF reports will automatically use the appropriate budget based on report type</li>
        </ul>
      </div>
    </div>
  );
};

export default BudgetsView;
