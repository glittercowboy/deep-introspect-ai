"use client"

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { SparklesCore } from '@/components/ui/aceternity/sparkles';

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast({
        title: "Error",
        description: "Please enter your email address.",
        variant: "destructive",
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      // This would typically call an API to send a password reset email
      // For now, we'll just simulate a successful response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSubmitted(true);
      toast({
        title: "Email Sent",
        description: "If an account exists with this email, you will receive a password reset link.",
      });
    } catch (error) {
      console.error('Password reset error:', error);
      toast({
        title: "Error",
        description: "Failed to send password reset email. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 relative">
      <div className="absolute inset-0 w-full h-full">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={30}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>
      
      <Card className="w-full max-w-md z-10 backdrop-blur-sm bg-background/80">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-3xl font-bold">Reset Password</CardTitle>
          <CardDescription>
            Enter your email to receive a password reset link
          </CardDescription>
        </CardHeader>
        
        {!submitted ? (
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            </CardContent>
            
            <CardFooter className="flex flex-col gap-4">
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading ? "Sending..." : "Send Reset Link"}
              </Button>
              
              <div className="text-center text-sm">
                Remember your password?{" "}
                <Link href="/auth/login" className="text-primary hover:underline">
                  Back to login
                </Link>
              </div>
            </CardFooter>
          </form>
        ) : (
          <CardContent className="space-y-4">
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-md text-center">
              <h3 className="font-medium text-green-800 dark:text-green-300 mb-2">
                Check your email
              </h3>
              <p className="text-green-700 dark:text-green-400 text-sm">
                We've sent a password reset link to <strong>{email}</strong>.
                Please check your inbox and follow the instructions.
              </p>
            </div>
            
            <div className="text-center mt-4">
              <Button 
                asChild
                variant="outline" 
                className="mx-auto"
              >
                <Link href="/auth/login">
                  Back to Login
                </Link>
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
}
