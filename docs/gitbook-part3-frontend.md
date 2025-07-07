# Part 3: Creating the Frontend

In this section, we'll build the React-based frontend for our SolanaAI Agent platform. This will provide users with an intuitive interface to interact with the agent, view transaction history, and manage their settings.

## Setting Up React Application

Our React application is already initialized. Let's configure it for our needs:

### 1. Configure Tailwind CSS

First, let's configure Tailwind CSS for styling our application:

```bash
cd frontend
```

Edit the `tailwind.config.js` file:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        'solana-green': '#14F195',
        'solana-purple': '#9945FF',
        'dark-blue': '#0A1128',
        'medium-blue': '#1C2F4F',
        'light-blue': '#2E4272',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      boxShadow: {
        'neon': '0 0 5px theme("colors.solana-purple"), 0 0 20px theme("colors.solana-purple")',
        'neon-green': '0 0 5px theme("colors.solana-green"), 0 0 20px theme("colors.solana-green")',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
```

### 2. Update App.css

Edit the `src/App.css` file:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-50 text-gray-900 dark:bg-dark-blue dark:text-white;
}

.container {
  @apply mx-auto px-4 max-w-7xl;
}

.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors duration-200;
}

.btn-primary {
  @apply bg-solana-purple text-white hover:bg-opacity-90;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-light-blue dark:text-white dark:hover:bg-opacity-90;
}

.btn-danger {
  @apply bg-red-500 text-white hover:bg-red-600;
}

.input {
  @apply px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-solana-purple focus:border-transparent dark:bg-medium-blue dark:border-light-blue;
}

.card {
  @apply bg-white p-6 rounded-lg shadow-md dark:bg-medium-blue;
}
```

### 3. Update index.html

Edit the `public/index.html` file to add fonts and icons:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="SolanaAI Agent Platform - Intelligent blockchain automation"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>SolanaAI Agent Platform</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

## Setting Up Project Structure

Now, let's set up our project structure:

### 1. Setting Up API Client

Create an API client for communication with our backend:

```bash
mkdir -p src/api
touch src/api/client.ts
touch src/api/auth.ts
touch src/api/agent.ts
touch src/api/browser.ts
```

Edit `src/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

class ApiClient {
  private client: AxiosInstance;
  private static instance: ApiClient;

  private constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add a request interceptor to add the auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add a response interceptor to handle common errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle 401 errors (unauthorized)
        if (error.response && error.response.status === 401) {
          // Clear token if it's invalid
          localStorage.removeItem('token');
          // Redirect to login page if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  public get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  public post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  public put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  public delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }
}

export default ApiClient.getInstance();
```

Edit `src/api/auth.ts`:

```typescript
import apiClient from './client';

export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    access_token: string;
    token_type: string;
    user: {
      id: string;
      email: string;
      username: string;
    };
  };
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  wallets: any[];
  profile: any;
  preferences: any;
  is_active: boolean;
  is_verified: boolean;
}

export interface ProfileResponse {
  success: boolean;
  message: string;
  data?: UserProfile;
}

// Register a new user
export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
  return response.data;
};

// Login a user
export const login = async (data: LoginData): Promise<AuthResponse> => {
  // Note: FastAPI expects form data for OAuth2 login
  const formData = new FormData();
  formData.append('username', data.email);
  formData.append('password', data.password);

  const response = await apiClient.post<AuthResponse>(
    '/api/auth/login',
    formData,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );

  // Store token if login is successful
  if (response.data.success && response.data.data?.access_token) {
    localStorage.setItem('token', response.data.data.access_token);
  }

  return response.data;
};

// Logout user
export const logout = async (): Promise<AuthResponse> => {
  try {
    const response = await apiClient.post<AuthResponse>('/api/auth/logout');
    localStorage.removeItem('token');
    return response.data;
  } catch (error) {
    // Clear token even if API call fails
    localStorage.removeItem('token');
    throw error;
  }
};

// Get user profile
export const getProfile = async (): Promise<ProfileResponse> => {
  const response = await apiClient.get<ProfileResponse>('/api/auth/me');
  return response.data;
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};
```

Edit `src/api/agent.ts`:

```typescript
import apiClient from './client';

export interface RunAgentRequest {
  prompt: string;
  model?: string;
}

export interface AgentRunResponse {
  success: boolean;
  message: string;
  data?: {
    run_id: string;
  };
}

export interface AgentRun {
  _id: string;
  user_id: string;
  prompt: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  steps: Array<{
    step_number: number;
    step_type: string;
    content: string;
    timestamp: string;
    observations?: string;
    observation_images?: string[];
  }>;
  result?: string;
  error?: string;
  model: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  payment_info?: any;
}

export interface GetAgentRunResponse {
  success: boolean;
  message: string;
  data?: AgentRun;
}

export interface GetAgentRunsResponse {
  success: boolean;
  message: string;
  data?: {
    runs: AgentRun[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      pages: number;
    };
  };
}

// Run the agent with a prompt
export const runAgent = async (request: RunAgentRequest): Promise<AgentRunResponse> => {
  const response = await apiClient.post<AgentRunResponse>('/api/agent/run', request);
  return response.data;
};

// Get an agent run by ID
export const getAgentRun = async (runId: string): Promise<GetAgentRunResponse> => {
  const response = await apiClient.get<GetAgentRunResponse>(`/api/agent/run/${runId}`);
  return response.data;
};

// Get all agent runs
export const getAgentRuns = async (
  page: number = 1,
  limit: number = 10,
  status?: string
): Promise<GetAgentRunsResponse> => {
  let url = `/api/agent/runs?page=${page}&limit=${limit}`;
  if (status) {
    url += `&status=${status}`;
  }
  
  const response = await apiClient.get<GetAgentRunsResponse>(url);
  return response.data;
};

// Cancel an agent run
export const cancelAgentRun = async (runId: string): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(`/api/agent/run/${runId}`);
  return response.data;
};
```

Edit `src/api/browser.ts`:

```typescript
import apiClient from './client';

export interface RunBrowserRequest {
  instructions: string;
  url?: string;
  developer_mode?: boolean;
}

export interface BrowserTaskResponse {
  success: boolean;
  message: string;
  data?: {
    task_id: string;
  };
}

export interface BrowserTask {
  _id: string;
  user_id: string;
  instructions: string;
  url?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  result?: string;
  error?: string;
  screenshots: string[];
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  developer_mode: boolean;
}

export interface GetBrowserTaskResponse {
  success: boolean;
  message: string;
  data?: BrowserTask;
}

export interface GetBrowserTasksResponse {
  success: boolean;
  message: string;
  data?: {
    tasks: BrowserTask[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      pages: number;
    };
  };
}

// Run browser automation
export const runBrowser = async (request: RunBrowserRequest): Promise<BrowserTaskResponse> => {
  const response = await apiClient.post<BrowserTaskResponse>('/api/browser/automate', request);
  return response.data;
};

// Get a browser task by ID
export const getBrowserTask = async (taskId: string): Promise<GetBrowserTaskResponse> => {
  const response = await apiClient.get<GetBrowserTaskResponse>(`/api/browser/task/${taskId}`);
  return response.data;
};

// Get all browser tasks
export const getBrowserTasks = async (
  page: number = 1,
  limit: number = 10,
  status?: string
): Promise<GetBrowserTasksResponse> => {
  let url = `/api/browser/tasks?page=${page}&limit=${limit}`;
  if (status) {
    url += `&status=${status}`;
  }
  
  const response = await apiClient.get<GetBrowserTasksResponse>(url);
  return response.data;
};

// Cancel a browser task
export const cancelBrowserTask = async (taskId: string): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(`/api/browser/task/${taskId}`);
  return response.data;
};
```

### 2. Setting Up Authentication Context

Create an authentication context to manage user state:

```bash
mkdir -p src/context
touch src/context/AuthContext.tsx
```

Edit `src/context/AuthContext.tsx`:

```typescript
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getProfile, isAuthenticated, login, logout, register, LoginData, RegisterData, UserProfile } from '../api/auth';

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  isLoggedIn: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(isAuthenticated());

  useEffect(() => {
    // Load user profile if authenticated
    const loadUser = async () => {
      if (isAuthenticated()) {
        try {
          const response = await getProfile();
          if (response.success && response.data) {
            setUser(response.data);
            setIsLoggedIn(true);
          } else {
            setUser(null);
            setIsLoggedIn(false);
            localStorage.removeItem('token');
          }
        } catch (error) {
          setUser(null);
          setIsLoggedIn(false);
          localStorage.removeItem('token');
        }
      } else {
        setUser(null);
        setIsLoggedIn(false);
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  const handleLogin = async (data: LoginData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await login(data);
      if (response.success && response.data) {
        // Load user profile after login
        const profileResponse = await getProfile();
        if (profileResponse.success && profileResponse.data) {
          setUser(profileResponse.data);
          setIsLoggedIn(true);
        }
      } else {
        setError(response.message || 'Login failed');
        setIsLoggedIn(false);
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed');
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: RegisterData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await register(data);
      if (response.success) {
        // Automatically login after successful registration
        await handleLogin({ email: data.email, password: data.password });
      } else {
        setError(response.message || 'Registration failed');
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      setUser(null);
      setIsLoggedIn(false);
    } catch (error) {
      // Even if API logout fails, clear local state
      setUser(null);
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isLoggedIn,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 3. Setting Up Solana Wallet Integration

Create a wallet integration module:

```bash
mkdir -p src/wallet
touch src/wallet/SolanaWalletProvider.tsx
```

Edit `src/wallet/SolanaWalletProvider.tsx`:

```typescript
import React, { FC, ReactNode, useMemo } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import {
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  TorusWalletAdapter,
  LedgerWalletAdapter,
  SlopeWalletAdapter,
} from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';

// Import the styles
import '@solana/wallet-adapter-react-ui/styles.css';

interface SolanaWalletProviderProps {
  children: ReactNode;
}

export const SolanaWalletProvider: FC<SolanaWalletProviderProps> = ({ children }) => {
  // The network can be set to 'devnet', 'testnet', or 'mainnet-beta'
  const network = (
    process.env.REACT_APP_SOLANA_NETWORK as WalletAdapterNetwork || WalletAdapterNetwork.Devnet
  );

  // Custom RPC endpoint if provided, otherwise use Solana's public endpoint
  const endpoint = useMemo(
    () => process.env.REACT_APP_SOLANA_RPC_URL || clusterApiUrl(network),
    [network]
  );

  // Initialize wallets
  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
      new SolflareWalletAdapter(),
      new TorusWalletAdapter(),
      new LedgerWalletAdapter(),
      new SlopeWalletAdapter(),
    ],
    []
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>{children}</WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
};
```

### 4. Creating Components

Now, let's create the main components for our application:

```bash
mkdir -p src/components/{common,auth,agent,browser,layout}
```

Create the layout components:

```bash
touch src/components/layout/Navbar.tsx
touch src/components/layout/Footer.tsx
touch src/components/layout/Sidebar.tsx
touch src/components/layout/Layout.tsx
```

Edit `src/components/layout/Navbar.tsx`:

```tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
  const { isLoggedIn, user, logout } = useAuth();
  const navigate = useNavigate();
  const { connected } = useWallet();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md dark:bg-dark-blue">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold bg-gradient-to-r from-solana-purple to-solana-green text-transparent bg-clip-text">
              SolanaAI
            </span>
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          {isLoggedIn ? (
            <>
              <WalletMultiButton className="!bg-solana-purple hover:!bg-opacity-90" />
              
              <div className="relative group">
                <button className="flex items-center space-x-2 focus:outline-none">
                  <div className="w-8 h-8 rounded-full bg-solana-purple flex items-center justify-center text-white">
                    {user?.username?.charAt(0).toUpperCase()}
                  </div>
                </button>
                
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 hidden group-hover:block dark:bg-medium-blue">
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-white dark:hover:bg-light-blue"
                  >
                    Profile
                  </Link>
                  <Link
                    to="/settings"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-white dark:hover:bg-light-blue"
                  >
                    Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-white dark:hover:bg-light-blue"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex space-x-2">
              <Link to="/login" className="btn btn-secondary">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
```

Edit `src/components/layout/Footer.tsx`:

```tsx
import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white py-6 dark:bg-dark-blue">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <span className="text-xl font-bold bg-gradient-to-r from-solana-purple to-solana-green text-transparent bg-clip-text">
              SolanaAI
            </span>
            <p className="text-sm text-gray-600 mt-1 dark:text-gray-400">
              Intelligent blockchain automation
            </p>
          </div>
          
          <div className="flex flex-wrap justify-center space-x-4">
            <Link
              to="/about"
              className="text-gray-600 hover:text-solana-purple dark:text-gray-400 dark:hover:text-solana-green"
            >
              About
            </Link>
            <Link
              to="/privacy"
              className="text-gray-600 hover:text-solana-purple dark:text-gray-400 dark:hover:text-solana-green"
            >
              Privacy
            </Link>
            <Link
              to="/terms"
              className="text-gray-600 hover:text-solana-purple dark:text-gray-400 dark:hover:text-solana-green"
            >
              Terms
            </Link>
            <a
              href="https://github.com/yourusername/solana-ai-agent-platform"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-solana-purple dark:text-gray-400 dark:hover:text-solana-green"
            >
              GitHub
            </a>
          </div>
        </div>
        
        <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          &copy; {new Date().getFullYear()} SolanaAI Agent Platform. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
```

Edit `src/components/layout/Sidebar.tsx`:

```tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  HomeIcon, 
  CommandLineIcon, 
  GlobeAltIcon,
  CurrencyDollarIcon, 
  PhotoIcon, 
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
    { name: 'AI Agent', path: '/agent', icon: CommandLineIcon },
    { name: 'Browser', path: '/browser', icon: GlobeAltIcon },
    { name: 'Blockchain', path: '/blockchain', icon: CurrencyDollarIcon },
    { name: 'NFT Creator', path: '/nft', icon: PhotoIcon },
    { name: 'Settings', path: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <aside className="w-64 h-screen fixed left-0 bg-white shadow-md dark:bg-medium-blue">
      <div className="h-full flex flex-col py-4">
        <div className="px-4 py-2 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            Navigation
          </h2>
        </div>
        
        <nav className="flex-1 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-solana-purple bg-opacity-10 text-solana-purple'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-light-blue'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        
        <div className="px-4 py-4 mt-auto">
          <div className="p-4 bg-gray-100 rounded-lg dark:bg-light-blue">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
              Need Help?
            </h3>
            <p className="mt-1 text-xs text-gray-700 dark:text-gray-300">
              Check our documentation or contact support.
            </p>
            <a
              href="https://docs.example.com"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 text-xs text-solana-purple hover:text-opacity-80 flex items-center"
            >
              View Documentation
              <svg
                className="ml-1 w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
```

Edit `src/components/layout/Layout.tsx`:

```tsx
import React, { ReactNode } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useAuth } from '../../context/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isLoggedIn } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <div className="flex flex-1">
        {isLoggedIn && <Sidebar />}
        
        <main className={`flex-1 ${isLoggedIn ? 'ml-64' : ''}`}>
          <div className="container mx-auto px-4 py-6">
            {children}
          </div>
        </main>
      </div>
      
      <Footer />
    </div>
  );
};

export default Layout;
```

### 5. Creating Pages

Now, let's create the pages for our application:

```bash
mkdir -p src/pages/{auth,dashboard,agent,browser,blockchain,nft,settings}
touch src/pages/auth/Login.tsx
touch src/pages/auth/Register.tsx
touch src/pages/dashboard/Dashboard.tsx
touch src/pages/agent/AgentChat.tsx
touch src/pages/agent/AgentHistory.tsx
touch src/pages/browser/BrowserAutomation.tsx
touch src/pages/browser/BrowserHistory.tsx
touch src/pages/Home.tsx
touch src/pages/NotFound.tsx
```

Edit `src/pages/Home.tsx`:

```tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const { isLoggedIn } = useAuth();

  return (
    <div className="bg-gray-50 dark:bg-dark-blue min-h-screen">
      <div className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            <span className="bg-gradient-to-r from-solana-purple to-solana-green text-transparent bg-clip-text">
              SolanaAI Agent Platform
            </span>
          </h1>
          <p className="text-xl text-gray-700 dark:text-gray-300 mb-10 max-w-2xl mx-auto">
            An intelligent agent for Solana blockchain development, token trading, and NFT creation
            using SmolAgents and Metaplex.
          </p>
          <div className="flex justify-center space-x-4">
            {isLoggedIn ? (
              <Link to="/dashboard" className="btn btn-primary py-3 px-8 text-lg">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary py-3 px-8 text-lg">
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-secondary py-3 px-8 text-lg">
                  Log In
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card p-8 border-t-4 border-solana-purple">
            <div className="w-12 h-12 bg-solana-purple bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-solana-purple"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">AI-Powered Research</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Automatically research Solana projects, analyze market trends, and extract valuable information
              from web sources.
            </p>
          </div>

          <div className="card p-8 border-t-4 border-solana-green">
            <div className="w-12 h-12 bg-solana-green bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-solana-green"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">Blockchain Integration</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Execute transactions, interact with smart contracts, and manage assets on the Solana blockchain
              with AI assistance.
            </p>
          </div>

          <div className="card p-8 border-t-4 border-blue-500">
            <div className="w-12 h-12 bg-blue-500 bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">NFT Creation</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Generate and mint NFTs on Solana with AI-powered image generation and metadata creation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
```

Edit `src/pages/NotFound.tsx`:

```tsx
import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-dark-blue px-4">
      <h1 className="text-6xl font-bold text-solana-purple mb-4">404</h1>
      <p className="text-2xl text-gray-700 dark:text-gray-300 mb-8">Page not found</p>
      <p className="text-gray-600 dark:text-gray-400 mb-8 text-center max-w-md">
        The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
      </p>
      <Link to="/" className="btn btn-primary">
        Go to Home
      </Link>
    </div>
  );
};

export default NotFound;
```

### 6. Creating Routes

Create the router configuration:

```bash
touch src/routes/index.tsx
```

Edit `src/routes/index.tsx`:

```tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/layout/Layout';

// Auth Pages
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';

// Main Pages
import Home from '../pages/Home';
import Dashboard from '../pages/dashboard/Dashboard';
import AgentChat from '../pages/agent/AgentChat';
import AgentHistory from '../pages/agent/AgentHistory';
import BrowserAutomation from '../pages/browser/BrowserAutomation';
import BrowserHistory from '../pages/browser/BrowserHistory';
import NotFound from '../pages/NotFound';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

// Public Route Component (redirects to dashboard if already logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (isLoggedIn) {
    return <Navigate to="/dashboard" />;
  }

  return <>{children}</>;
};

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/agent"
            element={
              <ProtectedRoute>
                <AgentChat />
              </ProtectedRoute>
            }
          />
          <Route
            path="/agent/history"
            element={
              <ProtectedRoute>
                <AgentHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/browser"
            element={
              <ProtectedRoute>
                <BrowserAutomation />
              </ProtectedRoute>
            }
          />
          <Route
            path="/browser/history"
            element={
              <ProtectedRoute>
                <BrowserHistory />
              </ProtectedRoute>
            }
          />

          {/* Not Found Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default AppRouter;
```

### 7. Update App.tsx

Edit `src/App.tsx`:

```tsx
import React from 'react';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import { SolanaWalletProvider } from './wallet/SolanaWalletProvider';
import AppRouter from './routes';

function App() {
  return (
    <AuthProvider>
      <SolanaWalletProvider>
        <AppRouter />
      </SolanaWalletProvider>
    </AuthProvider>
  );
}

export default App;
```

### 8. Run the Application

Now, let's run our application:

```bash
npm start
```

Your frontend application should now be running on [http://localhost:3000](http://localhost:3000).

## Next Steps

Now that we have set up the basic structure of our frontend application, in the next sections we'll implement the specific functionality for each page, including:

1. Authentication pages (Login/Register)
2. Dashboard page
3. Agent interaction interface
4. Browser automation interface
5. Blockchain operations interface
6. NFT creation interface
7. Settings page

This will give us a complete frontend application that can communicate with our backend server and provide users with a seamless experience for interacting with our SolanaAI Agent platform.
