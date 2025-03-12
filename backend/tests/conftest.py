"""
Pytest configuration and fixtures.
"""
import asyncio
import os
from datetime import datetime
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
import unittest.mock as mock
from typing import AsyncGenerator, Generator

# Set test environment
os.environ["ENV"] = "test"

# Mock data
MOCK_USER_ID = "test-user-id"
MOCK_USER_EMAIL = "test@example.com"
MOCK_CONVERSATION_ID = "test-conversation-id"

@pytest.fixture(scope="session")
def app() -> FastAPI:
    """
    Create a FastAPI app instance for testing.
    """
    from main import app as fastapi_app
    return fastapi_app

@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Create a TestClient instance for synchronous testing.
    """
    with TestClient(app) as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an AsyncClient instance for asynchronous testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def mock_supabase():
    """
    Mock Supabase client.
    """
    with mock.patch("app.db.supabase.supabase_client") as mock_client:
        # Mock user functions
        mock_client.get_user.return_value = {
            "id": MOCK_USER_ID,
            "email": MOCK_USER_EMAIL,
            "name": "Test User",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Mock conversation functions
        mock_client.get_conversation.return_value = {
            "id": MOCK_CONVERSATION_ID,
            "user_id": MOCK_USER_ID,
            "title": "Test Conversation",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "model": "anthropic"
        }
        
        mock_client.get_conversations.return_value = [
            {
                "id": f"{MOCK_CONVERSATION_ID}-1",
                "user_id": MOCK_USER_ID,
                "title": "First Conversation",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "model": "anthropic"
            },
            {
                "id": f"{MOCK_CONVERSATION_ID}-2",
                "user_id": MOCK_USER_ID,
                "title": "Second Conversation",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "model": "openai"
            }
        ]
        
        # Mock message functions
        mock_client.get_messages.return_value = [
            {
                "id": "test-message-id-1",
                "conversation_id": MOCK_CONVERSATION_ID,
                "role": "user",
                "content": "Hello, how are you?",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "test-message-id-2",
                "conversation_id": MOCK_CONVERSATION_ID,
                "role": "assistant",
                "content": "I'm doing well! How can I help you?",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Mock insight functions
        mock_client.get_insights.return_value = [
            {
                "id": "test-insight-id-1",
                "user_id": MOCK_USER_ID,
                "conversation_id": MOCK_CONVERSATION_ID,
                "type": "belief",
                "content": "Values personal growth",
                "evidence": "User mentioned growth several times",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "test-insight-id-2",
                "user_id": MOCK_USER_ID,
                "conversation_id": MOCK_CONVERSATION_ID,
                "type": "pattern",
                "content": "Prefers thoughtful reflection",
                "evidence": "User takes time to respond thoughtfully",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Mock create functions
        mock_client.create_user.return_value = {"id": MOCK_USER_ID}
        mock_client.create_conversation.return_value = {"id": MOCK_CONVERSATION_ID}
        mock_client.create_message.side_effect = lambda data: data
        mock_client.create_insight.side_effect = lambda data: data
        
        yield mock_client

@pytest.fixture(scope="function")
def mock_neo4j():
    """
    Mock Neo4j client.
    """
    with mock.patch("app.db.neo4j.neo4j_client") as mock_client:
        # Mock node creation
        mock_client.create_user_node.return_value = True
        mock_client.create_entity_node.return_value = True
        mock_client.create_concept_node.return_value = True
        mock_client.create_relationship.return_value = True
        
        # Mock graph retrieval
        mock_client.get_user_graph.return_value = {
            "nodes": [
                {"id": MOCK_USER_ID, "label": "User", "type": "user"},
                {"id": "entity-1", "label": "Work", "type": "concept"},
                {"id": "entity-2", "label": "Growth", "type": "value"},
            ],
            "links": [
                {"source": MOCK_USER_ID, "target": "entity-1", "type": "INTERESTED_IN"},
                {"source": MOCK_USER_ID, "target": "entity-2", "type": "VALUES"},
            ]
        }
        
        # Mock pattern retrieval
        mock_client.find_patterns.return_value = [
            {
                "id": "pattern-1",
                "name": "Reflection Pattern",
                "description": "Takes time to reflect before responding",
                "confidence": 0.85
            },
            {
                "id": "pattern-2",
                "name": "Growth Mindset",
                "description": "Views challenges as opportunities",
                "confidence": 0.9
            }
        ]
        
        yield mock_client

@pytest.fixture(scope="function")
def mock_llm():
    """
    Mock LLM service.
    """
    with mock.patch("app.services.llm.factory.llm_factory") as mock_factory:
        mock_service = mock.MagicMock()
        mock_service.generate_text.return_value = "This is a generated response."
        mock_service.generate_chat.return_value = "This is a chat response."
        mock_service.count_tokens.return_value = 10
        
        # Mock streaming generator
        async def mock_stream_generator():
            chunks = ["This ", "is ", "a ", "streaming ", "response."]
            for chunk in chunks:
                yield chunk
        
        mock_service.generate_stream.return_value = mock_stream_generator()
        
        mock_factory.get_service.return_value = mock_service
        yield mock_factory
