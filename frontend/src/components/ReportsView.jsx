import { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const ReportsView = () => {
  const [reportType, setReportType] = useState('daily');
  const [availableReports, setAvailableReports] = useState({ daily: [], weekly: [] });
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Fetch available reports
  useEffect(() => {
    fetchAvailableReports();
  }, []);

  const fetchAvailableReports = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/list`);
      if (response.ok) {
        const data = await response.json();
        setAvailableReports(data);
      }
    } catch (err) {
      console.error('Error fetching reports:', err);
    }
  };

  const generateReport = async (type) => {
    setGenerating(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate ${type} report`);
      }

      const result = await response.json();
      alert(`${type.charAt(0).toUpperCase() + type.slice(1)} report generated successfully!`);
      
      // Refresh available reports
      await fetchAvailableReports();
    } catch (err) {
      setError(err.message);
      alert(`Error: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = async (filename, type) => {
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/download/${type}/${filename}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Failed to download report: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (filename) => {
    // Extract date from filename
    const match = filename.match(/\d{4}-\d{2}-\d{2}/g);
    if (match) {
      return match.join(' to ');
    }
    return 'Unknown date';
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <div className="reports-view">
      <header className="header animate-fade-in">
        <div className="header-info">
          <h1 className="header-title">
            <span className="text-gradient">Reports Center</span>
          </h1>
          <p className="header-subtitle">Generate and download daily and weekly FinOps reports</p>
        </div>
      </header>

      {/* Report Type Selector */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.1s', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h3 style={{ marginBottom: '8px' }}>Report Type</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Select the type of report to view or generate
            </p>
          </div>
          <div className="period-selector">
            <button 
              onClick={() => setReportType('daily')}
              className={`period-button ${reportType === 'daily' ? 'active' : ''}`}
            >
              📅 Daily Reports
            </button>
            <button 
              onClick={() => setReportType('weekly')}
              className={`period-button ${reportType === 'weekly' ? 'active' : ''}`}
            >
              📊 Weekly Reports
            </button>
          </div>
        </div>

        {/* Report Description */}
        <div style={{
          background: 'var(--bg-elevated)',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          {reportType === 'daily' ? (
            <>
              <h4 style={{ marginBottom: '8px', color: 'var(--accent-primary)' }}>Daily Reports</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' }}>
                Daily reports provide a snapshot of yesterday's costs with detailed environment-wise breakdown, 
                anomaly detection, budget tracking, and optimization recommendations. Best for daily monitoring 
                and immediate alerts.
              </p>
              <div style={{ marginTop: '12px', display: 'flex', gap: '16px', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Coverage:</strong> Single day
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Trend Analysis:</strong> 7-day trends
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Best For:</strong> Daily monitoring
                </span>
              </div>
            </>
          ) : (
            <>
              <h4 style={{ marginBottom: '8px', color: 'var(--accent-primary)' }}>Weekly Reports</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' }}>
                Weekly reports aggregate the last 7 complete days of cost data with comprehensive trend analysis, 
                weekly patterns, and strategic insights. Includes daily averages and month-over-month comparisons. 
                Best for strategic planning and weekly reviews.
              </p>
              <div style={{ marginTop: '12px', display: 'flex', gap: '16px', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Coverage:</strong> 7 days
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Trend Analysis:</strong> 30-day trends
                </span>
                <span style={{ color: 'var(--text-secondary)' }}>
                  <strong>Best For:</strong> Strategic planning
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Generate New Report */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.2s', marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '8px' }}>Generate New Report</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px' }}>
          Create a new {reportType} report with the latest data from BigQuery
        </p>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={() => generateReport(reportType)}
            disabled={generating}
            style={{
              background: generating ? 'var(--bg-elevated)' : 'var(--accent-gradient)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: generating ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              opacity: generating ? 0.6 : 1
            }}
          >
            {generating ? (
              <>
                <span className="spinner"></span>
                Generating {reportType} report...
              </>
            ) : (
              <>
                ⚡ Generate {reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report
              </>
            )}
          </button>
          
          {generating && (
            <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
              This may take a few minutes...
            </span>
          )}
        </div>

        {error && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '6px',
            color: 'var(--danger)',
            fontSize: '13px'
          }}>
            {error}
          </div>
        )}
      </div>

      {/* Available Reports */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.3s' }}>
        <h3 style={{ marginBottom: '8px' }}>Available {reportType.charAt(0).toUpperCase() + reportType.slice(1)} Reports</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '20px' }}>
          Download previously generated reports
        </p>

        {availableReports[reportType]?.length > 0 ? (
          <div className="reports-grid">
            {availableReports[reportType].map((report, index) => (
              <div 
                key={index}
                className="report-card"
                style={{
                  background: 'var(--bg-elevated)',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '1px solid rgba(255,255,255,0.05)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--accent-primary)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '12px' }}>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    background: 'var(--accent-gradient)',
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '24px',
                    flexShrink: 0
                  }}>
                    📄
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h4 style={{ 
                      marginBottom: '4px', 
                      fontSize: '15px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {report.filename}
                    </h4>
                    <p style={{ 
                      color: 'var(--text-secondary)', 
                      fontSize: '13px',
                      marginBottom: '8px'
                    }}>
                      {formatDate(report.filename)}
                    </p>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        📦 {formatFileSize(report.size)}
                      </span>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        🕒 {new Date(report.modified).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => downloadReport(report.filename, reportType)}
                  disabled={loading}
                  style={{
                    width: '100%',
                    background: 'var(--bg-card)',
                    color: 'var(--accent-primary)',
                    border: '1px solid var(--accent-primary)',
                    padding: '10px',
                    borderRadius: '8px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    fontWeight: '600',
                    transition: 'all 0.2s ease',
                    opacity: loading ? 0.6 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.currentTarget.style.background = 'var(--accent-primary)';
                      e.currentTarget.style.color = 'white';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'var(--bg-card)';
                    e.currentTarget.style.color = 'var(--accent-primary)';
                  }}
                >
                  {loading ? 'Downloading...' : '⬇️ Download PDF'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'var(--bg-elevated)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>
              📭
            </div>
            <h4 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>
              No {reportType} reports available
            </h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Generate your first {reportType} report to get started
            </p>
          </div>
        )}
      </div>

      <style>{`
        .reports-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 20px;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .reports-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ReportsView;
