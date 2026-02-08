import os
import argparse


def extract_unique_phonemes(input_folder, output_file, output_dict_file):
    phonemes = set()

    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return

    print(f"Scanning files in: {input_folder}...")

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            phoneme = parts[-1]
                            phonemes.add(phoneme)
            except Exception as e:
                print(f"Warning: Could not read file {filename}. Reason: {e}")
    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for phoneme in sorted(phonemes):
            out_f.write(f"{phoneme}\n")
    print(f"Successfully wrote {len(phonemes)} phonemes to: {output_file}")

    with open(output_dict_file, "w", encoding='utf-8') as outf:
        for phoneme in sorted(phonemes):
            outf.write(f"{phoneme} {phoneme}\n")
        outf.write("SENT-START [] sil\nSENT-END [] sil\n")
    print(f"Successfully wrote dictionary to: {output_dict_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract unique phonemes from label files in a directory."
    )
    parser.add_argument(
        "input_folder", 
        type=str, 
        help="Path to the folder containing label files."
    )
    parser.add_argument(
        "--list", "-l", 
        type=str, 
        default="phonemes.list", 
        help="Path for the output phoneme list file (default: phonemes.list)"
    )
    parser.add_argument(
        "--dict", "-d", 
        type=str, 
        default="phoneme_dict.txt", 
        help="Path for the output dictionary file (default: phoneme_dict.txt)"
    )
    args = parser.parse_args()

    extract_unique_phonemes(args.input_folder, args.list, args.dict)


if __name__ == "__main__":
    main()
