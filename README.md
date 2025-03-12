# DeepIntrospect AI

A groundbreaking self-reflection AI chatbot that learns deeply about users through conversation. It helps users understand themselves and their life patterns, facilitating personal growth through AI-assisted introspection.

## Overview

DeepIntrospect AI creates a comprehensive understanding of users through natural conversation, building connections between information in a knowledge graph, and provides insights that help with personal growth and self-understanding.

## Core Features

- **Deep Learning Profile**: The chatbot creates a comprehensive understanding of the user through natural conversation
- **Multi-Model Support**: Switch between OpenAI and Anthropic models based on your preference
- **Knowledge Graph**: Behind the scenes, a Neo4j knowledge graph builds connections between user information
- **RAG Implementation**: Retrieval-Augmented Generation for hyper-optimized context retrieval
- **Persistent Memory**: Conversations and insights are saved for continuous learning
- **Dark Mode UI**: Beautiful, modern interface built with Next.js, shadcn UI, and Aceternity

## Tech Stack

### Frontend
- Next.js
- shadcn UI
- Aceternity UI
- TypeScript
- Framer Motion

### Backend
- Python (FastAPI)
- Supabase (Database & Authentication)
- mem0 (Persistent Memory)
- Neo4j (Knowledge Graph)
- LangChain/LlamaIndex (RAG Implementation)

### AI LLM Integration
- OpenAI API
- Anthropic API

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- Supabase account
- Neo4j account/instance
- OpenAI API key
- Anthropic API key

### Installation

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

3. Install backend dependencies
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables
   - Create a `.env.local` file in the frontend directory
   - Create a `.env` file in the backend directory
   - Add the necessary API keys and configuration values

5. Start the development servers
   - Frontend: `npm run dev` (in the frontend directory)
   - Backend: `uvicorn main:app --reload` (in the backend directory)

## Documentation

- [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md)
- [TODO List](./docs/TODO.md)
- [Changelog](./docs/CHANGELOG.md)

## Contributing

Please read the [Project Instructions](./docs/PROJECT_INSTRUCTIONS.md) for details on our code structure and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.