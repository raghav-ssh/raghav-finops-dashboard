# Frontend Reports Feature

## Overview

Added a comprehensive Reports Center to the frontend UI that allows users to:
- View and switch between daily and weekly reports
- Generate new reports on-demand
- Download previously generated reports
- See report metadata (size, date, etc.)

## New Components

### ReportsView Component
**Location:** `frontend/src/components/ReportsView.jsx`

A full-featured reports management interface with:
- Report type selector (Daily/Weekly)
- Report descriptions and use cases
- Generate new report button
- Grid view of available reports
- Download functionality
- Loading states and error handling

## Features

### 1. Report Type Selection
Users can toggle between:
- **Daily Reports**: Single day snapshots with 7-day trends
- **Weekly Reports**: 7-day aggregations with 30-day trends

### 2. Report Generation
- Click "Generate Report" button
- Backend runs the report generation script
- Shows loading spinner during generation
- Refreshes available reports list after completion

### 3. Report Download
- Grid view of all available reports
- Shows report metadata:
  - Filename
  - Date/date range
  - File size
  - Last modified date
- Click to download PDF

### 4. Visual Design
- Consistent with existing dashboard design
- Gradient accents and modern UI
- Responsive grid layout
- Hover effects and transitions
- Loading states

## Backend API Endpoints

### GET /api/reports/list
Lists all available daily and weekly reports.

**Response:**
```json
{
  "daily": [
    {
      "filename": "Daily_FinOps_Report_2026-03-10.pdf",
      "size": 1234567,
      "modified": "2026-03-10T08:00:00"
    }
  ],
  "weekly": [
    {
      "filename": "Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf",
      "size": 2345678,
      "modified": "2026-03-10T09:00:00"
    }
  ]
}
```

### POST /api/reports/generate
Generates a new report.

**Request:**
```json
{
  "type": "daily"  // or "weekly"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Daily report generated successfully",
  "filename": "Daily_FinOps_Report_2026-03-10.pdf"
}
```

### GET /api/reports/download/{report_type}/{filename}
Downloads a specific report file.

**Parameters:**
- `report_type`: "daily" or "weekly"
- `filename`: Name of the PDF file

**Response:** PDF file download

## UI Navigation

### Sidebar Menu
Added "Reports" menu item between Dashboard and Forecasting:
- 📊 Dashboard
- **📄 Reports** (NEW)
- 📈 Forecasting
- 🚨 Anomalies
- 💰 Budgets

### Reports View Layout

```
┌─────────────────────────────────────────────────────┐
│  Reports Center                                     │
│  Generate and download daily and weekly reports     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Report Type                                        │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ Daily Reports│  │Weekly Reports│               │
│  └──────────────┘  └──────────────┘               │
│                                                     │
│  [Report Description Box]                          │
│  - Coverage, Trend Analysis, Best For              │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Generate New Report                               │
│  ⚡ Generate Daily Report                          │
├─────────────────────────────────────────────────────┤
│  Available Daily Reports                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 📄       │  │ 📄       │  │ 📄       │        │
│  │ Report 1 │  │ Report 2 │  │ Report 3 │        │
│  │ Date     │  │ Date     │  │ Date     │        │
│  │ Size     │  │ Size     │  │ Size     │        │
│  │[Download]│  │[Download]│  │[Download]│        │
│  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────┘
```

## User Workflow

### Generate a New Report

1. Navigate to Reports from sidebar
2. Select report type (Daily or Weekly)
3. Click "Generate [Type] Report"
4. Wait for generation (shows spinner)
5. Report appears in available reports list
6. Download the generated report

### Download Existing Report

1. Navigate to Reports from sidebar
2. Select report type (Daily or Weekly)
3. Browse available reports in grid
4. Click "Download PDF" on desired report
5. PDF downloads to browser

## Code Changes

### Files Modified

1. **frontend/src/App.jsx**
   - Added import for ReportsView
   - Added 'reports' view case in render logic

2. **frontend/src/components/Sidebar.jsx**
   - Added Reports menu item
   - Positioned between Dashboard and Forecasting

3. **backend/api/api.py**
   - Updated imports to use new reporter classes
   - Added `/api/reports/list` endpoint
   - Added `/api/reports/generate` endpoint
   - Added `/api/reports/download/{type}/{filename}` endpoint
   - Updated existing endpoints to use new class names

### Files Created

1. **frontend/src/components/ReportsView.jsx**
   - Complete reports management UI
   - Report type selection
   - Generation and download functionality

## Styling

The ReportsView uses existing CSS variables and classes:
- `card` - Card containers
- `period-selector` / `period-button` - Toggle buttons
- `text-gradient` - Gradient text effects
- `animate-fade-in` - Fade-in animations
- Custom inline styles for report-specific elements

## Error Handling

### Frontend
- Shows error messages for failed generation
- Displays alerts for download failures
- Handles loading states gracefully
- Shows empty state when no reports available

### Backend
- Validates report type
- Checks file existence and permissions
- Handles subprocess timeouts
- Returns appropriate HTTP status codes
- Logs all errors for debugging

## Security

- File path validation to prevent directory traversal
- Only allows PDF file downloads
- Validates report type parameter
- Files must be in configured output directory

## Performance

- Report generation runs asynchronously
- 10-minute timeout for generation
- File listing is fast (directory scan)
- Downloads stream directly from disk

## Future Enhancements

Potential improvements:
1. Report scheduling/automation
2. Email delivery of reports
3. Report comparison view
4. Custom date range selection
5. Report preview before download
6. Bulk download multiple reports
7. Report deletion/cleanup
8. Report sharing links
9. Report templates
10. Export to other formats (CSV, Excel)

## Testing

### Manual Testing Checklist

- [ ] Reports menu item appears in sidebar
- [ ] Reports view loads without errors
- [ ] Can switch between daily and weekly tabs
- [ ] Report descriptions update correctly
- [ ] Generate button works for daily reports
- [ ] Generate button works for weekly reports
- [ ] Loading spinner shows during generation
- [ ] Success message appears after generation
- [ ] New reports appear in the list
- [ ] Can download daily reports
- [ ] Can download weekly reports
- [ ] Empty state shows when no reports
- [ ] Error handling works correctly
- [ ] File sizes display correctly
- [ ] Dates format correctly
- [ ] Responsive layout works on mobile

### API Testing

```bash
# List reports
curl http://localhost:8001/api/reports/list

# Generate daily report
curl -X POST http://localhost:8001/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "daily"}'

# Generate weekly report
curl -X POST http://localhost:8001/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "weekly"}'

# Download report
curl http://localhost:8001/api/reports/download/daily/Daily_FinOps_Report_2026-03-10.pdf \
  -o report.pdf
```

## Troubleshooting

### Reports Not Showing
- Check backend is running
- Verify `finops_reports/` directory exists
- Check file permissions
- Look for errors in browser console

### Generation Fails
- Check backend logs
- Verify BigQuery credentials
- Ensure Python dependencies installed
- Check disk space

### Download Fails
- Verify file exists in output directory
- Check file permissions
- Ensure correct report type specified
- Check browser download settings

## Documentation

Related documentation:
- [Report Structure](REPORT_STRUCTURE.md)
- [File Naming Conventions](REPORT_FILE_NAMING.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Upgrade Guide](UPGRADE_GUIDE.md)
