import argparse
import hashlib


def in_tuning_set(utterance_id, percent, seed):
    key = f"{seed}:{utterance_id}" if seed is not None else utterance_id
    digest = hashlib.md5(key.encode()).hexdigest()
    return int(digest[:8], 16) % 100 < percent


def filter_scp(input_path, output_path, percent, seed):
    with open(input_path, "r") as input_file, open(output_path, "w") as output_file:
        for line in input_file:
            stripped_line = line.strip()

            if not stripped_line:
                continue

            utterance_id = stripped_line.split(maxsplit=1)[0]

            if in_tuning_set(utterance_id, percent, seed):
                output_file.write(stripped_line + "\n")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_scp")
    parser.add_argument("output_scp")
    parser.add_argument("--percent", type=float, default=5.0)
    parser.add_argument("--seed", default=None)
    return parser.parse_args()


def main():
    args = parse_arguments()
    filter_scp(args.input_scp, args.output_scp, args.percent, args.seed)


if __name__ == "__main__":
    main()
