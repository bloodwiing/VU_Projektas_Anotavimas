# Path
PATH=$PATH:/mnt/c/Users/BLOODWIING/Documents/CourseWork/HTK-3.5-beta/htk/HTKTools

# Convert WAV -> MFCC
HCopy -C wavtomfc.conf -S wav.scp -T 1

# Create train.scp
ls mfc/*.mfc > train.scp

# Create train.labs
ls lab/*.lab > train.labs

# Generate List file
python generatelist.py

# Convert TextGrid -> Lab
python generatelab.py

# Create prototype HMM
perl MakeProtoHMMSet protoconf.pcf

# Fix prototype names
python fixprotonames.py

# Init ONE prototype
HInit -S train.scp -I labels.mlf -M hmms/hmm0 -l _ -T 3 proto/aa

# Create MLK
echo '#!MLF!#'                        > labels.mlf
for f in lab/*.lab; do
  echo "\"*/$(basename "$f")\""       >> labels.mlf
  cat "$f"                            >> labels.mlf
  echo "."                            >> labels.mlf
done

# Init ALL prototypes (windows)
for %i in (proto/*) do HInit -S train.scp -I labels.mlf -M hmms/hmm0 -l %i -T 1 proto\%i
copy /Y proto\UNK hmms\hmm0\UNK

HInit -S train.scp -I labels.mlf -M hmms/hmm0 -T 3 -H proto

# Init ALL prototypes (unix)
for f in proto\* ; do
  HInit -S train.scp -L lab -M hmms/hmm0 -T 3 $f
done

# Reestimate ALL prototypes (windows)
for %i in (hmms/hmm0/*) do HRest -S train.scp -I labels.mlf -M hmms/hmm1 -l %i -T 1 hmms\hmm0\%i

# Reestimate ALL prototypes (unix)
for f in proto\* ; do
  HRest -S train.scp -L lab -M hmms/hmm1 -T 3 $f
done

# Generate hmm2 list
python generatehmm2list.py


# HVite
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm3/newMacros -M hmms/hmm4 -T 3 -A -D list

# HERest
HERest -C mfc.conf -I labels.mlf -S train.scp -d hmms/hmm1 -M hmms/hmm2 -T 3 -A -D list
HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm2/newMacros -i align.mlf -y lab dict list

HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm2/newMacros -M hmms/hmm3 -T 3 -A -D list
HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm3/newMacros -i align.mlf -y lab dict list

HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm3/newMacros -M hmms/hmm4 -T 3 -A -D list
HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm4/newMacros -i align.mlf -y lab dict list

HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm4/newMacros -M hmms/hmm5 -T 3 -A -D list
HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm5/newMacros -i align.mlf -y lab dict list

HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm5/newMacros -M hmms/hmm6 -T 3 -A -D list
HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm6/newMacros -M hmms/hmm7 -T 3 -A -D list
HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm7/newMacros -M hmms/hmm8 -T 3 -A -D list

HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm8/newMacros -M hmms/hmm9 -T 3 -A -D list
HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm9/newMacros -M hmms/hmm10 -T 3 -A -D list

HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm10/newMacros -M hmms/hmm11 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm11/newMacros -M hmms/hmm12 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm12/newMacros -M hmms/hmm13 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm13/newMacros -M hmms/hmm14 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm14/newMacros -M hmms/hmm15 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm15/newMacros -M hmms/hmm16 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm16/newMacros -M hmms/hmm17 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm17/newMacros -M hmms/hmm18 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm18/newMacros -M hmms/hmm19 -T 3 -A -D list
HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm19/newMacros -M hmms/hmm20 -T 3 -A -D list

HERest -A -w 3 -v 0.05 -C herest.conf -u tmvw -d hmms/hmm1 -D -M hmms/hmm2 -I labels.mlf -t 2000.0 -T 1 -S train.scp -l w hmm2list

# Results
HResults -I labels.mlf hmms/hmm2/newMacros mfc/032a.mfc

# HCompV
for %i in (proto/*) do HCompV -C mfc.conf -I labels.mlf -f 0.01 -m -S train.scp -M hmms/hmm8 -T 2 -l %i proto/%i
HCompV -C mfc.conf -I labels.mlf -f 0.01 -m -S train.scp -M hmms/hmm1 -T 2 proto/


HVite -C mfc.conf -S test.scp -H hmms/hmm2/newMacros -i recout.mlf -y lab dict list
HVite -C mfc.conf -S test.scp -H hmms/hmm6/newMacros -i recout.mlf -o W -m -w phone.net -y lab dict list
HResults -I labels.mlf list recout.mlf



HVite -C mfc.conf -H hmms/hmm2/newMacros -T 3 -y lab -o W -m dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
h# sh iy hv ae dcl d y er dcl d aa r kcl k s uw dx ih ng gcl g r iy s iy w aa sh epi w aa dx er q ao l y iy axr h#  ==  [395 frames] -39.0367 [Ac=-15419.5 LM=0.0] (Act=70.1)


# List -> Grammar
python grammar.py -i list -o gramar --silence "h#"

# HBuild Phoneme network
HParse gramar phone.net

# Predict
HVite -C mfc.conf -H hmms/hmm2/newMacros -T 3 -y lab -o W -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
HVite -C mfc.conf -H hmms/hmm6/newMacros -T 3 -y lab -o W -i recout.mlf -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
HVite -C mfc.conf -H hmms/hmm6/newMacros -T 3 -y lab -o W -i recout.mlf -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_si2203.mfc



# Train accuracy
HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S train.scp dict list
# Test accuracy
HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S test.scp dict list
# Both (match the labels.mlf)
HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S test.scp -S train.scp dict list