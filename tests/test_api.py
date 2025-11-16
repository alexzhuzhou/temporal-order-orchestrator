"""
Integration tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from api.server import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_temporal_client():
    """Mock Temporal client for testing"""
    mock_client = AsyncMock()
    return mock_client


class TestAPIEndpoints:
    """Tests for API endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns health check"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Order Orchestration API"
        assert data["status"] == "running"

    @patch('api.server.temporal_client')
    def test_start_order_endpoint(self, mock_client_global, client):
        """Test starting a new order"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.id = "test-order-123"
        mock_handle.result_run_id = "run-123"

        mock_client = AsyncMock()
        mock_client.start_workflow = AsyncMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        response = client.post(
            "/orders/test-order-123/start",
            json={"payment_id": "test-payment-123"}
        )

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["payment_id"] == "test-payment-123"
        assert data["workflow_id"] == "test-order-123"
        assert "started successfully" in data["message"].lower()

    @patch('api.server.temporal_client')
    def test_cancel_order_endpoint(self, mock_client_global, client):
        """Test cancelling an order"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.signal = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        response = client.post("/orders/test-order-123/signals/cancel")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["signal"] == "cancel_order"
        assert data["status"] == "sent"

    @patch('api.server.temporal_client')
    def test_update_address_endpoint(self, mock_client_global, client):
        """Test updating shipping address"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.signal = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        address = {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA"
        }
        response = client.post(
            "/orders/test-order-123/signals/update-address",
            json=address
        )

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["signal"] == "update_address"
        assert data["status"] == "sent"
        assert data["address"]["street"] == "123 Main St"

    @patch('api.server.temporal_client')
    def test_approve_order_endpoint(self, mock_client_global, client):
        """Test approving an order"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.signal = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        response = client.post("/orders/test-order-123/signals/approve")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["signal"] == "approve_order"
        assert data["status"] == "sent"

    @patch('api.server.temporal_client')
    def test_get_status_endpoint(self, mock_client_global, client):
        """Test getting order status"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.query = AsyncMock(return_value={
            "state": "AWAITING_MANUAL_APPROVAL",
            "cancelled": False,
            "manual_review_approved": False,
            "last_error": None
        })

        mock_description = MagicMock()
        mock_description.status.name = "RUNNING"
        mock_handle.describe = AsyncMock(return_value=mock_description)

        mock_client = AsyncMock()
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        response = client.get("/orders/test-order-123/status")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["workflow_state"] == "AWAITING_MANUAL_APPROVAL"
        assert data["is_running"] is True

    @patch('api.server.temporal_client')
    def test_get_result_endpoint(self, mock_client_global, client):
        """Test getting workflow result"""
        # Setup mock
        mock_handle = AsyncMock()
        mock_handle.result = AsyncMock(return_value="DISPATCHED")

        mock_client = AsyncMock()
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        # Patch the global client
        import api.server
        api.server.temporal_client = mock_client

        # Make request
        response = client.get("/orders/test-order-123/result")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "test-order-123"
        assert data["result"] == "DISPATCHED"

    def test_workflow_not_found(self, client):
        """Test handling of workflow not found"""
        # Mock temporal client not initialized
        import api.server
        api.server.temporal_client = None

        # Make request
        response = client.post("/orders/nonexistent/signals/cancel")

        # Should return error
        assert response.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
