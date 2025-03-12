"use client"

import React, { useEffect, useRef, useState } from 'react';
import { MessageBubble } from './message-bubble';
import { MessageInput } from './message-input';
import { ModelSelector, ModelType } from './model-selector';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Share2, Trash2 } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  model: ModelType;
}

interface ChatContainerProps {
  conversation: Conversation | null;
  messages: Message[];
  onSendMessage: (content: string, model?: ModelType) => Promise<void>;
  onModelChange?: (model: ModelType) => void;
  onClearChat?: () => void;
  onShareChat?: () => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  className?: string;
}

export function ChatContainer({
  conversation,
  messages,
  onSendMessage,
  onModelChange,
  onClearChat,
  onShareChat,
  isLoading = false,
  isStreaming = false,
  className,
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [model, setModel] = useState<ModelType>((conversation?.model as ModelType) || 'anthropic');

  // Scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    await onSendMessage(content, model);
  };

  const handleModelChange = (newModel: ModelType) => {
    setModel(newModel);
    onModelChange?.(newModel);
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Chat header */}
      <div className="flex justify-between items-center p-4 border-b">
        <h2 className="text-lg font-semibold">
          {conversation?.title || 'New Conversation'}
        </h2>
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={onShareChat}
            title="Share conversation"
          >
            <Share2 className="h-4 w-4" />
          </Button>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={onClearChat}
            title="Clear chat"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground p-4">
            <h3 className="text-xl font-medium mb-2">Welcome to DeepIntrospect AI</h3>
            <p className="max-w-md mb-8">
              Start a conversation to explore your thoughts, beliefs, and patterns with AI-assisted introspection.
            </p>
            <div className="w-full max-w-sm">
              <ModelSelector 
                selectedModel={model} 
                onModelChange={handleModelChange} 
              />
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.created_at}
              isStreaming={isStreaming && message.id === messages[messages.length - 1].id && message.role === 'assistant'}
            />
          ))
        )}
        {isLoading && (
          <MessageBubble
            role="assistant"
            content=""
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t">
        <div className="flex flex-col gap-4">
          {messages.length > 0 && (
            <div className="w-full max-w-xs mx-auto">
              <ModelSelector 
                selectedModel={model} 
                onModelChange={handleModelChange} 
                disabled={isLoading || isStreaming}
              />
            </div>
          )}
          <MessageInput 
            onSend={handleSendMessage}
            isLoading={isLoading || isStreaming}
            placeholder="Ask something about yourself..."
          />
        </div>
      </div>
    </div>
  );
}
