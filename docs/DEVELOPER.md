# Developer Onboarding Guide

Welcome to the DeepIntrospect AI development team! This guide will help you understand the project architecture, set up your development environment, and understand the key components of the system.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Data Flow](#data-flow)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Project Overview

DeepIntrospect AI is a self-reflection AI chatbot that helps users understand themselves and their life patterns through AI-assisted introspection. The application has several key features:

- Deep Learning Profile: Creates a comprehensive understanding of users through conversation
- Knowledge Graph: Builds connections between information to discover patterns
- Persistent Memory: Saves conversations and insights for continuous learning
- Multi-Model Support: Integrates with both OpenAI and Anthropic LLMs
- Insights Generation: Analyzes conversations to generate meaningful insights

## Architecture Overview

The application uses a modern stack with separation between frontend and backend:

### Frontend
- **Next.js** with TypeScript for the UI
- **shadcn UI** and **Aceternity UI** for components
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Query** for data fetching

### Backend
- **FastAPI** for the REST API
- **Supabase** for database and authentication
- **Neo4j** for the knowledge graph
- **mem0** for persistent memory
- OpenAI and Anthropic integrations for LLM capabilities

### System Architecture Diagram

```
┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │
│    Frontend       │      │    Backend        │
│    (Next.js)      │◄────►│    (FastAPI)      │
│                   │      │                   │
└───────────────────┘      └──────┬────────────┘
                                  │
                                  ▼
┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │
│    Supabase       │◄────►│    LLM Services   │
│  (Auth & Database)│      │(OpenAI/Anthropic) │
│                   │      │                   │
└───────────────────┘      └───────────────────┘
        │                          │
        ▼                          ▼
┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │
│      Neo4j        │      │      mem0         │
│  (Knowledge Graph)│      │ (Memory System)   │
│                   │      │                   │
└───────────────────┘      └───────────────────┘
```

## Development Environment Setup

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- Supabase account
- Neo4j account/instance
- OpenAI API key
- Anthropic API key
- mem0 API key

### Setting Up the Frontend

1. Clone the repository
   ```bash
   git clone https://github.com/glittercowboy/deep-introspect-ai.git
   cd deep-introspect-ai
   ```

2. Install frontend dependencies
   ```bash
   cd frontend
   npm install
   ```

3. Create a `.env.local` file in the frontend directory:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start the development server
   ```bash
   npm run dev
   ```
   The frontend should now be running at http://localhost:3000

### Setting Up the Backend

1. Navigate to the backend directory
   ```bash
   cd ../backend
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
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

5. Start the backend server
   ```bash
   uvicorn main:app --reload
   ```
   The backend should now be running at http://localhost:8000

### Setting Up Supabase

1. Create a new project in Supabase
2. Create the following tables with appropriate columns:
   - `users`: For user information
   - `conversations`: For conversation metadata
   - `messages`: For message content
   - `insights`: For extracted insights

### Setting Up Neo4j

1. Create a Neo4j instance (Aura or self-hosted)
2. Use the Neo4j Browser to test connectivity
3. The application will create necessary constraints on startup

## Project Structure

### Frontend Structure

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
└── public/               # Static assets
```

### Backend Structure

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
└── main.py               # Application entry point
```

## Key Components

### Frontend Components

1. **Theme Provider**: Manages dark/light mode theming
2. **SparklesCore**: Aceternity UI component for particle animation
3. **Toast Notifications**: UI component for status messages
4. **Button**: Base UI component with various styles and variants

### Backend Components

1. **LLM Services**: 
   - `AnthropicService`: Integration with Claude models
   - `OpenAIService`: Integration with GPT models
   - `LLMFactory`: Factory pattern for switching between providers

2. **Memory Service**: 
   - Manages conversation context and history
   - Integrates with mem0 for persistent memory
   - Provides context-relevant message retrieval

3. **Knowledge Service**:
   - Manages the Neo4j knowledge graph
   - Extracts entities, concepts, beliefs, and patterns from conversations
   - Creates relationships between knowledge nodes

4. **Insights Service**:
   - Generates insights from conversations
   - Creates user summaries and knowledge visualizations
   - Processes patterns and trends in user data

5. **Chat Service**:
   - Manages chat conversations and interactions
   - Streams responses for real-time feedback
   - Processes conversation context for LLM input

## Data Flow

### Chat Flow

1. User sends a message from the frontend
2. Message is sent to the backend API (`/api/chat/[conversationId]`)
3. Backend adds user message to memory (Supabase + mem0)
4. Memory service retrieves relevant context
5. Chat service prepares context for the LLM
6. LLM service generates a response (streaming)
7. Response is sent back to frontend and added to memory
8. In the background, knowledge and insights are generated

### Insights Generation Flow

1. Chat service triggers insight processing for conversations
2. Knowledge service extracts entities, concepts, beliefs, and patterns
3. Extracted information is stored in the Neo4j knowledge graph
4. Insights service analyzes the knowledge graph
5. Insights are stored in Supabase
6. Insights are visualized on the frontend dashboard

### Authentication Flow

1. User signs up/logs in through the frontend
2. Supabase handles authentication
3. JWT token is returned and stored client-side
4. API requests include the token in Authorization header
5. Backend validates token for protected routes

## Development Workflow

1. **Create a new branch** for each feature or bug fix
   ```bash
   git checkout -b feature/feature-name
   ```

2. **Write tests** before implementing features
   ```bash
   # Frontend (Jest)
   cd frontend
   npm test
   
   # Backend (pytest)
   cd backend
   pytest
   ```

3. **Update the [TODO.md](./TODO.md)** file when completing tasks

4. **Update the [CHANGELOG.md](./CHANGELOG.md)** file for significant changes

5. **Submit a pull request** for review

## Testing

### Frontend Testing

- Jest for unit tests
- React Testing Library for component tests
- Cypress for end-to-end tests (to be implemented)

```bash
cd frontend
npm test
```

### Backend Testing

- pytest for API and service tests
- Test database fixtures for isolated testing

```bash
cd backend
pytest
```

## Troubleshooting

### Common Issues

#### Frontend

1. **Module not found errors**
   - Check your import paths, especially for `@/` imports
   - Ensure all dependencies are installed with `npm install`

2. **Styling issues with shadcn or Tailwind**
   - Clear your browser cache
   - Restart the development server
   - Check for CSS class conflicts

3. **API connection issues**
   - Confirm backend server is running
   - Check CORS configuration
   - Verify API endpoints and request formats

#### Backend

1. **Environment variables not loading**
   - Ensure `.env` file is in the correct location
   - Restart the server after changing environment variables
   - Check for typos in variable names

2. **Database connection errors**
   - Verify Supabase credentials
   - Check network connectivity to Supabase servers
   - Confirm table schemas match expected models

3. **Neo4j connection issues**
   - Confirm Neo4j instance is running
   - Check credentials and connection string
   - Verify Neo4j version compatibility

4. **LLM API errors**
   - Check API keys are valid
   - Verify API quotas have not been exceeded
   - Confirm internet connectivity

### Getting Help

- Check existing issues on GitHub
- Reach out to the team on the development Slack channel
- Document any new issues you discover in the GitHub issues section

---

This guide will be updated regularly as the project evolves. If you have suggestions for improvements, please submit a pull request!
