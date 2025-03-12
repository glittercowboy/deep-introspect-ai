import { PropsWithChildren } from 'react';
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Authentication - DeepIntrospect AI',
  description: 'Login or sign up to access DeepIntrospect AI, a personal self-reflection chatbot.',
};

export default function AuthLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-center p-4 border-b">
        <Link href="/" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
          DeepIntrospect AI
        </Link>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="py-4 px-6 text-center text-sm text-muted-foreground border-t">
        <p>&copy; {new Date().getFullYear()} DeepIntrospect AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
