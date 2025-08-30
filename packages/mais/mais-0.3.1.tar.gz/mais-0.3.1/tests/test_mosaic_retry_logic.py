"""Tests for MosaicModelRepository retry logic."""

from unittest.mock import Mock, patch

import pytest

from mais.infrastructure.api.mosaic_model_repository import (
    MosaicModelRepository,
)


class TestMosaicRetryLogic:
    """Test cases for the retry logic in MosaicModelRepository."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock MosaicModelRepository instance."""
        repo = MosaicModelRepository(
            api_url="https://api.example.com",
            api_token="test-token",
            enabled=True,
        )
        repo._quickscan_results = {
            "supplier/test-model": {"object_id": "test-object-id"}
        }
        return repo

    @patch("time.sleep")
    @patch("requests.get")
    def test_retry_on_pending_status(
        self, mock_get, mock_sleep, mock_repository
    ):
        """Test that the method returns None when first response has pending status."""
        pending_response = {
            "data": {
                "name": "test-model",
                "supplier": "test-supplier",
                "version": "1.0",
                "supplierCountry": "US",
                "riskOverview": {
                    "riskScore": "pending",
                    "findings": [],
                },
            }
        }

        # Configure mock to return pending
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = pending_response
        mock_get.return_value = mock_response
        mock_sleep.return_value = None

        # Test
        result = mock_repository.get_model_data_from_model_analysis(
            "supplier/test-model"
        )

        assert result is not None
        assert mock_get.call_count == 5

    @patch("time.sleep")
    @patch("requests.get")
    def test_max_retries_reached(self, mock_get, mock_sleep, mock_repository):
        """Test that the method returns Unknown when max retries are reached."""
        # Always return pending
        pending_response = {
            "data": {
                "name": "test-model",
                "supplier": "test-supplier",
                "version": "1.0",
                "supplierCountry": "US",
                "riskOverview": {
                    "riskScore": "pending",
                    "findings": [],
                },
            }
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = pending_response
        mock_get.return_value = mock_response
        mock_sleep.return_value = None

        # Test
        result = mock_repository.get_model_data_from_model_analysis(
            "supplier/test-model"
        )

        assert result is not None

        assert mock_get.call_count == 5

        # Should have slept once
        assert mock_sleep.call_count == 5

    @patch("requests.get")
    def test_no_retry_on_success(self, mock_get, mock_repository):
        """Test that the method doesn't retry when analysis is complete."""
        # Return complete on first try
        complete_response = {
            "data": {
                "name": "test-model",
                "supplier": "test-supplier",
                "version": "1.0",
                "supplierCountry": "US",
                "riskOverview": {
                    "riskScore": "Low",
                    "findings": [],
                },
            }
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = complete_response
        mock_get.return_value = mock_response

        # Test
        result = mock_repository.get_model_data_from_model_analysis(
            "supplier/test-model"
        )

        # Should return immediately
        assert result is not None
        assert result["risk_score"] == "Low"
        assert result["findings"] == []

        # Should have made only 1 API call
        assert mock_get.call_count == 1

    @patch("requests.get")
    def test_no_retry_on_404(self, mock_get, mock_repository):
        """Test that the method doesn't retry on 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test
        result = mock_repository.get_model_data_from_model_analysis(
            "supplier/test-model"
        )

        # Should return None immediately
        assert result is None

        # Should have made only 1 API call
        assert mock_get.call_count == 1

    @patch("time.sleep")
    @patch("requests.get")
    def test_no_model_data_in_response(
        self, mock_get, mock_sleep, mock_repository
    ):
        """Test handling when response has no model data."""

        empty_response = {"data": {}}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = empty_response
        mock_get.return_value = mock_response
        mock_sleep.return_value = None

        # Test
        result = mock_repository.get_model_data_from_model_analysis(
            "supplier/test-model"
        )
        assert result is not None
        assert result["risk_score"] == "Unknown"
        assert result["findings"] == []

        # Should retry all 5 times since empty data means analysis not complete
        assert mock_get.call_count == 5
