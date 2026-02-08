import argparse
import sys


def load_phones(path):
    phones = []
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            phones.append(ln)
    return phones


def make_grammar(phones, silence):
    loop_phones = [p for p in phones if p != silence]
    if not loop_phones:
        raise ValueError(f"No phones left to loop over (silence='{silence}').")

    lines = []
    body = "( " + silence + " ( " + " | ".join(loop_phones) + " )* " + silence + " )"
    lines.append(body)
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(
        description="Convert a phone-list into an HTK phoneloop grammar."
    )
    p.add_argument('-i','--input', required=True,
                   help="input phone list (one phone per line)")
    p.add_argument('-o','--output', default=None,
                   help="output grammar file (default stdout)")
    p.add_argument('--silence', default='sil',
                   help="name of the silence phone (default: sil)")
    args = p.parse_args()

    phones = load_phones(args.input)
    try:
        gram = make_grammar(phones, args.silence)
    except ValueError as e:
        sys.exit(f"Error: {e}")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(gram)
    else:
        sys.stdout.write(gram)


if __name__ == '__main__':
    main()
