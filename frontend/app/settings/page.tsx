"use client"

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-provider';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Save, Loader2, LogOut } from 'lucide-react';
import Link from 'next/link';
import * as api from '@/lib/api';

export default function SettingsPage() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const { toast } = useToast();
  
  // Profile state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  
  // Password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isPasswordLoading, setIsPasswordLoading] = useState(false);
  
  // Preferences state
  const [theme, setTheme] = useState('dark');
  const [defaultModel, setDefaultModel] = useState('anthropic');
  const [insightsEnabled, setInsightsEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [isPreferencesLoading, setIsPreferencesLoading] = useState(false);
  
  // Load user data on mount
  useEffect(() => {
    const loadUserProfile = async () => {
      if (!user) return;
      
      try {
        // Get user profile
        const profile = await api.getUserProfile();
        
        setName(profile.name || '');
        setEmail(profile.email || '');
        
        // Load preferences
        if (profile.preferences) {
          setTheme(profile.preferences.theme || 'dark');
          setDefaultModel(profile.preferences.default_model || 'anthropic');
          setInsightsEnabled(profile.preferences.insights_enabled !== false);
          setNotificationsEnabled(profile.preferences.notification_enabled !== false);
        }
      } catch (error) {
        console.error('Failed to load user profile:', error);
        toast({
          title: 'Error',
          description: 'Failed to load your profile information.',
          variant: 'destructive',
        });
      }
    };
    
    if (user) {
      loadUserProfile();
    }
  }, [user, toast]);
  
  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsProfileLoading(true);
    
    try {
      // Update profile
      await api.updateUserProfile({ name, email });
      
      toast({
        title: 'Profile Updated',
        description: 'Your profile information has been updated successfully.',
      });
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to update your profile. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsProfileLoading(false);
    }
  };
  
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      toast({
        title: 'Error',
        description: 'New passwords do not match.',
        variant: 'destructive',
      });
      return;
    }
    
    if (newPassword.length < 8) {
      toast({
        title: 'Error',
        description: 'New password must be at least 8 characters long.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsPasswordLoading(true);
    
    try {
      // Update password
      await api.updateUserProfile({ password: newPassword });
      
      // Clear form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      toast({
        title: 'Password Updated',
        description: 'Your password has been updated successfully.',
      });
    } catch (error) {
      console.error('Failed to update password:', error);
      toast({
        title: 'Error',
        description: 'Failed to update your password. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsPasswordLoading(false);
    }
  };
  
  const handlePreferencesUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsPreferencesLoading(true);
    
    try {
      // Update preferences
      await api.updateUserPreferences({
        theme,
        default_model: defaultModel,
        insights_enabled: insightsEnabled,
        notification_enabled: notificationsEnabled,
      });
      
      toast({
        title: 'Preferences Updated',
        description: 'Your preferences have been updated successfully.',
      });
    } catch (error) {
      console.error('Failed to update preferences:', error);
      toast({
        title: 'Error',
        description: 'Failed to update your preferences. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsPreferencesLoading(false);
    }
  };
  
  const handleLogout = () => {
    logout();
    toast({
      title: 'Logged Out',
      description: 'You have been logged out successfully.',
    });
  };
  
  if (authLoading) {
    return (
      <div className="container max-w-5xl mx-auto py-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container max-w-5xl mx-auto py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/chat">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Settings</h1>
        </div>
        <Button variant="destructive" onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </div>
      
      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>
        
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <form onSubmit={handleProfileUpdate}>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your basic profile information here.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  type="submit"
                  disabled={isProfileLoading}
                >
                  {isProfileLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
        
        <TabsContent value="password" className="space-y-4">
          <Card>
            <form onSubmit={handlePasswordUpdate}>
              <CardHeader>
                <CardTitle>Change Password</CardTitle>
                <CardDescription>
                  Update your password here. We recommend using a strong, unique password.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Current Password</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Password must be at least 8 characters.
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  type="submit"
                  disabled={isPasswordLoading}
                >
                  {isPasswordLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Update Password
                    </>
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
        
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <form onSubmit={handlePreferencesUpdate}>
              <CardHeader>
                <CardTitle>User Preferences</CardTitle>
                <CardDescription>
                  Customize your experience with DeepIntrospect AI.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Theme</Label>
                    <p className="text-sm text-muted-foreground">
                      Choose between light and dark theme.
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      type="button"
                      variant={theme === 'light' ? 'default' : 'outline'}
                      onClick={() => setTheme('light')}
                      className="w-20"
                    >
                      Light
                    </Button>
                    <Button
                      type="button"
                      variant={theme === 'dark' ? 'default' : 'outline'}
                      onClick={() => setTheme('dark')}
                      className="w-20"
                    >
                      Dark
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Default Model</Label>
                    <p className="text-sm text-muted-foreground">
                      Choose your preferred AI model.
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      type="button"
                      variant={defaultModel === 'anthropic' ? 'default' : 'outline'}
                      onClick={() => setDefaultModel('anthropic')}
                      className="w-28"
                    >
                      Anthropic
                    </Button>
                    <Button
                      type="button"
                      variant={defaultModel === 'openai' ? 'default' : 'outline'}
                      onClick={() => setDefaultModel('openai')}
                      className="w-28"
                    >
                      OpenAI
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="insights-toggle">Insights Generation</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow AI to generate insights from your conversations.
                    </p>
                  </div>
                  <Switch
                    id="insights-toggle"
                    checked={insightsEnabled}
                    onCheckedChange={setInsightsEnabled}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="notifications-toggle">Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive notifications for new insights and updates.
                    </p>
                  </div>
                  <Switch
                    id="notifications-toggle"
                    checked={notificationsEnabled}
                    onCheckedChange={setNotificationsEnabled}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  type="submit"
                  disabled={isPreferencesLoading}
                >
                  {isPreferencesLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Preferences
                    </>
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
