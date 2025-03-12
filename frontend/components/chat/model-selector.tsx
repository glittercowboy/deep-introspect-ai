"use client"

import React from 'react';
import { Check, ChevronDown, Sparkles, Stars } from 'lucide-react';
import { cn } from '@/lib/utils';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';

export type ModelType = 'anthropic' | 'openai';

interface Model {
  id: ModelType;
  name: string;
  description: string;
  icon: React.ReactNode;
}

interface ModelSelectorProps {
  selectedModel: ModelType;
  onModelChange: (model: ModelType) => void;
  disabled?: boolean;
}

const models: Model[] = [
  {
    id: 'anthropic',
    name: 'Claude (Anthropic)',
    description: 'Powerful model with superior self-reflection capabilities',
    icon: <Stars className="h-4 w-4" />
  },
  {
    id: 'openai',
    name: 'GPT (OpenAI)',
    description: 'Versatile model with fast response times',
    icon: <Sparkles className="h-4 w-4" />
  }
];

export function ModelSelector({
  selectedModel,
  onModelChange,
  disabled = false
}: ModelSelectorProps) {
  const selectedModelData = models.find(model => model.id === selectedModel) || models[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild disabled={disabled}>
        <Button 
          variant="outline" 
          className="w-full justify-between"
          disabled={disabled}
        >
          <div className="flex items-center gap-2">
            {selectedModelData.icon}
            <span>{selectedModelData.name}</span>
          </div>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[240px]">
        {models.map(model => (
          <DropdownMenuItem
            key={model.id}
            className={cn(
              "flex items-center gap-2 cursor-pointer",
              selectedModel === model.id && "bg-accent"
            )}
            onClick={() => onModelChange(model.id)}
          >
            <div className="flex-1">
              <div className="flex items-center gap-2">
                {model.icon}
                <span className="font-medium">{model.name}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {model.description}
              </p>
            </div>
            {selectedModel === model.id && (
              <Check className="h-4 w-4" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
