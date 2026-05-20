# Path
PATH=$PATH:/mnt/d/Uni/Bachelors/CourseWork/HTK-3.5-beta/htk/HTKTools
. env.sh

# Save wav.list
ls ../wav/*.wav > datasets/wav/wav.list

# Convert WAV -> MFCC
HCopy -C configs/wavtomfc.conf -S datasets/wav/wav.scp -T 1

# Preprocess phn files to lab
python scripts/phnpreprocess.py ../phon/ ./data/lab --ext phn --out-ext lab --no-sp

# Create train.scp
ls data/mfc/*.mfc > datasets/train/train.scp

# Create train.labs
ls data/lab/*.lab > datasets/train/train.labs

# Generate List and Dict file
python scripts/generatelistfromlab.py -l context/mono/list -d context/mono/dict data/lab

# Create prototype HMM
perl scripts/MakeProtoHMMSet configs/protoconf.pcf

# Fix prototype names
python scripts/fixprotonames.py

# Create MLF
python scripts/makemlf.py -i datasets/train/train.labs -o context/mono/labels.mlf

# Rename labels
# python scripts/editor.py -i context/mono/list -o context/mono/list -- "-ax-h" "+axh"
# mv context/mono/labels.mlf context/mono/bad_labels.mlf
# HLEd -l '*' -i context/mono/labels.mlf edit/rename.led context/mono/bad_labels.mlf
# rm context/mono/bad_labels.mlf
# python scripts/generatebasicdict.py context/mono/list context/mono/dict

# Create a new flat start based on statistics
command time -p -o hmms/flat/avg/time.txt HCompV -C configs/mfc.conf -f 0.01 -m -S datasets/train/train.scp -M hmms/flat/avg hmms/proto/a
python scripts/makeflatstart.py

# Initial test results
python scripts/editor.py -i context/mono/list -o context/mono/wordlist -- "+SENT-START" "+SENT-END"
HLStats -b context/mono/phones.arpa -o -t 1 -s SENT-START SENT-END context/mono/list context/mono/labels.mlf
HBuild -n context/mono/phones.arpa -s SENT-START SENT-END context/mono/wordlist context/mono/rec_network
HVite -T 1 -H hmms/flat/macros -H hmms/flat/hmmdefs -S datasets/train/train.scp -i hmms/flat/recout.mlf -w context/mono/rec_network context/mono/dict context/mono/list
HResults -I context/mono/labels.mlf context/mono/list hmms/flat/recout.mlf > hmms/flat/result.txt

# Reestimate prototypes 3 times
command time -p -o hmms/mono/1/time.txt HERest -C configs/mfc.conf -I context/mono/labels.mlf -S datasets/train/train.scp -H hmms/flat/macros -H hmms/flat/hmmdefs -M hmms/mono/1 context/mono/list
HVite -T 1 -H hmms/mono/1/macros -H hmms/mono/1/hmmdefs -S datasets/train/train.scp -i hmms/mono/1/recout.mlf -w context/mono/rec_network context/mono/dict context/mono/list
HResults -I context/mono/labels.mlf context/mono/list hmms/mono/1/recout.mlf > hmms/mono/1/result.txt

# Reestimate prototypes 3 times
command time -p -o hmms/mono/2/time.txt HERest -C configs/mfc.conf -I context/mono/labels.mlf -S datasets/train/train.scp -H hmms/mono/1/macros -H hmms/mono/1/hmmdefs -M hmms/mono/2 context/mono/list
HVite -T 1 -H hmms/mono/2/macros -H hmms/mono/2/hmmdefs -S datasets/train/train.scp -i hmms/mono/2/recout.mlf -w context/mono/rec_network context/mono/dict context/mono/list
HResults -I context/mono/labels.mlf context/mono/list hmms/mono/2/recout.mlf > hmms/mono/2/result.txt

# Reestimate prototypes 3 times
command time -p -o hmms/mono/3/time.txt HERest -C configs/mfc.conf -I context/mono/labels.mlf -S datasets/train/train.scp -H hmms/mono/2/macros -H hmms/mono/2/hmmdefs -M hmms/mono/3 context/mono/list
HVite -T 1 -H hmms/mono/3/macros -H hmms/mono/3/hmmdefs -S datasets/train/train.scp -i hmms/mono/3/recout.mlf -w context/mono/rec_network context/mono/dict context/mono/list
HResults -I context/mono/labels.mlf context/mono/list hmms/mono/3/recout.mlf > hmms/mono/3/result.txt

# Merge h# into sil
# Merge pau and epi into sp
# python scripts/editor.py -i context/mono/list -o context/mono_sil/list -- "-h#" "+sil" "-pau" "-epi" "+sp"
# python scripts/generatebasicdict.py context/mono_sil/list context/mono_sil/dict
# HLEd -l '*' -i context/mono_sil/labels.mlf edit/mergesil.led context/mono/labels.mlf
# python scripts/mergehmm.py -i hmms/mono/3/hmmdefs -o hmms/mono/4/hmmdefs -t sil "h#"
# python scripts/mergehmm.py -i hmms/mono/3/hmmdefs -o hmms/mono/4/hmmdefs -t sp pau epi
# command time -p -o hmms/mono/4/time.txt HHEd -H hmms/mono/4/hmmdefs -H hmms/mono/3/macros -M hmms/mono/4 -T 1 edit/silloop.hed context/mono_sil/list
# HBuild -t SENT-START SENT-END context/mono_sil/list context/mono_sil/rec_network

# HVite -H hmms/mono/4/macros -H hmms/mono/4/hmmdefs -S datasets/train/train.scp -i hmms/mono/4/recout.mlf -w context/mono_sil/rec_network context/mono_sil/dict context/mono_sil/list
# HResults -I context/mono_sil/labels.mlf context/mono_sil/list hmms/mono/4/recout.mlf > hmms/mono/4/result.txt

# Fix sil and sp
cp context/mono/list context/mono_sil/list
cp context/mono/dict context/mono_sil/dict
cp context/mono/labels.mlf context/mono_sil/labels.mlf
cp context/mono/rec_network context/mono_sil/rec_network
command time -p -o hmms/mono/4/time.txt HHEd -H hmms/mono/3/hmmdefs -H hmms/mono/3/macros -M hmms/mono/4 -T 1 edit/silloop.hed context/mono_sil/list

HVite -T 1 -H hmms/mono/4/macros -H hmms/mono/4/hmmdefs -S datasets/train/train.scp -i hmms/mono/4/recout.mlf -w context/mono_sil/rec_network context/mono_sil/dict context/mono_sil/list
HResults -I context/mono_sil/labels.mlf context/mono_sil/list hmms/mono/4/recout.mlf > hmms/mono/4/result.txt

# Reestimate prototypes 3 times
command time -p -o hmms/mono/5/time.txt HERest -C configs/mfc.conf -I context/mono_sil/labels.mlf -S datasets/train/train.scp -H hmms/mono/4/macros -H hmms/mono/4/hmmdefs -M hmms/mono/5 context/mono_sil/list
HVite -T 1 -H hmms/mono/5/macros -H hmms/mono/5/hmmdefs -S datasets/train/train.scp -i hmms/mono/5/recout.mlf -w context/mono_sil/rec_network context/mono_sil/dict context/mono_sil/list
HResults -I context/mono_sil/labels.mlf context/mono_sil/list hmms/mono/5/recout.mlf > hmms/mono/5/result.txt

# Make triphones
cp context/mono_sil/list context/tri/monolist
HLEd -n context/tri/trilist -l '*' -i context/tri/labels.mlf edit/mktri.led context/mono_sil/labels.mlf
cat context/tri/monolist context/tri/trilist | sort | uniq > context/tri/list
python scripts/producetriedit.py context/tri/monolist context/tri/list > edit/gen/mktri.hed
HHEd -H hmms/mono/5/hmmdefs -H hmms/mono/5/macros -M hmms/tri/1 -T 1 edit/gen/mktri.hed context/tri/monolist
cp context/mono_sil/rec_network context/tri/rec_network
cp context/mono_sil/dict context/tri/dict

# TODO: next
# Reestimate triphones 2 times
command time -p -o hmms/tri/2/time.txt HERest -C configs/mfc.conf -I context/tri/labels.mlf -S datasets/train/train.scp -H hmms/tri/1/macros -H hmms/tri/1/hmmdefs -M hmms/tri/2 context/tri/list
HVite -T 1 -C configs/hvitetri.conf -H hmms/tri/2/macros -H hmms/tri/2/hmmdefs -S datasets/train/train.scp -i hmms/tri/2/recout.mlf -w context/tri/rec_network context/tri/dict context/tri/list
HResults -s -I context/tri/labels.mlf context/tri/list hmms/tri/2/recout.mlf > hmms/tri/2/result.txt

# Reestimate triphones 2 times
command time -p -o hmms/tri/3/time.txt HERest -C configs/mfc.conf -I context/tri/labels.mlf -S datasets/train/train.scp -H hmms/tri/2/macros -H hmms/tri/2/hmmdefs -M hmms/tri/3 -s hmms/tri/3/stats context/tri/list
HVite -T 1 -C configs/hvitetri.conf -H hmms/tri/3/macros -H hmms/tri/3/hmmdefs -S datasets/train/train.scp -i hmms/tri/3/recout.mlf -w context/tri/rec_network context/tri/dict context/tri/list
HResults -s -I context/tri/labels.mlf context/tri/list hmms/tri/3/recout.mlf > hmms/tri/3/result.txt

# Questions
python scripts/validateqs.py edit/qs.hed context/mono_sil/list
python scripts/mirrorqs.py edit/qs.hed edit/gen/qs.hed

# Decision tree and state tying
python scripts/producetreeedit.py -m context/mono_sil/list -q edit/gen/qs.hed -s hmms/tri/3/stats -t 350 -r 100 -o edit/gen/mktie.hed -l context/tri_full/list -L context/tri_full/tiedlist -T context/tri_full/trees -c "sil"
command time -p -o hmms/tri/4/time.txt HHEd -H hmms/tri/3/macros -H hmms/tri/3/hmmdefs -M hmms/tri/4 -T 1 edit/gen/mktie.hed context/tri/list
cp context/tri/rec_network context/tri_full/rec_network
cp context/tri/dict context/tri_full/dict
cp context/tri/labels.mlf context/tri_full/labels.mlf

# Reestimate final tied-state triphones 3 times
command time -p -o hmms/tri/5/time.txt HERest -C configs/mfc.conf -I context/tri_full/labels.mlf -S datasets/train/train.scp -H hmms/tri/4/macros -H hmms/tri/4/hmmdefs -M hmms/tri/5 context/tri_full/tiedlist
HVite -T 1 -C configs/hvitetri.conf -H hmms/tri/5/macros -H hmms/tri/5/hmmdefs -S datasets/train/train.scp -i hmms/tri/5/recout.mlf -w context/tri_full/rec_network context/tri_full/dict context/tri_full/tiedlist
HResults -s -I context/tri_full/labels.mlf context/tri_full/tiedlist hmms/tri/5/recout.mlf > hmms/tri/5/result.txt

# Reestimate final tied-state triphones 3 times
command time -p -o hmms/tri/6/time.txt HERest -C configs/mfc.conf -I context/tri_full/labels.mlf -S datasets/train/train.scp -H hmms/tri/5/macros -H hmms/tri/5/hmmdefs -M hmms/tri/6 context/tri_full/tiedlist
HVite -T 1 -C configs/hvitetri.conf -H hmms/tri/6/macros -H hmms/tri/6/hmmdefs -S datasets/train/train.scp -i hmms/tri/6/recout.mlf -w context/tri_full/rec_network context/tri_full/dict context/tri_full/tiedlist
HResults -s -I context/tri_full/labels.mlf context/tri_full/tiedlist hmms/tri/6/recout.mlf > hmms/tri/6/result.txt

# Reestimate final tied-state triphones 3 times
command time -p -o hmms/tri/7/time.txt HERest -C configs/mfc.conf -I context/tri_full/labels.mlf -S datasets/train/train.scp -H hmms/tri/6/macros -H hmms/tri/6/hmmdefs -M hmms/tri/7 context/tri_full/tiedlist
HVite -T 1 -C configs/hvitetri.conf -H hmms/tri/7/macros -H hmms/tri/7/hmmdefs -S datasets/train/train.scp -i hmms/tri/7/recout.mlf -w context/tri_full/rec_network context/tri_full/dict context/tri_full/tiedlist
HResults -s -I context/tri_full/labels.mlf context/tri_full/tiedlist hmms/tri/7/recout.mlf > hmms/tri/7/result.txt

# Reestimate final tied-state triphones 3 times
command time -p -o hmms/tri/8/time.txt HERest -C configs/mfc.conf -I context/tri_full/labels.mlf -S datasets/train/train.scp -H hmms/tri/7/macros -H hmms/tri/7/hmmdefs -M hmms/tri/8 context/tri_full/tiedlist
PHVite -j 4 -T 1 -C configs/hvitetri.conf -H hmms/tri/8/macros -H hmms/tri/8/hmmdefs -S datasets/train/train.scp -i hmms/tri/8/recout.mlf -w context/tri_full/rec_network context/tri_full/dict context/tri_full/tiedlist
HResults -s -I context/tri_full/labels.mlf context/tri_full/tiedlist hmms/tri/8/recout.mlf > hmms/tri/8/result.txt

# # Init ONE prototype
# HInit -S train.scp -I labels.mlf -M hmms/hmm0 -l _ -T 3 proto/aa

# # Create MLK
# echo '#!MLF!#'                        > labels.mlf
# for f in lab/*.lab; do
#   echo "\"*/$(basename "$f")\""       >> labels.mlf
#   cat "$f"                            >> labels.mlf
#   echo "."                            >> labels.mlf
# done

# # Init ALL prototypes (windows)
# for %i in (proto/*) do HInit -S train.scp -I labels.mlf -M hmms/hmm0 -l %i -T 1 proto\%i
# copy /Y proto\UNK hmms\hmm0\UNK

# HInit -S train.scp -I labels.mlf -M hmms/hmm0 -T 3 -H proto

# # Init ALL prototypes (unix)
# for f in proto\* ; do
#   HInit -S train.scp -L lab -M hmms/hmm0 -T 3 $f
# done

# # Reestimate ALL prototypes (windows)
# for %i in (hmms/hmm0/*) do HRest -S train.scp -I labels.mlf -M hmms/hmm1 -l %i -T 1 hmms\hmm0\%i

# # Reestimate ALL prototypes (unix)
# for f in proto\* ; do
#   HRest -S train.scp -L lab -M hmms/hmm1 -T 3 $f
# done

# # Generate hmm2 list
# python generatehmm2list.py


# # HVite
# # HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm3/newMacros -M hmms/hmm4 -T 3 -A -D list

# # HERest
# HERest -C mfc.conf -I labels.mlf -S train.scp -d hmms/hmm1 -M hmms/hmm2 -T 3 -A -D list
# HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm2/newMacros -i align.mlf -y lab dict list

# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm2/newMacros -M hmms/hmm3 -T 3 -A -D list
# HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm3/newMacros -i align.mlf -y lab dict list

# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm3/newMacros -M hmms/hmm4 -T 3 -A -D list
# HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm4/newMacros -i align.mlf -y lab dict list

# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm4/newMacros -M hmms/hmm5 -T 3 -A -D list
# HVite -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm5/newMacros -i align.mlf -y lab dict list

# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm5/newMacros -M hmms/hmm6 -T 3 -A -D list
# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm6/newMacros -M hmms/hmm7 -T 3 -A -D list
# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm7/newMacros -M hmms/hmm8 -T 3 -A -D list

# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm8/newMacros -M hmms/hmm9 -T 3 -A -D list
# HERest -C mfc.conf -I align.mlf -S train.scp -H hmms/hmm9/newMacros -M hmms/hmm10 -T 3 -A -D list

# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm10/newMacros -M hmms/hmm11 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm11/newMacros -M hmms/hmm12 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm12/newMacros -M hmms/hmm13 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm13/newMacros -M hmms/hmm14 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm14/newMacros -M hmms/hmm15 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm15/newMacros -M hmms/hmm16 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm16/newMacros -M hmms/hmm17 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm17/newMacros -M hmms/hmm18 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm18/newMacros -M hmms/hmm19 -T 3 -A -D list
# HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/hmm19/newMacros -M hmms/hmm20 -T 3 -A -D list

# HERest -A -w 3 -v 0.05 -C herest.conf -u tmvw -d hmms/hmm1 -D -M hmms/hmm2 -I labels.mlf -t 2000.0 -T 1 -S train.scp -l w hmm2list

# # Results
# HResults -I labels.mlf hmms/hmm2/newMacros mfc/032a.mfc

# # HCompV
# for %i in (proto/*) do HCompV -C mfc.conf -I labels.mlf -f 0.01 -m -S train.scp -M hmms/hmm8 -T 2 -l %i proto/%i
# HCompV -C mfc.conf -I labels.mlf -f 0.01 -m -S train.scp -M hmms/hmm1 -T 2 proto/


# HVite -C mfc.conf -S test.scp -H hmms/hmm2/newMacros -i recout.mlf -y lab dict list
# HVite -C mfc.conf -S test.scp -H hmms/hmm6/newMacros -i recout.mlf -o W -m -w phone.net -y lab dict list
# HResults -I labels.mlf list recout.mlf



# HVite -C mfc.conf -H hmms/hmm2/newMacros -T 3 -y lab -o W -m dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
# h# sh iy hv ae dcl d y er dcl d aa r kcl k s uw dx ih ng gcl g r iy s iy w aa sh epi w aa dx er q ao l y iy axr h#  ==  [395 frames] -39.0367 [Ac=-15419.5 LM=0.0] (Act=70.1)


# # List -> Grammar
# python grammar.py -i list -o gramar --silence "h#"

# # HBuild Phoneme network
# HParse gramar phone.net

# # Predict
# HVite -C mfc.conf -H hmms/hmm2/newMacros -T 3 -y lab -o W -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
# HVite -C mfc.conf -H hmms/hmm6/newMacros -T 3 -y lab -o W -i recout.mlf -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_sa1.mfc
# HVite -C mfc.conf -H hmms/hmm6/newMacros -T 3 -y lab -o W -i recout.mlf -m -w phone.net dict list mfc/___archive_1__data_test_dr1_faks0_si2203.mfc



# # Train accuracy
# HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S train.scp dict list
# # Test accuracy
# HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S test.scp dict list
# # Both (match the labels.mlf)
# HVite -C mfc.conf -H hmms/hmm6/newMacros -y lab -o W -i recout.mlf -m -w phone.net -S test.scp -S train.scp dict list
