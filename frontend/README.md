# Order Orchestrator UI

React frontend dashboard for the Temporal Order Orchestration System.

## Features

- 🚀 **Start Orders** - Create new order workflows with auto-generated IDs
- 📊 **Real-Time Status** - Auto-refreshing order status every 2 seconds
- ⏸️ **Manual Approval** - Approve orders waiting for review
- ❌ **Cancellation** - Cancel orders before payment
- 📍 **Address Updates** - Update shipping address before dispatch
- 🎨 **Beautiful Timeline** - Visual workflow progress tracking

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Navigation
- **TanStack Query** - Data fetching with auto-refresh
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## Usage

### Prerequisites

Make sure the backend services are running:

1. **Docker services**: `docker-compose up -d` (in project root)
2. **Workers**: `python -m temporal_app.worker_dev`
3. **API Server**: `python -m api.server`

### Workflow

1. **Home Page** (`/`) - Start a new order
2. **Order Detail** (`/orders/:orderId`) - View status and send signals
3. **Orders List** (`/orders`) - Placeholder for order history

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

Endpoints used:
- `POST /orders/{id}/start` - Start workflow
- `GET /orders/{id}/status` - Get status
- `POST /orders/{id}/signals/approve` - Approve order
- `POST /orders/{id}/signals/cancel` - Cancel order
- `POST /orders/{id}/signals/update-address` - Update address

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── OrderForm.jsx          # Start new order form
│   │   ├── OrderTimeline.jsx      # Visual workflow progress
│   │   └── SignalButtons.jsx      # Action buttons
│   ├── pages/
│   │   ├── Home.jsx                # Landing page
│   │   ├── OrderDetail.jsx        # Order status page
│   │   └── Orders.jsx              # Orders list placeholder
│   ├── services/
│   │   └── api.js                  # API client
│   ├── App.jsx                     # Main app with routing
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Tailwind styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

---

Built with ❤️ using React + Vite
