import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@/components/theme-provider';

// Create a custom render function that includes providers
const AllProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
    >
      {children}
    </ThemeProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllProviders, ...options });

// re-export everything
export * from '@testing-library/react';

// override render method
export { customRender as render };

// Mock function for the formatDate utility
export const mockFormatDate = (date: string | number | Date): string => {
  const mockDate = new Date(date);
  return mockDate.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
};

// Mock function for the truncate utility
export const mockTruncate = (str: string, length: number): string => {
  return str.length > length ? `${str.substring(0, length)}...` : str;
};

// Mock sleep function
export const mockSleep = async (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, 0));
};

// Mock Supabase Auth Response
export const mockAuthSession = {
  data: {
    session: {
      user: {
        id: 'test-user-id',
        email: 'test@example.com',
      },
    },
  },
  error: null,
};

// Mock Empty Auth Response (logged out)
export const mockEmptyAuthSession = {
  data: { session: null },
  error: null,
};

// Mock Supabase Error Response
export const mockAuthError = {
  data: { session: null },
  error: { message: 'Auth error', status: 401 },
};

// Create a mock user
export const mockUser = {
  id: 'test-user-id',
  email: 'test@example.com',
  name: 'Test User',
  created_at: '2023-01-01T00:00:00.000Z',
  updated_at: '2023-01-01T00:00:00.000Z',
  preferences: {
    theme: 'dark',
    defaultModel: 'anthropic',
  },
};

// Create mock conversations
export const mockConversations = [
  {
    id: 'conv1',
    title: 'First Conversation',
    created_at: '2023-01-01T00:00:00.000Z',
    updated_at: '2023-01-02T00:00:00.000Z',
    user_id: 'test-user-id',
    messages_count: 10,
  },
  {
    id: 'conv2',
    title: 'Second Conversation',
    created_at: '2023-01-03T00:00:00.000Z',
    updated_at: '2023-01-04T00:00:00.000Z',
    user_id: 'test-user-id',
    messages_count: 5,
  },
];

// Create mock messages
export const mockMessages = [
  {
    id: 'msg1',
    conversation_id: 'conv1',
    role: 'user',
    content: 'Hello, how are you?',
    created_at: '2023-01-01T00:00:00.000Z',
  },
  {
    id: 'msg2',
    conversation_id: 'conv1',
    role: 'assistant',
    content: "I'm doing well! How can I help you today?",
    created_at: '2023-01-01T00:00:01.000Z',
  },
  {
    id: 'msg3',
    conversation_id: 'conv1',
    role: 'user',
    content: 'I wanted to talk about my goals.',
    created_at: '2023-01-01T00:00:02.000Z',
  },
];

// Create mock insights
export const mockInsights = [
  {
    id: 'insight1',
    user_id: 'test-user-id',
    type: 'belief',
    content: 'Values personal growth over immediate comfort',
    evidence: 'User consistently mentioned prioritizing learning over convenience',
    created_at: '2023-01-01T00:00:00.000Z',
    conversation_id: 'conv1',
  },
  {
    id: 'insight2',
    user_id: 'test-user-id',
    type: 'pattern',
    content: 'Tends to reflect deeply before making decisions',
    evidence: 'User described taking time to consider options in multiple scenarios',
    created_at: '2023-01-02T00:00:00.000Z',
    conversation_id: 'conv1',
  },
];

// Mock notifications
export const mockNotifications = [
  {
    id: 'notif1',
    user_id: 'test-user-id',
    type: 'insight',
    title: 'New Insight Generated',
    content: 'We discovered a new insight about your communication style',
    read: false,
    created_at: '2023-01-01T00:00:00.000Z',
    metadata: {
      insight_id: 'insight1',
    },
  },
  {
    id: 'notif2',
    user_id: 'test-user-id',
    type: 'message',
    title: 'New Message',
    content: 'You have a new message in your conversation',
    read: true,
    created_at: '2023-01-02T00:00:00.000Z',
    metadata: {
      conversation_id: 'conv1',
    },
  },
];
