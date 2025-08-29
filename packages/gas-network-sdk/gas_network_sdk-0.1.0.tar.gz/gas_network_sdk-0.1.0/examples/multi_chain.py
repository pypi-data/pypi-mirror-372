"""Multi-chain gas price comparison example."""

import asyncio
from gas_network_sdk import GasNetworkClient, Chain, GasNetworkError


async def main():
    """Compare gas prices across multiple chains."""
    import os
    api_key = os.getenv("GAS_NETWORK_API_KEY", "your_api_key_here")
    
    async with GasNetworkClient(api_key=api_key) as client:
        print("=== Multi-Chain Gas Price Comparison ===\n")

        chains_to_check = [
            Chain.ETHEREUM,
            Chain.BASE,
            Chain.ARBITRUM,
            Chain.OPTIMISM,
            Chain.POLYGON,
        ]

        for chain in chains_to_check:
            print(f"📊 {chain.value.upper()} Gas Prices:")
            
            try:
                prices = await client.get_gas_prices(chain)
                print(f"  Block: #{prices.current_block_number}")
                print(f"  Network: {prices.network}")
                print(f"  Unit: {prices.unit}")
                
                estimated = prices.estimated_prices()
                if estimated:
                    estimate = estimated[0]
                    print(f"  Recommended: {estimate.price} {prices.unit} ({estimate.confidence}% confidence)")
                    
                    if estimate.max_fee_per_gas:
                        print(f"  Max Fee: {estimate.max_fee_per_gas} {prices.unit}")
                    
                    if estimate.max_priority_fee_per_gas:
                        print(f"  Priority Fee: {estimate.max_priority_fee_per_gas} {prices.unit}")
                
                print(f"  Time since last block: ~{prices.ms_since_last_block} ms")
                
            except GasNetworkError as e:
                print(f"  ❌ Error: {e}")
            
            print()  # Empty line for spacing

        print("=== Chain Comparison Complete ===")


if __name__ == "__main__":
    asyncio.run(main())