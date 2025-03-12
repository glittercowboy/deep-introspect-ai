"use client"

import React from 'react';
import { Button } from '@/components/ui/button';
import { PlusCircle, MessageSquare, Stars, Sparkles } from 'lucide-react';
import { cn, formatDate, truncate } from '@/lib/utils';
import { Conversation } from './chat-container';
import { ModelType } from './model-selector';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId?: string;
  onSelectConversation: (conversation: Conversation) => void;
  onNewConversation: () => void;
  className?: string;
}

export function ConversationList({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onNewConversation,
  className,
}: ConversationListProps) {
  // Sort conversations by updated_at (newest first)
  const sortedConversations = [...conversations].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  );

  const getModelIcon = (model: string) => {
    switch (model as ModelType) {
      case 'anthropic':
        return <Stars className="h-3 w-3" />;
      case 'openai':
        return <Sparkles className="h-3 w-3" />;
      default:
        return <MessageSquare className="h-3 w-3" />;
    }
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      <div className="p-4">
        <Button 
          onClick={onNewConversation}
          className="w-full"
        >
          <PlusCircle className="mr-2 h-4 w-4" />
          New Conversation
        </Button>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="px-2 py-2 space-y-1">
          {sortedConversations.length === 0 ? (
            <div className="text-center text-muted-foreground px-4 py-8">
              No conversations yet. Start a new one.
            </div>
          ) : (
            sortedConversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => onSelectConversation(conversation)}
                className={cn(
                  "w-full text-left flex items-start p-3 rounded-md hover:bg-accent transition-colors",
                  selectedConversationId === conversation.id && "bg-accent"
                )}
              >
                <div className="mr-2 mt-0.5">
                  {getModelIcon(conversation.model)}
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="font-medium">
                    {truncate(conversation.title, 25)}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {formatDate(conversation.updated_at)}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
