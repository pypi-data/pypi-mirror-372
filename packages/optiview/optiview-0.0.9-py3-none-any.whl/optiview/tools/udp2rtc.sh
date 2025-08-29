#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <video_file.mp4> [num_streams (1–16)] [start_port (default: 9000)]"
  exit 1
fi

VIDEO_FILE="$1"
NUM_STREAMS="${2:-16}"
START_PORT="${3:-9000}"

if ! [[ "$NUM_STREAMS" =~ ^[0-9]+$ ]] || [ "$NUM_STREAMS" -lt 1 ] || [ "$NUM_STREAMS" -gt 16 ]; then
  echo "❌ Invalid number of streams: $NUM_STREAMS. Must be between 1 and 16."
  exit 1
fi

if ! [[ "$START_PORT" =~ ^[0-9]+$ ]] || [ "$START_PORT" -lt 1024 ] || [ "$START_PORT" -gt 65535 ]; then
  echo "❌ Invalid start port: $START_PORT. Must be between 1024 and 65535."
  exit 1
fi

# Trap Ctrl+C to exit the loop
stop_streaming=0
trap 'stop_streaming=1' SIGINT

while [ $stop_streaming -eq 0 ]; do
  echo "🔁 Restarting stream of $VIDEO_FILE to $NUM_STREAMS UDP sink(s) starting at port $START_PORT..."

  PIPELINE="gst-launch-1.0 -q \
    filesrc location=\"$VIDEO_FILE\" ! \
    qtdemux name=demux \
    demux.video_0 ! \
    h264parse ! rtph264pay config-interval=1 pt=96 ! tee name=t"

  for ((i=0; i<NUM_STREAMS; i++)); do
    PORT=$((START_PORT + i))
    PIPELINE+=" t. ! queue ! udpsink host=127.0.0.1 port=$PORT"
  done

  eval "$PIPELINE"
  sleep 1
done

echo "🛑 Streaming stopped."
