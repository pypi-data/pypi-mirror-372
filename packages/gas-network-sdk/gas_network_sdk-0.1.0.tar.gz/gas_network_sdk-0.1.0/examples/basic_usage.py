"""Basic usage example for the Gas Network SDK."""

import asyncio
from gas_network_sdk import GasNetworkClient, Chain, GasNetworkError


async def main():
    """Demonstrate basic Gas Network SDK usage."""
    # Create client with API key from environment or use placeholder
    import os
    api_key = os.getenv("GAS_NETWORK_API_KEY", "your_api_key_here")
    
    async with GasNetworkClient(api_key=api_key) as client:
        print("=== Gas Network SDK Example ===\n")

        # Example 1: Get gas prices for Ethereum
        print("1. Getting gas prices for Ethereum...")
        try:
            prices = await client.get_gas_prices(Chain.ETHEREUM)
            print(f"✓ Current block: {prices.current_block_number}")
            print(f"✓ Max price: {prices.max_price} {prices.unit}")
            
            estimated = prices.estimated_prices()
            if estimated:
                estimate = estimated[0]
                print(f"✓ Recommended price: {estimate.price} {prices.unit} ({estimate.confidence}% confidence)")
        except GasNetworkError as e:
            print(f"✗ Error: {e}")

        # Example 2: Get next block estimate with specific confidence
        print("\n2. Getting next block estimate (90% confidence)...")
        try:
            estimate = await client.get_next_block_estimate(Chain.ETHEREUM, confidence_level=90)
            print(f"✓ Price: {estimate.price} gwei")
            if estimate.max_fee_per_gas:
                print(f"✓ Max fee per gas: {estimate.max_fee_per_gas} gwei")
        except GasNetworkError as e:
            print(f"✗ Error: {e}")

        # Example 3: Get base fee estimates (Ethereum only)
        print("\n3. Getting base fee estimates...")
        try:
            base_fees = await client.get_base_fee_estimates(Chain.ETHEREUM)
            print(f"✓ Current block: {base_fees.current_block_number}")
            print(f"✓ Current base fee: {base_fees.base_fee_per_gas} {base_fees.unit}")
            print(f"✓ Blob base fee: {base_fees.blob_base_fee_per_gas} {base_fees.unit}")
            
            # Show first pending block estimate
            if base_fees.estimated_base_fees:
                first_block = base_fees.estimated_base_fees[0]
                for pending_block, estimates in first_block.pending_block.items():
                    if estimates:
                        estimate = estimates[0]
                        print(f"✓ {pending_block} estimate: {estimate.base_fee} {base_fees.unit} ({estimate.confidence}% confidence)")
                        break
        except GasNetworkError as e:
            print(f"✗ Error: {e}")

        # Example 4: Get gas distribution (Ethereum only)
        print("\n4. Getting gas price distribution...")
        try:
            distribution = await client.get_gas_distribution(Chain.ETHEREUM)
            print(f"✓ Current block: {distribution.current_block_number}")
            print(f"✓ Distribution entries: {len(distribution.top_n_distribution.distribution)}")
            if distribution.top_n_distribution.distribution:
                price, count = distribution.top_n_distribution.distribution[0]
                print(f"✓ Highest price: {price} {distribution.unit} ({count} transactions)")
        except GasNetworkError as e:
            print(f"✗ Error: {e}")

        # Example 5: Show supported chains
        print("\n5. Supported chains:")
        for chain in client.supported_chains():
            print(f"  - {chain.value}")

        print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())