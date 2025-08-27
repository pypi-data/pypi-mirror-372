#!/usr/bin/env python3
"""
Test suite for DDA with APE binary support.
Uses local APE binary and EDF file for testing.
"""

import os
import sys
import asyncio
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dda_py import init, DDARunner, run_dda, run_dda_async


def test_init_binary():
    """Test initializing the DDA binary path."""
    binary_path = "./run_DDA_AsciiEdf"
    
    print(f"Testing init with binary: {binary_path}")
    
    # Initialize the binary path
    result = init(binary_path)
    
    assert result == binary_path
    print("✓ Binary initialization successful")
    return True


def test_dda_runner_sync():
    """Test synchronous DDA execution with DDARunner."""
    binary_path = "./run_DDA_AsciiEdf"
    edf_file = "S04__05_02_screenprint.edf"
    
    print(f"\nTesting DDARunner sync with:")
    print(f"  Binary: {binary_path}")
    print(f"  EDF: {edf_file}")
    
    # Create runner instance
    runner = DDARunner(binary_path)
    
    # Run DDA with channels 1, 2, 3
    try:
        Q, output_path = runner.run(
            edf_file,
            output_file="test_output_sync",
            channel_list=["1", "2", "3"],
            cpu_time=True
        )
        
        print(f"✓ DDA execution completed")
        print(f"  Output shape: {Q.shape}")
        print(f"  Output file: {output_path}")
        
        # Verify output
        assert isinstance(Q, np.ndarray)
        assert Q.size > 0
        print("✓ Output validation passed")
        
        # Clean up
        if output_path.exists():
            output_path.unlink()
        st_file = output_path.with_name(f"{output_path.name}_ST")
        if st_file.exists():
            st_file.unlink()
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_dda_runner_async():
    """Test asynchronous DDA execution with DDARunner."""
    binary_path = "./run_DDA_AsciiEdf"
    edf_file = "S04__05_02_screenprint.edf"
    
    print(f"\nTesting DDARunner async with:")
    print(f"  Binary: {binary_path}")
    print(f"  EDF: {edf_file}")
    
    # Create runner instance
    runner = DDARunner(binary_path)
    
    # Run DDA asynchronously
    try:
        Q, output_path = await runner.run_async(
            edf_file,
            output_file="test_output_async",
            channel_list=["1", "2", "3"]
        )
        
        print(f"✓ Async DDA execution completed")
        print(f"  Output shape: {Q.shape}")
        print(f"  Output file: {output_path}")
        
        # Verify output
        assert isinstance(Q, np.ndarray)
        assert Q.size > 0
        print("✓ Output validation passed")
        
        # Clean up
        if output_path.exists():
            output_path.unlink()
        st_file = output_path.with_name(f"{output_path.name}_ST")
        if st_file.exists():
            st_file.unlink()
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_global_functions():
    """Test global convenience functions."""
    binary_path = "./run_DDA_AsciiEdf"
    edf_file = "S04__05_02_screenprint.edf"
    
    print(f"\nTesting global functions with:")
    print(f"  Binary: {binary_path}")
    print(f"  EDF: {edf_file}")
    
    # Initialize binary
    init(binary_path)
    
    try:
        # Test synchronous global function
        Q, output_path = run_dda(
            edf_file,
            channel_list=["1", "2", "3"]
        )
        
        print(f"✓ Global run_dda completed")
        print(f"  Output shape: {Q.shape}")
        
        # Clean up
        if output_path.exists():
            output_path.unlink()
        st_file = Path(str(output_path) + "_ST")
        if st_file.exists():
            st_file.unlink()
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_with_bounds():
    """Test DDA execution with time bounds."""
    binary_path = "./run_DDA_AsciiEdf"
    edf_file = "S04__05_02_screenprint.edf"
    
    print(f"\nTesting with time bounds:")
    print(f"  Binary: {binary_path}")
    print(f"  EDF: {edf_file}")
    print(f"  Bounds: (1000, 5000)")
    
    runner = DDARunner(binary_path)
    
    try:
        Q, output_path = runner.run(
            edf_file,
            channel_list=["1", "2", "3"],
            bounds=(1000, 5000)
        )
        
        print(f"✓ DDA with bounds completed")
        print(f"  Output shape: {Q.shape}")
        
        # Clean up
        if output_path.exists():
            output_path.unlink()
        st_file = Path(str(output_path) + "_ST")
        if st_file.exists():
            st_file.unlink()
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid inputs."""
    binary_path = "./run_DDA_AsciiEdf"
    
    print(f"\nTesting error handling:")
    
    runner = DDARunner(binary_path)
    
    # Test with non-existent file
    try:
        Q, output_path = runner.run(
            "non_existent_file.edf",
            channel_list=["1"],
            raise_on_error=True
        )
        print("✗ Should have raised an error for non-existent file")
        return False
    except Exception as e:
        print(f"✓ Correctly raised error for non-existent file: {type(e).__name__}")
    
    # Test with invalid binary path
    try:
        bad_runner = DDARunner("./non_existent_binary")
        Q, output_path = bad_runner.run(
            "S04__05_02_screenprint.edf",
            channel_list=["1"]
        )
        print("✗ Should have raised an error for invalid binary")
        return False
    except Exception as e:
        print(f"✓ Correctly raised error for invalid binary: {type(e).__name__}")
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("DDA APE Binary Test Suite")
    print("=" * 60)
    
    # Check prerequisites
    if not Path("./run_DDA_AsciiEdf").exists():
        print("✗ APE binary not found: ./run_DDA_AsciiEdf")
        print("  Please ensure the APE binary is in the current directory")
        return
    
    if not Path("S04__05_02_screenprint.edf").exists():
        print("✗ EDF file not found: S04__05_02_screenprint.edf")
        print("  Please ensure the test EDF file is in the current directory")
        return
    
    print("\nNote: APE binaries require special handling on macOS.")
    print("The 'Exec format error' is expected on macOS without proper APE loader.")
    print("These tests demonstrate the code structure works correctly.\n")
    
    # Run tests
    results = []
    
    # Synchronous tests
    results.append(("Init Binary", test_init_binary()))
    results.append(("DDARunner Sync", test_dda_runner_sync()))
    results.append(("Global Functions", test_global_functions()))
    results.append(("With Bounds", test_with_bounds()))
    results.append(("Error Handling", test_error_handling()))
    
    # Asynchronous test
    async_result = await test_dda_runner_async()
    results.append(("DDARunner Async", async_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name:20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)