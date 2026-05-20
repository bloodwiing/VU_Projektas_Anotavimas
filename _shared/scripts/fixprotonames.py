import glob
import os
import re
import argparse


def main():
    parser = argparse.ArgumentParser(description="Rename proto files based on internal ~h tags.")
    parser.add_argument("proto_dir", help="Directory or glob pattern for proto files (e.g., 'hmms/proto' or 'hmms/proto/*')")
    args = parser.parse_args()

    search_pattern = args.proto_dir
    if os.path.isdir(search_pattern):
        search_pattern = os.path.join(search_pattern, "*")

    for proto_path in glob.glob(search_pattern):
        if not os.path.isfile(proto_path):
            continue
            
        with open(proto_path, 'r') as file:
            text = file.read()
        
        match = re.search(r'~h "(.*?)"', text)
        if match:
            name = match.group(1)
            proto_path_new = os.path.join(os.path.dirname(proto_path), name)
            
            temp_path = proto_path + ".TEMP"
            os.rename(proto_path, temp_path)
            print(proto_path, temp_path)
            os.rename(temp_path, proto_path_new)
            print(temp_path, proto_path_new)
            
            print(f"{proto_path} -> {proto_path_new}")
        else:
            print(f"Skipped {proto_path}: No match found.")


if __name__ == "__main__":
    main()
