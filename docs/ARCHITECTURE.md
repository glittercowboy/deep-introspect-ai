# DeepIntrospect AI - Architecture Documentation

This document provides detailed information about the architecture, data models, and system flows of the DeepIntrospect AI application.

## Table of Contents

- [System Architecture](#system-architecture)
- [Data Model](#data-model)
- [Authentication Flow](#authentication-flow)
- [Conversation Processing Flow](#conversation-processing-flow)
- [Insights Generation Flow](#insights-generation-flow)
- [Knowledge Graph Architecture](#knowledge-graph-architecture)
- [Memory System](#memory-system)

## System Architecture

DeepIntrospect AI follows a client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│        Client Layer             │      │        Server Layer             │
│                                 │      │                                 │
│  ┌─────────────┐ ┌─────────────┐│      │ ┌─────────────┐ ┌─────────────┐ │
│  │ Next.js UI  │ │  Zustand    ││      │ │  FastAPI    │ │   Pydantic  │ │
│  │ Components  │ │   Store     ││      │ │  Endpoints  │ │   Models    │ │
│  └─────────────┘ └─────────────┘│      │ └─────────────┘ └─────────────┘ │
│           │            │        │      │        │              │        │
│           ▼            ▼        │      │        ▼              ▼        │
│  ┌─────────────┐ ┌─────────────┐│      │ ┌─────────────┐ ┌─────────────┐ │
│  │ React Query │ │ TypeScript  ││      │ │  Services   │ │  Database   │ │
│  │    Hooks    │ │   Types     ││      │ │   Layer     │ │   Access    │ │
│  └─────────────┘ └─────────────┘│      │ └─────────────┘ └─────────────┘ │
└─────────────────────────────────┘      └─────────────────────────────────┘
            │                                         │
            ▼                                         ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│       Transport Layer           │      │       External Services         │
│                                 │      │                                 │
│  ┌─────────────────────────────┐│      │ ┌─────────────┐ ┌─────────────┐ │
│  │        REST API              │◄─────┼─►│  Supabase   │ │   Neo4j     │ │
│  │     Communication            │      │ │  Database   │ │  Knowledge   │ │
│  └─────────────────────────────┘│      │ └─────────────┘ └─────────────┘ │
└─────────────────────────────────┘      │                                 │
                                         │ ┌─────────────┐ ┌─────────────┐ │
                                         │ │    mem0     │ │ OpenAI/     │ │
                                         │ │   Memory    │ │ Anthropic   │ │
                                         │ └─────────────┘ └─────────────┘ │
                                         └─────────────────────────────────┘
```

### Frontend Architecture

The frontend follows a component-based architecture using Next.js with TypeScript:

```
┌────────────────────────────────────────────────────────────────┐
│                         Next.js App                            │
│                                                                │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │     Pages       │   │    Components   │   │    Hooks     │  │
│  │                 │   │                 │   │              │  │
│  │ - Homepage      │   │ - Chat UI       │   │ - useChat    │  │
│  │ - Chat          │   │ - Insights      │   │ - useAuth    │  │
│  │ - Dashboard     │   │ - Knowledge     │   │ - useInsights│  │
│  │ - Settings      │   │ - UI Components │   │ - useStore   │  │
│  └─────────────────┘   └─────────────────┘   └──────────────┘  │
│                                                                │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │     API         │   │     Store       │   │   Utilities  │  │
│  │                 │   │                 │   │              │  │
│  │ - fetchMessages │   │ - authStore     │   │ - formatters │  │
│  │ - sendMessage   │   │ - chatStore     │   │ - validators │  │
│  │ - getInsights   │   │ - insightsStore │   │ - helpers    │  │
│  │ - getGraph      │   │ - settingsStore │   │ - constants  │  │
│  └─────────────────┘   └─────────────────┘   └──────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Backend Architecture

The backend uses a layered architecture with clear separation of concerns:

```
┌────────────────────────────────────────────────────────────────┐
│                         FastAPI App                            │
│                                                                │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │     Routes      │   │     Models      │   │  Dependencies │  │
│  │                 │   │                 │   │              │  │
│  │ - /auth         │   │ - UserModels    │   │ - get_current│  │
│  │ - /chat         │   │ - ChatModels    │   │   _user      │  │
│  │ - /insights     │   │ - InsightModels │   │ - get_db     │  │
│  │ - /users        │   │ - ResponseModels│   │ - validate   │  │
│  └─────────────────┘   └─────────────────┘   └──────────────┘  │
│                                                                │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │    Services     │   │   Database      │   │    Core      │  │
│  │                 │   │                 │   │              │  │
│  │ - ChatService   │   │ - SupabaseClient│   │ - config     │  │
│  │ - MemoryService │   │ - Neo4jClient   │   │ - security   │  │
│  │ - LLMService    │   │                 │   │ - exceptions │  │
│  │ - InsightService│   │                 │   │ - logging    │  │
│  └─────────────────┘   └─────────────────┘   └──────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Data Model

### Supabase Tables

#### Users Table
```
Table: users
Columns:
- id (UUID, primary key)
- email (String, unique)
- created_at (Timestamp)
- last_login (Timestamp)
- display_name (String)
- profile_image_url (String)
- settings (JSON)
```

#### Conversations Table
```
Table: conversations
Columns:
- id (UUID, primary key)
- user_id (UUID, foreign key -> users.id)
- title (String)
- created_at (Timestamp)
- updated_at (Timestamp)
- model (String) - "openai" or "anthropic"
- metadata (JSON)
```

#### Messages Table
```
Table: messages
Columns:
- id (UUID, primary key)
- conversation_id (UUID, foreign key -> conversations.id)
- role (String) - "user" or "assistant"
- content (Text)
- created_at (Timestamp)
- metadata (JSON)
```

#### Insights Table
```
Table: insights
Columns:
- id (UUID, primary key)
- user_id (UUID, foreign key -> users.id)
- conversation_id (UUID, foreign key -> conversations.id)
- type (String) - "belief", "value", "pattern", etc.
- content (Text)
- evidence (Text)
- created_at (Timestamp)
- confidence (Float)
- metadata (JSON)
```

### Neo4j Knowledge Graph

The knowledge graph uses the following node types:

- **User**: Represents a user of the system
- **Entity**: Named entities like people, places, organizations
- **Concept**: Abstract ideas and topics
- **Belief**: User's beliefs about the world
- **Value**: Principles important to the user
- **Pattern**: Recurring behaviors or thought processes
- **Trait**: Personality characteristics
- **Goal**: User's objectives and aspirations

Relationships between nodes include:

- `KNOWS_ABOUT`: User to Entity
- `HAS_KNOWLEDGE_OF`: User to Concept
- `HAS_BELIEF`: User to Belief
- `HAS_VALUE`: User to Value
- `HAS_PATTERN`: User to Pattern
- `RELATED_TO`: Between any node types
- `CONTRADICTS`: Between beliefs or values
- `SUPPORTS`: Between nodes that reinforce each other

## Authentication Flow

```
┌────────────┐        ┌────────────┐        ┌────────────┐
│            │        │            │        │            │
│  Frontend  │        │  Backend   │        │  Supabase  │
│            │        │            │        │            │
└─────┬──────┘        └─────┬──────┘        └─────┬──────┘
      │                     │                     │
      │  User Login         │                     │
      ├──────────────────►  │                     │
      │                     │                     │
      │                     │  Authentication     │
      │                     ├────────────────────►│
      │                     │                     │
      │                     │                     │
      │                     │  JWT Token          │
      │                     │◄────────────────────┤
      │                     │                     │
      │  Return JWT Token   │                     │
      │◄──────────────────  │                     │
      │                     │                     │
      │  Store Token        │                     │
      ├─┐                   │                     │
      │ │                   │                     │
      │◄┘                   │                     │
      │                     │                     │
      │  API Request with   │                     │
      │  Authorization      │                     │
      ├──────────────────►  │                     │
      │                     │                     │
      │                     │  Validate Token     │
      │                     ├─┐                   │
      │                     │ │                   │
      │                     │◄┘                   │
      │                     │                     │
      │  API Response       │                     │
      │◄──────────────────  │                     │
      │                     │                     │
```

1. User enters credentials in the frontend
2. Frontend sends credentials to backend
3. Backend authenticates with Supabase
4. Supabase validates and returns JWT token
5. Backend forwards token to frontend
6. Frontend stores token (localStorage/sessionStorage)
7. Frontend includes token in Authorization header for subsequent requests
8. Backend validates token and authorizes requests

## Conversation Processing Flow

```
┌────────────┐        ┌────────────┐        ┌────────────┐        ┌────────────┐
│            │        │            │        │            │        │            │
│  Frontend  │        │  Backend   │        │    LLM     │        │  Storage   │
│            │        │            │        │ Service    │        │ Services   │
└─────┬──────┘        └─────┬──────┘        └─────┬──────┘        └─────┬──────┘
      │                     │                     │                     │
      │  Send User Message  │                     │                     │
      ├──────────────────►  │                     │                     │
      │                     │                     │                     │
      │                     │  Store User Message │                     │
      │                     ├────────────────────────────────────────► │
      │                     │                     │                     │
      │                     │  Get Context        │                     │
      │                     ├────────────────────────────────────────► │
      │                     │                     │                     │
      │                     │  Return Context     │                     │
      │                     │◄────────────────────────────────────────┤ │
      │                     │                     │                     │
      │                     │  Generate Response  │                     │
      │                     ├────────────────────►│                     │
      │                     │                     │                     │
      │                     │  Stream Response    │                     │
      │                     │◄────────────────────┤                     │
      │                     │                     │                     │
      │  Stream Response    │                     │                     │
      │◄──────────────────  │                     │                     │
      │                     │                     │                     │
      │                     │  Store Assistant    │                     │
      │                     │  Message            │                     │
      │                     ├────────────────────────────────────────► │
      │                     │                     │                     │
      │                     │  Process Insights   │                     │
      │                     │  (Background)       │                     │
      │                     ├─┐                   │                     │
      │                     │ │                   │                     │
      │                     │◄┘                   │                     │
      │                     │                     │                     │
```

1. User sends message from frontend
2. Backend receives message and stores it (Supabase + mem0)
3. Backend retrieves relevant conversation context
4. Backend sends context and user message to LLM service
5. LLM generates response and streams back to backend
6. Backend streams response to frontend in real-time
7. Backend stores assistant response
8. In the background, conversation is processed for insights

## Insights Generation Flow

```
┌────────────┐        ┌────────────┐        ┌────────────┐        ┌────────────┐
│            │        │            │        │            │        │            │
│  Chat      │        │ Knowledge  │        │  Insights  │        │  Storage   │
│ Service    │        │ Service    │        │  Service   │        │ Services   │
└─────┬──────┘        └─────┬──────┘        └─────┬──────┘        └─────┬──────┘
      │                     │                     │                     │
      │ Process Conversation│                     │                     │
      ├────────────────────►│                     │                     │
      │                     │                     │                     │
      │                     │ Extract Entities    │                     │
      │                     ├─┐                   │                     │
      │                     │ │                   │                     │
      │                     │◄┘                   │                     │
      │                     │                     │                     │
      │                     │ Extract Concepts    │                     │
      │                     ├─┐                   │                     │
      │                     │ │                   │                     │
      │                     │◄┘                   │                     │
      │                     │                     │                     │
      │                     │ Extract Beliefs     │                     │
      │                     ├─┐                   │                     │
      │                     │ │                   │                     │
      │                     │◄┘                   │                     │
      │                     │                     │                     │
      │                     │ Extract Patterns    │                     │
      │                     ├─┐                   │                     │
      │                     │ │                   │                     │
      │                     │◄┘                   │                     │
      │                     │                     │                     │
      │                     │ Store in Neo4j      │                     │
      │                     ├────────────────────────────────────────► │
      │                     │                     │                     │
      │                     │                     │                     │
      │                     │ Generate Insights   │                     │
      │                     ├────────────────────►│                     │
      │                     │                     │                     │
      │                     │                     │ Analyze Knowledge   │
      │                     │                     ├────────────────────►│
      │                     │                     │                     │
      │                     │                     │ Return Knowledge    │
      │                     │                     │◄────────────────────┤
      │                     │                     │                     │
      │                     │                     │ Create Insights     │
      │                     │                     ├─┐                   │
      │                     │                     │ │                   │
      │                     │                     │◄┘                   │
      │                     │                     │                     │
      │                     │                     │ Store Insights      │
      │                     │                     ├────────────────────►│
      │                     │                     │                     │
```

1. Chat service initiates background insight processing
2. Knowledge service extracts entities, concepts, beliefs, and patterns
3. Knowledge service stores information in Neo4j graph database
4. Insights service analyzes the knowledge graph
5. Insights service generates insights from patterns and relationships
6. Insights are stored in Supabase for retrieval

## Knowledge Graph Architecture

The knowledge graph uses a property graph model in Neo4j:

```
                          ┌─────────────┐
                          │   User      │
                          │             │
                          └─────┬───────┘
                                │
            ┌─────────────┬─────┴─────┬─────────────┬─────────────┐
            │             │           │             │             │
     ┌──────▼─────┐ ┌─────▼────┐ ┌────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
     │  Entity    │ │ Concept  │ │ Belief   │ │ Value     │ │ Pattern   │
     │            │ │          │ │          │ │           │ │           │
     └──────┬─────┘ └─────┬────┘ └────┬─────┘ └─────┬─────┘ └─────┬─────┘
            │             │           │             │             │
            └─────────────┴──────┬────┴─────────────┴─────────────┘
                                 │
                         ┌───────▼───────┐
                         │ Relationships │
                         └───────────────┘
```

The Neo4j graph allows for:

1. Connecting related concepts and entities
2. Identifying patterns across conversations
3. Finding contradictions in beliefs and values
4. Tracking changes in user's perspective over time
5. Visualizing interconnected knowledge

## Memory System

The memory system uses a dual approach:

1. **Database Memory**: Traditional storage in Supabase
2. **Semantic Memory**: Context-aware memory using mem0

```
┌────────────────────────────────────────────────────────────────┐
│                        Memory System                           │
│                                                                │
│  ┌─────────────────┐                   ┌─────────────────┐     │
│  │   Short-term    │                   │   Long-term     │     │
│  │     Memory      │                   │     Memory      │     │
│  │  (Conversation  │                   │  (Historical    │     │
│  │    Context)     │                   │   Knowledge)    │     │
│  └────────┬────────┘                   └────────┬────────┘     │
│           │                                     │              │
│           ▼                                     ▼              │
│  ┌─────────────────┐                   ┌─────────────────┐     │
│  │   Relevance     │                   │  Knowledge      │     │
│  │    Engine       │                   │    Graph        │     │
│  │   (mem0 RAG)    │                   │   (Neo4j)       │     │
│  └────────┬────────┘                   └────────┬────────┘     │
│           │                                     │              │
│           └─────────────────┬───────────────────┘              │
│                             │                                  │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Unified        │                         │
│                    │  Context        │                         │
│                    │  Builder        │                         │
│                    └─────────────────┘                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

The memory system provides:

1. **Context Management**: Retrieves relevant context for current conversations
2. **Semantic Search**: Finds similar past conversations based on meaning
3. **Pattern Recognition**: Identifies recurring themes and patterns
4. **Persistence**: Maintains user information across sessions
5. **Summarization**: Creates concise summaries of past conversations

---

This architecture documentation is maintained by the DeepIntrospect AI development team. For questions or suggestions, please reach out to the architecture team.
