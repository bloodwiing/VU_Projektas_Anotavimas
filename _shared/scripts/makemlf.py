import os
import argparse

def main():
    # 1. Setup Argparse
    parser = argparse.ArgumentParser(
        description="Generate a Master Label File (MLF) from a list of label files."
    )
    
    parser.add_argument(
        '-i', '--input', 
        dest='labs_list',
        required=True,
        help="Path to the file listing the lab files"
    )
    
    parser.add_argument(
        '-o', '--output', 
        dest='output_mlf',
        required=True,
        help="Path to the output MLF file"
    )

    args = parser.parse_args()

    # 2. Main Logic
    try:
        with open(args.output_mlf, 'w') as mlf_out:
            mlf_out.write("#!MLF!#\n")
            
            # Check if input list exists before trying to read
            if not os.path.exists(args.labs_list):
                print(f"Error: The input file list '{args.labs_list}' was not found.")
                return

            with open(args.labs_list, 'r') as f:
                for line in f:
                    path = line.strip()
                    if not path: continue
                    
                    # Get filename
                    filename = os.path.basename(path) # Cleaner way to get filename than split('/')[-1]
                    
                    # Write HTK header
                    mlf_out.write(f'"*/{filename}"\n')
                    
                    # Read content and write to MLF
                    try:
                        with open(path, 'r') as lab_file:
                            content = lab_file.read().strip()
                            mlf_out.write(content + "\n")
                    except FileNotFoundError:
                        print(f"Warning: Could not find individual lab file: {path}")
                        continue
                        
                    # Write terminating period
                    mlf_out.write(".\n")

        print(f"Successfully created {args.output_mlf}")

    except IOError as e:
        print(f"An I/O error occurred: {e}")

if __name__ == "__main__":
    main()
