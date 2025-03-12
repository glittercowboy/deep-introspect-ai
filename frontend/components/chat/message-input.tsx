"use client"

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SendIcon, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessageInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

export function MessageInput({
  onSend,
  isLoading = false,
  placeholder = "Type a message...",
  className,
}: MessageInputProps) {
  const [message, setMessage] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // Reset height - important to shrink on delete
    textarea.style.height = 'auto';
    
    // Set height based on scrollHeight
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;
    
    onSend(trimmedMessage);
    setMessage('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift key)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className={cn(
        "flex flex-col space-y-2 border rounded-md p-2 bg-background", 
        className
      )}
    >
      <div className="flex items-end gap-2">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 resize-none overflow-hidden min-h-[40px] max-h-[200px] p-2"
          disabled={isLoading}
          rows={1}
        />
        <Button 
          type="submit" 
          size="icon" 
          disabled={!message.trim() || isLoading}
          className="shrink-0"
        >
          {isLoading ? (
            <Sparkles className="h-4 w-4 animate-pulse" />
          ) : (
            <SendIcon className="h-4 w-4" />
          )}
        </Button>
      </div>
      <div className="flex justify-end px-2">
        <span className="text-xs text-muted-foreground">
          Press Enter to send, Shift+Enter for a new line
        </span>
      </div>
    </form>
  );
}
