"use client";

import { useState, useEffect } from "react";
import { Bell, X, BrainCircuit, MessageSquare, Info, ChevronRight, Check } from "lucide-react";
import { createClientComponentClient } from "@supabase/supabase-js";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useRouter } from "next/navigation";

interface Notification {
  id: string;
  user_id: string;
  type: "insight" | "message" | "system";
  title: string;
  content: string;
  read: boolean;
  created_at: string;
  metadata: {
    conversation_id?: string;
    insight_id?: string;
    url?: string;
  }
}

export function NotificationCenter() {
  const supabase = createClientComponentClient();
  const { toast } = useToast();
  const router = useRouter();
  
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Fetch notifications on mount and when popover opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  // Set up real-time notification subscription
  useEffect(() => {
    const setupSubscription = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;
      
      // Subscribe to new notifications
      const channel = supabase
        .channel('notification_changes')
        .on(
          'postgres_changes',
          {
            event: 'INSERT', 
            schema: 'public',
            table: 'notifications',
            filter: `user_id=eq.${session.user.id}`,
          },
          (payload) => {
            // Update notifications list
            setNotifications(prev => [payload.new as Notification, ...prev]);
            
            // Update unread count
            setUnreadCount(prev => prev + 1);
            
            // Show toast notification
            const newNotification = payload.new as Notification;
            toast({
              title: newNotification.title,
              description: newNotification.content,
            });
          }
        )
        .subscribe();
        
      // Cleanup subscription on unmount
      return () => {
        supabase.removeChannel(channel);
      };
    };
    
    setupSubscription();
  }, []);

  // Fetch notifications from API
  const fetchNotifications = async () => {
    try {
      setIsLoading(true);
      
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;
      
      // Get notifications from Supabase
      const { data, error } = await supabase
        .from('notifications')
        .select('*')
        .eq('user_id', session.user.id)
        .order('created_at', { ascending: false })
        .limit(20);
        
      if (error) throw error;
      
      // Calculate unread count
      const unread = data?.filter(n => !n.read).length || 0;
      
      setNotifications(data || []);
      setUnreadCount(unread);
      
    } catch (error) {
      console.error("Error fetching notifications:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Mark notification as read
  const markAsRead = async (id: string) => {
    try {
      const { error } = await supabase
        .from('notifications')
        .update({ read: true })
        .eq('id', id);
        
      if (error) throw error;
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
      
      // Update unread count
      setUnreadCount(prev => Math.max(0, prev - 1));
      
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;
      
      const { error } = await supabase
        .from('notifications')
        .update({ read: true })
        .eq('user_id', session.user.id)
        .eq('read', false);
        
      if (error) throw error;
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => ({ ...n, read: true }))
      );
      
      // Reset unread count
      setUnreadCount(0);
      
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    markAsRead(notification.id);
    
    // Navigate based on notification type
    switch (notification.type) {
      case "insight":
        if (notification.metadata.insight_id) {
          router.push(`/insights?highlight=${notification.metadata.insight_id}`);
        } else {
          router.push("/insights");
        }
        break;
        
      case "message":
        if (notification.metadata.conversation_id) {
          router.push(`/chat/${notification.metadata.conversation_id}`);
        } else {
          router.push("/chat");
        }
        break;
        
      case "system":
        if (notification.metadata.url) {
          router.push(notification.metadata.url);
        }
        break;
        
      default:
        break;
    }
    
    // Close popover
    setIsOpen(false);
  };

  // Render notification icon based on type
  const renderNotificationIcon = (type: string) => {
    switch (type) {
      case "insight":
        return <BrainCircuit className="h-4 w-4" />;
      case "message":
        return <MessageSquare className="h-4 w-4" />;
      case "system":
        return <Info className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };
  
  // Function to generate sample notifications for development
  const generateSampleNotifications = () => {
    const samples = [
      {
        id: "sample-1",
        user_id: "user-id",
        type: "insight" as const,
        title: "New Insight Generated",
        content: "We've identified a pattern in your communication style that shows strong empathy.",
        read: false,
        created_at: new Date().toISOString(),
        metadata: {
          insight_id: "insight-1",
        }
      },
      {
        id: "sample-2",
        user_id: "user-id",
        type: "message" as const,
        title: "New Response Available",
        content: "Your conversation 'Career Planning' has a new response.",
        read: false,
        created_at: new Date(Date.now() - 3600000).toISOString(),
        metadata: {
          conversation_id: "conversation-1",
        }
      },
      {
        id: "sample-3",
        user_id: "user-id",
        type: "system" as const,
        title: "Weekly Summary Ready",
        content: "Your weekly introspection summary is now available to view.",
        read: true,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        metadata: {
          url: "/insights",
        }
      }
    ];
    
    setNotifications(samples);
    setUnreadCount(2);
    toast({
      title: "Sample Notifications Created",
      description: "Created 3 sample notifications for testing.",
    });
  };

  // Generate notification content (for empty state and testing)
  const notificationContent = 
    notifications.length === 0 ? (
      <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
        <Bell className="h-12 w-12 mb-4 text-muted-foreground" />
        <h3 className="text-lg font-medium mb-2">No notifications</h3>
        <p className="text-sm text-muted-foreground mb-6">
          You'll receive notifications about new insights, 
          conversation updates, and system announcements.
        </p>
        {process.env.NODE_ENV === "development" && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={generateSampleNotifications}
          >
            Generate Sample Notifications
          </Button>
        )}
      </div>
    ) : (
      <>
        <div className="flex items-center justify-between p-4">
          <h3 className="font-medium">Notifications</h3>
          {unreadCount > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="h-8 text-xs"
              onClick={markAllAsRead}
            >
              <Check className="h-3 w-3 mr-1" />
              Mark all as read
            </Button>
          )}
        </div>
        
        <Separator />
        
        <div className="overflow-y-auto max-h-[400px]">
          <Accordion type="multiple" className="w-full">
            {notifications.map((notification) => (
              <AccordionItem 
                key={notification.id} 
                value={notification.id}
                className={!notification.read ? "bg-muted/30" : ""}
              >
                <div className="flex items-start p-3">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-2 ${
                    notification.type === "insight" ? "bg-purple-100 text-purple-500 dark:bg-purple-900/30 dark:text-purple-300" :
                    notification.type === "message" ? "bg-blue-100 text-blue-500 dark:bg-blue-900/30 dark:text-blue-300" :
                    "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-300"
                  }`}>
                    {renderNotificationIcon(notification.type)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-medium">{notification.title}</h4>
                        {!notification.read && (
                          <Badge variant="secondary" className="text-xs h-5">New</Badge>
                        )}
                      </div>
                      <AccordionTrigger className="h-4 w-4 p-0">
                        <ChevronRight className="h-4 w-4" />
                      </AccordionTrigger>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDate(notification.created_at)}
                    </p>
                  </div>
                </div>
                
                <AccordionContent className="px-3 pb-3 pt-0 ml-10">
                  <p className="text-sm mb-2">{notification.content}</p>
                  <div className="flex justify-between items-center mt-2">
                    <Button 
                      variant="link" 
                      size="sm" 
                      className="p-0 h-auto text-xs"
                      onClick={() => handleNotificationClick(notification)}
                    >
                      View Details
                    </Button>
                    {!notification.read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() => markAsRead(notification.id)}
                      >
                        Mark as read
                      </Button>
                    )}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </>
    );

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] text-destructive-foreground">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          notificationContent
        )}
      </PopoverContent>
    </Popover>
  );
}
