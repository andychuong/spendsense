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

## Features Implemented

### Task 10.1: Frontend Project Setup ✅

- ✅ React 18.2.0 with TypeScript 5.3.3
- ✅ Vite 5.0.11 build tool configured
- ✅ React Router 6.21.1 with all routes configured
- ✅ Zustand for client state management (auth store)
- ✅ React Query for server state management
- ✅ Axios configured with request/response interceptors
- ✅ Token refresh mechanism
- ✅ Protected routes and operator routes
- ✅ Project structure with all directories
- ✅ Environment variables configured

### Task 10.2: Authentication UI ✅

- ✅ Login page with email/password and phone/SMS
- ✅ Registration page with email/password and phone/SMS
- ✅ Phone verification component with countdown timer
- ✅ OAuth buttons (Google, GitHub, Facebook, Apple) with proper icons
- ✅ Form validation (email, password, phone)
- ✅ Error handling and loading states
- ✅ Tailwind CSS styling (modern, responsive design)
- ✅ React Icons for OAuth provider icons

### Routes Configured

- **Public Routes**: `/login`, `/register`
- **Protected Routes**: `/`, `/profile`, `/recommendations`, `/recommendations/:id`, `/settings`, `/upload`
- **Operator Routes**: `/operator`, `/operator/review/:id`, `/operator/analytics`

### API Integration

- Axios instance configured with base URL from environment variables
- Request interceptor adds JWT token to Authorization header
- Response interceptor handles 401 errors and token refresh
- Automatic token refresh on expiration
- Token storage in localStorage

### State Management

- **Auth Store** (Zustand): User authentication state, tokens, login/logout
- **React Query**: Server state caching, background refetching, optimistic updates

## Development Tasks

See [PROJECT-PLAN.md](../docs/PROJECT-PLAN.md) for detailed task breakdown.

- ✅ **Task 10.1**: Frontend Project Setup
- ✅ **Task 10.2**: Authentication UI
- **Task 10.3**: Token Management (completed in 10.1)
- **Task 10.4**: Account Linking UI
- **Task 11.1**: Dashboard Page
- **Task 11.2**: Profile View
- And more...


