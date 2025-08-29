import pytest
from unittest.mock import Mock, patch
from liveramp_automation.helpers.grafana import (
    GrafanaClient,
    GrafanaAuthenticationError,
    GrafanaAPIError
)


class TestGrafanaClient:
    """Test cases for GrafanaClient class."""

    @pytest.fixture
    def mock_playwright(self):
        """Mock Playwright components."""
        with patch('liveramp_automation.helpers.grafana.sync_playwright') as mock_playwright:
            mock_p = Mock()
            mock_browser = Mock()
            mock_context = Mock()
            mock_page = Mock()
            
            mock_playwright.return_value.start.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            
            yield {
                'playwright': mock_playwright,
                'p': mock_p,
                'browser': mock_browser,
                'context': mock_context,
                'page': mock_page
            }

    @pytest.fixture
    def client_config(self):
        """Sample client configuration."""
        return {
            'username': 'test@example.com',
            'password': 'testpass',
            'base_url': 'https://test.grafana.net',
            'headless': True,
            'timeout': 30000
        }

    def test_init(self, client_config):
        """Test GrafanaClient initialization."""
        client = GrafanaClient(**client_config)
        
        assert client._username == 'test@example.com'
        assert client._password == 'testpass'
        assert client._base_url == 'https://test.grafana.net'
        assert client._headless is True
        assert client._timeout == 30000
        assert client._login_url == 'https://test.grafana.net/login'
        assert client._api_url == 'https://test.grafana.net/api/ds/query'

    def test_init_with_trailing_slash(self):
        """Test that trailing slashes are properly handled."""
        client = GrafanaClient('user', 'pass', base_url='https://test.grafana.net/')
        assert client._base_url == 'https://test.grafana.net'

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_success(self, mock_logger, mock_playwright, client_config):
        """Test successful context manager entry."""
        mock_playwright['page'].wait_for_url.return_value = None
        
        with GrafanaClient(**client_config) as client:
            assert client is not None
            assert client._p is not None
            assert client._browser is not None
            assert client._context is not None
            assert client._page is not None

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_failure(self, mock_logger, mock_playwright, client_config):
        """Test context manager entry failure."""
        mock_playwright['p'].chromium.launch.side_effect = Exception("Launch failed")
        
        with pytest.raises(GrafanaAuthenticationError, match="Failed to initialize: Launch failed"):
            with GrafanaClient(**client_config) as client:
                pass

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_exit(self, mock_logger, mock_playwright, client_config):
        """Test context manager exit."""
        mock_playwright['page'].wait_for_url.return_value = None
        
        client = GrafanaClient(**client_config)
        client._p = mock_playwright['p']
        client._browser = mock_playwright['browser']
        client._context = mock_playwright['context']
        client._page = mock_playwright['page']
        
        client.__exit__(None, None, None)
        
        mock_playwright['page'].close.assert_called_once()
        mock_playwright['context'].close.assert_called_once()
        mock_playwright['browser'].close.assert_called_once()
        mock_playwright['p'].stop.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_cleanup_with_errors(self, mock_logger, mock_playwright, client_config):
        """Test cleanup handles errors gracefully."""
        mock_playwright['page'].close.side_effect = Exception("Close failed")
        
        client = GrafanaClient(**client_config)
        client._page = mock_playwright['page']
        
        # Should not raise exception
        client._cleanup()
        mock_logger.warning.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_authentication_success(self, mock_logger, mock_playwright, client_config):
        """Test successful authentication flow."""
        # Mock successful authentication
        mock_playwright['page'].wait_for_url.return_value = None
        
        client = GrafanaClient(**client_config)
        client._page = mock_playwright['page']
        
        # Should not raise exception
        client._authenticate()

    def test_query_loki_success(self, mock_playwright, client_config):
        """Test successful Loki query."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status = 200
        mock_response.json.return_value = {"data": {"result": []}}
        
        mock_playwright['context'].request.post.return_value = mock_response
        
        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']
        
        payload = {"queries": [], "from": "now-1h", "to": "now"}
        result = client.query_loki(payload)
        
        assert result == {"data": {"result": []}}
        mock_playwright['context'].request.post.assert_called_once()

    def test_query_loki_failure(self, mock_playwright, client_config):
        """Test Loki query failure."""
        # Mock failed response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        
        mock_playwright['context'].request.post.return_value = mock_response
        
        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']
        
        payload = {"queries": [], "from": "now-1h", "to": "now"}
        
        with pytest.raises(GrafanaAPIError, match="API query failed"):
            client.query_loki(payload)

    def test_query_loki_timestamp_override(self, mock_playwright, client_config):
        """Test that timestamp overrides work correctly."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status = 200
        mock_response.json.return_value = {"data": {"result": []}}
        
        mock_playwright['context'].request.post.return_value = mock_response
        
        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']
        
        original_payload = {"queries": [], "from": "original", "to": "original"}
        result = client.query_loki(
            original_payload, 
            from_timestamp="new_from", 
            to_timestamp="new_to"
        )
        
        # Verify the original payload wasn't modified
        assert original_payload["from"] == "original"
        assert original_payload["to"] == "original"
        
        # Verify the API call used the new timestamps
        call_args = mock_playwright['context'].request.post.call_args
        sent_payload = call_args[1]['data']
        assert "new_from" in sent_payload
        assert "new_to" in sent_payload

    def test_query_loki_network_error(self, mock_playwright, client_config):
        """Test handling of network errors in Loki queries."""
        mock_playwright['context'].request.post.side_effect = Exception("Network error")
        
        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']
        
        payload = {"queries": [], "from": "now-1h", "to": "now"}
        
        with pytest.raises(GrafanaAPIError, match="API query failed: Network error"):
            client.query_loki(payload)


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_grafana_authentication_error(self):
        """Test GrafanaAuthenticationError exception."""
        error = GrafanaAuthenticationError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, Exception)

    def test_grafana_api_error(self):
        """Test GrafanaAPIError exception."""
        error = GrafanaAPIError("API failed")
        assert str(error) == "API failed"
        assert isinstance(error, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
