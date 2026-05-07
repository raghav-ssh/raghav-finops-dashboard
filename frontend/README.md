# FinOps Dashboard Frontend

Modern React-based dashboard for GCP cost analytics and reporting.

## Features

- Real-time cost tracking across environments
- Interactive charts and visualizations
- Anomaly detection and alerts
- Budget tracking and forecasting
- Responsive design with dark theme

## Tech Stack

- React 19
- Vite
- CSS3 with custom properties
- REST API integration

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://localhost:8001
```

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── main.jsx         # Application entry point
│   ├── index.css        # Global styles and theme
│   └── App.css          # Component-specific styles
├── public/              # Static assets
├── index.html           # HTML template
└── vite.config.js       # Vite configuration
```

## API Integration

The frontend connects to the FastAPI backend at the configured `VITE_API_URL`.

### Endpoints Used

- `GET /api/dashboard?period={period}` - Fetch dashboard data
- `GET /health` - Health check

## Styling

The app uses CSS custom properties for theming. Main theme variables are defined in `index.css`:

- Dark color scheme optimized for readability
- Gradient accents for visual interest
- Smooth transitions and animations
- Responsive breakpoints for mobile support

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Proprietary
