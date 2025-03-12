"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { createClientComponentClient } from "@supabase/supabase-js";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoonIcon, SunIcon, Menu, X, User, Settings, LogOut, BarChart, MessageSquare, BrainCircuit } from "lucide-react";
import { useTheme } from "next-themes";
import { NotificationCenter } from "@/components/notifications/notification-center";

export default function MainNav({ className }: { className?: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState(null);
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const supabase = createClientComponentClient();
  
  const routes = [
    {
      name: "Chat",
      path: "/chat",
      icon: <MessageSquare className="h-4 w-4 mr-2" />,
    },
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: <BarChart className="h-4 w-4 mr-2" />,
    },
    {
      name: "Insights",
      path: "/insights",
      icon: <BrainCircuit className="h-4 w-4 mr-2" />,
    },
  ];

  // Get user session on mount
  useEffect(() => {
    async function getUser() {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
    }
    
    getUser();
    
    // Subscribe to auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user || null);
      }
    );
    
    return () => {
      subscription.unsubscribe();
    };
  }, [supabase.auth]);

  // Handle sign out
  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  // Toggle theme
  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <div className="flex items-center justify-between w-full">
          {/* Logo and Desktop Nav */}
          <div className="hidden md:flex items-center gap-6 md:gap-10">
            <Link href="/" className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
              DeepIntrospect AI
            </Link>
            
            {user && (
              <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
                {routes.map((route) => (
                  <Link
                    key={route.path}
                    href={route.path}
                    className={cn(
                      "flex items-center transition-colors hover:text-foreground/80",
                      pathname === route.path
                        ? "text-foreground font-semibold"
                        : "text-foreground/60"
                    )}
                  >
                    {route.icon}
                    {route.name}
                  </Link>
                ))}
              </nav>
            )}
          </div>
          
          {/* Mobile Nav Toggle */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="icon"
              aria-label="Toggle Menu"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
          
          {/* User Menu and Theme Toggle */}
          <div className="hidden md:flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              aria-label="Toggle Theme"
              onClick={toggleTheme}
            >
              {theme === "dark" ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </Button>
            
            {user && <NotificationCenter />}
            
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-8 w-8 rounded-full"
                    aria-label="User Menu"
                  >
                    <User className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleSignOut}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center gap-2">
                <Button asChild variant="ghost">
                  <Link href="/login">Log in</Link>
                </Button>
                <Button asChild>
                  <Link href="/signup">Sign up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 top-16 z-50 bg-background">
          <div className="container grid gap-6 px-4 py-6">
            {user ? (
              <>
                <nav className="flex flex-col gap-4">
                  {routes.map((route) => (
                    <Link
                      key={route.path}
                      href={route.path}
                      onClick={() => setIsOpen(false)}
                      className={cn(
                        "flex items-center text-base py-2",
                        pathname === route.path
                          ? "text-foreground font-semibold"
                          : "text-foreground/60"
                      )}
                    >
                      {route.icon}
                      {route.name}
                    </Link>
                  ))}
                </nav>
                
                <div className="flex flex-col gap-4 pt-4 border-t">
                  <Link
                    href="/settings"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center text-base py-2 text-foreground/60"
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </Link>
                  
                  <div className="flex items-center justify-between">
                    <button
                      onClick={toggleTheme}
                      className="flex items-center text-base py-2 text-foreground/60"
                    >
                      {theme === "dark" ? (
                        <><SunIcon className="h-4 w-4 mr-2" /> Light Mode</>
                      ) : (
                        <><MoonIcon className="h-4 w-4 mr-2" /> Dark Mode</>
                      )}
                    </button>
                  </div>
                  
                  <button
                    onClick={handleSignOut}
                    className="flex items-center text-base py-2 text-foreground/60"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Log out
                  </button>
                </div>
              </>
            ) : (
              <div className="flex flex-col gap-2">
                <Button asChild size="lg" className="w-full">
                  <Link href="/login" onClick={() => setIsOpen(false)}>
                    Log in
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="w-full">
                  <Link href="/signup" onClick={() => setIsOpen(false)}>
                    Sign up
                  </Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
