import os
import argparse


def convert_phn_to_lab(phn_path, lab_path, sample_rate=16000):
    with open(phn_path, 'r') as fin, open(lab_path, 'w') as fout:
        for line in fin:
            start_samp, end_samp, label = line.strip().split()
            start_tick = int(int(start_samp) / sample_rate * 1e7)
            end_tick   = int(int(end_samp)   / sample_rate * 1e7)
            fout.write(f"{start_tick} {end_tick} {label}\n")


def main():
    p = argparse.ArgumentParser(
        description="Convert all .phn files under an input folder (recursively)\n"
                    "into .lab files in a single output folder."
    )
    p.add_argument("input_dir",  help="Root folder to search for .phn files")
    p.add_argument("output_dir", help="Folder where all .lab files will be saved")
    p.add_argument("--sample_rate", type=int, default=16000,
                   help="Audio sample rate (Hz), default=16000")
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    count = 0
    for root, _, files in os.walk(args.input_dir):
        for fname in files:
            if not fname.lower().endswith(".phn"):
                continue
            phn_path = os.path.join(root, fname)
            lab_pref = ''.join([a if a in 'abcdfeghijklmonpqrstuvwxyz0123456789' else '_' for a in root.lower()])
            lab_fname = lab_pref + '_' + os.path.splitext(fname)[0].lower() + ".lab"
            lab_path  = os.path.join(args.output_dir, lab_fname)
            convert_phn_to_lab(phn_path, lab_path, args.sample_rate)
            count += 1

    print(f"Converted {count} .phn files from “{args.input_dir}” → “{args.output_dir}”")


if __name__ == "__main__":
    main()
