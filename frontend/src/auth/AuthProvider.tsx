import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/types';
import authService from './authService';
export interface AuthContextType {
  user: User | null;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({
  children
}) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // 初始化认证状态
    const storedUser = authService.getUser();
    const token = authService.getToken();

    if (storedUser && token) {
      setUser(storedUser);
    }
  }, []);

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const hasPermission = (permission: string) => {
    return authService.hasPermission(permission);
  };

  return (
    <AuthContext.Provider value={{ user, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};
