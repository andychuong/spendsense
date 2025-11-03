# SpendSense Frontend

React frontend application for the SpendSense platform.

## Technology Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.11
- **Routing**: React Router 6.21.1
- **State Management**: Zustand or Redux
- **HTTP Client**: Axios 1.6.5
- **Data Fetching**: React Query 5.17.0

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── store/               # State management (Zustand/Redux)
│   ├── services/            # API services
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript types
│   ├── styles/              # Global styles
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── vite-env.d.ts        # Vite types
├── public/                  # Static assets
├── tests/                   # Test suite
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```

## Development Tasks

See [PROJECT-PLAN.md](../docs/PROJECT-PLAN.md) for detailed task breakdown.

- **Task 10.1**: Frontend Project Setup
- **Task 10.2**: Authentication UI
- **Task 11.1**: Dashboard Page
- **Task 11.2**: Profile View
- And more...


