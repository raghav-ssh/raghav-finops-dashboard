# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Google Cloud Platform account with billing export configured
- GCP service account with BigQuery access

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd /path/to/project

# Make setup script executable
chmod +x setup_dev.sh

# Run setup (installs all dependencies)
./setup_dev.sh
```

## Step 2: Configure Environment Variables

### Backend Configuration

Create `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_DATASET=gcp_billing
GCP_TABLE=gcp_billing_export_resource_v1_01D037_3AB34D_12AAE9

# Governance
REQUIRED_LABEL=env
ALERT_THRESHOLD=90

# Notifications (Optional)
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@example.com
```

### Frontend Configuration

Create `frontend/.env` file:

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8001
```

## Step 3: Run Backend

### Option A: Direct Python

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run the API server
python api.py
```

The backend will start on `http://localhost:8001`

### Option B: Using Make

```bash
make run-backend
```

### Verify Backend is Running

Open browser or use curl:
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{"status": "healthy", "service": "finops-api"}
```

## Step 4: Run Frontend

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### Option B: Using Make

```bash
make run-frontend
```

## Step 5: Access Dashboard

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the FinOps Dashboard with:
- Cost metrics
- Environment breakdown
- Cost trends chart
- Critical alerts

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

---

**Problem**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**: Set up GCP credentials
```bash
# Option 1: Use service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-gcp-sa.json"

# Option 2: Use gcloud auth
gcloud auth application-default login
```

---

**Problem**: `BigQuery access denied`

**Solution**: Ensure service account has these roles:
- BigQuery Data Viewer
- BigQuery Job User

---

**Problem**: `Port 8001 already in use`

**Solution**: Kill existing process or change port
```bash
# Find process using port 8001
lsof -ti:8001 | xargs kill -9

# Or change port in api.py (last line)
uvicorn.run(app, host="0.0.0.0", port=8002)
```

### Frontend Issues

**Problem**: `npm: command not found`

**Solution**: Install Node.js
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node
```

---

**Problem**: `Failed to fetch data - Network error`

**Solution**: 
1. Verify backend is running: `curl http://localhost:8001/health`
2. Check CORS settings in `api.py`
3. Verify `VITE_API_URL` in `frontend/.env`

---

**Problem**: `Port 5173 already in use`

**Solution**: Kill process or use different port
```bash
# Kill process
lsof -ti:5173 | xargs kill -9

# Or specify different port
npm run dev -- --port 5174
```

---

**Problem**: `Module not found` errors in frontend

**Solution**: Reinstall dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Running Both Simultaneously

### Option 1: Two Terminal Windows

**Terminal 1 (Backend)**:
```bash
python api.py
```

**Terminal 2 (Frontend)**:
```bash
cd frontend && npm run dev
```

### Option 2: Using tmux

```bash
# Start tmux session
tmux new -s finops

# Split window horizontally
Ctrl+b "

# In first pane (top)
python api.py

# Switch to second pane
Ctrl+b ↓

# In second pane (bottom)
cd frontend && npm run dev

# Detach from session
Ctrl+b d

# Reattach later
tmux attach -t finops
```

### Option 3: Using screen

```bash
# Start backend in background
screen -dmS backend bash -c 'python api.py'

# Start frontend in background
screen -dmS frontend bash -c 'cd frontend && npm run dev'

# View backend logs
screen -r backend

# View frontend logs
screen -r frontend

# Detach: Ctrl+a d
```

### Option 4: Background Processes

```bash
# Start backend in background
nohup python api.py > backend.log 2>&1 &

# Start frontend in background
cd frontend && nohup npm run dev > ../frontend.log 2>&1 &

# View logs
tail -f backend.log
tail -f frontend.log

# Stop processes
pkill -f "python api.py"
pkill -f "npm run dev"
```

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t finops-reporting .

# Run container
docker run -d \
  -p 8001:8001 \
  -v $(pwd)/.env:/app/.env \
  --name finops-backend \
  finops-reporting

# Check logs
docker logs -f finops-backend
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8001:8001"
    env_file:
      - .env
    volumes:
      - ./finops_reports:/app/finops_reports
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8001
    depends_on:
      - backend
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## Testing the Setup

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8001/health

# Get dashboard data (daily)
curl http://localhost:8001/api/dashboard?period=daily

# Get dashboard data (weekly)
curl http://localhost:8001/api/dashboard?period=weekly

# Force refresh cache
curl http://localhost:8001/api/dashboard?period=daily&refresh=true
```

### 2. Test Frontend

1. Open `http://localhost:5173`
2. Check that data loads
3. Try switching periods (hourly/daily/weekly/monthly)
4. Verify charts render
5. Check environment table displays

### 3. Generate Full Report

```bash
# Generate daily report
python daily_env_finops_enhanced.py --period daily

# Check outputs
ls -lh finops_reports/

# View PDF report
open finops_reports/Enhanced_Daily_FinOps_Report_*.pdf
```

## Development Workflow

### 1. Start Development Session

```bash
# Terminal 1: Backend with auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend with hot-reload
cd frontend && npm run dev
```

### 2. Make Changes

- Backend changes auto-reload with uvicorn
- Frontend changes hot-reload with Vite
- No need to restart servers

### 3. Format Code

```bash
# Format all code
./format_code.sh

# Or use Make
make format
```

### 4. Run Linters

```bash
make lint
```

## Next Steps

1. **Customize Budgets**: Edit budgets in `daily_env_finops_enhanced.py`
2. **Configure Alerts**: Set up Slack webhook for notifications
3. **Schedule Reports**: Add cron job for automated reports
4. **Explore Data**: Check CSV outputs in `finops_reports/`
5. **Review Architecture**: Read `ARCHITECTURE.md` for details

## Useful Commands

```bash
# View backend logs
tail -f backend.log

# View frontend logs
tail -f frontend.log

# Check running processes
ps aux | grep -E "python|node"

# Check ports in use
lsof -i :8001
lsof -i :5173

# Clean generated files
make clean

# Restart everything
pkill -f "python api.py"
pkill -f "npm run dev"
python api.py &
cd frontend && npm run dev &
```

## Support

For issues or questions:
1. Check logs in `backend.log` and `frontend.log`
2. Review `ARCHITECTURE.md` for system details
3. Check `README.md` for comprehensive documentation
4. Contact the FinOps team

## Quick Reference

| Component | Command | URL |
|-----------|---------|-----|
| Backend | `python api.py` | http://localhost:8001 |
| Frontend | `cd frontend && npm run dev` | http://localhost:5173 |
| Health Check | `curl http://localhost:8001/health` | - |
| API Docs | - | http://localhost:8001/docs |
| Generate Report | `python daily_env_finops_enhanced.py` | - |

---

**Ready to go!** 🚀

Start with: `python api.py` in one terminal and `cd frontend && npm run dev` in another.
