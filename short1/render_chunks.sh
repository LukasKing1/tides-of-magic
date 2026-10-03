#!/bin/bash
# usage: ./render_chunks.sh k1 k2 ...   (chunk k = frames [90k, 90k+90), two workers in parallel)
cd /home/claude/short1
mkdir -p chunks
run() {
  for k in "$@"; do
    i0=$((k*90)); i1=$(( (k+1)*90 )); [ $i1 -gt 1590 ] && i1=1590
    python3 short1.py range $i0 $i1 chunks/c$(printf %02d $k).mp4 > chunks/log$k.txt 2>&1
  done
}
args=("$@"); A=(); B=()
for i in "${!args[@]}"; do if (( i % 2 == 0 )); then A+=("${args[$i]}"); else B+=("${args[$i]}"); fi; done
run "${A[@]}" & run "${B[@]}" & wait
echo all-done
