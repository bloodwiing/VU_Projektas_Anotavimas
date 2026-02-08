import argparse


def generate_hed(monophone_file, triphone_file):
    try:
        with open(monophone_file, 'r') as f:
            # Read lines and filter out empty ones
            phones = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not read monophone file '{monophone_file}'")
        return

    print(f'CL "{triphone_file}"')
    print("")

    for p in phones:
        if p == "sp":
            continue
            
        print(f"TI T_{p} {{(*-{p}+*,{p}+*,*-{p},{p}).transP}}")


def main():
    parser = argparse.ArgumentParser(description="Generate HTK HHEd cloning script.")
    parser.add_argument("monophones", help="Path to your existing monophone list file")
    parser.add_argument("triphones", help="Name of the triphone list file for the CL command")

    args = parser.parse_args()
    generate_hed(args.monophones, args.triphones)


if __name__ == "__main__":
    main()
