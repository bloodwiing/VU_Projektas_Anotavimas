import re
import argparse


def process_qs_file(input_file, output_file):
    qs_pattern = re.compile(r'^\s*QS\s+"([^"]+)"\s+\{(.*)\}\s*$')

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            stripped_line = line.strip()

            if stripped_line.startswith('#'):
                continue

            if not stripped_line:
                outfile.write(line)
                continue

            match = qs_pattern.match(stripped_line)
            if match:
                name = match.group(1)
                content = match.group(2)

                # Split items by comma and strip whitespace
                items = [item.strip() for item in content.split(',')]

                # Generate Left Context line (Name -> L_Name, item -> item-*)
                l_name = f"L_{name}"
                l_items = [f"{item}-*" for item in items]
                l_line = f'QS "{l_name}" {{{",".join(l_items)}}}\n'

                # Generate Right Context line (Name -> R_Name, item -> *+item)
                r_name = f"R_{name}"
                r_items = [f"*+{item}" for item in items]
                r_line = f'QS "{r_name}" {{{",".join(r_items)}}}\n'

                # Write both new lines to output
                outfile.write(l_line)
                outfile.write(r_line)
            else:
                # If a line has content but isn't a QS line, write it as is
                outfile.write(line)

    print(f"Successfully converted '{input_file}' to '{output_file}'")


def main():
    parser = argparse.ArgumentParser(description="Convert HTS/Merlin QS file format to Left/Right context format.")
    parser.add_argument("input", help="Path to the input file")
    parser.add_argument("output", help="Path to the output file")

    args = parser.parse_args()

    try:
        process_qs_file(args.input, args.output)
    except FileNotFoundError:
        print(f"Error: The file '{args.input}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
