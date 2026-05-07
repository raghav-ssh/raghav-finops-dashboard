# FinOps Reporting System

Comprehensive cost analytics and reporting platform for Google Cloud Platform.

## Quick Start

```bash
# Setup (first time only)
./scripts/setup_dev.sh

# Start everything
./scripts/start.sh
```

Access dashboard at: http://localhost:5173

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [How to Run](docs/RUN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Improvements](docs/IMPROVEMENTS.md)

## Project Structure

```
.
├── backend/           # Python backend
│   ├── api/          # FastAPI endpoints
│   ├── core/         # Core functionality
│   ├── services/     # Business logic
│   ├── reports/      # Report generation
│   └── utils/        # Utilities
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── services/
│       └── utils/
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── outputs/          # Generated reports
```

## Commands

```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev

# Generate report
cd backend && python run_report.py --period daily
```

For detailed instructions, see [docs/RUN.md](docs/RUN.md)
# raghav-finops-dashboard
