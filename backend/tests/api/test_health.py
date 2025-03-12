"""
Tests for the health check endpoint.
"""
import pytest
from fastapi import status
from httpx import AsyncClient

@pytest.mark.api
class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test the health check endpoint."""
        # Act
        response = await async_client.get("/api/health")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
