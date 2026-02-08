from textgrid import TextGrid
import glob
import os


invalid_symbols = '?'
uppercase_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

tg_dir = "../textgridai_Aiste/"
lab_dir = "lab/"
os.makedirs(lab_dir, exist_ok=True)


allowed_phonemes=[]
with open('list', 'r') as file:
    allowed_phonemes = file.read().strip().splitlines()


for tg_path in glob.glob(os.path.join(tg_dir, "*.TextGrid")):
    basename = os.path.splitext(os.path.basename(tg_path))[0]
    tg = TextGrid.fromFile(tg_path)
    phone_tier = tg.getFirst("phones") if "phones" in [t.name for t in tg.tiers] else tg.tiers[0]
    lab_path = os.path.join(lab_dir, basename + ".lab")

    phoneme_start = 0
    last_end = 0
    phoneme = None

    with open(lab_path, "w") as outf:
        for interval in phone_tier.intervals:
            start_ns100 = int(interval.minTime * 1e7)
            end_ns100   = int(interval.maxTime * 1e7)
            label = interval.mark.strip() or "sp"
            for symbol in invalid_symbols:
                label = label.replace(symbol, '_')
            if label in ['_?', '_+', '_!']:
                label = '_'
            # for upper in uppercase_symbols:
            #     label = label.replace(upper, upper.lower() + '_upper')
            # label=label.strip('+?!*\'-').lower()[-1]
            if label not in allowed_phonemes:
                last_end = end_ns100
                continue
            if phoneme and label != phoneme:
                outf.write(f"{phoneme_start} {start_ns100} {phoneme}\n")
                phoneme_start = start_ns100
            last_end = end_ns100
            phoneme = label
        outf.write(f"{phoneme_start} {last_end} {phoneme}\n")

    print(f"Wrote {lab_path}")
