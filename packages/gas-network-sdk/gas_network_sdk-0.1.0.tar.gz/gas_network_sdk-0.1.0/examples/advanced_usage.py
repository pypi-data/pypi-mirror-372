"""Advanced usage example showing error handling and context management."""

import asyncio
import os
from gas_network_sdk import (
    GasNetworkClient,
    Chain,
    GasNetworkError,
    APIError,
    UnsupportedChainError,
    NetworkError,
)


async def demonstrate_error_handling():
    """Demonstrate comprehensive error handling."""
    print("=== Error Handling Demo ===\n")
    
    # Example with invalid API key
    print("1. Testing with invalid API key...")
    try:
        async with GasNetworkClient(api_key="invalid_key") as client:
            await client.get_gas_prices(Chain.ETHEREUM)
    except APIError as e:
        print(f"✓ Caught API error: {e.message} (Status: {e.response_code})")
    except GasNetworkError as e:
        print(f"✓ Caught network error: {e}")
    
    # Example with unsupported chain operation
    print("\n2. Testing unsupported chain operation...")
    try:
        async with GasNetworkClient() as client:
            await client.get_base_fee_estimates(Chain.BITCOIN)
    except UnsupportedChainError as e:
        print(f"✓ Caught unsupported chain error: {e.message}")
        print(f"  Chain: {e.chain}, Operation: {e.operation}")
    
    print()


async def demonstrate_context_management():
    """Demonstrate proper context management."""
    print("=== Context Management Demo ===\n")
    
    # Good practice: using async context manager
    print("1. Using async context manager (recommended):")
    async with GasNetworkClient() as client:
        chains = client.supported_chains()
        print(f"✓ Supported chains: {len(chains)}")
    print("✓ Client automatically closed")
    
    # Alternative: manual management
    print("\n2. Manual client management:")
    client = GasNetworkClient()
    try:
        chains = client.supported_chains()
        print(f"✓ Supported chains: {len(chains)}")
    finally:
        await client.close()
        print("✓ Client manually closed")
    
    print()


async def demonstrate_batch_requests():
    """Demonstrate making multiple requests efficiently."""
    print("=== Batch Requests Demo ===\n")
    
    api_key = os.getenv("GAS_NETWORK_API_KEY", "your_api_key_here")
    
    async with GasNetworkClient(api_key=api_key) as client:
        # Get gas prices for multiple chains concurrently
        chains = [Chain.ETHEREUM, Chain.BASE, Chain.ARBITRUM]
        
        print("Getting gas prices for multiple chains concurrently...")
        
        tasks = []
        for chain in chains:
            task = asyncio.create_task(
                client.get_gas_prices(chain),
                name=f"gas_prices_{chain.value}"
            )
            tasks.append((chain, task))
        
        # Wait for all tasks to complete
        results = []
        for chain, task in tasks:
            try:
                result = await task
                results.append((chain, result, None))
                print(f"✓ {chain.value}: {result.max_price} {result.unit}")
            except GasNetworkError as e:
                results.append((chain, None, e))
                print(f"✗ {chain.value}: {e}")
        
        print(f"\nCompleted {len(results)} requests")
    
    print()


async def demonstrate_confidence_levels():
    """Demonstrate different confidence levels for estimates."""
    print("=== Confidence Levels Demo ===\n")
    
    api_key = os.getenv("GAS_NETWORK_API_KEY", "your_api_key_here")
    
    async with GasNetworkClient(api_key=api_key) as client:
        confidence_levels = [99, 95, 90, 80, 70]
        
        print("Getting estimates for different confidence levels:")
        for confidence in confidence_levels:
            try:
                estimate = await client.get_next_block_estimate(
                    Chain.ETHEREUM,
                    confidence_level=confidence
                )
                print(f"  {confidence}% confidence: {estimate.price} gwei")
            except GasNetworkError as e:
                print(f"  {confidence}% confidence: Error - {e}")
    
    print()


async def main():
    """Run all advanced usage examples."""
    print("=== Advanced Gas Network SDK Usage ===\n")
    
    await demonstrate_error_handling()
    await demonstrate_context_management() 
    await demonstrate_batch_requests()
    await demonstrate_confidence_levels()
    
    print("=== Advanced Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())