'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, Organization, TokenResponse, UserRole } from '@/types/auth';
import { ApiClient } from '@/lib/api-client';

interface AuthContextType {
  user: User | null;
  organization: Organization | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  demoLogin: (role: UserRole) => Promise<void>;
  switchRole: (role: UserRole) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check localStorage for existing session
    const savedToken = localStorage.getItem('supportswarm_token');
    const savedUser = localStorage.getItem('supportswarm_user');
    const savedOrg = localStorage.getItem('supportswarm_org');

    if (savedToken && savedUser && savedOrg) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setOrganization(JSON.parse(savedOrg));
    }
    setIsLoading(false);
  }, []);

  const handleAuthSuccess = (data: TokenResponse) => {
    setToken(data.access_token);
    setUser(data.user);
    setOrganization(data.organization);
    localStorage.setItem('supportswarm_token', data.access_token);
    localStorage.setItem('supportswarm_user', JSON.stringify(data.user));
    localStorage.setItem('supportswarm_org', JSON.stringify(data.organization));
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await ApiClient.post<TokenResponse>('/auth/login', { email, password });
      handleAuthSuccess(data);
    } finally {
      setIsLoading(false);
    }
  };

  const demoLogin = async (role: UserRole) => {
    setIsLoading(true);
    try {
      const data = await ApiClient.post<TokenResponse>('/auth/demo-login', {
        role,
        organization_slug: 'demo-fintech',
      });
      handleAuthSuccess(data);
    } finally {
      setIsLoading(false);
    }
  };

  const switchRole = async (role: UserRole) => {
    await demoLogin(role);
  };

  const logout = () => {
    setUser(null);
    setOrganization(null);
    setToken(null);
    localStorage.removeItem('supportswarm_token');
    localStorage.removeItem('supportswarm_user');
    localStorage.removeItem('supportswarm_org');
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        organization,
        token,
        isLoading,
        login,
        demoLogin,
        switchRole,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
