import re
import argparse


def consolidate_hmm(input_file, output_file, target, sources):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    template_content = None
    for src in sources:
        pattern = re.compile(fr'~h "{src}".*?\n(?=~h|\Z)', re.DOTALL)
        match = pattern.search(content)
        if match:
            print(f"Using '{src}' as the template for '{target}'...")
            template_content = match.group(0).replace(f'~h "{src}"', f'~h "{target}"')
            break
    
    if not template_content:
        print(f"Error: None of the source models {sources} were found in the file.")
        return

    all_to_remove = sources + [target]
    for label in all_to_remove:
        content = re.sub(fr'~h "{label}".*?\n(?=~h|\Z)', '', content, flags=re.DOTALL)

    new_content = content.strip() + "\n" + template_content
    
    with open(output_file, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully consolidated {sources} into '{target}' in file: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Consolidate multiple HMM labels into one.")
    parser.add_argument("-i", "--input", required=True, help="Input hmmdefs file")
    parser.add_argument("-o", "--output", required=True, help="Output hmmdefs file")
    parser.add_argument("-t", "--target", default="sil", help="The new label name (default: sil)")
    parser.add_argument("sources", nargs="+", help="The labels to be merged (e.g., h# pau epi)")

    args = parser.parse_args()
    consolidate_hmm(args.input, args.output, args.target, args.sources)


if __name__ == "__main__":
    main()
