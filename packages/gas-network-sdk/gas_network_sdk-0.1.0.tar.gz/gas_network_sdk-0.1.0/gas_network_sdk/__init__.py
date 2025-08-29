"""Gas Network SDK - Python client for Gas Network API."""

try:
    from .client import GasNetworkClient
    _CLIENT_AVAILABLE = True
except ImportError:
    _CLIENT_AVAILABLE = False
    GasNetworkClient = None

from .exceptions import (
    GasNetworkError,
    APIError,
    UnsupportedChainError,
    InvalidAPIKeyError,
)
from .types import (
    Chain,
    GasPriceEstimate,
    GasPriceResponse,
    BlockPrice,
    BaseFeeResponse,
    BaseFeeEstimate,
    PendingBlockBaseFee,
    PriorityFee,
    DistributionResponse,
    TopNDistribution,
    GasDistribution,
    OraclePayload,
    OracleRecord,
    OracleType,
)

__version__ = "0.1.0"
__author__ = "rshuwy"
__email__ = ""

__all__ = [
    # Client
    "GasNetworkClient",
    # Exceptions
    "GasNetworkError",
    "APIError",
    "UnsupportedChainError",
    "InvalidAPIKeyError",
    # Types
    "Chain",
    "GasPriceEstimate",
    "GasPriceResponse", 
    "BlockPrice",
    "BaseFeeResponse",
    "BaseFeeEstimate",
    "PendingBlockBaseFee",
    "PriorityFee",
    "DistributionResponse",
    "TopNDistribution",
    "GasDistribution",
    "OraclePayload",
    "OracleRecord",
    "OracleType",
]