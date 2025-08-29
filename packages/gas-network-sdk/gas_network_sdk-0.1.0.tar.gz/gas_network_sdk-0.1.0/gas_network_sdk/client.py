"""Main client for the Gas Network SDK."""

import asyncio
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from .exceptions import (
    APIError,
    GasNetworkError,
    InvalidAPIKeyError,
    NetworkError,
    TimeoutError,
    UnsupportedChainError,
)
from .types import (
    BaseFeeResponse,
    Chain,
    DistributionResponse,
    GasPriceEstimate,
    GasPriceResponse,
    OraclePayload,
)


class GasNetworkClient:
    """Client for interacting with the Gas Network API."""
    
    BASE_URL = "https://api.blocknative.com"
    RPC_URL = "https://rpc.gas.network"
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        base_url: Optional[str] = None,
        rpc_url: Optional[str] = None,
    ) -> None:
        """Initialize the Gas Network client.
        
        Args:
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            base_url: Optional custom base URL
            rpc_url: Optional custom RPC URL
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self.rpc_url = rpc_url or self.RPC_URL
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "gas-network-sdk-python/0.1.0",
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Create HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
        )
        self._closed = False
    
    async def __aenter__(self) -> "GasNetworkClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if not self._closed:
            await self._client.aclose()
            self._closed = True
    
    def __del__(self) -> None:
        """Destructor to ensure client is closed."""
        if not self._closed:
            try:
                asyncio.create_task(self.close())
            except RuntimeError:
                # Event loop is not running
                pass
    
    async def _make_request(
        self,
        method: str,
        url: str,
        base_url: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make an HTTP request with error handling.
        
        Args:
            method: HTTP method
            url: Endpoint URL
            base_url: Base URL to use (defaults to self.base_url)
            **kwargs: Additional arguments for httpx
            
        Returns:
            HTTP response
            
        Raises:
            Various GasNetworkError subclasses
        """
        if self._closed:
            raise GasNetworkError("Client has been closed")
        
        full_url = urljoin(base_url or self.base_url, url)
        
        try:
            response = await self._client.request(method, full_url, **kwargs)
            
            # Handle authentication errors
            if response.status_code == 401:
                raise InvalidAPIKeyError("Invalid or missing API key")
            
            # Handle other client errors
            if response.status_code >= 400:
                error_text = response.text
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    response.status_code,
                    error_text,
                )
            
            return response
            
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", e) from e
    
    async def get_gas_prices(self, chain: Chain) -> GasPriceResponse:
        """Get gas prices for a specific chain.
        
        Args:
            chain: The blockchain network
            
        Returns:
            Gas price response
        """
        response = await self._make_request(
            "GET",
            f"/gasprices/blockprices?chain={chain.value}"
        )
        
        try:
            return GasPriceResponse.model_validate(response.json())
        except ValidationError as e:
            raise GasNetworkError(f"Failed to parse response: {e}") from e
    
    async def get_base_fee_estimates(self, chain: Chain) -> BaseFeeResponse:
        """Get base fee estimates for Ethereum.
        
        Args:
            chain: The blockchain network (must be Ethereum)
            
        Returns:
            Base fee response
            
        Raises:
            UnsupportedChainError: If chain is not Ethereum
        """
        if chain != Chain.ETHEREUM:
            raise UnsupportedChainError(chain.value, "Base fee estimates")
        
        response = await self._make_request("GET", "/gasprices/basefee-estimates")
        
        try:
            return BaseFeeResponse.model_validate(response.json())
        except ValidationError as e:
            raise GasNetworkError(f"Failed to parse response: {e}") from e
    
    async def get_gas_distribution(self, chain: Chain) -> DistributionResponse:
        """Get gas price distribution for Ethereum.
        
        Args:
            chain: The blockchain network (must be Ethereum)
            
        Returns:
            Distribution response
            
        Raises:
            UnsupportedChainError: If chain is not Ethereum
        """
        if chain != Chain.ETHEREUM:
            raise UnsupportedChainError(chain.value, "Gas distribution")
        
        response = await self._make_request(
            "GET",
            f"/gasprices/distribution?chain={chain.value}"
        )
        
        try:
            return DistributionResponse.model_validate(response.json())
        except ValidationError as e:
            raise GasNetworkError(f"Failed to parse response: {e}") from e
    
    async def get_oracle_data(self, chain_id: int) -> OraclePayload:
        """Get oracle data for a specific chain ID.
        
        Args:
            chain_id: The chain ID (e.g., 1 for Ethereum mainnet)
            
        Returns:
            Oracle payload
        """
        response = await self._make_request(
            "GET",
            f"/oracle?chainId={chain_id}",
            base_url=self.rpc_url
        )
        
        try:
            return OraclePayload.model_validate(response.json())
        except ValidationError as e:
            raise GasNetworkError(f"Failed to parse response: {e}") from e
    
    async def get_next_block_estimate(
        self,
        chain: Chain,
        confidence_level: Optional[int] = None,
    ) -> GasPriceEstimate:
        """Get gas price estimate for the next block.
        
        Args:
            chain: The blockchain network
            confidence_level: Desired confidence level (defaults to 90)
            
        Returns:
            Gas price estimate
            
        Raises:
            GasNetworkError: If no estimate is found for the confidence level
        """
        gas_prices = await self.get_gas_prices(chain)
        confidence = confidence_level or 90
        
        # Get estimates from the first block
        estimated = gas_prices.estimated_prices()
        for estimate in estimated:
            if estimate.confidence >= confidence:
                return estimate
        
        raise GasNetworkError(
            f"No estimate found for confidence level {confidence}"
        )
    
    @staticmethod
    def supported_chains() -> List[Chain]:
        """Get list of supported blockchain networks.
        
        Returns:
            List of supported chains
        """
        return list(Chain)
    
    @staticmethod
    def chains_supporting_base_fee() -> List[Chain]:
        """Get list of chains that support base fee estimates.
        
        Returns:
            List of chains supporting base fee
        """
        return [Chain.ETHEREUM]
    
    @staticmethod
    def chains_supporting_distribution() -> List[Chain]:
        """Get list of chains that support gas distribution.
        
        Returns:
            List of chains supporting distribution
        """
        return [Chain.ETHEREUM]
    
    def get_api_key(self) -> Optional[str]:
        """Get the API key used by this client.
        
        Returns:
            API key if set, None otherwise
        """
        return self.api_key