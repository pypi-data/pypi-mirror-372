"""Tests for the Gas Network client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from gas_network_sdk import (
    GasNetworkClient,
    Chain,
    GasNetworkError,
    APIError,
    UnsupportedChainError,
    InvalidAPIKeyError,
)


class TestGasNetworkClient:
    """Test cases for GasNetworkClient."""

    def test_client_initialization(self):
        """Test client initialization with different parameters."""
        # Default initialization
        client = GasNetworkClient()
        assert client.api_key is None
        assert client.timeout == GasNetworkClient.DEFAULT_TIMEOUT
        assert client.base_url == GasNetworkClient.BASE_URL
        
        # With API key
        client = GasNetworkClient(api_key="test_key")
        assert client.api_key == "test_key"
        
        # With custom parameters
        client = GasNetworkClient(
            api_key="test_key",
            timeout=60.0,
            base_url="https://custom.api.com",
            rpc_url="https://custom.rpc.com"
        )
        assert client.timeout == 60.0
        assert client.base_url == "https://custom.api.com"
        assert client.rpc_url == "https://custom.rpc.com"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        async with GasNetworkClient(api_key="test") as client:
            assert not client._closed
        assert client._closed

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test closing the client."""
        client = GasNetworkClient()
        assert not client._closed
        await client.close()
        assert client._closed

    def test_supported_chains(self):
        """Test supported chains static method."""
        chains = GasNetworkClient.supported_chains()
        assert Chain.ETHEREUM in chains
        assert Chain.BITCOIN in chains
        assert len(chains) == len(Chain)

    def test_chains_supporting_base_fee(self):
        """Test chains supporting base fee."""
        chains = GasNetworkClient.chains_supporting_base_fee()
        assert chains == [Chain.ETHEREUM]

    def test_chains_supporting_distribution(self):
        """Test chains supporting distribution."""
        chains = GasNetworkClient.chains_supporting_distribution()
        assert chains == [Chain.ETHEREUM]

    def test_get_api_key(self):
        """Test getting API key."""
        client = GasNetworkClient()
        assert client.get_api_key() is None
        
        client = GasNetworkClient(api_key="test_key")
        assert client.get_api_key() == "test_key"

    @pytest.mark.asyncio
    async def test_request_after_close(self):
        """Test making requests after client is closed."""
        client = GasNetworkClient()
        await client.close()
        
        with pytest.raises(GasNetworkError, match="Client has been closed"):
            await client.get_gas_prices(Chain.ETHEREUM)

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling."""
        with patch('httpx.AsyncClient.request') as mock_request:
            # Mock 401 response
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_request.return_value = mock_response
            
            async with GasNetworkClient() as client:
                with pytest.raises(InvalidAPIKeyError):
                    await client.get_gas_prices(Chain.ETHEREUM)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test timeout error handling."""
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")
            
            async with GasNetworkClient() as client:
                with pytest.raises(GasNetworkError, match="Request timed out"):
                    await client.get_gas_prices(Chain.ETHEREUM)

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network error handling."""
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")
            
            async with GasNetworkClient() as client:
                with pytest.raises(GasNetworkError, match="Network error"):
                    await client.get_gas_prices(Chain.ETHEREUM)

    @pytest.mark.asyncio
    async def test_unsupported_chain_base_fee(self):
        """Test unsupported chain for base fee estimates."""
        async with GasNetworkClient() as client:
            with pytest.raises(UnsupportedChainError) as exc_info:
                await client.get_base_fee_estimates(Chain.BITCOIN)
            
            assert exc_info.value.chain == "bitcoin"
            assert "Base fee estimates" in exc_info.value.operation

    @pytest.mark.asyncio
    async def test_unsupported_chain_distribution(self):
        """Test unsupported chain for gas distribution."""
        async with GasNetworkClient() as client:
            with pytest.raises(UnsupportedChainError) as exc_info:
                await client.get_gas_distribution(Chain.BITCOIN)
            
            assert exc_info.value.chain == "bitcoin"
            assert "Gas distribution" in exc_info.value.operation