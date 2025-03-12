"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClientComponentClient } from "@supabase/supabase-js";
import { formatDate, truncate } from "@/lib/utils";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import MainNav from "@/components/layout/main-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { 
  MessageSquare, 
  Plus, 
  Clock, 
  Calendar, 
  MoreVertical, 
  Edit, 
  Trash2, 
  Download, 
  Search 
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Types
interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages_count: number;
}

export default function ChatPage() {
  const router = useRouter();
  const { toast } = useToast();
  const supabase = createClientComponentClient();
  
  const [isLoading, setIsLoading] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Fetch conversations from API
  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      
      // Check authentication
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        router.push("/login");
        return;
      }
      
      // Fetch conversations
      const { data, error } = await supabase
        .from("conversations")
        .select("id, title, created_at, updated_at, messages_count")
        .eq("user_id", session.user.id)
        .order("updated_at", { ascending: false });
        
      if (error) throw error;
      
      setConversations(data || []);
      
    } catch (error) {
      console.error("Error fetching conversations:", error);
      toast({
        title: "Error",
        description: "Failed to load conversations. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

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

  // Delete a conversation
  const deleteConversation = async (id: string) => {
    try {
      setIsDeleting(true);
      
      // Delete conversation
      const { error } = await supabase
        .from("conversations")
        .delete()
        .eq("id", id);
        
      if (error) throw error;
      
      // Update local state
      setConversations(conversations.filter(c => c.id !== id));
      
      toast({
        title: "Conversation deleted",
        description: "The conversation has been deleted successfully.",
      });
      
    } catch (error) {
      console.error("Error deleting conversation:", error);
      toast({
        title: "Error",
        description: "Failed to delete conversation. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // Open rename dialog
  const openRenameDialog = (conversation: Conversation) => {
    setSelectedConversation(conversation);
    setNewTitle(conversation.title);
    setIsRenameDialogOpen(true);
  };

  // Rename a conversation
  const renameConversation = async () => {
    if (!selectedConversation) return;
    
    try {
      // Update conversation
      const { error } = await supabase
        .from("conversations")
        .update({ title: newTitle })
        .eq("id", selectedConversation.id);
        
      if (error) throw error;
      
      // Update local state
      setConversations(conversations.map(c => 
        c.id === selectedConversation.id 
          ? { ...c, title: newTitle } 
          : c
      ));
      
      // Close dialog
      setIsRenameDialogOpen(false);
      setSelectedConversation(null);
      
      toast({
        title: "Conversation renamed",
        description: "The conversation has been renamed successfully.",
      });
      
    } catch (error) {
      console.error("Error renaming conversation:", error);
      toast({
        title: "Error",
        description: "Failed to rename conversation. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Export conversation as text
  const exportConversation = async (id: string) => {
    try {
      // Fetch conversation messages
      const { data, error } = await supabase
        .from("messages")
        .select("role, content, created_at")
        .eq("conversation_id", id)
        .order("created_at", { ascending: true });
        
      if (error) throw error;
      
      // Format messages for export
      const conversation = conversations.find(c => c.id === id);
      let content = `# ${conversation?.title || "Conversation"}\n`;
      content += `Exported on ${new Date().toLocaleString()}\n\n`;
      
      data.forEach((message) => {
        const timestamp = new Date(message.created_at).toLocaleString();
        content += `## ${message.role === "user" ? "You" : "DeepIntrospect AI"} (${timestamp})\n\n`;
        content += `${message.content}\n\n`;
      });
      
      // Create download link
      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${conversation?.title || "conversation"}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Conversation exported",
        description: "The conversation has been exported successfully.",
      });
      
    } catch (error) {
      console.error("Error exporting conversation:", error);
      toast({
        title: "Error",
        description: "Failed to export conversation. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Filter conversations by search query
  const filteredConversations = conversations.filter(
    (conversation) => 
      conversation.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

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
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
            <p className="text-muted-foreground mt-1">
              Your chat history with DeepIntrospect AI
            </p>
          </div>
          
          <Button onClick={createNewConversation}>
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </header>
        
        {/* Search Bar */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        
        {/* Conversations List */}
        <div className="space-y-4">
          {filteredConversations.length > 0 ? (
            filteredConversations.map((conversation) => (
              <Card key={conversation.id} className="overflow-hidden">
                <div className="flex items-center p-6">
                  <div className="mr-4 flex-shrink-0">
                    <div className="bg-primary/10 rounded-full p-2">
                      <MessageSquare className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <Link 
                      href={`/chat/${conversation.id}`}
                      className="block hover:underline font-medium"
                    >
                      {truncate(conversation.title, 50)}
                    </Link>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(conversation.created_at)}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {new Date(conversation.updated_at).toLocaleTimeString()}
                      </span>
                      <span className="flex items-center">
                        <MessageSquare className="h-3 w-3 mr-1" />
                        {conversation.messages_count || 0} messages
                      </span>
                    </div>
                  </div>
                  
                  <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      asChild
                    >
                      <Link href={`/chat/${conversation.id}`}>
                        Continue
                      </Link>
                    </Button>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" aria-label="More actions">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openRenameDialog(conversation)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => exportConversation(conversation.id)}>
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => deleteConversation(conversation.id)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <Card className="py-12">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                {searchQuery ? (
                  <>
                    <h3 className="text-lg font-medium mb-2">No conversations found</h3>
                    <p className="text-muted-foreground mb-4">
                      No conversations match your search query.
                    </p>
                    <Button variant="outline" onClick={() => setSearchQuery("")}>
                      Clear search
                    </Button>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-medium mb-2">No conversations yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Start a new conversation with DeepIntrospect AI.
                    </p>
                    <Button onClick={createNewConversation}>
                      Start a conversation
                    </Button>
                  </>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
      
      {/* Rename Dialog */}
      <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Conversation</DialogTitle>
            <DialogDescription>
              Enter a new title for this conversation.
            </DialogDescription>
          </DialogHeader>
          <Input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="mt-4"
            placeholder="Enter new title"
          />
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setIsRenameDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={renameConversation} disabled={!newTitle.trim()}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
