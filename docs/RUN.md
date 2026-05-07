# How to Run - Simple Guide

## 🚀 Quick Start (Easiest Way)

### 1. One-Command Startup

```bash
./start.sh
```

This will:
- ✅ Start the backend API on port 8001
- ✅ Start the frontend dashboard on port 5173
- ✅ Show you the URLs to access
- ✅ Display logs from both services

### 2. Access the Dashboard

Open your browser:
```
http://localhost:5173
```

### 3. Stop Everything

Press `Ctrl+C` in the terminal where start.sh is running

Or run:
```bash
./stop.sh
```

---

## 📋 Manual Method (Step by Step)

### Backend

**Terminal 1:**
```bash
# Start backend
python api.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Frontend

**Terminal 2:**
```bash
# Navigate to frontend
cd frontend

# Start frontend
npm run dev
```

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Access

Open browser: `http://localhost:5173`

---

## 🔧 First Time Setup

If this is your first time running the project:

### 1. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy example files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Edit .env with your GCP credentials
nano .env

# Edit frontend/.env with API URL (usually default is fine)
nano frontend/.env
```

### 3. Run Setup Script (Optional)

```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

---

## 🎯 What You'll See

### Backend (Terminal)
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Frontend (Terminal)
```
  VITE v7.3.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

### Dashboard (Browser)
- Cost metrics cards
- 7-day cost trend chart
- Environment breakdown table
- Critical alerts panel
- Period selector (hourly/daily/weekly/monthly)

---

## ✅ Verify Everything Works

### 1. Check Backend Health

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{"status":"healthy","service":"finops-api"}
```

### 2. Check API Data

```bash
curl http://localhost:8001/api/dashboard?period=daily
```

Should return JSON with cost data.

### 3. Check Frontend

Open `http://localhost:5173` - you should see the dashboard loading.

---

## 🛑 How to Stop

### If using start.sh
Press `Ctrl+C` in the terminal

### If running manually
Press `Ctrl+C` in each terminal window (backend and frontend)

### If running in background
```bash
./stop.sh
```

Or manually:
```bash
# Kill backend
pkill -f "python.*api.py"

# Kill frontend
pkill -f "vite"
```

---

## 🐛 Common Issues

### "Port already in use"

**Backend (8001):**
```bash
# Find and kill process
lsof -ti:8001 | xargs kill -9
```

**Frontend (5173):**
```bash
# Find and kill process
lsof -ti:5173 | xargs kill -9
```

### "Module not found"

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### "Cannot connect to API"

1. Check backend is running: `curl http://localhost:8001/health`
2. Check `frontend/.env` has correct API URL
3. Check browser console for errors

### "GCP credentials error"

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp-sa.json"

# Or use gcloud
gcloud auth application-default login
```

---

## 📊 URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://localhost:5173 | Main UI |
| API | http://localhost:8001 | Backend API |
| API Docs | http://localhost:8001/docs | Interactive API docs |
| Health Check | http://localhost:8001/health | Status check |

---

## 💡 Tips

### Run in Background

```bash
# Start backend in background
nohup python api.py > backend.log 2>&1 &

# Start frontend in background
cd frontend && nohup npm run dev > ../frontend.log 2>&1 &

# View logs
tail -f backend.log
tail -f frontend.log
```

### Development Mode

Backend with auto-reload:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

Frontend already has hot-reload enabled by default.

### Production Mode

```bash
# Build frontend
cd frontend
npm run build

# Serve with a web server
npm run preview
```

---

## 🎓 Next Steps

1. ✅ Get it running (you're here!)
2. 📖 Read `QUICKSTART.md` for detailed setup
3. 🏗️ Read `ARCHITECTURE.md` to understand the system
4. 📝 Read `README.md` for full documentation
5. 🔧 Customize budgets and alerts
6. 📊 Generate reports with `python daily_env_finops_enhanced.py`

---

## 🆘 Need Help?

1. Check logs: `tail -f backend.log frontend.log`
2. Review `QUICKSTART.md` for troubleshooting
3. Check `ARCHITECTURE.md` for system details
4. Contact the FinOps team

---

**That's it! You're ready to go.** 🎉

Just run `./start.sh` and open `http://localhost:5173`
