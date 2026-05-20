import numpy as np
from collections import defaultdict
from itertools import combinations

input_file = "rez_mfcc.txt"
output_file = "annotation_score_intra_inter.txt"

# phoneme -> list of blocks, block = list of MFCC vectors
phoneme_blocks = defaultdict(list)

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

mfcc_dim = int(lines[0].strip())

current_phoneme = None
current_block = []

for line in lines[1:]:
    line = line.strip()
    if not line:
        continue

    phoneme, values = line.split(">", 1)
    phoneme = phoneme.strip()
    mfcc = np.fromstring(values, sep=" ")

    if phoneme != current_phoneme:
        if current_block:
            phoneme_blocks[current_phoneme].append(current_block)
        current_phoneme = phoneme
        current_block = []

    current_block.append(mfcc)

if current_block:
    phoneme_blocks[current_phoneme].append(current_block)

# --- Intra-phoneme std ---
phoneme_stds = []
phoneme_means = {}

for phoneme, blocks in phoneme_blocks.items():
    block_stds = []
    all_frames = []

    for block in blocks:
        block = np.vstack(block)
        block_stds.append(np.mean(np.std(block, axis=0)))
        all_frames.append(block)

    phoneme_stds.append(np.mean(block_stds))
    phoneme_means[phoneme] = np.mean(np.vstack(all_frames), axis=0)

std_within_phoneme = np.mean(phoneme_stds)

# --- Inter-phoneme distance ---
distances = []
for p1, p2 in combinations(phoneme_means.keys(), 2):
    d = np.linalg.norm(phoneme_means[p1] - phoneme_means[p2])
    distances.append(d)

distance_to_other_phonemes = np.mean(distances)

# --- Final score ---
score = std_within_phoneme / distance_to_other_phonemes

with open(output_file, "w") as f:
    f.write(f"{score:.6f}\n")

print(f"Score saved to {output_file}")
print(f"Score = {score:.6f}")
