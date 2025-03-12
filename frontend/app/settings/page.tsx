"use client";

import { useState, useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import { createClientComponentClient } from "@supabase/supabase-js";

import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import { useTheme } from "next-themes";
import MainNav from "@/components/layout/main-nav";

// Define form schemas
const profileFormSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  email: z.string().email({
    message: "Please enter a valid email address.",
  }),
});

const passwordFormSchema = z.object({
  currentPassword: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
  newPassword: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
  confirmPassword: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

const appearanceFormSchema = z.object({
  theme: z.enum(["light", "dark", "system"]),
  animationsEnabled: z.boolean(),
});

const aiSettingsFormSchema = z.object({
  defaultModel: z.enum(["openai", "anthropic"]),
  memoryEnabled: z.boolean(),
  insightsEnabled: z.boolean(),
});

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  const router = useRouter();
  const supabase = createClientComponentClient();
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);

  // Profile form
  const profileForm = useForm<z.infer<typeof profileFormSchema>>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      name: "",
      email: "",
    },
  });

  // Password form
  const passwordForm = useForm<z.infer<typeof passwordFormSchema>>({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  });

  // Appearance form
  const appearanceForm = useForm<z.infer<typeof appearanceFormSchema>>({
    resolver: zodResolver(appearanceFormSchema),
    defaultValues: {
      theme: "dark",
      animationsEnabled: true,
    },
  });

  // AI Settings form
  const aiSettingsForm = useForm<z.infer<typeof aiSettingsFormSchema>>({
    resolver: zodResolver(aiSettingsFormSchema),
    defaultValues: {
      defaultModel: "anthropic",
      memoryEnabled: true,
      insightsEnabled: true,
    },
  });

  // Fetch user data
  useEffect(() => {
    async function getUserData() {
      try {
        setIsLoading(true);
        
        // Get user session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError || !session) {
          router.push("/login");
          return;
        }
        
        // Get user profile
        const { data, error } = await supabase
          .from("users")
          .select("*")
          .eq("id", session.user.id)
          .single();
          
        if (error) throw error;
        
        setUserData(data);
        
        // Update form values
        profileForm.reset({
          name: data.name || "",
          email: data.email || session.user.email,
        });
        
        // Update appearance form
        appearanceForm.reset({
          theme: data.preferences?.theme || "dark",
          animationsEnabled: data.preferences?.animationsEnabled !== false,
        });
        
        // Update AI settings form
        aiSettingsForm.reset({
          defaultModel: data.preferences?.defaultModel || "anthropic",
          memoryEnabled: data.preferences?.memoryEnabled !== false,
          insightsEnabled: data.preferences?.insightsEnabled !== false,
        });
        
      } catch (error) {
        console.error("Error fetching user data:", error);
        toast({
          title: "Error",
          description: "Failed to load user data. Please try again.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    }
    
    getUserData();
  }, [supabase, toast, router, profileForm, appearanceForm, aiSettingsForm]);

  // Handle profile form submission
  async function onProfileSubmit(values: z.infer<typeof profileFormSchema>) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        router.push("/login");
        return;
      }
      
      // Update auth email if changed
      if (values.email !== session.user.email) {
        const { error: updateEmailError } = await supabase.auth.updateUser({
          email: values.email,
        });
        
        if (updateEmailError) throw updateEmailError;
      }
      
      // Update profile in database
      const { error: updateProfileError } = await supabase
        .from("users")
        .update({
          name: values.name,
          updated_at: new Date().toISOString(),
        })
        .eq("id", session.user.id);
        
      if (updateProfileError) throw updateProfileError;
      
      toast({
        title: "Profile updated",
        description: "Your profile has been updated successfully.",
      });
      
    } catch (error) {
      console.error("Error updating profile:", error);
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive",
      });
    }
  }

  // Handle password form submission
  async function onPasswordSubmit(values: z.infer<typeof passwordFormSchema>) {
    try {
      // Update password
      const { error } = await supabase.auth.updateUser({
        password: values.newPassword,
      });
      
      if (error) throw error;
      
      // Reset form
      passwordForm.reset({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      
      toast({
        title: "Password updated",
        description: "Your password has been updated successfully.",
      });
      
    } catch (error) {
      console.error("Error updating password:", error);
      toast({
        title: "Error",
        description: "Failed to update password. Please try again.",
        variant: "destructive",
      });
    }
  }

  // Handle appearance form submission
  async function onAppearanceSubmit(values: z.infer<typeof appearanceFormSchema>) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        router.push("/login");
        return;
      }
      
      // Update theme
      setTheme(values.theme);
      
      // Get current preferences
      const { data, error: fetchError } = await supabase
        .from("users")
        .select("preferences")
        .eq("id", session.user.id)
        .single();
        
      if (fetchError && fetchError.code !== "PGRST116") throw fetchError;
      
      const currentPreferences = data?.preferences || {};
      
      // Update preferences in database
      const { error: updateError } = await supabase
        .from("users")
        .update({
          preferences: {
            ...currentPreferences,
            theme: values.theme,
            animationsEnabled: values.animationsEnabled,
          },
          updated_at: new Date().toISOString(),
        })
        .eq("id", session.user.id);
        
      if (updateError) throw updateError;
      
      toast({
        title: "Appearance updated",
        description: "Your appearance settings have been updated.",
      });
      
    } catch (error) {
      console.error("Error updating appearance:", error);
      toast({
        title: "Error",
        description: "Failed to update appearance settings. Please try again.",
        variant: "destructive",
      });
    }
  }

  // Handle AI settings form submission
  async function onAISettingsSubmit(values: z.infer<typeof aiSettingsFormSchema>) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        router.push("/login");
        return;
      }
      
      // Get current preferences
      const { data, error: fetchError } = await supabase
        .from("users")
        .select("preferences")
        .eq("id", session.user.id)
        .single();
        
      if (fetchError && fetchError.code !== "PGRST116") throw fetchError;
      
      const currentPreferences = data?.preferences || {};
      
      // Update preferences in database
      const { error: updateError } = await supabase
        .from("users")
        .update({
          preferences: {
            ...currentPreferences,
            defaultModel: values.defaultModel,
            memoryEnabled: values.memoryEnabled,
            insightsEnabled: values.insightsEnabled,
          },
          updated_at: new Date().toISOString(),
        })
        .eq("id", session.user.id);
        
      if (updateError) throw updateError;
      
      toast({
        title: "AI settings updated",
        description: "Your AI settings have been updated successfully.",
      });
      
    } catch (error) {
      console.error("Error updating AI settings:", error);
      toast({
        title: "Error",
        description: "Failed to update AI settings. Please try again.",
        variant: "destructive",
      });
    }
  }

  // Handle account deletion
  async function handleDeleteAccount() {
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      try {
        const { error } = await supabase.rpc("delete_user_account");
        
        if (error) throw error;
        
        // Sign out
        await supabase.auth.signOut();
        
        // Redirect to home
        router.push("/");
        
        toast({
          title: "Account deleted",
          description: "Your account has been deleted successfully.",
        });
        
      } catch (error) {
        console.error("Error deleting account:", error);
        toast({
          title: "Error",
          description: "Failed to delete account. Please try again.",
          variant: "destructive",
        });
      }
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      <div className="absolute inset-0 -z-10">
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
      
      <MainNav />
      
      <div className="container max-w-6xl py-8 mx-auto">
        <div className="flex flex-col space-y-4">
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences.
          </p>
        </div>
        
        <Tabs defaultValue="profile" className="mt-6">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="password">Password</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="ai-settings">AI Settings</TabsTrigger>
          </TabsList>
          
          {/* Profile Settings */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Profile</CardTitle>
                <CardDescription>
                  Manage your profile information.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...profileForm}>
                  <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-6">
                    <FormField
                      control={profileForm.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name</FormLabel>
                          <FormControl>
                            <Input placeholder="Your name" {...field} />
                          </FormControl>
                          <FormDescription>
                            This is the name that will be displayed to others.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={profileForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input placeholder="your.email@example.com" {...field} />
                          </FormControl>
                          <FormDescription>
                            Your email address is used for notifications and account recovery.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Button type="submit">Save changes</Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
            
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Account</CardTitle>
                <CardDescription>
                  Manage your account settings.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Delete your account and all associated data. This action cannot be undone.
                  </p>
                  <Button variant="destructive" onClick={handleDeleteAccount}>
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Password Settings */}
          <TabsContent value="password">
            <Card>
              <CardHeader>
                <CardTitle>Password</CardTitle>
                <CardDescription>
                  Change your password. We recommend using a strong, unique password.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...passwordForm}>
                  <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-6">
                    <FormField
                      control={passwordForm.control}
                      name="currentPassword"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Current Password</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="••••••••" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={passwordForm.control}
                      name="newPassword"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>New Password</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="••••••••" {...field} />
                          </FormControl>
                          <FormDescription>
                            Use at least 8 characters with a mix of letters, numbers, and symbols.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={passwordForm.control}
                      name="confirmPassword"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Confirm New Password</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="••••••••" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Button type="submit">Update password</Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Appearance Settings */}
          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <CardTitle>Appearance</CardTitle>
                <CardDescription>
                  Customize how DeepIntrospect AI looks and feels.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...appearanceForm}>
                  <form onSubmit={appearanceForm.handleSubmit(onAppearanceSubmit)} className="space-y-6">
                    <FormField
                      control={appearanceForm.control}
                      name="theme"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Theme</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a theme" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="light">Light</SelectItem>
                              <SelectItem value="dark">Dark</SelectItem>
                              <SelectItem value="system">System</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormDescription>
                            Choose between light, dark, or system theme.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={appearanceForm.control}
                      name="animationsEnabled"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between p-4 rounded-lg border">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Enable Animations</FormLabel>
                            <FormDescription>
                              Toggle UI animations and effects.
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <Button type="submit">Save appearance</Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* AI Settings */}
          <TabsContent value="ai-settings">
            <Card>
              <CardHeader>
                <CardTitle>AI Settings</CardTitle>
                <CardDescription>
                  Configure how the AI works with your data.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...aiSettingsForm}>
                  <form onSubmit={aiSettingsForm.handleSubmit(onAISettingsSubmit)} className="space-y-6">
                    <FormField
                      control={aiSettingsForm.control}
                      name="defaultModel"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Default AI Model</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a model" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="anthropic">Anthropic Claude</SelectItem>
                              <SelectItem value="openai">OpenAI GPT</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormDescription>
                            Select which AI model to use by default in conversations.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Separator className="my-4" />
                    
                    <FormField
                      control={aiSettingsForm.control}
                      name="memoryEnabled"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between p-4 rounded-lg border">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Memory</FormLabel>
                            <FormDescription>
                              Allow AI to remember past conversations for better context.
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={aiSettingsForm.control}
                      name="insightsEnabled"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between p-4 rounded-lg border">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">Insights Generation</FormLabel>
                            <FormDescription>
                              Generate insights about you based on conversations.
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <Button type="submit">Save AI settings</Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
