#!/bin/bash
# render chunks of 300 frames, 2 at a time
cd /home/claude/main/ch1
N=2730
STEP=300
i=0
jobs_run=0
for ((s=0; s<N; s+=STEP)); do
  e=$((s+STEP)); if [ $e -gt $N ]; then e=$N; fi
  name=$(printf "chunks/c%02d.mp4" $((s/STEP)))
  python3 ch1.py range $s $e $name > /dev/null 2>&1 &
  jobs_run=$((jobs_run+1))
  if [ $jobs_run -ge 2 ]; then wait -n; jobs_run=$((jobs_run-1)); fi
done
wait
ls chunks/*.mp4 | sort | sed "s/^chunks\///" | awk '{print "file \x27"$0"\x27"}' > chunks/list.txt
cd chunks && ffmpeg -y -v error -f concat -safe 0 -i list.txt -c copy ../video_only.mp4
echo ALLDONE
