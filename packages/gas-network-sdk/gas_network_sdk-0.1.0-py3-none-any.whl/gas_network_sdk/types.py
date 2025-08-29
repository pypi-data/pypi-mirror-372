"""Type definitions for the Gas Network SDK."""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Chain(str, Enum):
    """Supported blockchain networks."""
    
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BITCOIN = "bitcoin" 
    SEI = "sei"
    OPTIMISM = "optimism"
    ARBITRUM = "arbitrum"
    BASE = "base"
    LINEA = "linea"
    UNICHAIN = "unichain"


class OracleType(int, Enum):
    """Oracle data types."""
    
    BASE_FEE_PER_GAS = 107
    BLOB_BASE_FEE_PER_GAS = 112
    PREDICTED_MAX_PRIORITY_FEE_PER_GAS = 322


class GasPriceEstimate(BaseModel):
    """Gas price estimate with confidence level."""
    
    confidence: int
    price: float
    max_priority_fee_per_gas: Optional[float] = Field(alias="maxPriorityFeePerGas", default=None)
    max_fee_per_gas: Optional[float] = Field(alias="maxFeePerGas", default=None)

    class Config:
        populate_by_name = True


class BlockPrice(BaseModel):
    """Block price information."""
    
    block_number: int = Field(alias="blockNumber")
    estimated_transaction_count: int = Field(alias="estimatedTransactionCount")
    base_fee_per_gas: Optional[float] = Field(alias="baseFeePerGas", default=None)
    blob_base_fee_per_gas: Optional[float] = Field(alias="blobBaseFeePerGas", default=None)
    estimated_prices: List[GasPriceEstimate] = Field(alias="estimatedPrices")

    class Config:
        populate_by_name = True


class GasPriceResponse(BaseModel):
    """Gas price response from the API."""
    
    system: str
    network: str
    unit: str
    max_price: float = Field(alias="maxPrice")
    current_block_number: int = Field(alias="currentBlockNumber")
    ms_since_last_block: int = Field(alias="msSinceLastBlock")
    block_prices: List[BlockPrice] = Field(alias="blockPrices")
    
    class Config:
        populate_by_name = True
    
    def estimated_prices(self) -> List[GasPriceEstimate]:
        """Get estimated prices from the first block for convenience."""
        if self.block_prices:
            return self.block_prices[0].estimated_prices
        return []


class PriorityFee(BaseModel):
    """Priority fee information."""
    
    blob_count: int = Field(alias="blobCount")
    tip: float

    class Config:
        populate_by_name = True


class BaseFeeEstimate(BaseModel):
    """Base fee estimate with confidence level."""
    
    confidence: int
    base_fee: float = Field(alias="baseFee")
    blob_base_fee: float = Field(alias="blobBaseFee")
    priority_fee: List[PriorityFee] = Field(alias="priorityFee")

    class Config:
        populate_by_name = True


class PendingBlockBaseFee(BaseModel):
    """Pending block base fee estimates."""
    
    pending_block: Dict[str, List[BaseFeeEstimate]] = Field(default_factory=dict)

    class Config:
        extra = "allow"
    
    def __init__(self, **data):
        # Handle dynamic keys like "pending+1", "pending+2", etc.
        pending_block = {}
        for key, value in data.items():
            if key.startswith("pending"):
                pending_block[key] = [BaseFeeEstimate.model_validate(item) for item in value]
        super().__init__(pending_block=pending_block)


class BaseFeeResponse(BaseModel):
    """Base fee response from the API."""
    
    system: str
    network: str
    unit: str
    current_block_number: int = Field(alias="currentBlockNumber")
    ms_since_last_block: int = Field(alias="msSinceLastBlock")
    base_fee_per_gas: float = Field(alias="baseFeePerGas")
    blob_base_fee_per_gas: float = Field(alias="blobBaseFeePerGas")
    estimated_base_fees: List[PendingBlockBaseFee] = Field(alias="estimatedBaseFees")

    class Config:
        populate_by_name = True


class GasDistribution(BaseModel):
    """Gas distribution entry."""
    
    price: float
    transaction_count: int


class TopNDistribution(BaseModel):
    """Top N distribution data."""
    
    distribution: List[List[Union[float, int]]]
    n: int


class DistributionResponse(BaseModel):
    """Gas distribution response from the API."""
    
    system: str
    network: str
    unit: str
    max_price: float = Field(alias="maxPrice")
    current_block_number: int = Field(alias="currentBlockNumber")
    ms_since_last_block: int = Field(alias="msSinceLastBlock")
    top_n_distribution: TopNDistribution = Field(alias="topNDistribution")

    class Config:
        populate_by_name = True


class OracleRecord(BaseModel):
    """Oracle record data."""
    
    typ: int
    value: str


class OraclePayload(BaseModel):
    """Oracle payload response."""
    
    height: int
    timestamp: int
    systemid: int
    chainid: int
    payloads: List[OracleRecord]