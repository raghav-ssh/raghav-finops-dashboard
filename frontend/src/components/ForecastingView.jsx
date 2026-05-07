import React from 'react';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

export default function ForecastingView({ forecast, forecastsDetails, downloadReport }) {
  if (!forecast || !forecastsDetails || Object.keys(forecastsDetails).length === 0) {
    return (
      <div className="card animate-fade-in" style={{ padding: '32px', textAlign: 'center' }}>
        <h3>Forecasting Data Unavailable</h3>
        <p className="text-secondary" style={{ marginTop: '16px' }}>
          We could not load forecasting data. Please ensure it is generated.
        </p>
      </div>
    );
  }

  const detailedCards = Object.values(forecastsDetails).filter(d => d.category !== 'LABELED_TOTAL');

  return (
    <div className="forecasting-container animate-fade-in">
      <header className="header animate-fade-in">
        <div className="header-info">
          <h1 className="header-title">Cost <span className="text-gradient">Forecasting</span></h1>
          <p className="header-subtitle">ML-driven cost predictions and trend analysis</p>
        </div>
        <div className="header-controls">
          <button 
            onClick={downloadReport}
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
        </div>
      </header>

      {/* Summary Stats */}
      <div className="metrics-grid">
        <div className="card metric-card">
          <div className="metric-header">
            <span className="metric-title">Forecasted Weekly (Total)</span>
            <span className="metric-icon">📅</span>
          </div>
          <div className="metric-value">
            {formatCurrency(forecast.total_forecasted_weekly || 0)}
          </div>
        </div>

        <div className="card metric-card">
          <div className="metric-header">
            <span className="metric-title">Forecasted Monthly (Total)</span>
            <span className="metric-icon">📆</span>
          </div>
          <div className="metric-value text-gradient">
            {formatCurrency(forecast.total_forecasted_monthly || 0)}
          </div>
        </div>

        <div className="card metric-card">
          <div className="metric-header">
            <span className="metric-title">Unlabeled Monthly Forecast</span>
            <span className="metric-icon">🏷️</span>
          </div>
          <div className="metric-value" style={{ color: 'var(--warning)' }}>
            {formatCurrency(forecast.unlabeled_forecasted_monthly || 0)}
            <span className="metric-trend trend-down">{forecast.unlabeled_percent_of_forecast?.toFixed(1) || 0}% Unlabeled</span>
          </div>
        </div>
      </div>

      <div className="card animate-fade-in" style={{ animationDelay: '0.2s', marginTop: '24px' }}>
        <h3 style={{ marginBottom: '8px' }}>Detailed Forecast By Environment</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px' }}>
          Historical cost, projections & confidence score
        </p>

        <table className="data-table">
          <thead>
            <tr>
              <th>Category/Env</th>
              <th>Trend</th>
              <th>Confidence</th>
              <th>Current Daily Avg</th>
              <th>Forecasted Weekly</th>
              <th>Forecasted Monthly</th>
            </tr>
          </thead>
          <tbody>
            {detailedCards.map((f, i) => (
              <tr key={i}>
                <td style={{ fontWeight: '600', textTransform: 'uppercase' }}>{f.category}</td>
                <td>
                  <span className={`badge ${
                    f.trend === 'increasing' ? 'badge-danger' : 
                    f.trend === 'decreasing' ? 'badge-success' : 'badge-info'
                  }`}>
                    {f.trend}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{f.confidence?.toFixed(0) || 0}%</span>
                    <div className="progress-container" style={{ width: '40px', height: '6px', marginTop: 0 }}>
                      <div className="progress-fill" style={{ 
                        width: `${f.confidence || 0}%`,
                        background: f.confidence > 80 ? 'var(--success)' : f.confidence > 50 ? 'var(--warning)' : 'var(--danger)'
                      }}></div>
                    </div>
                  </div>
                </td>
                <td style={{ fontFamily: 'monospace' }}>{formatCurrency(f.current_daily_avg || 0)}</td>
                <td style={{ fontFamily: 'monospace' }}>{formatCurrency(f.forecasted_weekly || 0)}</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{formatCurrency(f.forecasted_monthly || 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
