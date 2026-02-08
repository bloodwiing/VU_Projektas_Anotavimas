PHONEME_LIST = "context/mono/list"
VFLOORS_FILE = "hmms/flat/avg/vFloors"
PROTO_FILE   = "hmms/flat/avg/a"
MACROS_OUT   = "hmms/flat/macros"
HMMDEFS_OUT  = "hmms/flat/hmmdefs"


with open(VFLOORS_FILE, 'r') as vf, open(MACROS_OUT, 'w') as mac:
    mac.write("~o\n")
    mac.write("<STREAMINFO> 1 39\n")
    mac.write("<VECSIZE> 39 <MFCC_D_A_0>\n")
    mac.write(vf.read())



with open(PROTO_FILE, 'r') as pf:
    all_lines = pf.readlines()
    start_index = 0
    for i, line in enumerate(all_lines):
        if "<BEGINHMM>" in line:
            start_index = i
            break
    proto_body = all_lines[start_index:] 


with open(PHONEME_LIST, 'r') as pl, open(HMMDEFS_OUT, 'w') as hd:
    for line in pl:
        phone = line.strip()
        if not phone: continue
        hd.write(f'~h "{phone}"\n')
        hd.writelines(proto_body)
