# Copyright (c) 2025 SiMa.ai
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import threading
import gi
import os
import psutil

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

BASE_PORT = 7001
pipeline_registry = {}

def boost_thread_priority():
    try:
        p = psutil.Process(os.getpid())
        p.nice(-10)
        logging.info("Thread priority boosted")
    except Exception as e:
        logging.warning(f"Failed to boost priority: {e}")

class MediaStream:
    def __init__(self, index, file_path):
        self.index = index
        self.file_path = file_path
        self.port = BASE_PORT + int(index)
        self.pipeline = None
        self.loop = None
        self.thread = None
        self._stopping = False

    def build_pipeline(self):
        # pipeline_str = f"""
        #                 filesrc location={self.file_path} !
        #                 qtdemux name=demux
        #                 demux.video_0 !
        #                 h264parse config-interval=1 !
        #                 video/x-h264, stream-format=byte-stream, alignment=au !
        #                 rtph264pay config-interval=1 pt=96 !
        #                 udpsink host=127.0.0.1 port={self.port} sync=false async=false
        #                 """
        pipeline_str = f"""
            filesrc location={self.file_path} !
            qtdemux name=demux
            demux.video_0 ! h264parse config-interval=1 !
            mpegtsmux !
            udpsink host=127.0.0.1 port={self.port}
        """

        pipeline = Gst.parse_launch(pipeline_str.strip())
        if not pipeline:
            raise RuntimeError("Failed to parse GStreamer pipeline")
        return pipeline

    def _bus_watch(self, bus, msg):
        t = msg.type
        if t == Gst.MessageType.EOS:
            if self._stopping:
                logging.info(f"EOS on stream {self.index}, stopping loop")
                self.loop.quit()
            else:
                logging.info(f"EOS on stream {self.index}, seeking to start")
                if not self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0):
                    logging.error(f"Failed to seek to beginning for stream {self.index}")
        elif t == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            logging.error(f"Error on stream {self.index}: {err}, {debug}")
            self.loop.quit()
        return True
    
    def _start_thread(self):
        boost_thread_priority()
        self.loop = GLib.MainLoop()
        try:
            self.pipeline = self.build_pipeline()
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._bus_watch)

            self.pipeline.set_state(Gst.State.PLAYING)
            logging.info(f"Media stream {self.index} started on port {self.port}")

            self.loop.run()
        except Exception as e:
            logging.exception(f"Failed to start media stream {self.index}: {e}")
        finally:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline.get_state(Gst.CLOCK_TIME_NONE)
                self.pipeline = None
                logging.info(f"Media stream {self.index} stopped")

    def start(self):
        if self.thread and self.thread.is_alive():
            logging.warning(f"Stream {self.index} is already running")
            return False, "Already running"
        self.thread = threading.Thread(target=self._start_thread, daemon=True)
        self.thread.start()
        pipeline_registry[self.index] = self
        return True, None

    def stop(self):
        self._stopping = True
        if self.pipeline:
            logging.info(f"Sending EOS to pipeline for stream {self.index}")
            self.pipeline.send_event(Gst.Event.new_eos())
        else:
            logging.warning(f"No pipeline to send EOS for stream {self.index}")

        if self.thread:
            self.thread.join(timeout=5)
            logging.info(f"Thread for stream {self.index} joined")

        pipeline_registry.pop(self.index, None)

def start_media_stream(index, file_path):
    if not file_path:
        return False, 'No file assigned'

    index -= 1
    stream = pipeline_registry.get(index)
    if stream:
        logging.info(f"Stream {index} already exists, reusing")
        return stream.start()

    try:
        stream = MediaStream(index, file_path)
        return stream.start()
    except Exception as e:
        logging.exception(f"Exception starting media stream {index}")
        return False, str(e)

def stop_media_stream(index):
    index -= 1
    stream = pipeline_registry.get(index)
    if stream:
        logging.info(f"Stopping stream {index}")
        stream.stop()
    else:
        logging.warning(f"No active stream for index {index}")
