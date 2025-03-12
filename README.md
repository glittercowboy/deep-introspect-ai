# DeepIntrospect AI

A groundbreaking self-reflection AI chatbot that learns deeply about users through conversation. It helps users understand themselves and their life patterns, facilitating personal growth through AI-assisted introspection.

<div align="center">
  <kbd>
    <img src="https://github.com/glittercowboy/deep-introspect-ai/assets/username/screenshot.png" alt="DeepIntrospect AI Screenshot" width="600"/>
  </kbd>
  <p><em>Note: Replace with actual screenshot when available</em></p>
</div>

## Overview

DeepIntrospect AI creates a comprehensive understanding of users through natural conversation, building connections between information in a knowledge graph, and provides insights that help with personal growth and self-understanding.

## Core Features

- **Deep Learning Profile**: Creates a comprehensive understanding of users through natural conversation
- **Multi-Model Support**: Switch between OpenAI and Anthropic models based on preference
- **Knowledge Graph**: Neo4j knowledge graph builds connections between user information
- **RAG Implementation**: Retrieval-Augmented Generation for hyper-optimized context retrieval
- **Persistent Memory**: Conversations and insights are saved for continuous learning
- **Real-time Notifications**: Alerts for new insights and conversation updates
- **Interactive Visualizations**: Knowledge graph visualization and insight exploration
- **User Self-Reflection Guide**: Comprehensive resources for effective self-reflection
- **Dark/Light Mode**: Beautiful, modern interface with theme customization
- **Mobile Responsive**: Fully responsive design that works on all devices

## Tech Stack

### Frontend
- Next.js 14 with App Router
- TypeScript
- shadcn UI component library
- Aceternity UI for animations
- Tailwind CSS
- Zustand for state management
- React Force Graph for visualizations
- Jest & React Testing Library

### Backend
- Python with FastAPI
- Supabase for database & authentication
- Neo4j for knowledge graph
- mem0 for persistent memory
- LangChain/LlamaIndex for RAG
- WebSockets for real-time updates
- pytest for testing

### AI LLM Integration
- OpenAI API (GPT-4)
- Anthropic API (Claude)

## Project Structure

```
project/
├── frontend/               # Next.js frontend application
│   ├── app/                # App router pages
│   │   ├── api/            # API routes
│   │   ├── chat/           # Chat interface
│   │   ├── dashboard/      # User dashboard
│   │   ├── insights/       # User insights
│   │   ├── settings/       # User settings
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Home page
│   ├── components/         # Reusable React components
│   │   ├── ui/             # UI components
│   │   ├── layout/         # Layout components 
│   │   ├── chat/           # Chat components
│   │   └── insights/       # Insights components
│   ├── lib/                # Utility functions and API clients
│   └── tests/              # Frontend tests
├── backend/                # FastAPI backend application
│   ├── app/                # Main application package
│   │   ├── api/            # API endpoints and routes
│   │   ├── core/           # Core configurations
│   │   ├── db/             # Database clients
│   │   └── services/       # Business logic services
│   │       ├── chat/       # Chat service
│   │       ├── insights/   # Insights service
│   │       ├── knowledge/  # Knowledge graph service
│   │       ├── llm/        # LLM integration
│   │       └── memory/     # Memory service
│   └── tests/              # Backend tests
└── docs/                   # Project documentation
    ├── ARCHITECTURE.md     # System architecture documentation
    ├── CHANGELOG.md        # History of changes
    ├── DEVELOPER.md        # Developer onboarding guide
    ├── PROJECT_INSTRUCTIONS.md # Project architecture and standards
    └── TODO.md             # Development tasks and progress
```

## Comprehensive Setup Guide

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- Supabase account
- Neo4j database (cloud or local)
- OpenAI API key
- Anthropic API key
- mem0 API key

### Step 1: Clone Repository

```bash
git clone https://github.com/glittercowboy/deep-introspect-ai.git
cd deep-introspect-ai
```

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file (if not using .env.example)
touch .env.local
```

Required variables in `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd ../backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file (if not using .env.example)
touch .env
```

Required variables in `.env`:
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

### Step 4: Database Setup

#### Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Create the following tables in the Supabase dashboard:

**Users Table**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE,
  display_name TEXT,
  profile_image_url TEXT,
  settings JSONB DEFAULT '{}'::JSONB
);
```

**Conversations Table**
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  title TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  model TEXT DEFAULT 'anthropic',
  metadata JSONB DEFAULT '{}'::JSONB
);
```

**Messages Table**
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::JSONB
);
```

**Insights Table**
```sql
CREATE TABLE insights (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  conversation_id UUID REFERENCES conversations(id),
  type TEXT NOT NULL,
  content TEXT NOT NULL,
  evidence TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  confidence FLOAT DEFAULT 0.5,
  metadata JSONB DEFAULT '{}'::JSONB
);
```

3. Set up Row Level Security (RLS) policies for each table

#### Neo4j Setup

1. Create a Neo4j database on [Neo4j Aura](https://neo4j.com/cloud/aura/) or install locally
2. Copy the connection URI, username, and password
3. The application will create necessary constraints on startup (defined in `backend/app/db/neo4j.py`)

#### mem0 Setup

1. Sign up for mem0 API at [mem0.ai](https://mem0.ai)
2. Get your API key from the dashboard
3. Add it to your backend `.env` file

### Step 5: Start Development Servers

#### Frontend
```bash
cd frontend
npm run dev
```
Frontend will be available at: http://localhost:3000

#### Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend API will be available at: http://localhost:8000

API documentation will be at: http://localhost:8000/api/docs

## Data Flow Architecture

DeepIntrospect AI follows a clean architecture pattern with clear separation between frontend and backend:

```
┌────────────┐        ┌────────────┐        ┌────────────┐
│            │        │            │        │            │
│  Frontend  │◄─────► │  Backend   │◄─────► │ Databases  │
│  (Next.js) │        │  (FastAPI) │        │ & Services │
│            │        │            │        │            │
└────────────┘        └────────────┘        └────────────┘
```

When a user sends a message to the AI, the following happens:

1. Frontend sends message to backend API
2. Message is stored in Supabase and mem0
3. Relevant context is retrieved from memory system
4. LLM (OpenAI/Anthropic) generates a response
5. Response is streamed back to the user in real-time
6. In the background, the message is analyzed to extract:
   - Entities (people, places, things)
   - Concepts (abstract ideas)
   - Beliefs (what the user believes to be true)
   - Values (what matters to the user)
   - Patterns (recurring behaviors or thoughts)
7. This extracted information is stored in the Neo4j knowledge graph
8. Insights are generated from patterns in the knowledge graph
9. Insights are stored in Supabase for display on the dashboard

For a detailed architecture overview, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Running Tests

### Frontend Tests
```bash
cd frontend
npm test                # Run all tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Generate test coverage report
```

### Backend Tests
```bash
cd backend
python -m pytest                   # Run all tests
python -m pytest tests/api/        # Run API tests only
python -m pytest tests/services/   # Run service tests only
python -m pytest -v                # Verbose output
```

## Development Workflow

1. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement your changes** following the project's code style
   - Frontend: TypeScript with ESLint rules
   - Backend: PEP 8 style guide with type hints

3. **Write tests** for your changes
   - Frontend: Jest + React Testing Library
   - Backend: pytest

4. **Run the tests** to ensure your changes don't break existing functionality
   ```bash
   # Frontend
   cd frontend
   npm test
   
   # Backend
   cd backend
   python -m pytest
   ```

5. **Update documentation** if necessary
   - Update README.md if adding new features
   - Update CHANGELOG.md with your changes
   - Update TODO.md to mark completed tasks

6. **Create a pull request** to the `main` branch
   - Provide a clear description of your changes
   - Reference any related issues

## Additional Resources

- [Developer Onboarding Guide](./docs/DEVELOPER.md) - Comprehensive guide for new developers
- [Architecture Documentation](./docs/ARCHITECTURE.md) - Detailed system architecture
- [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md) - Project architecture and standards
- [TODO List](./docs/TODO.md) - Current development tasks and progress
- [Changelog](./docs/CHANGELOG.md) - History of changes and features
- [API Documentation](http://localhost:8000/api/docs) - Interactive API docs (when backend is running)

## Troubleshooting

### Common Issues

#### Frontend

- **Module not found errors**
  - Ensure all dependencies are installed (`npm install`)
  - Check import paths, especially for `@/` imports
  - Verify tsconfig.json paths configuration

- **Type errors**
  - Make sure TypeScript definitions are correct
  - Run `npm run typecheck` to validate types

- **API connection errors**
  - Verify backend is running and CORS is configured correctly
  - Check that API URL in .env.local is correct
  - Inspect browser console for specific error messages

#### Backend

- **Database connection errors**
  - Check your connection strings in `.env`
  - Verify database credentials have correct permissions
  - Ensure database tables are created with the right schema

- **API key errors**
  - Verify all API keys are correct and have necessary permissions
  - Check for API rate limiting or quota issues

- **Dependency issues**
  - Ensure you're using the correct Python version (3.9+)
  - Try recreating virtual environment if dependencies conflict

For more detailed troubleshooting, see the [Developer Onboarding Guide](./docs/DEVELOPER.md).

## Contributing

Please read the [Developer Onboarding Guide](./docs/DEVELOPER.md) and [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md) for details on our code structure and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.