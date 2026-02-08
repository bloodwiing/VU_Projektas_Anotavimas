@echo off

set NUM_ITERS=30

set SKIP=6

set /A START=SKIP+1

set PREV=hmm%SKIP%

echo ====================================================
echo Resuming HERest: skipping first %SKIP% iterations
echo Will run iterations %START% through %NUM_ITERS%
echo Initial model dir: %PREV%
echo ====================================================

for /L %%I in (%START%,1,%NUM_ITERS%) do (
    set NEXT=hmm%%I
    echo --- Iteration %%I ---
    echo  Previous model dir: %PREV%
    echo  New model dir     : %NEXT%

    if not exist "hmms\%NEXT%" mkdir "hmms\%NEXT%"

    HERest -C mfc.conf -I labels.mlf -S train.scp -H hmms/%PREV%/newMacros -M hmms/%NEXT% -T 1 -A -D list

    echo [Iteration %%I complete] models in %NEXT%

    set PREV=!NEXT!
)
