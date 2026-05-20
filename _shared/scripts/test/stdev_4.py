import numpy as np

input_file = "rez_mfcc.txt"
output_file = "a_transition_sharpness.txt"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

mfcc_dim = int(lines[0].strip())

# --- Build ordered phoneme blocks ---
blocks = []  # list of (phoneme, np.array of frames)

current_phoneme = None
current_frames = []

for line in lines[1:]:
    line = line.strip()
    if not line:
        continue

    phoneme, values = line.split(">", 1)
    phoneme = phoneme.strip()
    mfcc = np.fromstring(values, sep=" ")

    if phoneme != current_phoneme:
        if current_frames:
            blocks.append(
                (current_phoneme, np.vstack(current_frames))
            )
        current_phoneme = phoneme
        current_frames = []

    current_frames.append(mfcc)

# last block
if current_frames:
    blocks.append(
        (current_phoneme, np.vstack(current_frames))
    )

# --- Compute transition sharpness ---
distances = []

for i in range(len(blocks) - 1):
    _, left_block = blocks[i]
    _, right_block = blocks[i + 1]

    mean_left = np.mean(left_block, axis=0)
    mean_right = np.mean(right_block, axis=0)

    D = np.linalg.norm(mean_left - mean_right)
    distances.append(D)

transition_sharpness = np.mean(distances)

# --- Save result ---
with open(output_file, "w") as f:
    f.write(f"{transition_sharpness:.6f}\n")

print(f"Transition sharpness saved to {output_file}")
print(f"Transition sharpness = {transition_sharpness:.6f}")
