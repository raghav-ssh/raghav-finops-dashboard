# Budget Management Feature

## Overview

Added comprehensive budget management with support for daily, weekly, and monthly budgets per environment. The PDF reports automatically use the appropriate budget based on the report type.

## Features

### 1. Multi-Period Budgets
Set separate budgets for each period:
- **Daily Budget**: Used for daily reports and daily tracking
- **Weekly Budget**: Used for weekly reports (typically 7x daily)
- **Monthly Budget**: Used for monthly projections and forecasting

### 2. Frontend UI
Complete budget management interface:
- View budgets by period (Daily/Weekly/Monthly toggle)
- Edit all three budget types simultaneously
- Visual budget cards with environment icons
- Comprehensive budget overview table
- Real-time validation and formatting

### 3. Automatic Report Integration
- Daily reports use daily budgets for tracking
- Weekly reports use weekly budgets for tracking
- Both use monthly budgets for projections
- Budget alerts based on appropriate thresholds

## How It Works

### Frontend (BudgetsView)

1. **View Mode**
   - Toggle between Daily/Weekly/Monthly view
   - See current budget for selected period
   - All three budgets shown in small text
   - Color-coded by environment

2. **Edit Mode**
   - Edit all three budgets at once
   - Separate input fields for each period
   - Real-time currency formatting
   - Save/Cancel buttons

3. **Budget Overview Table**
   - Shows all budgets in one view
   - Status indicators (Active/Not Set)
   - Environment icons and colors

### Backend (budgets.py)

1. **Budget Format**
   ```json
   {
     "prod": {
       "daily": 20000.0,
       "weekly": 140000.0,
       "monthly": 600000.0
     },
     "uat": {
       "daily": 5000.0,
       "weekly": 35000.0,
       "monthly": 150000.0
     }
   }
   ```

2. **Backward Compatibility**
   - Old format (single number) automatically converted
   - `600000` → `{daily: 20000, weekly: 140000, monthly: 600000}`
   - Seamless migration
   - All services handle both formats (BudgetTracker, AnomalyDetector)

3. **Helper Functions**
   - `get_budgets()` - Returns normalized budgets
   - `update_budgets()` - Saves with normalization
   - `get_budget_for_period()` - Gets specific period budget
   - `normalize_budget()` - Converts old to new format

### Budget Tracker

1. **Period-Aware Tracking**
   ```python
   # Daily report
   tracker = BudgetTracker(budgets, period='daily')
   
   # Weekly report
   tracker = BudgetTracker(budgets, period='weekly')
   ```

2. **Smart Budget Selection**
   - Uses appropriate budget for the report type
   - Falls back to monthly budget if period not set
   - Handles both old and new formats

3. **Projection Logic**
   - Always uses monthly budget for projections
   - Calculates burn rate based on current spending
   - Provides budget usage percentage

## Usage

### Setting Budgets in UI

1. Navigate to "💰 Budgets" in sidebar
2. Click "✏️ Edit Budgets"
3. Enter budgets for each period:
   - Daily: Per-day spending limit
   - Weekly: 7-day spending limit
   - Monthly: Full month spending limit
4. Click "💾 Save Changes"

### Viewing Budgets

1. Use period toggle to switch views:
   - 📅 Daily
   - 📊 Weekly
   - 📆 Monthly
2. See large display of selected period
3. Small text shows all three budgets

### Budget Recommendations

**Daily Budget:**
- Divide monthly budget by 30
- Example: ₹600,000/month = ₹20,000/day

**Weekly Budget:**
- Multiply daily budget by 7
- Example: ₹20,000/day × 7 = ₹140,000/week

**Monthly Budget:**
- Total spending limit for the month
- Example: ₹600,000/month

## API Endpoints

### GET /api/budgets
Returns all budgets in new format:
```json
{
  "prod": {
    "daily": 20000.0,
    "weekly": 140000.0,
    "monthly": 600000.0
  }
}
```

### POST /api/budgets
Update budgets:
```json
{
  "budgets": {
    "prod": {
      "daily": 25000.0,
      "weekly": 175000.0,
      "monthly": 750000.0
    }
  }
}
```

## PDF Report Integration

### Daily Reports
- Use `daily` budget for tracking
- Show daily budget in budget section
- Calculate usage: `actual_daily_cost / daily_budget`
- Alert if exceeds 75% or 90%

### Weekly Reports
- Use `weekly` budget for tracking
- Show weekly budget in budget section
- Calculate usage: `actual_weekly_cost / weekly_budget`
- Alert if exceeds 75% or 90%

### Both Reports
- Use `monthly` budget for projections
- Project end-of-month spending
- Show projected vs monthly budget
- Provide budget status

## Budget Alerts

Alerts trigger at these thresholds:
- **75%**: Warning alert (⚠️)
- **90%**: Critical alert (🔴)
- **100%+**: Over budget (❌)

Shown in:
- PDF reports (Budget Tracking section)
- Dashboard (Budget status)
- Email notifications (if configured)

## Default Budgets

If no budgets are set, these defaults apply:

| Environment | Daily | Weekly | Monthly |
|-------------|-------|--------|---------|
| Production  | ₹20,000 | ₹140,000 | ₹600,000 |
| UAT         | ₹5,000  | ₹35,000  | ₹150,000 |
| Development | ₹3,333  | ₹23,333  | ₹100,000 |
| Unlabeled   | ₹1,667  | ₹11,667  | ₹50,000  |

## Files Modified

### Frontend
- `frontend/src/components/BudgetsView.jsx` - Complete rewrite with multi-period support

### Backend
- `backend/core/budgets.py` - Added multi-period support and normalization
- `backend/services/budget_tracker.py` - Added period parameter and smart budget selection
- `backend/services/anomaly_detector.py` - Updated to handle both old and new budget formats
- `backend/reports/daily_env_finops_enhanced.py` - Pass 'daily' period to tracker
- `backend/reports/weekly_env_finops_report.py` - Pass 'weekly' period to tracker

## Migration

### Existing Budgets
Old budgets are automatically converted:
```json
// Old format
{
  "prod": 600000.0
}

// Automatically becomes
{
  "prod": {
    "daily": 20000.0,
    "weekly": 140000.0,
    "monthly": 600000.0
  }
}
```

### No Action Required
- Existing budgets continue to work
- Conversion happens automatically
- No data loss
- Seamless upgrade

## Benefits

1. **More Accurate Tracking**
   - Daily reports use daily budgets
   - Weekly reports use weekly budgets
   - Better budget compliance

2. **Flexible Budgeting**
   - Set different budgets for different periods
   - Account for weekly/monthly variations
   - More granular control

3. **Better Alerts**
   - Alerts based on appropriate budget
   - Fewer false positives
   - More actionable insights

4. **User-Friendly**
   - Easy to set and view budgets
   - Visual feedback
   - Clear documentation

## Examples

### Setting Production Budgets
```
Daily: ₹25,000
Weekly: ₹175,000 (7 × ₹25,000)
Monthly: ₹750,000 (30 × ₹25,000)
```

### Setting Development Budgets
```
Daily: ₹5,000
Weekly: ₹35,000
Monthly: ₹150,000
```

### Viewing in Reports
- Daily report shows: "Daily Budget: ₹25,000"
- Weekly report shows: "Weekly Budget: ₹175,000"
- Both show: "Monthly Projection: ₹750,000"

## Tips

1. **Start with Monthly**: Set monthly budget first, then divide by 30 for daily
2. **Weekly = 7x Daily**: Keep weekly budget as 7 times daily for consistency
3. **Review Regularly**: Adjust budgets quarterly based on actual spending
4. **Use Alerts**: Pay attention to 75% and 90% warnings
5. **Track Trends**: Compare actual vs budget over time

## Troubleshooting

### Budgets Not Saving
- Check backend is running
- Verify API endpoint is accessible
- Check browser console for errors

### Wrong Budget in Report
- Verify budget is set for correct period
- Check report type matches budget period
- Regenerate report after budget update

### Budget Alerts Not Showing
- Ensure budgets are set (> 0)
- Check spending exceeds threshold (75% or 90%)
- Verify budget tracker is using correct period

## Future Enhancements

Potential improvements:
1. Budget history tracking
2. Budget vs actual charts
3. Budget recommendations based on trends
4. Multi-currency support
5. Budget approval workflows
6. Budget templates
7. Automated budget adjustments
8. Budget forecasting
