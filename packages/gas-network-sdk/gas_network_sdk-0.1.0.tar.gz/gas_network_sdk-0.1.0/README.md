# Gas Network SDK

A Python SDK for the Gas Network API, providing gas price prediction and optimization for blockchain transactions.

## Features

- **Multi-chain support**: Ethereum, Polygon, Bitcoin, SEI, Optimism, Arbitrum, Base, Linea, Unichain
- **Real-time gas price estimates** with confidence levels
- **Base fee and blob fee predictions** (Ethereum only)
- **Gas price distribution analysis** (Ethereum only)
- **Oracle integration** for on-chain gas data
- **Async/await support** with httpx
- **Type-safe** with Pydantic models
- **Comprehensive error handling**

## Installation

```bash
pip install gas-network-sdk
```

## Quick Start

```python
import asyncio
from gas_network_sdk import GasNetworkClient, Chain

async def main():
    # Create client with your API key (optional)
    client = GasNetworkClient(api_key="your_api_key_here")
    
    # Get gas prices for Ethereum
    gas_prices = await client.get_gas_prices(Chain.ETHEREUM)
    print(f"Current gas prices: {gas_prices}")
    
    # Get next block estimate with 90% confidence
    estimate = await client.get_next_block_estimate(Chain.ETHEREUM, confidence_level=90)
    print(f"Next block estimate: {estimate.price} gwei")
    
    await client.close()

# Run the example
asyncio.run(main())
```

## API Reference

### Client Creation

```python
from gas_network_sdk import GasNetworkClient

# With API key (recommended for higher rate limits)
client = GasNetworkClient(api_key="your_api_key")

# Without API key (rate limited)
client = GasNetworkClient()
```

### Gas Price Estimation

```python
# Get comprehensive gas price data
prices = await client.get_gas_prices(Chain.BASE)

# Get specific confidence level estimate
estimate = await client.get_next_block_estimate(Chain.ETHEREUM, confidence_level=95)
```

### Base Fee Prediction (Ethereum only)

```python
base_fees = await client.get_base_fee_estimates(Chain.ETHEREUM)
print(f"Current base fee: {base_fees.base_fee_per_gas} gwei")
print(f"Blob base fee: {base_fees.blob_base_fee_per_gas} gwei")

# Get estimates for next 5 blocks
for block_estimate in base_fees.estimated_base_fees:
    for pending_block, estimates in block_estimate.pending_block.items():
        for estimate in estimates:
            print(f"{pending_block}: Base fee {estimate.base_fee} gwei ({estimate.confidence}% confidence)")
```

### Gas Distribution Analysis (Ethereum only)

```python
distribution = await client.get_gas_distribution(Chain.ETHEREUM)
print(f"Current block: {distribution.current_block_number}")
for price, count in distribution.top_n_distribution.distribution:
    print(f"Price: {price} gwei, Transactions: {count}")
```

### Oracle Data

```python
# Get oracle data for a specific chain ID
oracle_data = await client.get_oracle_data(1)  # Ethereum mainnet
```

## Supported Chains

- Ethereum
- Polygon  
- Bitcoin
- SEI
- Optimism
- Arbitrum
- Base
- Linea
- Unichain

## Error Handling

The SDK uses comprehensive error handling:

```python
from gas_network_sdk import GasNetworkError, UnsupportedChainError, APIError

try:
    prices = await client.get_gas_prices(Chain.ETHEREUM)
    print(f"Success: {prices}")
except UnsupportedChainError as e:
    print(f"Unsupported chain: {e}")
except APIError as e:
    print(f"API error: {e}")
except GasNetworkError as e:
    print(f"Other error: {e}")
```

## Context Manager Usage

```python
async with GasNetworkClient(api_key="your_api_key") as client:
    prices = await client.get_gas_prices(Chain.ETHEREUM)
    print(prices)
# Client is automatically closed
```

## Authentication

You can optionally use an API key from [Blocknative](https://blocknative.com) for higher rate limits. The API works without authentication but with rate limitations.

## License

Licensed under either of

- Apache License, Version 2.0
- MIT License

at your option.