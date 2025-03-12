# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created GitHub repository
- Created initial project documentation
- Added project instructions
- Added TODO list
- Added changelog
- Set up frontend project structure with Next.js, TypeScript, and Tailwind CSS
- Created home page with Aceternity UI components
- Added shadcn UI components (button, toast, theme provider)
- Created utility functions and theme context
- Set up backend project structure with FastAPI
- Added configuration and logging modules
- Created security utilities for JWT authentication
- Added custom exceptions and exception handlers
- Implemented Supabase client for database operations
- Implemented Neo4j client for knowledge graph operations
- Created base LLM service and implemented OpenAI and Anthropic providers
- Added LLM service factory for model switching
- Implemented memory service for conversation history and context
- Created knowledge graph service for entity and concept extraction
- Implemented insights service for generating user insights
- Added chat service with streaming response support
- Implemented dark mode theming support
- Created core database models and schemas
- Implemented knowledge extraction from conversations
- Added pattern recognition for user behavior analysis
- Created service for periodically generating user insights
- Implemented RAG system with semantic search functionality
- Added conversation context retrieval for personalized responses
- Created Auth API models and routes (login, registration, password reset)
- Created User API models and routes (profile, preferences)
- Created Chat API models and routes (conversations, messages, streaming)
- Created Insights API models and routes (insights, knowledge graph, analysis)
- Added WebSocket support for real-time chat
- Implemented streaming response endpoints for LLM responses
- Created frontend chat components (message bubble, message input, model selector)
- Built conversation list component for chat history
- Implemented chat container component that combines all chat UI elements
- Created main chat page with responsive layout
- Added frontend API client for communicating with backend
- Implemented streaming message display on frontend

### Core Features Implemented
- Multi-model LLM support with OpenAI and Anthropic
- Knowledge graph with Neo4j for building connections between user information
- Persistent memory with mem0 integration
- Natural language insights extraction
- Pattern recognition for user behavior
- Dark mode UI
- Responsive chat interface
- Streaming message responses
- Model switching (OpenAI/Anthropic)

### In Progress
- Authentication flow implementation
- Insights visualization
- User dashboard development
- Database setup and connection