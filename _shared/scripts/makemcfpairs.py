import sys
import argparse


def transform(path: str) -> str:
    base = path.rstrip()
    while base.lower().endswith('.wav'):
        base = base[:-4]
    mangled = ''.join(
        (ch.lower() if ch.isalnum() else '_')
        for ch in base
    )
    return f'mfc\\{mangled}.mfc'


def main():
    parser = argparse.ArgumentParser(
        description='Read a file of WAV paths and output each original path plus its MFC name.'
    )
    parser.add_argument(
        '-i','--input',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='text file with one WAV path per line (default: stdin)'
    )
    parser.add_argument(
        '-o','--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='where to write the mappings (default: stdout)'
    )
    parser.add_argument(
        '-s','--single',
        default=False,
        help='do not generate pairs (default: False)',
        action='store_true'
    )
    args = parser.parse_args()

    for line in args.input:
        line = line.strip()
        if not line:
            continue
        mapped = transform(line)
        if args.single:
            args.output.write(f'{mapped}\n')
        else:
            args.output.write(f'{line} {mapped}\n')


if __name__ == '__main__':
    main()
