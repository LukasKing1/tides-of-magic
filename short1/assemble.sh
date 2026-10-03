#!/bin/bash
# concat all chunks + mix.wav -> Short1.mp4 (full quality) and a preview under 30 MB
cd /home/claude/short1
(cd chunks && ls c*.mp4 | sort | sed "s/^/file '/; s/$/'/") > chunks/list.txt
ffmpeg -y -v error -f concat -safe 0 -i chunks/list.txt -c copy video_only.mp4
ffmpeg -y -v error -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest Short1.mp4
ffmpeg -y -v error -i Short1.mp4 -c:v libx264 -preset slow -b:v 3800k -maxrate 4500k -bufsize 9000k -pix_fmt yuv420p -c:a aac -b:a 192k Short1_preview.mp4
ls -la Short1.mp4 Short1_preview.mp4
