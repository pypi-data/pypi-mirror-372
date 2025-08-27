#!/usr/bin/env python3
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dda_py import init, DDARunner


def run_dda_command(edf_file, output_file, ape_binary_path, channels=[1, 2, 3]):
    """Run DDA using the dda-py package with APE binary support."""
    
    print(f"Initializing DDA with APE binary: {ape_binary_path}")
    
    # Initialize DDA with the APE binary
    init(ape_binary_path)
    
    # Create DDA runner
    runner = DDARunner(ape_binary_path)
    
    # Convert channels to strings
    channel_list = [str(ch) for ch in channels]
    
    print(f"Running DDA analysis on channels: {channel_list}")
    
    # Run DDA
    Q, output_path = runner.run(
        edf_file,
        output_file=output_file,
        channel_list=channel_list,
        cpu_time=True
    )
    
    print("✓ DDA execution completed")
    print(f"✓ Q matrix shape: {Q.shape}")
    
    return Q


def main():
    if len(sys.argv) != 3:
        print("Usage: python demo.py <ape_binary_path> <edf_file>")
        print("Example: python demo.py ./run_DDA_AsciiEdf data.edf")
        sys.exit(1)

    ape_binary_path = sys.argv[1]
    edf_file = sys.argv[2]
    
    # Add ./ prefix if not present for local binaries
    if not ape_binary_path.startswith('./') and not ape_binary_path.startswith('/'):
        ape_binary_path = './' + ape_binary_path

    if not os.path.exists(ape_binary_path):
        print(f"Error: APE binary '{ape_binary_path}' not found")
        sys.exit(1)

    if not os.path.exists(edf_file):
        print(f"Error: EDF file '{edf_file}' not found")
        sys.exit(1)

    print("\n=== DDA Demo (APE Compatible) ===")
    print(f"APE Binary: {ape_binary_path}")
    print(f"Processing: {edf_file}\n")

    output_file = "dda_output"

    try:
        Q = run_dda_command(edf_file, output_file, ape_binary_path, channels=[1, 2, 3])

        print(f"✓ Q matrix shape: {Q.shape}")

        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.imshow(Q, aspect="auto", cmap="viridis", interpolation="nearest")
        plt.colorbar(label="DDA Value")
        plt.title("DDA Heatmap (Q)")

        plt.subplot(2, 1, 2)
        for i in range(min(Q.shape[0], 3)):
            plt.plot(Q[i, :])

        plt.xlabel("Time Window")
        plt.ylabel("DDA Value")
        plt.title("DDA Time Series")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("dda_results.png")
        print("\n✓ Results saved to dda_results.png")

        plt.show()

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
