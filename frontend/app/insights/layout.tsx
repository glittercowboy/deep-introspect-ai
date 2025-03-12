import { PropsWithChildren } from 'react';
import { Metadata } from 'next';
import { ProtectedRoute } from '@/components/auth/protected-route';

export const metadata: Metadata = {
  title: 'Insights - DeepIntrospect AI',
  description: 'View your personalized insights, patterns, and knowledge graph based on your conversations.',
};

export default function InsightsLayout({ children }: PropsWithChildren) {
  return (
    <main className="min-h-screen">
      <ProtectedRoute>
        {children}
      </ProtectedRoute>
    </main>
  );
}
