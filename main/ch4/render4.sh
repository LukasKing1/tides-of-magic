#!/bin/bash
# Testszene Kapitel 4 rendern: 6 Stücke, je 2 parallel, dann zusammenfügen und Ton anlegen
cd /home/claude/main/ch4
mkdir -p chunks
N=$(python3 -c "import math;print(int(round(58.6*30)))")
STEP=300
i=0; pids=()
for ((s=0; s<N; s+=STEP)); do
  e=$((s+STEP)); [ $e -gt $N ] && e=$N
  f=chunks/c_$(printf %04d $s).mp4
  python3 scene4.py range $s $e $f > chunks/log_$s.txt 2>&1 &
  pids+=($!)
  i=$((i+1))
  if [ $((i%2)) -eq 0 ]; then wait ${pids[@]}; pids=(); fi
done
wait
ls chunks/c_*.mp4 | sed "s/^/file '/;s/$/'/" | sed "s#file 'chunks/#file '#" > chunks/list.txt
(cd chunks && ffmpeg -y -v error -f concat -safe 0 -i list.txt -c copy ../video4.mp4)
ffmpeg -y -v error -i video4.mp4 -i mix4.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 6000k -maxrate 8000k -bufsize 12000k -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart Kapitel4_Testszene_v1.mp4
echo RENDER_DONE
