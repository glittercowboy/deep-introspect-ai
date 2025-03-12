"use client"

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface SummaryCardProps {
  title: string;
  description?: string;
  content: string;
  isLoading?: boolean;
  className?: string;
}

export function SummaryCard({
  title,
  description,
  content,
  isLoading = false,
  className,
}: SummaryCardProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            {content}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface CategorySummaryProps {
  title: string;
  items: string[];
  isLoading?: boolean;
  className?: string;
}

export function CategorySummary({
  title,
  items,
  isLoading = false,
  className,
}: CategorySummaryProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          {items.length} item{items.length !== 1 ? 's' : ''}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : (
          <ul className="list-disc pl-5 space-y-1">
            {items.map((item, index) => (
              <li key={index} className="text-sm">
                {item}
              </li>
            ))}
            {items.length === 0 && (
              <li className="text-sm text-muted-foreground italic">
                No items yet. Continue conversations to gather more insights.
              </li>
            )}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

interface UserSummaryData {
  summary: string;
  categories: {
    [key: string]: string[];
  };
}

interface UserSummaryProps {
  data?: UserSummaryData;
  isLoading?: boolean;
}

export function UserSummary({
  data,
  isLoading = false,
}: UserSummaryProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <SummaryCard
          title="User Profile Summary"
          description="Generated from your conversations"
          content=""
          isLoading={true}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CategorySummary title="Key Traits" items={[]} isLoading={true} />
          <CategorySummary title="Values & Beliefs" items={[]} isLoading={true} />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-4">
        <SummaryCard
          title="User Profile Summary"
          description="Generated from your conversations"
          content="No summary available yet. Continue conversations to generate insights."
          isLoading={false}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CategorySummary title="Key Traits" items={[]} isLoading={false} />
          <CategorySummary title="Values & Beliefs" items={[]} isLoading={false} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <SummaryCard
        title="User Profile Summary"
        description="Generated from your conversations"
        content={data.summary}
        isLoading={false}
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CategorySummary 
          title="Key Traits" 
          items={data.categories['Key Traits'] || []} 
          isLoading={false} 
        />
        <CategorySummary 
          title="Values & Beliefs" 
          items={[
            ...(data.categories['Values'] || []),
            ...(data.categories['Beliefs'] || [])
          ]} 
          isLoading={false} 
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CategorySummary 
          title="Goals & Aspirations" 
          items={data.categories['Goals & Aspirations'] || []} 
          isLoading={false} 
        />
        <CategorySummary 
          title="Challenges" 
          items={data.categories['Challenges'] || []} 
          isLoading={false} 
        />
      </div>
    </div>
  );
}
