import argparse
from itertools import product


def main():
    parser = argparse.ArgumentParser(description="Generate monophones, biphones, and triphones from a monophone list")
    parser.add_argument("input", help="Path to monophone list file")
    parser.add_argument("output", help="Path to output file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        monophones = [line.strip() for line in f if line.strip()]

    with open(args.output, "w") as f:
        for p in monophones:
            f.write(p + "\n")

        for a, b in product(monophones, repeat=2):
            f.write(f"{a}-{b}\n")

        for a, b, c in product(monophones, repeat=3):
            f.write(f"{a}-{b}+{c}\n")


if __name__ == "__main__":
    main()
