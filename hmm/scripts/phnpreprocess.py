import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Segment:
    start: int
    end: int
    label: str


def parse_segments(lines: list[str], src: str = "<input>") -> list[Segment]:
    segs: list[Segment] = []
    for lineno, line in enumerate(lines, start=1):
        raw = line
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"{src}:{lineno}: expected 3 columns, got {len(parts)}: {raw!r}")
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError as e:
            raise ValueError(f"{src}:{lineno}: start/end must be integers: {raw!r}") from e
        label = parts[2]
        if end < start:
            raise ValueError(f"{src}:{lineno}: end < start: {raw!r}")
        segs.append(Segment(start=start, end=end, label=label))
    return segs


def process_segments(
    segs: list[Segment],
    pause_units: int = 100_000,
    max_fraction: float = 0.5,
    insert_sp: bool = True,
) -> list[Segment]:
    plus_indices = [i for i, s in enumerate(segs) if "+" in s.label]
    to_insert = set(plus_indices[1:-1]) if len(plus_indices) >= 3 else set()

    out: list[Segment] = []
    for i, s in enumerate(segs):
        base_label = s.label.replace("-", "").replace("+", "").replace(",", "")

        if base_label.startswith('_'):
            base_label = 'sil'

        if base_label.endswith("'"):
            base_label = base_label[:-1] + '_pal'

        candidates = []
        
        if insert_sp and i in to_insert:
            dur = s.end - s.start
            max_by_fraction = int(dur * max_fraction)
            p = min(pause_units, max_by_fraction)

            if p <= 0:
                candidates.append(Segment(s.start, s.end, base_label))
            else:
                phon_end = s.end - p
                if phon_end <= s.start:
                    candidates.append(Segment(s.start, s.end, base_label))
                else:
                    candidates.append(Segment(s.start, phon_end, base_label))
                    candidates.append(Segment(phon_end, s.end, "sp"))
        else:
            candidates.append(Segment(s.start, s.end, base_label))

        if candidates:
            first_cand = candidates[0]
        
            if out and out[-1].label == first_cand.label:
                out[-1].end = first_cand.end
                
                if len(candidates) > 1:
                    out.append(candidates[1])
            else:
                out.extend(candidates)

    return out


def iter_input_files(in_dir: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted([p for p in in_dir.rglob("*") if p.is_file()])
    return sorted([p for p in in_dir.iterdir() if p.is_file()])


def normalize_ext(ext: str | None) -> str | None:
    if ext is None:
        return None
    ext = ext.strip()
    if not ext:
        return None
    return ext if ext.startswith(".") else "." + ext


def output_path_for(src_path: Path, in_dir: Path, out_dir: Path, out_ext: str | None) -> Path:
    rel = src_path.relative_to(in_dir)
    dst = out_dir / rel
    if out_ext is not None:
        dst = dst.with_suffix(out_ext)
    return dst


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch strip '-' and insert 'sp' after internal '+' markers.")
    ap.add_argument("input_dir", help="Folder containing input files")
    ap.add_argument("output_dir", help="Folder to write output files")
    ap.add_argument(
        "--pause-units",
        type=int,
        default=100_000,
        help="Pause duration in time units (default: 100000 = 10ms in your units)",
    )
    ap.add_argument(
        "--max-fraction",
        type=float,
        default=0.5,
        help="Max pause as fraction of the '+' phoneme duration (default: 0.5)",
    )
    ap.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process files and mirror directory structure in output",
    )
    ap.add_argument(
        "--ext",
        default=None,
        help="Only process input files with this extension (e.g. .lab). Default: process all files.",
    )
    ap.add_argument(
        "--out-ext",
        default=None,
        help="Force output extension (e.g. .lab, .txt). Default: keep original extension.",
    )
    ap.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding for reading/writing files (default: utf-8)",
    )
    ap.add_argument(
        "--no-sp",
        default=False,
        action='store_true',
        help="Disable inserting SP in word boundaries",
    )

    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists() or not in_dir.is_dir():
        print(f"ERROR: input_dir is not a directory: {in_dir}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    in_ext = normalize_ext(args.ext)
    out_ext = normalize_ext(args.out_ext)

    files = iter_input_files(in_dir, args.recursive)
    if in_ext:
        files = [p for p in files if p.suffix == in_ext]

    if not files:
        print("No files found to process.", file=sys.stderr)
        return 0

    processed = 0
    failed = 0

    for src_path in files:
        rel = src_path.relative_to(in_dir)
        dst_path = output_path_for(src_path, in_dir, out_dir, out_ext)
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            text = src_path.read_text(encoding=args.encoding)
            segs = parse_segments(text.splitlines(True), src=str(rel))
            out = process_segments(segs, pause_units=args.pause_units, max_fraction=args.max_fraction, insert_sp=not args.no_sp)
            out_text = "".join(f"{s.start} {s.end} {s.label}\n" for s in out)
            dst_path.write_text(out_text, encoding=args.encoding)
            processed += 1
        except Exception as e:
            failed += 1
            print(f"FAILED: {rel}: {e}", file=sys.stderr)

    print(f"Done. Processed={processed}, Failed={failed}", file=sys.stderr)
    return


if __name__ == "__main__":
    main()
