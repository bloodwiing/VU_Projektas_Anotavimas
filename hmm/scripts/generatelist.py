from textgrid import TextGrid
import glob
import os
import pathlib


invalid_symbols = '?'
uppercase_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

tg_dir = "../textgridai_Aiste/"
labs_file = "train.labs"
list_file = "list"
dict_file = "dict"

phone_count = {}

req_paths = set()


with open(labs_file, 'r') as file:
    for item in file.read().strip().splitlines():
        req_paths.add(pathlib.Path(item).stem)


for tg_path in glob.glob(os.path.join(tg_dir, "*.TextGrid")):
    if pathlib.Path(tg_path).stem not in req_paths:
        continue

    print(f"Checking {os.path.basename(tg_path)}")
    basename = os.path.splitext(os.path.basename(tg_path))[0]
    tg = TextGrid.fromFile(tg_path)
    phone_tier = tg.getFirst("phones") if "phones" in [t.name for t in tg.tiers] else tg.tiers[0]

    for interval in phone_tier.intervals:
        label = interval.mark.strip() or "sp"
        for symbol in invalid_symbols:
            label = label.replace(symbol, '_')
        if label in ['_?', '_+', '_!', '__']:
            label = '_'
        # for upper in uppercase_symbols:
        #     label = label.replace(upper, upper.lower() + '_upper')
        # label=label.strip('+?!*\'-').lower()[-1]
        phone_count[label] = phone_count.get(label, 0) + 1


with open(list_file, "w") as outf:
    for label in phone_count:
        if phone_count[label] < 30:
            continue
        outf.write(f"{label}\n")


print(f"Wrote {list_file}")


with open(dict_file, "w") as outf:
    for label in phone_count:
        if phone_count[label] < 30:
            continue
        outf.write(f"{label} {label}\n")

   
print(f"Wrote {dict_file}")
