import argparse
import re
from collections import Counter


RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner_error(missing_phonemes):
    border = "#" * 60
    print(f"\n{RED}{BOLD}{border}")
    print(f"CRITICAL ERROR: MISSING PHONEMES")
    print(f"{border}{RESET}")
    print(f"\nThe following phonemes are present in your list but")
    print(f"were {RED}NOT FOUND{RESET} in any question (QS) definition:\n")
    
    for p in sorted(missing_phonemes):
        print(f"  X  {p}")
    
    print(f"\n{RED}{BOLD}{border}{RESET}\n")


def print_excs_banner_error(excessive):
    border = "#" * 60
    print(f"\n{RED}{BOLD}{border}")
    print(f"CRITICAL ERROR: EXCESSIVE PHONEMES")
    print(f"{border}{RESET}")
    print(f"\nThe following phonemes are present in questions (QS) definitions but")
    print(f"were {RED}NOT FOUND{RESET} in your phoneme list:\n")
    
    for p in sorted(excessive):
        print(f"  X  {p}")
    
    print(f"\n{RED}{BOLD}{border}{RESET}\n")


def normalize_qs_item(item):
    item = item.strip()
    if item.endswith("-*"):
        item = item[:-2]
    if item.startswith("*+"):
        item = item[2:]
    return item


def parse_qs_file(filepath):
    qs_counts = Counter()
    brace_pattern = re.compile(r"^QS +\"\w+\" +\{([^}]+)\}", flags=re.MULTILINE)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = brace_pattern.findall(content)
            for match in matches:
                items = match.split(',')
                for item in items:
                    clean_item = normalize_qs_item(item)
                    if clean_item:
                        qs_counts[clean_item] += 1
    except FileNotFoundError:
        print(f"{RED}Error: QS file not found at {filepath}{RESET}")
        return Counter()
    return qs_counts


def parse_phoneme_list(filepath):
    phonemes = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                p = line.strip()
                if p:
                    phonemes.add(p)
    except FileNotFoundError:
        print(f"{RED}Error: Phoneme list file not found at {filepath}{RESET}")
        return set()
    return phonemes


def main():
    parser = argparse.ArgumentParser(
        description="Validate QS file coverage against a phoneme list.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("qs_file", help="Path to the .hed or QS definition file")
    parser.add_argument("phoneme_list", help="Path to the file containing the list of phonemes")
    
    parser.add_argument(
        "ignored_phonemes", 
        nargs="*", 
        help="Optional: Any remaining arguments will be treated as\nphonemes to IGNORE (suppress errors for them)."
    )
    
    args = parser.parse_args()

    qs_counts = parse_qs_file(args.qs_file)
    required_phonemes = parse_phoneme_list(args.phoneme_list)
    ignored_set = set(args.ignored_phonemes)

    real_missing = []
    ignored_missing = []
    excessive = []

    for p in required_phonemes:
        if p not in qs_counts:
            if p in ignored_set:
                ignored_missing.append(p)
            else:
                real_missing.append(p)

    for p in qs_counts:
        if p not in required_phonemes:
            excessive.append(p)

    if excessive:
        print_excs_banner_error(excessive)

        return

    if real_missing:
        print_banner_error(real_missing)
        
        if ignored_missing:
            print(f"{YELLOW}Note: The following missing phonemes were manually ignored:{RESET}")
            print(f"{YELLOW}{', '.join(sorted(ignored_missing))}{RESET}\n")
            
        return
    
    else:
        print(f"\n{GREEN}{BOLD}" + "="*60)
        print("SUCCESS: ALL (NON-IGNORED) PHONEMES ACCOUNTED FOR")
        print("="*60 + f"{RESET}\n")
        
        print(f"{'PHONEME':<15} | {'OCCURRENCES IN QS'}")
        print("-" * 35)
        
        for p in sorted(required_phonemes):
            if p in qs_counts:
                count = qs_counts[p]
                print(f"{p:<15} | {count}")
            elif p in ignored_set:
                print(f"{p:<15} | {YELLOW}IGNORED (Missing){RESET}")

        print("-" * 35)
        print(f"Total checked: {len(required_phonemes)}")
        if ignored_set:
            print(f"Ignored count: {len(ignored_set)}")


if __name__ == "__main__":
    main()
