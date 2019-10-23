#!/usr/bin/sh
ffmpeg -re \
  -f video4linux2 \
  -i /dev/video0 \
  -vcodec libx264 \
  -vprofile baseline \
  -preset veryfast \
  -acodec aac \
  -strict -2 \
  -f flv \
  -pix_fmt yuv420p \
  -bufsize 6000k \
  rtmp://localhost/show/stream
