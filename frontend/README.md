# SpendSense Frontend

React frontend application for the SpendSense platform.

## Technology Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.11
- **Routing**: React Router 6.21.1
- **State Management**:
  - Zustand 4.4.7 (client state)
  - React Query 5.17.0 (server state)
- **HTTP Client**: Axios 1.6.5
- **Styling**: Tailwind CSS 4.0+ with @tailwindcss/postcss
- **Icons**: React Icons 5.0+

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/               # Route page components
│   ├── hooks/               # Custom React hooks
│   ├── store/               # Zustand state stores
│   │   ├── authStore.ts     # Authentication state
│   │   └── index.ts
│   ├── services/            # API client services
│   │   ├── api.ts           # Axios instance with interceptors
│   │   └── index.ts
│   ├── utils/               # Utility functions
│   │   ├── queryClient.ts   # React Query client config
│   │   └── index.ts
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── styles/              # Global styles
│   │   └── index.css
│   ├── assets/              # Images, fonts, etc.
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # Entry point
│   └── vite-env.d.ts        # Vite environment types
├── public/                  # Static assets
├── tests/                   # Test suite
├── index.html               # HTML entry point
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .eslintrc.cjs
├── .env.local               # Environment variables (gitignored)
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   # Create .env.local file (already created with defaults)
   # Edit .env.local with your configuration:
   VITE_API_BASE_URL=http://localhost:8000
   VITE_ENV=development
   ```

3. Run development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

4. Build for production:
   ```bash
   npm run build
   ```

5. Preview production build:
   ```bash
   npm run preview
   ```

## Available Scripts

In the project directory, you can run:


