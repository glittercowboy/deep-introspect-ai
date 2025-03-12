# Project Instructions

## Overview

DeepIntrospect AI is a self-reflection AI chatbot designed to help users understand themselves better through conversation and AI-assisted introspection. This document outlines the project architecture, coding standards, and development workflow to maintain consistency across chat sessions and development iterations.

## Architecture

### Frontend Architecture

The frontend is built with Next.js using the App Router pattern for routing. We use shadcn UI and Aceternity UI for component libraries, styled with Tailwind CSS, and animated with Framer Motion.

```
frontend/
├── app/                  # Next.js App Router structure
│   ├── api/              # API routes
│   ├── chat/             # Chat interface
│   ├── dashboard/        # User dashboard
│   ├── insights/         # User insights
│   ├── settings/         # User settings
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable components
│   ├── ui/               # UI components from shadcn
│   ├── layout/           # Layout components
│   ├── chat/             # Chat-specific components
│   └── insights/         # Insights components
├── lib/                  # Utility functions and shared code
│   ├── api/              # API client functions
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Helper functions
├── public/               # Static assets
└── styles/               # Global styles
```

### Backend Architecture

The backend is built with Python using FastAPI framework. It integrates with Supabase for authentication and database, mem0 for persistent memory, Neo4j for knowledge graph, and LangChain/LlamaIndex for RAG implementation.

```
backend/
├── app/                  # Main application package
│   ├── api/              # API endpoints
│   │   ├── routes/       # API route definitions
│   │   ├── models/       # Pydantic models for API
│   │   └── dependencies/ # API dependencies
│   ├── core/             # Core application code
│   │   ├── config.py     # Configuration settings
│   │   ├── security.py   # Authentication and security
│   │   └── exceptions.py # Custom exceptions
│   ├── db/               # Database related code
│   │   ├── supabase.py   # Supabase client
│   │   └── neo4j.py      # Neo4j client
│   ├── services/         # Business logic
│   │   ├── llm/          # LLM integration
│   │   ├── memory/       # Memory and persistence
│   │   ├── knowledge/    # Knowledge graph operations
│   │   └── insights/     # User insights generation
│   └── utils/            # Utility functions
├── tests/                # Test cases
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
└── main.py              # Application entry point
```

## Coding Standards

### Frontend

- Use TypeScript for all frontend code
- Follow the [AirBnB JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use React Query for API data fetching and caching
- Use Zustand for client-side state management
- Create reusable components in the components directory
- Use Tailwind CSS for styling
- Document components with JSDoc comments

### Backend

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all functions and methods
- Document functions and classes with docstrings
- Write unit tests for all business logic
- Use dependency injection pattern for services
- Use environment variables for configuration

## Development Workflow

1. **Create a new branch** for each feature or bug fix
2. **Write tests** before implementing features
3. **Update the [TODO.md](./TODO.md)** file when completing tasks
4. **Update the [CHANGELOG.md](./CHANGELOG.md)** file for significant changes
5. **Submit a pull request** for review

## Environment Setup

### Frontend Environment Variables (.env.local)

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables (.env)

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MEM0_API_KEY=your_mem0_api_key
```

## Deployment

- Frontend: Deploy to Vercel
- Backend: Deploy to a service like Heroku, Railway, or self-hosted
- Database: Use Supabase cloud
- Neo4j: Use Neo4j Aura or self-hosted

## Best Practices

### Security

- Never commit API keys or secrets to the repository
- Use Supabase Row Level Security for database access control
- Implement proper authentication and authorization
- Sanitize user inputs
- Use HTTPS for all API requests

### Performance

- Optimize Neo4j queries for performance
- Implement caching for frequently used data
- Use server-side rendering or static generation where appropriate
- Optimize bundle size with code splitting

### User Experience

- Implement loading states for async operations
- Provide meaningful error messages
- Ensure responsive design for all screen sizes
- Implement dark mode toggle
- Add keyboard shortcuts for common actions

This document will be updated as the project evolves to reflect current best practices and new requirements.