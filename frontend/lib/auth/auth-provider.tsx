"use client"

import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ui/use-toast';
import * as api from '@/lib/api';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (typeof localStorage !== 'undefined') {
          const token = localStorage.getItem('token');
          
          if (token) {
            // Verify the token and get user data
            const userData = await api.getCurrentUser();
            setUser(userData);
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        // Clear invalid token
        localStorage.removeItem('token');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    
    try {
      const authData = await api.login(email, password);
      
      // Token is saved in the API function
      
      // Get user data
      const userData = await api.getCurrentUser();
      setUser(userData);
      
      toast({
        title: "Login Successful",
        description: "Welcome back!",
      });
      
      // Redirect to chat page
      router.push('/chat');
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: "Login Failed",
        description: error instanceof Error ? error.message : "Invalid credentials",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    setIsLoading(true);
    
    try {
      await api.register(email, password, name);
      
      toast({
        title: "Registration Successful",
        description: "Your account has been created. Please log in.",
      });
      
      // Redirect to login page
      router.push('/auth/login');
    } catch (error) {
      console.error('Registration error:', error);
      toast({
        title: "Registration Failed",
        description: error instanceof Error ? error.message : "Failed to create account",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out.",
    });
    router.push('/');
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
