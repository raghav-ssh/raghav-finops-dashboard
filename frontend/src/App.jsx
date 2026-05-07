import { useState, useEffect } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import ForecastingView from './components/ForecastingView';
import BudgetsView from './components/BudgetsView';
import ReportsView from './components/ReportsView';

// Constants
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const PERIODS = [
  { id: 'daily', label: 'Daily' },
  { id: 'weekly', label: 'Weekly' },
  { id: 'monthly', label: 'Monthly' }
];

// Utility Functions
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

const getStatusBadge = (status) => {
  const statusMap = {
    'Good': <span className="badge badge-success">Good</span>,
    'Warning': <span className="badge badge-warning">Warning</span>,
    'Critical': <span className="badge badge-danger">Critical</span>,
    'On Track': <span className="badge badge-success">On Track</span>,
    'Over Budget': <span className="badge badge-danger">Over Budget</span>
  };
  return statusMap[status] || <span className="badge badge-info">{status}</span>;
};

// Main Component
export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('daily');
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showDateFilter, setShowDateFilter] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Function to refresh dashboard data
  const refreshDashboard = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Fetch dashboard data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let url = `${API_BASE_URL}/api/dashboard?period=${period}&refresh=true`;
        if (startDate && endDate) {
          url += `&start_date=${startDate}&end_date=${endDate}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch data`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [period, startDate, endDate, refreshTrigger]);

  // Loading State
  if (loading || !data) {
    return (
      <div className="loading-container">
        <div className="text-gradient loading-text">
          Loading FinOps {period.charAt(0).toUpperCase() + period.slice(1)} Data...
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="error-container">
        <div className="text-gradient error-title">
          Error Loading Data
        </div>
        <div className="error-message">
          {error}
        </div>
        <div className="error-hint">
          Ensure the backend API is running on {API_BASE_URL}
        </div>
      </div>
    );
  }

  // Extract data
  const { summary, costTrends, environments, criticalAlerts } = data;
  const maxCost = costTrends.length > 0 ? Math.max(...costTrends.map(t => t.cost)) : 1;
  
  // Period-specific labels and formatting
  const periodConfig = {
    daily: {
      title: 'Daily Cost',
      chartTitle: 'Daily Cost Trends (Last 7 Days)',
      dateRange: `${new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toLocaleDateString()} to ${new Date().toLocaleDateString()}`,
      budgetLabel: 'Daily Budget',
      costLabel: 'Daily Cost'
    },
    weekly: {
      title: 'Weekly Cost',
      chartTitle: 'Weekly Cost Trends (Last 4 Weeks)',
      dateRange: `${new Date(Date.now() - 28 * 24 * 60 * 60 * 1000).toLocaleDateString()} to ${new Date().toLocaleDateString()}`,
      budgetLabel: 'Weekly Budget',
      costLabel: 'Weekly Cost'
    },
    monthly: {
      title: 'Monthly Cost',
      chartTitle: 'Monthly Cost Trends',
      dateRange: `01 ${new Date().toLocaleString('default', { month: 'long', year: 'numeric' })} to ${new Date().toLocaleDateString()}`,
      budgetLabel: 'Monthly Budget',
      costLabel: 'Month-to-Date Cost'
    }
  };
  
  const currentPeriodConfig = periodConfig[period] || periodConfig.daily;
  
  // Download report function
  const downloadReport = async () => {
    try {
      let url = `${API_BASE_URL}/api/download-report?period=${period}`;
      if (startDate && endDate) {
        url += `&start_date=${startDate}&end_date=${endDate}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Download error:', errorText);
        throw new Error(`Download failed: ${response.status}`);
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `finops_report_${period}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Download error:', err);
      alert(`Failed to download report: ${err.message}`);
    }
  };
  
  const applyDateFilter = () => {
    if (startDate && endDate) {
      setShowDateFilter(false);
    }
  };
  
  const clearDateFilter = () => {
    setStartDate('');
    setEndDate('');
    setShowDateFilter(false);
  };

  return (
    <div className="app-layout">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <div className="main-content">
        <div className="dashboard-container">
          {currentView === 'dashboard' ? (
            <>
      <header className="header animate-fade-in">
        <div className="header-info">
          <h1 className="header-title">Enhanced <span className="text-gradient">FinOps Dashboard</span></h1>
          <p className="header-subtitle">Environment-wise Cost Intelligence & Anomaly Detection</p>
        </div>
        <div className="header-controls">
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <button 
              onClick={() => downloadReport('pdf')}
              style={{
                background: 'var(--accent-gradient)',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500'
              }}
            >
              📄 Download PDF Report
            </button>
            <button 
              onClick={refreshDashboard}
              style={{
                background: 'var(--bg-elevated)',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.1)',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500'
              }}
            >
              🔄 Refresh
            </button>
            <button 
              onClick={() => setShowDateFilter(!showDateFilter)}
              style={{
                background: showDateFilter ? 'var(--accent-gradient)' : 'var(--bg-elevated)',
                color: 'white',
                border: showDateFilter ? 'none' : '1px solid rgba(255,255,255,0.1)',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500'
              }}
            >
              📅 Custom Date
            </button>
          </div>
          
          {showDateFilter && (
            <div style={{
              background: 'var(--bg-elevated)',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '8px',
              display: 'flex',
              gap: '8px',
              alignItems: 'center'
            }}>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{
                  background: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  fontSize: '13px'
                }}
              />
              <span style={{ color: 'var(--text-secondary)' }}>to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{
                  background: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  fontSize: '13px'
                }}
              />
              <button
                onClick={applyDateFilter}
                style={{
                  background: 'var(--success)',
                  color: 'white',
                  border: 'none',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '500'
                }}
              >
                Apply
              </button>
              <button
                onClick={clearDateFilter}
                style={{
                  background: 'var(--danger)',
                  color: 'white',
                  border: 'none',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '500'
                }}
              >
                Clear
              </button>
            </div>
          )}
          
          <div className="period-selector">
            {PERIODS.map(p => (
              <button 
                key={p.id} 
                onClick={() => setPeriod(p.id)}
                className={`period-button ${period === p.id ? 'active' : ''}`}
              >
                {p.label}
              </button>
            ))}
          </div>
          <div className="report-date">
            Report Date: {currentPeriodConfig.dateRange}
            {startDate && endDate && (
              <span style={{ marginLeft: '8px', color: 'var(--accent-primary)' }}>
                (Custom: {startDate} to {endDate})
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Top Metrics Cards */}
      <div className="metrics-grid">
        <div className="card metric-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="metric-header">
            <span className="metric-title" style={{ textTransform: 'uppercase' }}>
              {currentPeriodConfig.costLabel}
            </span>
            <span className="metric-icon" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-primary)' }}>₹</span>
          </div>
          <div className="metric-value">
            {formatCurrency(summary.dailyTotalCost)}
            <span className={`metric-trend ${summary.costTrendPercent >= 0 ? 'trend-up' : 'trend-down'}`}>
              {summary.costTrendPercent >= 0 ? '↑' : '↓'} {Math.abs(summary.costTrendPercent)}%
            </span>
          </div>
        </div>

        <div className="card metric-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <div className="metric-header">
            <span className="metric-title">Active Environments</span>
            <span className="metric-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>⚡</span>
          </div>
          <div className="metric-value">
            {summary.envCount}
            <span className="metric-trend" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>Tracked</span>
          </div>
        </div>

        <div className="card metric-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="metric-header">
            <span className="metric-title">Unlabeled Spend</span>
            <span className="metric-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>🏷️</span>
          </div>
          <div className="metric-value">
            {formatCurrency(summary.unlabeledSpend.amount)}
            <span className="metric-trend trend-down">↓ {summary.unlabeledSpend.percent}%</span>
          </div>
        </div>

        <div className="card metric-card animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <div className="metric-header">
            <span className="metric-title">Anomalies Detected</span>
            <span className="metric-icon" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)' }}>🚨</span>
          </div>
          <div className="metric-value">
            {summary.anomalies.total}
            <span className="metric-trend trend-up">{summary.anomalies.critical} Critical</span>
          </div>
        </div>
      </div>

      <div className="two-col-grid">
        {/* Main Chart */}
        <div className="card animate-fade-in" style={{ animationDelay: '0.5s' }}>
          <h3 style={{ marginBottom: '8px' }}>{currentPeriodConfig.chartTitle}</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Overall environment cost aggregation</p>
          
          <div className="chart-container">
            {costTrends.map((point, i) => {
              const heightPercentage = (point.cost / maxCost) * 100;
              return (
                <div key={i} className="bar-wrapper">
                  <div className="bar-value">{formatCurrency(point.cost)}</div>
                  <div 
                    className="bar" 
                    style={{ height: `${heightPercentage}%`, animationDelay: `${0.1 * i}s` }}
                  ></div>
                  <span className="bar-label">{point.date}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="card animate-fade-in" style={{ animationDelay: '0.6s' }}>
          <h3 style={{ marginBottom: '8px' }}>
            <span className="text-gradient">Critical Alerts</span>
          </h3>
          <p className="card-subtitle">Requires immediate attention</p>
          
          <div className="alerts-container">
            {criticalAlerts.length > 0 ? (
              criticalAlerts.map((alert, i) => (
                <div key={i} className="alert-item">
                  <div className="alert-header">
                    <span className="alert-env">{alert.env}</span>
                  </div>
                  <p className="alert-message">{alert.message}</p>
                </div>
              ))
            ) : (
              <div className="no-alerts">
                <span>✓ No critical alerts</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Table view */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.7s' }}>
        <h3 style={{ marginBottom: '8px' }}>Environment Breakdown</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px' }}>Cost and compliance breakdown by active environment</p>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Environment</th>
              <th>Status</th>
              <th>{currentPeriodConfig.costLabel}</th>
              <th>{currentPeriodConfig.budgetLabel}</th>
              <th>Budget Used</th>
              <th>Apps</th>
              <th>Anomalies</th>
              <th>Unlabeled %</th>
            </tr>
          </thead>
          <tbody>
            {environments.map((env, i) => (
              <tr key={i}>
                <td style={{ fontWeight: '600', textTransform: 'uppercase' }}>{env.name}</td>
                <td>{getStatusBadge(env.budgetStatus)}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '15px' }}>{formatCurrency(env.cost)}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '14px', color: 'var(--text-secondary)' }}>
                  {env.budgetAmount > 0 ? formatCurrency(env.budgetAmount) : 'N/A'}
                </td>
                <td>
                  {env.budgetAmount > 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ minWidth: '40px', fontSize: '14px' }}>{env.budgetPercent}%</span>
                      <div className="progress-container" style={{ width: '80px', height: '6px' }}>
                        <div 
                          className="progress-fill" 
                          style={{ 
                            width: `${Math.min(env.budgetPercent, 100)}%`,
                            background: env.budgetPercent > 90 ? 'var(--danger)' : env.budgetPercent > 75 ? 'var(--warning)' : 'var(--success)'
                          }}
                        ></div>
                      </div>
                    </div>
                  ) : (
                    <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>N/A</span>
                  )}
                </td>
                <td>{env.apps}</td>
                <td>
                  <span style={{ color: env.anomalies > 3 ? 'var(--danger)' : 'var(--text-primary)' }}>
                    {env.anomalies}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ minWidth: '40px' }}>{env.unlabeledPercent}%</span>
                    <div className="progress-container" style={{ width: '60px', height: '6px' }}>
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${env.unlabeledPercent}%`,
                          background: env.unlabeledPercent > 20 ? 'var(--danger)' : env.unlabeledPercent > 10 ? 'var(--warning)' : 'var(--success)'
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      </>
          ) : currentView === 'reports' ? (
            <ReportsView />
          ) : currentView === 'forecasting' ? (
            <ForecastingView forecast={data?.forecast} forecastsDetails={data?.forecastsDetails} downloadReport={() => downloadReport('pdf')} />
          ) : currentView === 'budgets' ? (
            <BudgetsView onBudgetUpdate={refreshDashboard} />
          ) : (
            <div className="card animate-fade-in">
              <h2>View Component Not Found</h2>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
