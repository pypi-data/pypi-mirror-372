"""Tests for type definitions."""

import pytest
from pydantic import ValidationError

from gas_network_sdk.types import (
    Chain,
    OracleType,
    GasPriceEstimate,
    BlockPrice,
    GasPriceResponse,
    BaseFeeEstimate,
    PriorityFee,
    BaseFeeResponse,
    PendingBlockBaseFee,
    TopNDistribution,
    DistributionResponse,
    OracleRecord,
    OraclePayload,
)


class TestChain:
    """Test Chain enum."""

    def test_chain_values(self):
        """Test chain enum values."""
        assert Chain.ETHEREUM.value == "ethereum"
        assert Chain.BITCOIN.value == "bitcoin"
        assert Chain.BASE.value == "base"


class TestOracleType:
    """Test OracleType enum."""

    def test_oracle_type_values(self):
        """Test oracle type enum values."""
        assert OracleType.BASE_FEE_PER_GAS.value == 107
        assert OracleType.BLOB_BASE_FEE_PER_GAS.value == 112
        assert OracleType.PREDICTED_MAX_PRIORITY_FEE_PER_GAS.value == 322


class TestGasPriceEstimate:
    """Test GasPriceEstimate model."""

    def test_valid_gas_price_estimate(self):
        """Test valid gas price estimate creation."""
        data = {
            "confidence": 95,
            "price": 20.5,
            "maxPriorityFeePerGas": 2.0,
            "maxFeePerGas": 25.0,
        }
        estimate = GasPriceEstimate.model_validate(data)
        assert estimate.confidence == 95
        assert estimate.price == 20.5
        assert estimate.max_priority_fee_per_gas == 2.0
        assert estimate.max_fee_per_gas == 25.0

    def test_gas_price_estimate_with_snake_case(self):
        """Test gas price estimate with snake_case field names."""
        data = {
            "confidence": 90,
            "price": 15.0,
            "max_priority_fee_per_gas": 1.5,
            "max_fee_per_gas": 20.0,
        }
        estimate = GasPriceEstimate.model_validate(data)
        assert estimate.confidence == 90
        assert estimate.price == 15.0

    def test_gas_price_estimate_optional_fields(self):
        """Test gas price estimate with optional fields."""
        data = {
            "confidence": 80,
            "price": 10.0,
        }
        estimate = GasPriceEstimate.model_validate(data)
        assert estimate.confidence == 80
        assert estimate.price == 10.0
        assert estimate.max_priority_fee_per_gas is None
        assert estimate.max_fee_per_gas is None


class TestBlockPrice:
    """Test BlockPrice model."""

    def test_valid_block_price(self):
        """Test valid block price creation."""
        data = {
            "blockNumber": 12345,
            "estimatedTransactionCount": 150,
            "baseFeePerGas": 15.5,
            "blobBaseFeePerGas": 0.000000001,
            "estimatedPrices": [
                {
                    "confidence": 95,
                    "price": 20.0,
                    "maxPriorityFeePerGas": 2.0,
                    "maxFeePerGas": 25.0,
                }
            ],
        }
        block_price = BlockPrice.model_validate(data)
        assert block_price.block_number == 12345
        assert block_price.estimated_transaction_count == 150
        assert block_price.base_fee_per_gas == 15.5
        assert len(block_price.estimated_prices) == 1


class TestGasPriceResponse:
    """Test GasPriceResponse model."""

    def test_valid_gas_price_response(self):
        """Test valid gas price response creation."""
        data = {
            "system": "ethereum",
            "network": "main",
            "unit": "gwei",
            "maxPrice": 100.0,
            "currentBlockNumber": 12345,
            "msSinceLastBlock": 12000,
            "blockPrices": [
                {
                    "blockNumber": 12346,
                    "estimatedTransactionCount": 150,
                    "baseFeePerGas": 15.5,
                    "estimatedPrices": [
                        {
                            "confidence": 95,
                            "price": 20.0,
                        }
                    ],
                }
            ],
        }
        response = GasPriceResponse.model_validate(data)
        assert response.system == "ethereum"
        assert response.network == "main"
        assert response.unit == "gwei"
        assert response.max_price == 100.0
        assert len(response.block_prices) == 1

    def test_estimated_prices_helper(self):
        """Test estimated_prices helper method."""
        data = {
            "system": "ethereum",
            "network": "main",
            "unit": "gwei",
            "maxPrice": 100.0,
            "currentBlockNumber": 12345,
            "msSinceLastBlock": 12000,
            "blockPrices": [
                {
                    "blockNumber": 12346,
                    "estimatedTransactionCount": 150,
                    "estimatedPrices": [
                        {
                            "confidence": 95,
                            "price": 20.0,
                        }
                    ],
                }
            ],
        }
        response = GasPriceResponse.model_validate(data)
        estimated = response.estimated_prices()
        assert len(estimated) == 1
        assert estimated[0].confidence == 95

    def test_estimated_prices_empty_blocks(self):
        """Test estimated_prices with empty block prices."""
        data = {
            "system": "ethereum",
            "network": "main", 
            "unit": "gwei",
            "maxPrice": 100.0,
            "currentBlockNumber": 12345,
            "msSinceLastBlock": 12000,
            "blockPrices": [],
        }
        response = GasPriceResponse.model_validate(data)
        estimated = response.estimated_prices()
        assert estimated == []


class TestBaseFeeModels:
    """Test base fee related models."""

    def test_priority_fee(self):
        """Test PriorityFee model."""
        data = {
            "blobCount": 3,
            "tip": 2.5,
        }
        priority_fee = PriorityFee.model_validate(data)
        assert priority_fee.blob_count == 3
        assert priority_fee.tip == 2.5

    def test_base_fee_estimate(self):
        """Test BaseFeeEstimate model."""
        data = {
            "confidence": 99,
            "baseFee": 15.5,
            "blobBaseFee": 0.000000001,
            "priorityFee": [
                {
                    "blobCount": 1,
                    "tip": 2.0,
                }
            ],
        }
        estimate = BaseFeeEstimate.model_validate(data)
        assert estimate.confidence == 99
        assert estimate.base_fee == 15.5
        assert estimate.blob_base_fee == 0.000000001
        assert len(estimate.priority_fee) == 1

    def test_pending_block_base_fee(self):
        """Test PendingBlockBaseFee model."""
        data = {
            "pending+1": [
                {
                    "confidence": 99,
                    "baseFee": 15.5,
                    "blobBaseFee": 0.000000001,
                    "priorityFee": [],
                }
            ],
            "pending+2": [
                {
                    "confidence": 95,
                    "baseFee": 16.0,
                    "blobBaseFee": 0.000000001,
                    "priorityFee": [],
                }
            ],
        }
        pending_block = PendingBlockBaseFee(**data)
        assert "pending+1" in pending_block.pending_block
        assert "pending+2" in pending_block.pending_block
        assert len(pending_block.pending_block["pending+1"]) == 1


class TestDistributionModels:
    """Test distribution related models."""

    def test_top_n_distribution(self):
        """Test TopNDistribution model."""
        data = {
            "distribution": [[10.0, 5], [8.0, 10], [5.0, 15]],
            "n": 30,
        }
        distribution = TopNDistribution.model_validate(data)
        assert len(distribution.distribution) == 3
        assert distribution.n == 30
        assert distribution.distribution[0] == [10.0, 5]

    def test_distribution_response(self):
        """Test DistributionResponse model."""
        data = {
            "system": "ethereum",
            "network": "main",
            "unit": "gwei",
            "maxPrice": 10.0,
            "currentBlockNumber": 12345,
            "msSinceLastBlock": 8000,
            "topNDistribution": {
                "distribution": [[10.0, 1], [5.0, 2]],
                "n": 3,
            },
        }
        response = DistributionResponse.model_validate(data)
        assert response.system == "ethereum"
        assert response.max_price == 10.0
        assert len(response.top_n_distribution.distribution) == 2


class TestOracleModels:
    """Test oracle related models."""

    def test_oracle_record(self):
        """Test OracleRecord model."""
        data = {
            "typ": 107,
            "value": "15500000000",
        }
        record = OracleRecord.model_validate(data)
        assert record.typ == 107
        assert record.value == "15500000000"

    def test_oracle_payload(self):
        """Test OraclePayload model."""
        data = {
            "height": 12345,
            "timestamp": 1640995200,
            "systemid": 1,
            "chainid": 1,
            "payloads": [
                {
                    "typ": 107,
                    "value": "15500000000",
                }
            ],
        }
        payload = OraclePayload.model_validate(data)
        assert payload.height == 12345
        assert payload.timestamp == 1640995200
        assert payload.systemid == 1
        assert payload.chainid == 1
        assert len(payload.payloads) == 1