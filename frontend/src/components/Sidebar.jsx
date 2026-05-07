import React from 'react';

const Sidebar = ({ currentView, setCurrentView }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>FinOps Menu</h2>
      </div>
      <nav className="sidebar-nav">
        <button 
          className={`sidebar-link ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentView('dashboard')}
        >
          <span>📊</span> Dashboard
        </button>
        <button 
          className={`sidebar-link ${currentView === 'reports' ? 'active' : ''}`}
          onClick={() => setCurrentView('reports')}
        >
          <span>📄</span> Reports
        </button>
        <button 
          className={`sidebar-link ${currentView === 'forecasting' ? 'active' : ''}`}
          onClick={() => setCurrentView('forecasting')}
        >
          <span>📈</span> Forecasting
        </button>
        <button 
          className="sidebar-link"
          onClick={() => alert('Anomaly Reports opening...')}
        >
          <span>🚨</span> Anomalies
        </button>
        <button 
          className={`sidebar-link ${currentView === 'budgets' ? 'active' : ''}`}
          onClick={() => setCurrentView('budgets')}
        >
          <span>💰</span> Budgets
        </button>
      </nav>
      <div className="sidebar-footer">
        <div className="text-secondary" style={{ fontSize: '12px' }}>
          Enhanced FinOps Tracker
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
