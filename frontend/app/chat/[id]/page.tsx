"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClientComponentClient } from "@supabase/supabase-js";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import MainNav from "@/components/layout/main-nav";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import { SendHorizonal, Loader2, Bot, User, Brain } from "lucide-react";

// Types
interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const supabase = createClientComponentClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const [conversationId, setConversationId] = useState<string>("");
  const [conversationTitle, setConversationTitle] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [aiModel, setAiModel] = useState<string>("anthropic");
  const [streamingMessage, setStreamingMessage] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  // Initialize conversation data
  useEffect(() => {
    if (params.id) {
      setConversationId(params.id as string);
      fetchConversation(params.id as string);
    }
  }, [params.id]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Auto-resize textarea as content grows
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  // Fetch conversation data
  const fetchConversation = async (id: string) => {
    try {
      setIsLoading(true);
      
      // Check authentication
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        router.push("/login");
        return;
      }
      
      // Fetch conversation details
      const { data: conversationData, error: conversationError } = await supabase
        .from("conversations")
        .select("*")
        .eq("id", id)
        .single();
      
      if (conversationError) throw conversationError;
      
      // Verify ownership
      if (conversationData.user_id !== session.user.id) {
        toast({
          title: "Access denied",
          description: "You don't have permission to view this conversation.",
          variant: "destructive",
        });
        router.push("/chat");
        return;
      }
      
      setConversationTitle(conversationData.title);
      setAiModel(conversationData.model || "anthropic");
      
      // Fetch messages
      const { data: messagesData, error: messagesError } = await supabase
        .from("messages")
        .select("*")
        .eq("conversation_id", id)
        .order("created_at", { ascending: true });
      
      if (messagesError) throw messagesError;
      
      setMessages(messagesData || []);
      
    } catch (error) {
      console.error("Error fetching conversation:", error);
      toast({
        title: "Error",
        description: "Failed to load conversation. Please try again.",
        variant: "destructive",
      });
      router.push("/chat");
    } finally {
      setIsLoading(false);
    }
  };

  // Send a message
  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    if (!inputMessage.trim() || isSending) return;
    
    try {
      setIsSending(true);
      
      // Add user message to state immediately
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: conversationId,
        role: "user",
        content: inputMessage,
        created_at: new Date().toISOString(),
      };
      
      setMessages([...messages, userMessage]);
      setInputMessage("");
      
      // Send message to API
      const response = await fetch(`/api/chat/${conversationId}/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: userMessage.content,
          model: aiModel,
        }),
      });
      
      // Handle streaming response
      if (response.ok && response.body) {
        setIsStreaming(true);
        setStreamingMessage("");
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        let done = false;
        let accumulatedMessage = "";
        
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          
          if (value) {
            const chunk = decoder.decode(value);
            accumulatedMessage += chunk;
            setStreamingMessage(accumulatedMessage);
          }
        }
        
        // Add assistant message to state
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          conversation_id: conversationId,
          role: "assistant",
          content: accumulatedMessage,
          created_at: new Date().toISOString(),
        };
        
        setMessages([...messages, userMessage, assistantMessage]);
        setIsStreaming(false);
        setStreamingMessage("");
        
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to send message");
      }
      
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSending(false);
    }
  };

  // Handle key press events
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Change AI model
  const changeModel = async (model: string) => {
    try {
      setAiModel(model);
      
      // Update conversation model preference
      await supabase
        .from("conversations")
        .update({ model })
        .eq("id", conversationId);
      
    } catch (error) {
      console.error("Error changing model:", error);
      toast({
        title: "Error",
        description: "Failed to change AI model. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Format message content with markdown
  const formatMessageContent = (content: string) => {
    // Replace URLs with links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const withLinks = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">$1</a>');
    
    // Replace newlines with <br>
    return withLinks.replace(/\n/g, "<br>");
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex flex-col">
      <div className="absolute inset-0 -z-10">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={20}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>
      
      <MainNav />
      
      <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto px-4">
        {/* Chat Header */}
        <div className="flex items-center justify-between py-4">
          <div>
            <h1 className="text-xl font-semibold truncate max-w-md">{conversationTitle}</h1>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>{messages.length} messages</span>
              <span>•</span>
              <Select
                value={aiModel}
                onValueChange={changeModel}
              >
                <SelectTrigger className="h-7 w-[150px] text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="anthropic">
                    <div className="flex items-center">
                      <Brain className="h-3 w-3 mr-1" />
                      Claude 3 Opus
                    </div>
                  </SelectItem>
                  <SelectItem value="openai">
                    <div className="flex items-center">
                      <Brain className="h-3 w-3 mr-1" />
                      GPT-4 Turbo
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <Button variant="outline" size="sm" onClick={() => router.push("/chat")}>
            View All
          </Button>
        </div>
        
        <Separator />
        
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto py-4 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center">
              <Bot className="h-12 w-12 mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">Start the conversation</h3>
              <p className="text-muted-foreground max-w-md mb-8">
                Send a message to begin your journey with DeepIntrospect AI. 
                The chatbot will learn about you through thoughtful conversation.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={cn(
                    "flex",
                    message.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  <div 
                    className={cn(
                      "max-w-3xl rounded-lg px-4 py-3",
                      message.role === "user" 
                        ? "bg-primary text-primary-foreground ml-12"
                        : "bg-muted mr-12"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {message.role === "assistant" ? (
                        <Badge variant="outline" className="text-xs font-normal bg-background/50">
                          <Bot className="h-3 w-3 mr-1" />
                          DeepIntrospect AI
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs font-normal">
                          <User className="h-3 w-3 mr-1" />
                          You
                        </Badge>
                      )}
                    </div>
                    <div 
                      className="prose prose-sm dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                    />
                  </div>
                </div>
              ))}
              
              {/* Streaming Message */}
              {isStreaming && (
                <div className="flex justify-start">
                  <div className="max-w-3xl rounded-lg px-4 py-3 bg-muted mr-12">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-xs font-normal bg-background/50">
                        <Bot className="h-3 w-3 mr-1" />
                        DeepIntrospect AI
                      </Badge>
                    </div>
                    <div 
                      className="prose prose-sm dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{ __html: formatMessageContent(streamingMessage) }}
                    />
                    {!streamingMessage && (
                      <div className="flex items-center gap-1 text-muted-foreground animate-pulse">
                        <div className="h-1 w-1 rounded-full bg-current"></div>
                        <div className="h-1 w-1 rounded-full bg-current"></div>
                        <div className="h-1 w-1 rounded-full bg-current"></div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
          
          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Message Input */}
        <div className="py-4">
          <form onSubmit={sendMessage} className="flex items-end gap-2">
            <Textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="resize-none min-h-[60px] max-h-[200px]"
              disabled={isSending || isStreaming}
            />
            <Button 
              type="submit" 
              size="icon" 
              className="h-[60px] w-[60px] flex-shrink-0"
              disabled={!inputMessage.trim() || isSending || isStreaming}
            >
              {isSending || isStreaming ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <SendHorizonal className="h-5 w-5" />
              )}
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for a new line
          </p>
        </div>
      </div>
    </div>
  );
}
