clearinfo
eadir$=preferencesDirectory$+"\plugin_easyalign\"
Read from file... en2.wav
Read Strings from raw text file... en2.txt
pause Sound and transcription loaded. Launch step#1 Utterance segmentation ?
select Sound en2
plus Strings en2
execute "'eadir$'utt_seg2.praat" ortho yes
pause Utterance segmentation done. Launch step#2 Phonetisation ?
editor TextGrid en2
 Close
endeditor
select TextGrid en2
execute "'eadir$'phonetize_orthotier2.praat" ortho phono en2 yes yes
pause Phonetisation. Launch step#3 Phoneme Segmentation ?
editor TextGrid en2
 Close
endeditor
select Sound en2
plus TextGrid en2
execute "'eadir$'align_sound.praat" ortho phono yes en2 }?^ no yes no 90 yes yes
   
