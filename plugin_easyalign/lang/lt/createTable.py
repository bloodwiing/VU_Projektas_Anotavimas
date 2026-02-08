import argparse
import re
import sys


REGEX_LIST = [
    re.compile(r"^[A-Za-z]{2}_pal$"),
    re.compile(r"^[A-Za-z]{2}$"),
    re.compile(r"^[A-Za-z]{1}_pal$"),
    re.compile(r"^[A-Za-z]{1}$"),
    re.compile(r"^sil$"),
]
REGEX_SAMPAIFICATION = [
    (re.compile(r"_pal$"),"'")
]


def filter_file(in_path: str | None, out_path: str | None) -> int:
    inp = sys.stdin if in_path is None else open(in_path, "r", encoding="utf-8")
    lines_in = inp.readlines()
    if inp is not sys.stdin:
        inp.close()
    lines_out: list[tuple[str, str]] = []
    for regex in REGEX_LIST:
        for raw in lines_in:
            line = raw.rstrip("\n")
            stripped = line.strip()

            if stripped == "":
                lines_out.append((line, line))
                continue

            if not regex.fullmatch(stripped):
                continue

            sampa = line
            for convert,replace in REGEX_SAMPAIFICATION:
                sampa = convert.sub(replace, sampa)

            lines_out.append((sampa, line))
    
    outlines = "caen\tsampa\thtk\texample\n"
    outlines += "\n".join([f'{sampa}\t{sampa}\t{htk}\t' for sampa, htk in lines_out]) + ("\n" if lines_out else "")

    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(outlines)
    else:
        sys.stdout.write(outlines)

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Filter out lines that match ^[a-zA-Z]{1}$ (single letter)."
    )
    ap.add_argument("input", nargs="?", help="Input file (default: stdin)")
    ap.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = ap.parse_args()
    return filter_file(args.input, args.output)


if __name__ == "__main__":
    main()
