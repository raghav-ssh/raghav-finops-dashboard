# Frontend Quick Start - Reports Feature

## Getting Started

### 1. Start the Backend
```bash
cd backend
python api/api.py
```
Backend will run on http://localhost:8001

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend will run on http://localhost:5173

### 3. Access Reports Center
1. Open http://localhost:5173 in your browser
2. Click "📄 Reports" in the left sidebar
3. You're now in the Reports Center!

## Using the Reports Center

### View Daily Reports
1. Click the "📅 Daily Reports" tab (selected by default)
2. See description of daily reports
3. View all available daily reports in the grid

### View Weekly Reports
1. Click the "📊 Weekly Reports" tab
2. See description of weekly reports
3. View all available weekly reports in the grid

### Generate a New Report

#### Daily Report
1. Select "📅 Daily Reports" tab
2. Click "⚡ Generate Daily Report" button
3. Wait 2-5 minutes for generation
4. Report appears in the grid when complete

#### Weekly Report
1. Select "📊 Weekly Reports" tab
2. Click "⚡ Generate Weekly Report" button
3. Wait 5-10 minutes for generation
4. Report appears in the grid when complete

### Download a Report
1. Find the report you want in the grid
2. Click "⬇️ Download PDF" button
3. PDF downloads to your browser's download folder

## UI Overview

```
┌─────────────────────────────────────────────────────┐
│ FinOps Menu                                         │
│ ┌─────────────────┐                                │
│ │ 📊 Dashboard    │                                │
│ │ 📄 Reports      │ ← Click here                   │
│ │ 📈 Forecasting  │                                │
│ │ 🚨 Anomalies    │                                │
│ │ 💰 Budgets      │                                │
│ └─────────────────┘                                │
└─────────────────────────────────────────────────────┘

Reports Center
┌─────────────────────────────────────────────────────┐
│ Reports Center                                      │
│ Generate and download daily and weekly reports      │
├─────────────────────────────────────────────────────┤
│ Report Type                                         │
│ ┌──────────────┐  ┌──────────────┐                │
│ │📅 Daily      │  │📊 Weekly     │                │
│ │  Reports     │  │  Reports     │                │
│ └──────────────┘  └──────────────┘                │
│                                                     │
│ [Description of selected report type]              │
├─────────────────────────────────────────────────────┤
│ Generate New Report                                 │
│ ⚡ Generate Daily Report                           │
├─────────────────────────────────────────────────────┤
│ Available Daily Reports                             │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│ │ 📄       │  │ 📄       │  │ 📄       │         │
│ │ Report 1 │  │ Report 2 │  │ Report 3 │         │
│ │ 2026-03-10│ │ 2026-03-09│ │ 2026-03-08│        │
│ │ 2.5 MB   │  │ 2.4 MB   │  │ 2.3 MB   │         │
│ │⬇️Download│  │⬇️Download│  │⬇️Download│         │
│ └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

## Report Information

### Daily Reports
- **Coverage**: Single day (yesterday's data)
- **Trend Analysis**: 7-day trends
- **Best For**: Daily monitoring, immediate alerts
- **File Name**: `Daily_FinOps_Report_YYYY-MM-DD.pdf`
- **Generation Time**: 2-5 minutes

### Weekly Reports
- **Coverage**: Last 7 complete days
- **Trend Analysis**: 30-day trends
- **Best For**: Strategic planning, weekly reviews
- **File Name**: `Weekly_FinOps_Report_YYYY-MM-DD_to_YYYY-MM-DD.pdf`
- **Generation Time**: 5-10 minutes

## Troubleshooting

### Reports Not Showing
**Problem**: No reports appear in the grid

**Solutions**:
1. Check if backend is running (http://localhost:8001/health)
2. Generate a new report first
3. Check browser console for errors
4. Verify `backend/finops_reports/` directory exists

### Generation Fails
**Problem**: Report generation shows error

**Solutions**:
1. Check backend logs for errors
2. Verify BigQuery credentials are configured
3. Ensure Python dependencies are installed
4. Check disk space

### Download Fails
**Problem**: Download button doesn't work

**Solutions**:
1. Check browser console for errors
2. Verify file exists in `backend/finops_reports/`
3. Check browser download settings
4. Try a different browser

### Slow Generation
**Problem**: Report takes too long to generate

**Expected**:
- Daily reports: 2-5 minutes
- Weekly reports: 5-10 minutes

**If slower**:
1. Check BigQuery query performance
2. Verify network connection
3. Check system resources (CPU, memory)

## Features

### ✅ What You Can Do
- Switch between daily and weekly reports
- Generate new reports on-demand
- Download any available report
- See report metadata (size, date)
- View report descriptions
- Responsive design (works on mobile)

### ⏳ Coming Soon
- Custom date range selection
- Report scheduling
- Email delivery
- Report comparison
- Bulk download
- Report preview

## Tips

1. **Generate reports regularly**: Set up a schedule to generate reports daily/weekly
2. **Check file sizes**: Larger files may indicate more data or issues
3. **Use appropriate report type**: Daily for monitoring, Weekly for planning
4. **Download important reports**: Keep copies of key reports locally
5. **Monitor generation time**: Unusually long times may indicate issues

## Keyboard Shortcuts

Currently no keyboard shortcuts, but you can:
- Use Tab to navigate between buttons
- Press Enter to activate focused button
- Use browser shortcuts (Ctrl+S to save downloaded PDF)

## Mobile Support

The Reports Center is fully responsive:
- Grid adapts to screen size
- Touch-friendly buttons
- Optimized for mobile browsers
- Works on tablets and phones

## Browser Support

Tested and working on:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Next Steps

After using the Reports Center:
1. Explore the Dashboard view
2. Check Forecasting for cost predictions
3. Review Budgets for spending limits
4. Set up automated report generation
5. Share reports with your team

## Support

For issues or questions:
- Check [Frontend Reports Feature](FRONTEND_REPORTS_FEATURE.md) documentation
- Review [Quick Reference](QUICK_REFERENCE.md)
- See [Troubleshooting](UPGRADE_GUIDE.md#common-issues)
