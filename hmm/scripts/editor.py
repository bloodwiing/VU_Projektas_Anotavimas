import argparse
import fnmatch


def main():
    parser = argparse.ArgumentParser(description="Edit, filter, and sort file lines.")
    
    parser.add_argument('-i', '--input', required=True, help="Input file path")
    parser.add_argument('-o', '--output', required=True, help="Output file path")
    
    parser.add_argument('commands', nargs=argparse.REMAINDER, 
                        help="Commands starting with + or -")

    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        return

    to_add = []
    to_remove_patterns = []

    for cmd in args.commands:
        cmd = cmd.strip()
        
        if cmd.startswith('+'):
            to_add.append(cmd[1:])
        elif cmd.startswith('-'):
            to_remove_patterns.append(cmd[1:])

    lines.extend(to_add)
    final_lines = [
        line for line in lines 
        if not any(fnmatch.fnmatch(line, pat) for pat in to_remove_patterns)
    ]

    final_lines.sort()

    with open(args.output, 'w') as f:
        for line in final_lines:
            f.write(line + '\n')
            
    print(f"Done! Processed {len(final_lines)} lines.")

if __name__ == "__main__":
    main()
