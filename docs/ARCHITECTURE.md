# FinOps Reporting System - Architecture

## Overview

The FinOps Reporting System is a comprehensive cost analytics platform for Google Cloud Platform that provides real-time cost tracking, anomaly detection, budget management, and optimization recommendations.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  React Dashboard (Vite)                                │ │
│  │  - Cost Visualizations                                 │ │
│  │  - Real-time Metrics                                   │ │
│  │  - Interactive Charts                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI Backend                                       │ │
│  │  - /api/dashboard (GET)                                │ │
│  │  - /health (GET)                                       │ │
│  │  - Caching Layer                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Anomaly    │  │   Budget     │  │     Cost     │      │
│  │  Detection   │  │   Tracking   │  │ Optimization │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Environment  │  │  Governance  │  │    Report    │      │
│  │   Analysis   │  │   Metrics    │  │  Generation  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  BigQuery Client                                       │ │
│  │  - Query Execution                                     │ │
│  │  - Data Transformation                                 │ │
│  │  - Schema Management                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   BigQuery   │  │    Slack     │  │    Email     │      │
│  │   Billing    │  │ Notifications│  │    SMTP      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: React 19 + Vite

**Components**:
- `App.jsx` - Main dashboard component
- `main.jsx` - Application entry point
- `index.css` - Global styles and theme

**Features**:
- Real-time cost metrics display
- Interactive period selection (hourly/daily/weekly/monthly)
- Environment breakdown table
- Cost trend charts
- Critical alerts panel
- Responsive design

**State Management**:
- React hooks (useState, useEffect)
- Local state for data and UI state
- API polling for data refresh

### 2. API Layer

**Technology**: FastAPI

**File**: `api.py`

**Endpoints**:

```python
GET /api/dashboard?period={period}&refresh={bool}
- Returns dashboard data for specified period
- Supports caching to reduce BigQuery queries
- Parameters:
  - period: hourly|daily|weekly|monthly
  - refresh: force cache refresh

GET /health
- Health check endpoint
- Returns service status
```

**Features**:
- CORS middleware for frontend access
- In-memory caching
- Error handling and logging
- Data transformation for frontend

### 3. Business Logic Layer

#### 3.1 Anomaly Detection (`anomaly_detector.py`)

**Purpose**: Detect unusual cost patterns and generate alerts

**Detection Types**:
- Day-over-day cost spikes (>20% increase)
- Unusual cost drops (>30% decrease)
- High unlabeled spend (>25% of total)
- Budget threshold breaches
- Service-level anomalies

**Output**: List of `Anomaly` objects with severity levels

#### 3.2 Budget Tracking (`budget_tracker.py`)

**Purpose**: Track budget usage and forecast month-end costs

**Features**:
- Environment-specific budget tracking
- Burn rate calculation
- Projected monthly cost forecasting
- Budget status classification (on_track, warning, critical, over_budget)
- Daily savings recommendations

**Output**: List of `BudgetStatus` objects

#### 3.3 Cost Optimization (`cost_optimizer.py`)

**Purpose**: Identify cost savings opportunities

**Analysis Types**:
- Idle compute instances
- Unattached persistent disks
- Oversized resources
- Commitment use discount opportunities

**Output**: List of `Optimization` objects with potential savings

#### 3.4 Environment Analysis (`env_cost_analyzer.py`)

**Purpose**: Provide detailed environment-wise cost breakdowns

**Analysis Types**:
- Anomaly costs by environment
- Optimization opportunities by environment
- Budget summary by environment
- Service costs by environment
- Resource counts and metrics
- Governance compliance details

**Output**: Multiple DataFrames with environment-specific metrics

#### 3.5 Report Generation

**Chart Generator** (`enhanced_chart_generator.py`):
- Environment comparison charts
- 7-day trend charts
- Day-over-day change charts
- Top resources charts
- Service breakdown pie charts
- Budget tracking charts

**PDF Generator** (`pdf_generator.py`):
- Professional PDF reports
- Tables and charts integration
- Custom styling
- Multi-page reports

**Notification Service** (`notification_service.py`):
- Email reports with attachments
- Slack notifications
- Anomaly alerts
- Daily summaries

### 4. Data Layer

#### BigQuery Client (`bigquery_client.py`)

**Purpose**: Wrapper for BigQuery operations

**Features**:
- Query execution with error handling
- DataFrame conversion
- Schema inspection
- Connection management

#### Query Templates (`queries.py`)

**Purpose**: SQL query templates for cost analysis

**Query Types**:
- Period cost detail
- Daily cost breakdown
- Service cost breakdown
- Weekly app costs
- Compute Engine costs
- Network costs
- Unlabeled resources
- Label compliance

### 5. Configuration & Utilities

#### Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Config Classes**:
- `GCPConfig` - BigQuery connection settings
- `ReportConfig` - Report output settings
- `GovernanceConfig` - Compliance settings

#### Logger (`logger.py`)

**Purpose**: Structured logging setup

**Features**:
- Console and file logging
- Configurable log levels
- Formatted output

#### Utils (`utils.py`)

**Purpose**: Common utility functions

**Functions**:
- Currency formatting
- Percentage calculations
- Data aggregation
- Compliance rate calculation
- DataFrame validation
- CSV export

## Data Flow

### Dashboard Data Request Flow

```
1. User selects period in frontend
   ↓
2. Frontend sends GET /api/dashboard?period=daily
   ↓
3. API checks cache
   ├─ Cache hit → Return cached data
   └─ Cache miss → Continue
   ↓
4. API instantiates EnhancedDailyEnvFinOpsReporter
   ↓
5. Reporter fetches data from BigQuery
   ├─ Daily environment costs
   ├─ Environment summary
   ├─ Daily trends
   └─ Governance metrics
   ↓
6. Reporter runs analytics
   ├─ Detect anomalies
   ├─ Track budgets
   └─ Calculate metrics
   ↓
7. API transforms data to frontend format
   ↓
8. API caches result
   ↓
9. API returns JSON response
   ↓
10. Frontend updates UI with data
```

### Report Generation Flow

```
1. Run daily_env_finops_enhanced.py
   ↓
2. Fetch data from BigQuery
   ↓
3. Calculate metrics and analytics
   ↓
4. Generate charts (PNG files)
   ↓
5. Generate CSV reports
   ↓
6. Generate PDF report
   ↓
7. Send notifications (Email/Slack)
   ↓
8. Save outputs to finops_reports/
```

## Database Schema

### BigQuery Billing Export Table

**Table**: `{project}.{dataset}.gcp_billing_export_resource_v1_*`

**Key Fields**:
- `usage_start_time` - Timestamp of usage
- `cost` - Cost amount
- `credits` - Applied credits
- `service.description` - GCP service name
- `sku.description` - SKU description
- `resource.name` - Resource identifier
- `location.region` - GCP region
- `labels` - Resource labels (array)
  - `key` - Label key (e.g., "env", "app")
  - `value` - Label value

## Security Considerations

### Authentication & Authorization
- GCP service account with BigQuery Data Viewer role
- Environment variables for sensitive credentials
- No hardcoded secrets

### Data Access
- Read-only access to billing data
- No PII in cost data
- Secure credential storage

### API Security
- CORS configuration for frontend access
- Input validation on API endpoints
- Error handling without exposing internals

## Performance Optimization

### Caching Strategy
- In-memory cache for API responses
- Cache key: `{date}_{period}`
- Cache invalidation on refresh parameter

### Query Optimization
- Filtered queries with date ranges
- Cost thresholds to reduce data volume
- Aggregation at query level
- Indexed label lookups

### Frontend Optimization
- Lazy loading of components
- Efficient re-renders with React hooks
- CSS animations with GPU acceleration
- Responsive images and charts

## Scalability

### Current Limitations
- In-memory cache (single instance)
- Synchronous report generation
- Single BigQuery connection

### Future Enhancements
- Redis for distributed caching
- Async report generation with queues
- Connection pooling
- Horizontal scaling with load balancer

## Monitoring & Observability

### Logging
- Structured logging with timestamps
- Log levels: INFO, WARNING, ERROR
- File and console output

### Metrics
- API response times
- BigQuery query duration
- Cache hit rates
- Error rates

### Alerts
- Critical anomaly detection
- Budget threshold breaches
- API health checks
- Failed report generation

## Deployment

### Development
```bash
# Backend
python api.py

# Frontend
cd frontend && npm run dev
```

### Production
```bash
# Docker
docker build -t finops-reporting .
docker run -p 8001:8001 finops-reporting

# Or with docker-compose
docker-compose up -d
```

## Maintenance

### Regular Tasks
- Review and update budgets monthly
- Clean old reports (>90 days)
- Update dependencies quarterly
- Review anomaly thresholds

### Backup & Recovery
- BigQuery data is managed by GCP
- Configuration in version control
- Report outputs archived to GCS

## Future Roadmap

### Phase 1 (Current)
- ✅ Multi-period reporting
- ✅ Anomaly detection
- ✅ Budget tracking
- ✅ Cost optimization
- ✅ Dashboard UI

### Phase 2 (Planned)
- [ ] Historical trend analysis (6+ months)
- [ ] Predictive cost forecasting with ML
- [ ] Custom alert rules
- [ ] Multi-project support
- [ ] User authentication

### Phase 3 (Future)
- [ ] Cost allocation by team
- [ ] Chargeback reporting
- [ ] Integration with JIRA/ServiceNow
- [ ] Mobile app
- [ ] Advanced analytics dashboard
