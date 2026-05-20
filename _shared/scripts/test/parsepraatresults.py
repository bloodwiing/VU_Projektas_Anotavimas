import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    total_correct = 0
    total_incorrect = 0

    with open(args.input, 'r', encoding='utf-8') as infile:
        next(infile) 
        for line in infile:
            parts = line.strip().split()
            if len(parts) >= 3:
                total_correct += int(parts[1])
                total_incorrect += int(parts[2])

    if total_correct + total_incorrect > 0:
        accuracy = total_correct / (total_correct + total_incorrect)
    else:
        accuracy = 0.0

    with open(args.output, 'w', encoding='utf-8') as outfile:
        outfile.write(f"{accuracy}\n")


if __name__ == "__main__":
    main()
