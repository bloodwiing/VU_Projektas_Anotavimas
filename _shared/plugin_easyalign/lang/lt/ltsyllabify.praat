tgID=selected("TextGrid")
include ../../utils.praat
printline Syllabify (LT)...
select 'tgID'

call findtierbyname phones 1 1
phonesTID = findtierbyname.return
call findtierbyname syll 0 1
syllTID = findtierbyname.return

if syllTID!=0
  Remove tier... 'syllTID'
  printline Removing previous syll tier
endif

syllTID=phonesTID+1
Duplicate tier... 'phonesTID' 'syllTID' syll

call findtierbyname phono 1 1
phonoTID = findtierbyname.return

limit = Get number of intervals... 'syllTID'
current = 1

call getcurrentsentence
sentence$ = getcurrentsentence.return$

sylltext$=""

current = 0
for .ii to limit
  current = current+1
  phon$ = Get label of interval... 'syllTID' 'current'
  printline '.ii' ('current') : |'sylltext$'| |'phon$'|

  if sylltext$==""
    call getcurrentsentence
    sentence$=getcurrentsentence.return$
  endif

  if phon$=="_"
    sylltext$=""
  elsif phon$==""
  elsif sylltext$==""
    sylltext$=phon$
  else
    test1$=sylltext$+phon$

    if startsWith(sentence$,test1$)==0
      test2$=sylltext$+" "+phon$
      if startsWith(sentence$,test2$)==0
        test3$=sylltext$+"|"+phon$
        if startsWith(sentence$,test3$)==0
          test4$=sylltext$+"-"+phon$
          if startsWith(sentence$,test4$)==0
            printline Failed to reconstruct
            printline Sentence: 'sentence$'
            printline Attempt 1: 'test1$'
            printline Attempt 2: 'test2$'
            printline Attempt 3: 'test3$'
            printline Attempt 4: 'test4$'
            exit Failed to reconstruct syllables
          else
            # - separator
            # this is the separator between phones of the same syllable
            printline deleting boundary at |'sylltext$'| and |'phon$'|
            call delcurrent
            current = current-1
            sylltext$=test4$
          endif
        else
          # | separator
          sylltext$=test3$
        endif

      else
        # space separator
        sylltext$=test2$
      endif
    else
      # no separator
      sylltext$=test1$
    endif
  endif
endfor

procedure delcurrent
  start = Get starting point... 'syllTID' 'current'
  printline 'start' of 'current'
  Remove boundary at time... 'syllTID' 'start'
endproc

procedure getcurrentsentence
  start = Get starting point... 'syllTID' 'current'
  .int = Get interval at time... 'phonoTID' 'start'
  .return$ = Get label of interval... 'phonoTID' '.int'
endproc
