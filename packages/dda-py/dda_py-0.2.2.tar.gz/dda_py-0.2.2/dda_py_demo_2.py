import dda_py
import matplotlib.pyplot as plt

DDA_PATH = "./run_DDA_AsciiEdf"
INPUT_FILE = "./patient1_S05__01_03.edf"
OUTPUT_FILE = "./dda_results.png"
CHANNEL_LIST = list(range(1, 79))
COLORMAP = "viridis"

# Initialize with APE binary path
dda_py.init(DDA_PATH)

# Run DDA analysis
Q, output_path = dda_py.run_dda(input_file=INPUT_FILE, channel_list=CHANNEL_LIST)

print(f"Result shape: {Q.shape}")

fig, ax = plt.subplots(nrows=2, figsize=(12, 8))

ax[0].imshow(Q, aspect="auto")
ax[0].set_title("DDA Heatmap")

for i in range(Q.shape[0]):
    ax[1].plot(Q[i, :])

ax[1].set_xlabel("t")
ax[1].set_ylabel("DDA Value")
ax[1].set_title("DDA Line Plot")
ax[1].grid(True, alpha=0.3)

fig.tight_layout()

fig.savefig(OUTPUT_FILE)
print(f"\n✓ Results saved to {OUTPUT_FILE}")

plt.show()
