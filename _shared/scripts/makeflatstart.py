import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTK flat start macros and hmmdefs from prototype and vFloors."
    )

    parser.add_argument(
        "-p", "--phoneme-list", 
        default="context/mono/list",
        help="Path to the input phoneme list file (default: context/mono/list)"
    )
    parser.add_argument(
        "-v", "--vfloors", 
        default="hmms/flat/avg/vFloors",
        help="Path to the input vFloors file (default: hmms/flat/avg/vFloors)"
    )
    parser.add_argument(
        "-pr", "--proto", 
        default="hmms/flat/avg/a",
        help="Path to the input prototype HMM file (default: hmms/flat/avg/a)"
    )
    parser.add_argument(
        "-m", "--macros-out", 
        default="hmms/flat/macros",
        help="Path for the output macros file (default: hmms/flat/macros)"
    )
    parser.add_argument(
        "-hd", "--hmmdefs-out", 
        default="hmms/flat/hmmdefs",
        help="Path for the output hmmdefs file (default: hmms/flat/hmmdefs)"
    )

    args = parser.parse_args()

    try:
        with open(args.vfloors, 'r') as vf, open(args.macros_out, 'w') as mac:
            mac.write("~o\n")
            mac.write("<STREAMINFO> 1 39\n")
            mac.write("<VECSIZE> 39 <MFCC_D_A_0>\n")
            mac.write(vf.read())
    except IOError as e:
        print(f"Error processing macros: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.proto, 'r') as pf:
            all_lines = pf.readlines()
            start_index = 0
            for i, line in enumerate(all_lines):
                if "<BEGINHMM>" in line:
                    start_index = i
                    break
            proto_body = all_lines[start_index:] 
    except IOError as e:
        print(f"Error reading prototype file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.phoneme_list, 'r') as pl, open(args.hmmdefs_out, 'w') as hd:
            for line in pl:
                phone = line.strip()
                if not phone: 
                    continue
                hd.write(f'~h "{phone}"\n')
                hd.writelines(proto_body)
    except IOError as e:
        print(f"Error processing hmmdefs: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Files successfully generated.")


if __name__ == "__main__":
    main()
