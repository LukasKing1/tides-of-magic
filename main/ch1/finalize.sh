#!/bin/bash
cd /home/claude/main/ch1
ffmpeg -y -v error -i video_only.mp4 -i mix.wav -c:v copy -c:a aac -b:a 256k -shortest Ch1_master_1080.mp4
# preview under 30 MB: two-pass x264 at ~2.3 Mbps
ffmpeg -y -v error -i video_only.mp4 -c:v libx264 -preset slow -b:v 2300k -pass 1 -an -f null /dev/null
ffmpeg -y -v error -i video_only.mp4 -i mix.wav -c:v libx264 -preset slow -b:v 2300k -pass 2 -c:a aac -b:a 160k -movflags +faststart -shortest Kapitel1_Vorschau_v1.mp4
ls -la Ch1_master_1080.mp4 Kapitel1_Vorschau_v1.mp4
