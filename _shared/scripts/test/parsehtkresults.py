import argparse
import csv
import json
import re
import sys


def parse_word_accuracy(content):
    match = re.search(r'WORD:.*?Acc=([\d.]+)', content)
    return float(match.group(1)) / 100 if match else None


def parse_confusion_matrix(content):
    section = re.search(
        r'Confusion Matrix\s*-*\n(.*?)(?=\n=+|\n-{4,}|\Z)',
        content, re.DOTALL,
    )
    if not section:
        return None

    lines = section.group(1).split('\n')

    def strip_stats(line):
        return re.sub(r'\s*\[[^\]]*\]\s*$', '', line)

    def parse_data_row(line):
        body = strip_stats(line)
        tokens = body.split()
        if len(tokens) < 2:
            return None
        try:
            counts = [int(t) for t in tokens[1:]]
        except ValueError:
            return None
        return tokens[0], counts

    first_data_idx = None
    for i, line in enumerate(lines):
        if parse_data_row(line):
            first_data_idx = i
            break
    if first_data_idx is None:
        return None

    header_lines = [strip_stats(l) for l in lines[:first_data_idx]]
    data_lines = lines[first_data_idx:]

    first_data_body = strip_stats(lines[first_data_idx])
    spans = [(m.start(), m.end()) for m in re.finditer(r'\S+', first_data_body)]
    if len(spans) < 2:
        return None

    columns = []
    prev_end = spans[0][1]
    for (_, end) in spans[1:]:
        chars = []
        for hline in header_lines:
            segment = hline[prev_end:end] if prev_end < len(hline) else ''
            chars.append(segment.strip())
        columns.append(''.join(chars))
        prev_end = end

    confusion = {}
    correct = {}
    insertions = {}

    for line in data_lines:
        parsed = parse_data_row(line)
        if not parsed:
            continue
        label, counts = parsed

        if label == 'Ins':
            for col, count in zip(columns, counts):
                if col != 'Del':
                    insertions[col] = count
        else:
            row = dict(zip(columns, counts))
            confusion[label] = row
            correct[label] = row.get(label, 0)

    return {
        'labels': [c for c in columns if c != 'Del'],
        'confusion': confusion,
        'correct': correct,
        'insertions': insertions,
    }


def merge_score(stats, x, y):
    cxy = stats['confusion'].get(x, {}).get(y, 0)
    cyx = stats['confusion'].get(y, {}).get(x, 0)
    denom = stats['correct'].get(x, 0) + stats['correct'].get(y, 0)
    return (cxy + cyx) / denom if denom else 0.0


def total_occurrences(stats):
    return {label: sum(row.values()) for label, row in stats['confusion'].items()}


def all_merge_scores(stats, min_occurrences=0):
    labels = stats['labels']
    occ = total_occurrences(stats)
    pairs = []
    for i, x in enumerate(labels):
        for y in labels[i + 1:]:
            xo, yo = occ.get(x, 0), occ.get(y, 0)
            if min_occurrences and (xo < min_occurrences or yo < min_occurrences):
                continue
            pairs.append((x, y, merge_score(stats, x, y), xo, yo))
    pairs.sort(key=lambda p: -p[2])
    return pairs


def write_matrix_csv(stats, path):
    labels = stats['labels']
    columns = labels + ['Del']
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([''] + columns)
        for ref in labels:
            row = stats['confusion'].get(ref, {})
            w.writerow([ref] + [row.get(c, 0) for c in columns])
        if stats['insertions']:
            ins = ['Ins']
            for c in columns:
                ins.append('' if c == 'Del' else stats['insertions'].get(c, 0))
            w.writerow(ins)


def write_merges_csv(scores, path):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['x', 'y', 'merge_score', 'x_occ', 'y_occ'])
        for x, y, s, xo, yo in scores:
            w.writerow([x, y, f'{s:.6f}', xo, yo])


def parse_htk_results(input_path, output_path, phonemes_output=None, matrix_csv=None, merges_csv=None, min_occurrences=0):
    try:
        with open(input_path, 'r') as f:
            content = f.read()

        acc = parse_word_accuracy(content)
        if acc is None:
            print("Error: Could not find 'Acc=' value in the WORD results section.", file=sys.stderr)
            sys.exit(1)

        with open(output_path, 'w') as f:
            f.write(f"{acc:.4f}")
        print(f"Successfully parsed accuracy: {acc:.4f}")

        stats = parse_confusion_matrix(content)
        if stats is None:
            return

        scores = all_merge_scores(stats, min_occurrences=min_occurrences)
        out_json = phonemes_output or output_path + '.phonemes.json'
        out_matrix = matrix_csv or output_path + '.matrix.csv'
        out_merges = merges_csv or output_path + '.merges.csv'

        with open(out_json, 'w') as f:
            json.dump({
                'labels': stats['labels'],
                'confusion': stats['confusion'],
                'correct': stats['correct'],
                'insertions': stats['insertions'],
                'occurrences': total_occurrences(stats),
                'min_occurrences': min_occurrences,
                'merge_scores': [
                    {'x': x, 'y': y, 'score': s, 'x_occ': xo, 'y_occ': yo}
                    for x, y, s, xo, yo in scores
                ],
            }, f, indent=2)

        write_matrix_csv(stats, out_matrix)
        write_merges_csv(scores, out_merges)

        print(f"Wrote phoneme analysis to {out_json}")
        print(f"Wrote confusion matrix to {out_matrix}")
        print(f"Wrote merge scores to {out_merges}")
        if scores:
            note = f" (min_occurrences={min_occurrences})" if min_occurrences else ""
            print(f"Top 5 confusable pairs by merge_score{note}:")
            for x, y, s, xo, yo in scores[:5]:
                print(f"  {x:>6} <-> {y:<6}  {s:.4f}   (occ {xo} / {yo})")

    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract word accuracy and phoneme stats from HTK results.")
    parser.add_argument("input", help="Path to the HTK results text file")
    parser.add_argument("output", help="Path where the accuracy value will be saved")
    parser.add_argument("-j", "--phonemes-out", help="Path for phoneme analysis JSON (default: <output>.phonemes.json)")
    parser.add_argument("-m", "--matrix-csv", help="Path for confusion matrix CSV (default: <output>.matrix.csv)")
    parser.add_argument("-s", "--merges-csv", help="Path for merge scores CSV (default: <output>.merges.csv)")
    parser.add_argument("-n", "--min-occurrences", type=int, default=0, help="Drop merge pairs where either label has fewer than N reference occurrences (default: 0)")

    args = parser.parse_args()
    parse_htk_results(args.input, args.output, args.phonemes_out, args.matrix_csv, args.merges_csv, args.min_occurrences)
