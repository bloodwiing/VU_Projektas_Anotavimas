import argparse
import os
import re
import sys
from collections import Counter


def basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]


def load_scp_basenames(scp_path):
    basenames = set()
    with open(scp_path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            entry = line.split('=', 1)[0]
            entry = entry.split('[', 1)[0]
            basenames.add(basename_no_ext(entry.strip()))
    return basenames


def is_number(tok):
    try:
        float(tok)
        return True
    except ValueError:
        return False


def extract_label(line):
    tokens = line.split()
    for tok in tokens:
        if not is_number(tok):
            return tok
    return None


def count_phonemes(mlf_path, allowed_basenames):
    counts = Counter()
    matched = 0
    included = False
    current_basename = None

    with open(mlf_path) as f:
        for raw in f:
            line = raw.rstrip('\n').strip()
            if not line or line == '#!MLF!#':
                continue

            m = re.match(r'^"(.+)"$', line)
            if m:
                current_basename = basename_no_ext(m.group(1))
                included = current_basename in allowed_basenames
                if included:
                    matched += 1
                continue

            if line == '.':
                included = False
                current_basename = None
                continue

            if not included:
                continue

            label = extract_label(line)
            if label:
                counts[label] += 1

    return counts, matched


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count phoneme occurrences in an MLF, restricted to the utterances listed in an SCP file.")
    parser.add_argument("mlf", help="Path to the MLF file")
    parser.add_argument("scp", help="Path to the SCP file (subset of utterances to include)")
    parser.add_argument("phonemes", nargs='*', help="Phonemes to report. If omitted, prints all phonemes sorted by count.")

    args = parser.parse_args()

    try:
        scp_set = load_scp_basenames(args.scp)
    except FileNotFoundError:
        print(f"Error: SCP file '{args.scp}' not found.", file=sys.stderr)
        sys.exit(1)

    if not scp_set:
        print(f"Error: SCP file '{args.scp}' is empty.", file=sys.stderr)
        sys.exit(1)

    try:
        counts, matched = count_phonemes(args.mlf, scp_set)
    except FileNotFoundError:
        print(f"Error: MLF file '{args.mlf}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Counting in {matched}/{len(scp_set)} utterances from SCP:")

    if args.phonemes:
        for p in args.phonemes:
            print(f"{p}: {counts.get(p, 0)}")
    else:
        for p, n in counts.most_common():
            print(f"{p}: {n}")
