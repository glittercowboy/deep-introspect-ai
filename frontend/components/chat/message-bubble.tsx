"use client"

import React from 'react';
import { Avatar } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { Bot, User } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import { Card, CardContent } from "@/components/ui/card";
import { AnimatePresence, motion } from 'framer-motion';

export type MessageRole = 'user' | 'assistant';

export interface MessageProps {
  role: MessageRole;
  content: string;
  timestamp?: string;
  isLoading?: boolean;
  isStreaming?: boolean;
}

export function MessageBubble({
  role,
  content,
  timestamp,
  isLoading = false,
  isStreaming = false,
}: MessageProps) {
  const isUser = role === 'user';
  
  return (
    <div
      className={cn(
        "flex w-full items-start gap-4 py-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <Avatar className="h-8 w-8 rounded-md bg-primary/10">
          <Bot className="h-4 w-4 text-primary" />
        </Avatar>
      )}
      
      <Card className={cn(
        "max-w-[80%] overflow-hidden",
        isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
      )}>
        <CardContent className="p-3">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            {!isLoading ? (
              <div>
                {content}
                {isStreaming && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ repeat: Infinity, duration: 0.7 }}
                    className="ml-1 inline-block"
                  >
                    ▋
                  </motion.span>
                )}
              </div>
            ) : (
              <LoadingDots />
            )}
          </div>
          
          {timestamp && (
            <div className={cn(
              "text-xs mt-2",
              isUser ? "text-primary-foreground/70" : "text-secondary-foreground/70"
            )}>
              {formatDate(timestamp)}
            </div>
          )}
        </CardContent>
      </Card>
      
      {isUser && (
        <Avatar className="h-8 w-8 rounded-md bg-primary">
          <User className="h-4 w-4 text-primary-foreground" />
        </Avatar>
      )}
    </div>
  );
}

function LoadingDots() {
  return (
    <div className="flex space-x-1 items-center">
      <AnimatePresence>
        {[0, 1, 2].map((dot) => (
          <motion.span
            key={dot}
            initial={{ opacity: 0.2 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0.2 }}
            transition={{ repeat: Infinity, duration: 0.8, delay: dot * 0.15 }}
            className="rounded-full h-1.5 w-1.5 bg-current inline-block"
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
