"use client"

import React, { useState, useEffect } from 'react';
import { ChatContainer, Conversation, Message } from '@/components/chat/chat-container';
import { ConversationList } from '@/components/chat/conversation-list';
import { ModelType } from '@/components/chat/model-selector';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import * as api from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { toast } = useToast();
  const router = useRouter();

  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data = await api.getConversations();
        setConversations(data);
      } catch (error) {
        console.error('Failed to load conversations:', error);
        toast({
          title: 'Error',
          description: 'Failed to load conversations. Please try again.',
          variant: 'destructive',
        });
      }
    };

    loadConversations();
  }, [toast]);

  // Load messages when conversation changes
  useEffect(() => {
    if (!currentConversation) return;

    const loadMessages = async () => {
      try {
        const data = await api.getConversation(currentConversation.id);
        setMessages(data.messages);
      } catch (error) {
        console.error('Failed to load messages:', error);
        toast({
          title: 'Error',
          description: 'Failed to load conversation messages. Please try again.',
          variant: 'destructive',
        });
      }
    };

    loadMessages();
  }, [currentConversation, toast]);

  const handleSendMessage = async (content: string, model?: ModelType) => {
    try {
      if (!currentConversation) {
        // Create a new conversation first
        setIsLoading(true);
        const { conversation, welcome_message } = await api.startConversation(
          `Conversation ${new Date().toLocaleString()}`,
          model
        );
        setConversations((prev) => [conversation, ...prev]);
        setCurrentConversation(conversation);
        setMessages([welcome_message]);
        setIsLoading(false);
        
        // Now send the message to the new conversation
        await sendMessageToConversation(conversation.id, content, model);
      } else {
        // Send message to existing conversation
        await sendMessageToConversation(currentConversation.id, content, model);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
      setIsStreaming(false);
      toast({
        title: 'Error',
        description: 'Failed to send message. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const sendMessageToConversation = async (conversationId: string, content: string, model?: ModelType) => {
    try {
      // Add user message optimistically
      const tempUserMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, tempUserMessage]);
      
      // Start streaming response
      setIsStreaming(true);
      
      // Add placeholder for assistant response
      const tempAssistantMessage: Message = {
        id: `temp-assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, tempAssistantMessage]);
      
      // Stream the response
      const stream = await api.streamMessage(conversationId, content, model);
      
      if (stream) {
        const reader = stream.getReader();
        let assistantResponse = '';
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          // Decode the chunk
          const chunk = new TextDecoder().decode(value);
          
          // Parse the SSE data
          const lines = chunk.split('\n\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6);
              assistantResponse += data;
              
              // Update the assistant message with the accumulated response
              setMessages((prev) => {
                const updated = [...prev];
                const lastIndex = updated.length - 1;
                
                if (lastIndex >= 0 && updated[lastIndex].role === 'assistant') {
                  updated[lastIndex] = {
                    ...updated[lastIndex],
                    content: assistantResponse,
                  };
                }
                
                return updated;
              });
            }
          }
        }
      }
      
      // Get the updated conversation and messages
      const { conversation } = await api.getConversation(conversationId);
      
      // Update the conversations list with the latest data
      setConversations((prev) => 
        prev.map((conv) => (conv.id === conversationId ? conversation : conv))
      );
      
      setIsStreaming(false);
    } catch (error) {
      console.error('Failed to stream message:', error);
      setIsStreaming(false);
      toast({
        title: 'Error',
        description: 'Failed to receive response. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleNewConversation = async () => {
    setCurrentConversation(null);
    setMessages([]);
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation);
  };

  const handleModelChange = async (model: ModelType) => {
    if (!currentConversation) return;
    
    try {
      // Update the conversation model
      // This would typically be an API call to update the conversation
      // For now, we'll just update the local state
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === currentConversation.id
            ? { ...conv, model }
            : conv
        )
      );
      
      if (currentConversation) {
        setCurrentConversation({ ...currentConversation, model });
      }
    } catch (error) {
      console.error('Failed to update model:', error);
      toast({
        title: 'Error',
        description: 'Failed to update model. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleClearChat = async () => {
    if (!currentConversation) return;
    
    // This would typically be an API call to delete messages
    // For now, we'll just clear the local state
    setMessages([]);
  };

  const handleShareChat = async () => {
    if (!currentConversation) return;
    
    // This would typically generate a shareable link
    toast({
      title: 'Share Feature',
      description: 'Sharing functionality will be implemented soon.',
    });
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar (mobile toggle) */}
      <div className="lg:hidden fixed left-4 top-4 z-50">
        <Button 
          variant="outline" 
          size="icon"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? <X /> : <Menu />}
        </Button>
      </div>
      
      {/* Sidebar */}
      <div 
        className={`w-80 border-r bg-background flex-shrink-0 ${
          sidebarOpen ? 'fixed inset-y-0 left-0 z-40 lg:relative lg:translate-x-0' : 'hidden lg:block'
        }`}
      >
        <ConversationList
          conversations={conversations}
          selectedConversationId={currentConversation?.id}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          className="h-full"
        />
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex flex-col">
        <ChatContainer
          conversation={currentConversation}
          messages={messages}
          onSendMessage={handleSendMessage}
          onModelChange={handleModelChange}
          onClearChat={handleClearChat}
          onShareChat={handleShareChat}
          isLoading={isLoading}
          isStreaming={isStreaming}
          className="h-full"
        />
      </div>
    </div>
  );
}
