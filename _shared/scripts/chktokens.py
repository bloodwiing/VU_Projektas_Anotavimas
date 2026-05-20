import argparse
from itertools import product


def read_tokens(path: str) -> list[str]:
    tokens = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            if not s.strip():
                continue
            tokens.append(s.strip())

    return list(dict.fromkeys(tokens))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens_file", help="Path to file with one token per line")
    args = ap.parse_args()

    tokens = read_tokens(args.tokens_file)
    if not tokens:
        raise ValueError("No tokens found (file empty or only blank lines).")

    token_set = set(tokens)

    bad_pairs = []
    for a, b in product(tokens, repeat=2):
        merged = a + b
        if merged in token_set:
            bad_pairs.append((a, b, merged))

    if bad_pairs:
        print("COLLISIONS (a + b forms an existing token):")
        for a, b, merged in bad_pairs:
            print(f"{a!r} + {b!r} -> {merged!r}")
    else:
        print("OK: No pairwise merges produce an existing token.")


if __name__ == "__main__":
    main()
