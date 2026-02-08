import glob
import os
import re


proto_dir = "hmms/proto/*"


for proto_path in glob.glob(proto_dir):
    with open(proto_path, 'r') as file:
        text = file.read()
    name = re.search(r'~h "(.*?)"', text).group(1)
    proto_path_new = os.path.join(os.path.dirname(proto_path), name)
    os.rename(proto_path, 'TEMP')
    os.rename('TEMP', proto_path_new)
    print(proto_path, '->', proto_path_new)
