import argparse
import os


def process_file(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            count = 0
            for line in infile:
                clean_text = line.strip()
                if clean_text:
                    # Double the text
                    outfile.write(f"{clean_text} {clean_text}\n")
                    count += 1
        
        print(f"Success! Processed {count} lines.")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description="Read a file and duplicate the content of each line.")
    parser.add_argument("input", help="The path to the text file you want to read.")
    parser.add_argument("output", help="The path where the result should be saved.")
    args = parser.parse_args()

    process_file(args.input, args.output)


if __name__ == "__main__":
    main()
