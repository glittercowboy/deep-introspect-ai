"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClientComponentClient } from "@supabase/supabase-js";
import { formatDate, truncate } from "@/lib/utils";
import { useTheme } from "next-themes";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import MainNav from "@/components/layout/main-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, BrainCircuit, Calendar, Lightbulb, Clock, Plus } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

// Types
interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages_count: number;
}

interface Insight {
  id: string;
  type: string;
  content: string;
  created_at: string;
  conversation_id: string;
  evidence: string;
}

interface UserStats {
  total_conversations: number;
  total_messages: number;
  total_insights: number;
  conversation_frequency: {
    label: string;
    count: number;
  }[];
}

export default function DashboardPage() {
  const router = useRouter();
  const { theme } = useTheme();
  const { toast } = useToast();
  const supabase = createClientComponentClient();
  
  const [isLoading, setIsLoading] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [userStats, setUserStats] = useState<UserStats>({
    total_conversations: 0,
    total_messages: 0,
    total_insights: 0,
    conversation_frequency: [],
  });

  // Fetch data on mount
  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true);
        
        // Check authentication
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError || !session) {
          router.push("/login");
          return;
        }
        
        // Fetch conversations
        const { data: conversationsData, error: conversationsError } = await supabase
          .from("conversations")
          .select("id, title, created_at, updated_at, messages_count")
          .eq("user_id", session.user.id)
          .order("updated_at", { ascending: false })
          .limit(5);
          
        if (conversationsError) throw conversationsError;
        
        // Fetch insights
        const { data: insightsData, error: insightsError } = await supabase
          .from("insights")
          .select("id, type, content, created_at, conversation_id, evidence")
          .eq("user_id", session.user.id)
          .order("created_at", { ascending: false })
          .limit(5);
          
        if (insightsError) throw insightsError;
        
        // Fetch user stats
        const { data: statsData, error: statsError } = await supabase
          .rpc("get_user_stats", { user_id: session.user.id });
          
        if (statsError) throw statsError;
        
        // Set state
        setConversations(conversationsData || []);
        setInsights(insightsData || []);
        
        if (statsData) {
          setUserStats(statsData);
        }
        
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        toast({
          title: "Error",
          description: "Failed to load dashboard data. Please try again.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchData();
  }, [supabase, router, toast]);

  // Create a new conversation
  const createNewConversation = async () => {
    try {
      // Check authentication
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        router.push("/login");
        return;
      }
      
      // Create conversation
      const { data, error } = await supabase
        .from("conversations")
        .insert([
          {
            user_id: session.user.id,
            title: `Conversation ${new Date().toLocaleString()}`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ])
        .select("id")
        .single();
        
      if (error) throw error;
      
      // Navigate to chat
      router.push(`/chat/${data.id}`);
      
    } catch (error) {
      console.error("Error creating conversation:", error);
      toast({
        title: "Error",
        description: "Failed to create a new conversation. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Helper function to get insight type badge color
  const getInsightTypeBadgeColor = (type: string) => {
    const types: Record<string, string> = {
      belief: "bg-blue-500",
      value: "bg-purple-500",
      pattern: "bg-amber-500",
      trait: "bg-emerald-500",
      goal: "bg-indigo-500",
    };
    
    return types[type.toLowerCase()] || "bg-gray-500";
  };

  return (
    <div className="relative min-h-screen pb-12">
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
      
      <div className="container max-w-7xl px-4 mx-auto mt-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back. Here's an overview of your activity and insights.
          </p>
        </header>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Total Conversations
              </CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {userStats.total_conversations}
              </div>
              <p className="text-xs text-muted-foreground">
                {userStats.total_conversations > 0 
                  ? `${userStats.total_messages} messages exchanged`
                  : "Start your first conversation"}
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Total Insights
              </CardTitle>
              <BrainCircuit className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {userStats.total_insights}
              </div>
              <p className="text-xs text-muted-foreground">
                {userStats.total_insights > 0 
                  ? "Generated from your conversations"
                  : "No insights generated yet"}
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Last Activity
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {conversations.length > 0
                  ? formatDate(conversations[0].updated_at).split(',')[0]
                  : "No activity"}
              </div>
              <p className="text-xs text-muted-foreground">
                {conversations.length > 0
                  ? `Last active ${new Date(conversations[0].updated_at).toLocaleTimeString()}`
                  : "Start a conversation to track activity"}
              </p>
            </CardContent>
          </Card>
        </div>
        
        {/* Main Tabs */}
        <Tabs defaultValue="recent" className="mb-8">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="recent">Recent Activity</TabsTrigger>
            <TabsTrigger value="insights">Key Insights</TabsTrigger>
          </TabsList>
          
          {/* Recent Activity Tab */}
          <TabsContent value="recent">
            <div className="grid grid-cols-1 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Recent Conversations</CardTitle>
                    <CardDescription>
                      Your most recent conversations with DeepIntrospect AI
                    </CardDescription>
                  </div>
                  <Button onClick={createNewConversation}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Chat
                  </Button>
                </CardHeader>
                <CardContent>
                  {conversations.length > 0 ? (
                    <div className="space-y-4">
                      {conversations.map((conversation) => (
                        <div key={conversation.id} className="flex items-center">
                          <div className="flex-1 min-w-0">
                            <Link 
                              href={`/chat/${conversation.id}`}
                              className="block hover:underline font-medium"
                            >
                              {truncate(conversation.title, 50)}
                            </Link>
                            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                              <span className="flex items-center">
                                <Calendar className="h-3 w-3 mr-1" />
                                {formatDate(conversation.created_at)}
                              </span>
                              <span className="flex items-center">
                                <MessageSquare className="h-3 w-3 mr-1" />
                                {conversation.messages_count || 0} messages
                              </span>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            asChild
                            className="ml-2"
                          >
                            <Link href={`/chat/${conversation.id}`}>
                              Continue
                            </Link>
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-12 text-center">
                      <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-medium mb-2">No conversations yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Start a new conversation with DeepIntrospect AI to begin your journey.
                      </p>
                      <Button onClick={createNewConversation}>
                        Start a conversation
                      </Button>
                    </div>
                  )}
                </CardContent>
                {conversations.length > 0 && (
                  <CardFooter className="border-t px-6 py-4">
                    <Button
                      variant="outline"
                      className="w-full"
                      asChild
                    >
                      <Link href="/chat">
                        View all conversations
                      </Link>
                    </Button>
                  </CardFooter>
                )}
              </Card>
              
              {/* Activity Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle>Activity Timeline</CardTitle>
                  <CardDescription>
                    Your conversation frequency over time
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {userStats.conversation_frequency.length > 0 ? (
                    <div className="space-y-4">
                      {userStats.conversation_frequency.map((item, index) => (
                        <div key={index} className="flex items-center">
                          <div className="w-20 flex-shrink-0 text-sm text-muted-foreground">
                            {item.label}
                          </div>
                          <div className="ml-2 flex-1">
                            <div className="bg-secondary h-3 rounded-full w-full overflow-hidden">
                              <div 
                                className="bg-primary h-full rounded-full" 
                                style={{ width: `${Math.min(100, (item.count / Math.max(...userStats.conversation_frequency.map(i => i.count))) * 100)}%` }} 
                              />
                            </div>
                          </div>
                          <div className="ml-2 text-sm font-medium">
                            {item.count} {item.count === 1 ? 'chat' : 'chats'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-12 text-center">
                      <Calendar className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-medium mb-2">No activity data yet</h3>
                      <p className="text-muted-foreground">
                        Your activity timeline will be displayed once you have more conversations.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Key Insights Tab */}
          <TabsContent value="insights">
            <div className="grid grid-cols-1 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Insights</CardTitle>
                  <CardDescription>
                    Insights generated from your conversations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {insights.length > 0 ? (
                    <div className="space-y-6">
                      {insights.map((insight) => (
                        <div key={insight.id} className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="capitalize">
                              {insight.type}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {formatDate(insight.created_at)}
                            </span>
                          </div>
                          <p className="font-medium">{insight.content}</p>
                          <div className="text-sm text-muted-foreground italic border-l-2 pl-3 mt-1">
                            "{truncate(insight.evidence, 100)}"
                          </div>
                          <Separator className="my-2" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-12 text-center">
                      <Lightbulb className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-medium mb-2">No insights yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Insights will be generated as you have more conversations with DeepIntrospect AI.
                      </p>
                      <Button onClick={createNewConversation}>
                        Start a conversation
                      </Button>
                    </div>
                  )}
                </CardContent>
                {insights.length > 0 && (
                  <CardFooter className="border-t px-6 py-4">
                    <Button
                      variant="outline"
                      className="w-full"
                      asChild
                    >
                      <Link href="/insights">
                        View all insights
                      </Link>
                    </Button>
                  </CardFooter>
                )}
              </Card>
              
              {/* Insight Categories */}
              <Card>
                <CardHeader>
                  <CardTitle>Insight Categories</CardTitle>
                  <CardDescription>
                    Distribution of insights by category
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {insights.length > 0 ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                      {['Belief', 'Value', 'Pattern', 'Trait', 'Goal'].map((type) => {
                        const count = insights.filter(
                          (insight) => insight.type.toLowerCase() === type.toLowerCase()
                        ).length;
                        
                        return (
                          <div
                            key={type}
                            className="flex flex-col items-center justify-center p-4 rounded-lg bg-secondary"
                          >
                            <div className="text-2xl font-bold mb-1">{count}</div>
                            <div className="text-sm text-muted-foreground">{type}s</div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="py-8 text-center">
                      <p className="text-muted-foreground">
                        Insight categories will appear as insights are generated.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
