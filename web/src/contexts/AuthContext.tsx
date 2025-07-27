import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { apiClient } from '../api/client';

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is logged in by calling /me endpoint
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const { data, error } = await apiClient.GET('/auth/me');
      if (data && !error) {
        // TODO: Update when backend returns user data
        // For now, the backend returns "Not implemented yet"
        // setUser({ email: data.email });
      }
    } catch (err) {
      // User is not authenticated
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      const { data, error: apiError } = await apiClient.POST('/auth/login', {
        body: { email, password },
      });

      if (apiError) {
        throw new Error(apiError.detail?.[0]?.msg || 'Login failed');
      }

      if (data) {
        // Cookie is set by backend, just update user state
        const responseData = data as { email: string; message: string };
        setUser({ email: responseData.email });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      const { data, error: apiError } = await apiClient.POST('/auth/register', {
        body: { email, password },
      });

      if (apiError) {
        throw new Error(apiError.detail?.[0]?.msg || 'Registration failed');
      }

      if (data) {
        // After successful registration, log the user in
        await login(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.POST('/auth/logout');
      setUser(null);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        isLoading,
        error,
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