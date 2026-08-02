# CustomerIQ React Frontend

Production-grade Vite + React dashboard for the CustomerIQ FastAPI platform.

## Folder Structure

```text
frontend/
  index.html
  package.json
  vite.config.js
  tailwind.config.js
  postcss.config.js
  nginx.react.conf
  .env.example
  src/
    App.jsx
    main.jsx
    styles/
      index.css
    services/
      api.js
    hooks/
      useDashboardData.js
      useGsapCounter.js
      usePageIntro.js
    data/
      mockData.js
    components/
      charts/
      common/
      dashboard/
      layout/
      predict/
      three/
      ui/
    pages/
      HeroPage.jsx
      DashboardPage.jsx
      PredictPage.jsx
      SegmentsPage.jsx
      IntelligencePage.jsx
```

## Local Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

The app runs at `http://localhost:5173`. FastAPI should run at `http://localhost:8000`.

Use these frontend environment variables:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEMO_AUTH_TOKEN=dummy-token
VITE_ENABLE_DEMO_FALLBACK=true
```

For containerized deploys behind the root Nginx reverse proxy, build with:

```env
VITE_API_BASE_URL=/api/v1
VITE_ENABLE_DEMO_FALLBACK=false
```

## Stack

- React 18 + Vite
- Tailwind CSS dark command-center theme
- React Router v6
- Axios centralized API client with interceptors
- Three.js via react-three-fiber and drei
- GSAP with ScrollTrigger counters and route reveals
- Recharts for dense 2D analytics panels

## Docker Compose Service

The root `docker-compose.yml` now builds `Dockerfile.frontend`, exposes the static Nginx frontend on the internal Docker network, and the root `nginx.conf` proxies `/` to `frontend:80` plus `/api/` to FastAPI.
