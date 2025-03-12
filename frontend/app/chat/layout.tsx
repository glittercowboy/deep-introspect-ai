import { PropsWithChildren } from 'react';
import { Metadata } from 'next';
import { ProtectedRoute } from '@/components/auth/protected-route';

export const metadata: Metadata = {
  title: 'Chat - DeepIntrospect AI',
  description: 'Have a conversation with DeepIntrospect AI to better understand yourself through AI-assisted introspection.',
};

export default function ChatLayout({ children }: PropsWithChildren) {
  return (
    <main className="h-screen overflow-hidden">
      <ProtectedRoute>
        {children}
      </ProtectedRoute>
    </main>
  );
}
