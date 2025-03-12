# DeepIntrospect AI

A groundbreaking self-reflection AI chatbot that learns deeply about users through conversation. It helps users understand themselves and their life patterns, facilitating personal growth through AI-assisted introspection.

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
│   ├── components/         # Reusable React components
│   ├── lib/                # Utility functions and API clients
│   └── tests/              # Frontend tests
├── backend/                # FastAPI backend application
│   ├── app/                # Main application package
│   │   ├── api/            # API endpoints and routes
│   │   ├── core/           # Core configurations
│   │   ├── db/             # Database clients
│   │   └── services/       # Business logic services
│   └── tests/              # Backend tests
└── docs/                   # Project documentation
```

## Detailed Setup Guide

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

# Create environment file
cp .env.example .env.local

# Edit .env.local with your API keys and configuration
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

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your API keys and configuration
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

1. Create a new Supabase project
2. Run the database initialization SQL scripts:
   ```bash
   cd scripts
   supabase db push
   ```
3. Set up Row Level Security (RLS) policies for each table
4. Create storage buckets if needed

#### Neo4j Setup

1. Create a Neo4j database (AuraDB or local)
2. Run initialization Cypher scripts to create constraints:
   ```cypher
   CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
   CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
   // Additional constraints in backend/app/db/neo4j.py
   ```

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

- [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md) - Detailed project architecture and standards
- [TODO List](./docs/TODO.md) - Current development tasks and progress
- [Changelog](./docs/CHANGELOG.md) - History of changes and features
- [User Guide](./app/guide) - User guide for self-reflection techniques
- [API Documentation](http://localhost:8000/api/docs) - Interactive API documentation (when backend is running)

## Troubleshooting

### Common Issues

#### Frontend
- **Module not found errors**: Ensure all dependencies are installed (`npm install`)
- **Type errors**: Make sure TypeScript definitions are correct
- **API connection errors**: Verify backend is running and CORS is configured correctly

#### Backend
- **Database connection errors**: Check your connection strings in `.env`
- **API key errors**: Verify all API keys are correct and have necessary permissions
- **Dependency issues**: Ensure you're using the correct Python version (3.9+)

## Contributing

Please read the [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md) for details on our code structure and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.