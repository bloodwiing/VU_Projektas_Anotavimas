set -euo pipefail

NUM_ITERS=30

HMM_DIR="hmms"
CONFIG="mfc.conf"
MLF="labels.mlf"
SCP="train.scp"
DICT="dict"
LIST="list"

for (( i=6; i<=NUM_ITERS; i++ )); do
  PREV="${HMM_DIR}/hmm${i}"
  NEXT="${HMM_DIR}/hmm$((i+1))"
  
  echo "=== ITERATION $i: ${PREV} → ${NEXT} ==="
  
  mkdir -p "${NEXT}"
  
  HERest \
    -C "${CONFIG}" \
    -I "${MLF}" \
    -S "${SCP}" \
    -H "${PREV}/newMacros" \
    -M "${NEXT}" \
    -T 1 -A -D list
  
  echo
done

echo "All ${NUM_ITERS} iterations complete."
