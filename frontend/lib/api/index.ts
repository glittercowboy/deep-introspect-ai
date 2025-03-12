/**
 * API client for communicating with the backend
 */

import { Conversation, Message } from '@/components/chat/chat-container';
import { ModelType } from '@/components/chat/model-selector';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Get auth token from local storage or context
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }
  
  return response;
}

// Auth API
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }
  
  const data = await response.json();
  
  // Store token in local storage
  localStorage.setItem('token', data.access_token);
  
  return data;
}

export async function register(email: string, password: string, name?: string) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Registration failed');
  }
  
  return response.json();
}

export async function logout() {
  localStorage.removeItem('token');
}

// User API
export async function getCurrentUser() {
  const response = await fetchWithAuth(`${API_URL}/users/me`);
  return response.json();
}

export async function getUserProfile() {
  const response = await fetchWithAuth(`${API_URL}/users/me/profile`);
  return response.json();
}

export async function updateUserProfile(data: { name?: string, email?: string, password?: string }) {
  const response = await fetchWithAuth(`${API_URL}/users/me`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response.json();
}

// Chat API
export async function getConversations(): Promise<Conversation[]> {
  const response = await fetchWithAuth(`${API_URL}/chat/conversations`);
  return response.json();
}

export async function getConversation(conversationId: string): Promise<{ id: string, user_id: string, title: string, messages: Message[] }> {
  const response = await fetchWithAuth(`${API_URL}/chat/conversations/${conversationId}`);
  return response.json();
}

export async function startConversation(title?: string, model?: ModelType): Promise<{ conversation: Conversation, welcome_message: Message }> {
  const response = await fetchWithAuth(`${API_URL}/chat/conversations`, {
    method: 'POST',
    body: JSON.stringify({ title, model }),
  });
  return response.json();
}

export async function sendMessage(conversationId: string, content: string, model?: ModelType): Promise<{ message: Message, conversation: Conversation }> {
  const response = await fetchWithAuth(`${API_URL}/chat/messages`, {
    method: 'POST',
    body: JSON.stringify({ conversation_id: conversationId, content, model }),
  });
  return response.json();
}

export async function streamMessage(conversationId: string, content: string, model?: ModelType): Promise<ReadableStream<Uint8Array> | null> {
  const response = await fetchWithAuth(`${API_URL}/chat/messages/stream`, {
    method: 'POST',
    body: JSON.stringify({ conversation_id: conversationId, content, model }),
  });
  
  return response.body;
}

export async function summarizeConversation(conversationId: string): Promise<{ summary: string }> {
  const response = await fetchWithAuth(`${API_URL}/chat/conversations/${conversationId}/summarize`, {
    method: 'POST',
  });
  return response.json();
}

// Insights API
export async function getUserInsights() {
  const response = await fetchWithAuth(`${API_URL}/insights`);
  return response.json();
}

export async function getUserSummary() {
  const response = await fetchWithAuth(`${API_URL}/insights/summary`);
  return response.json();
}

export async function getKnowledgeGraph() {
  const response = await fetchWithAuth(`${API_URL}/insights/graph`);
  return response.json();
}

export async function getInsightCategories() {
  const response = await fetchWithAuth(`${API_URL}/insights/categories`);
  return response.json();
}

export async function generateConversationInsights(conversationId: string) {
  const response = await fetchWithAuth(`${API_URL}/insights/conversations`, {
    method: 'POST',
    body: JSON.stringify({ conversation_id: conversationId }),
  });
  return response.json();
}
