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

import os
import logging
import psutil
import re
import argparse
import shutil
import tempfile
import json
import signal
import platform
import subprocess
import zipfile, tarfile
import paramiko
import fnmatch
import socket
from pathlib import Path
from flask import Flask, request, Response, render_template, jsonify, abort, stream_with_context, send_from_directory, send_file
from datetime import datetime
from werkzeug.utils import secure_filename
from pymediainfo import MediaInfo
from PIL import Image
from optiview.app_manager import AppManager
from optiview.mediasrc import start_media_stream, stop_media_stream
from optiview.process_manager import ProcessManager
from optiview.utils import tail_lines, init_environment, is_sima_board, start_processes, cleanup_processes, board_type, check_and_generate_self_signed_cert, parse_build_info
from optiview.utils import EXCLUDED_EXTENSIONS, EXCLUDED_FOLDERS, get_lan_ip, extract_pipeline_dir
from optiview.watcher import start_app_watcher
from optiview.gst_graph import generate_dot_from_pipeline
from optiview.remotefs import read_remote_file, write_remote_file, build_remote_tree
from optiview.remote_devkit import is_remote_devkit_connected, get_remote_metrics, is_remote_devkit_configured, get_remote_devkit_ip
from optiview.remote_devkit import handle_remote_mpk_upload, run_remote_gst_pipeline, stop_remote_process, run_remote_gst_inspect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

env = init_environment()
MEDIA_DIR = env["MEDIA_DIR"]
MEDIA_SRC_DATA_FILE = env["MEDIA_SRC_DATA_FILE"]
UPLOAD_ROOT = env["UPLOAD_ROOT"]
DEFAULT_SOURCE_COUNT = env["DEFAULT_SOURCE_COUNT"]
MPK_APPS_ROOT = env["MPK_SRC_PATH"]
CFG_PATH = env["OPTVIEW_DATA"] / "cfg.json" 

app = Flask(__name__)
app_manager = AppManager(MPK_APPS_ROOT)
process_manager = ProcessManager()
start_app_watcher(app_manager, MPK_APPS_ROOT)
process_manager.start()
current_started_app_name = None

LOG_DIR = "/var/log"
ALLOWED_LOGS = {
    "EV74": "simaai_EV74.log",
    "syslog": "syslog"
}

DEFAULT_SOURCE_COUNT = 8

logging.info(env)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

@app.route("/apps", methods=["GET"])
def list_apps():
    app_manager.refresh_apps()
    return {"apps": app_manager.get_available_apps()}

@app.route("/start/<app_name>", methods=["POST"])
def start_app(app_name):
    manifest = app_manager.get_app_config(app_name)
    if not manifest:
        return {"error": f"App '{app_name}' not found or invalid"}, 404

    try:
        # 1. Parse debug level from request
        debug_level = None
        if request.is_json:
            debug_level = request.json.get("gst_debug")
        else:
            debug_level = request.args.get("gst_debug")

        # Default fallback
        debug_level = str(debug_level) if debug_level is not None else "0"
        if debug_level not in {"0", "1", "2", "3", "4", "5"}:
            return {"error": f"Invalid gst_debug level: {debug_level}"}, 400

        # 2. Extract application block
        applications = manifest.get("applications", [])
        app_block = next((a for a in applications if a.get("name") == app_name), None)
        if not app_block:
            return {"error": f"No application block with name '{app_name}' in manifest."}, 400

        config = app_block.get("configuration", {})
        pipelines = app_block.get("pipelines", [])
        if not pipelines:
            return {"error": "No pipelines defined in manifest."}, 400

        pipeline_def = pipelines[0]
        gst_command = pipeline_def.get("gst", "").strip()
        if not gst_command:
            return {"error": "No 'gst' command defined in pipeline."}, 400

        # 3. Build environment
        env_vars = {}
        for line in config.get("environment", []):
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

        for opt in config.get("gst", {}).get("options", []):
            if "--gst-plugin-path" in opt:
                path = opt.split("=")[-1].strip("'\"")
                env_vars["GST_PLUGIN_PATH"] = path

        # Add debug level
        env_vars["GST_DEBUG"] = debug_level

        if is_remote_devkit_configured():
            success, error = run_remote_gst_pipeline(app_name, gst_command, env_vars)
            if not success:
                return {"error": error}, 500
        else:
            full_env = os.environ.copy()
            full_env.update(env_vars)

            logging.info(f"🛠 GST_DEBUG={debug_level} set for app '{app_name}'")
            process_manager.submit_command(gst_command, full_env)

        global current_started_app_name
        current_started_app_name = app_name
        return {"status": "started", "app": app_name, "gst_debug": debug_level}

    except Exception as e:
        logging.exception(f"Failed to start app {app_name}")
        return {"error": str(e)}, 500

@app.route("/stop", methods=["POST"])
def stop_pipeline():
    if is_remote_devkit_configured():
        if is_remote_devkit_connected():
            if not current_started_app_name:
                return {"error": "Missing appName for remote stop"}, 400

            result = stop_remote_process(current_started_app_name)
            if "error" in result:
                return {"error": result["error"]}, 500
            return {"status": "remote stopped", "pids": result.get("stopped_pids", [])}
        else:
            return {"error": "Remote devkit not connected"}, 503

    # Fallback: local stop
    try:
        process_manager.submit_command('STOP', None)
        return {"status": "local stopped"}
    except Exception as e:
        logging.exception("Failed to stop local pipeline")
        return {"error": str(e)}, 500

@app.route("/gstlogs", methods=["GET"])
def stream_gstlogs():
    app_name = request.args.get("folder", "")
    log_path = f"/tmp/{app_name}.log"

    if is_remote_devkit_configured():
        if is_remote_devkit_connected():
            try:
                content = read_remote_file(log_path)
                return Response(content, mimetype="text/plain")
            except Exception as e:
                return Response(f"[ERROR] Failed to read remote log: {str(e)}\n", mimetype="text/plain")

        return Response("[ERROR] Remote device not connected, unable to read gst log\n", mimetype="text/plain")

    # fallback to local logs (still streamed)
    @stream_with_context
    def generate_local():
        for line in process_manager.stream_logs():
            yield line

    return Response(generate_local(), mimetype="text/plain")

# @app.route("/analyze-pipeline", methods=["POST"])
# def analyze_pipeline():
#     try:
#         if not request.is_json:
#             return {"error": "Expected JSON body with 'pipeline'"}, 400

#         pipeline_str = request.json.get("pipeline")
#         if not pipeline_str:
#             return {"error": "Missing 'pipeline' string in request"}, 400

#         dot_path = generate_dot_from_pipeline(
#             gst_string=pipeline_str,
#             output_path='/tmp',
#             output_name="analyzed"
#         )

#         return send_file(
#             dot_path,
#             mimetype="text/vnd.graphviz",
#             as_attachment=True,
#             download_name="pipeline.dot"
#         )

#     except Exception as e:
#         logging.exception("Failed to analyze GStreamer pipeline")
#         return jsonify({"error": str(e)}), 500

@app.route("/analyze-pipeline", methods=["POST"])
def analyze_pipeline():
    try:
        if not request.is_json:
            return {"error": "Expected JSON body with 'pipeline' and 'file'"}, 400

        pipeline_str = request.json.get("pipeline")
        app_name = request.json.get("file")

        if not pipeline_str or not app_name:
            return {"error": "Missing 'pipeline' or 'file' in request"}, 400

        manifest = app_manager.get_app_config(app_name)
        if not manifest:
            return {"error": f"App '{app_name}' not found"}, 404

        app_block = next((a for a in manifest.get("applications", []) if a.get("name") == app_name), None)
        config = app_block.get("configuration", {})

        # Extract relevant env vars
        env_vars = {}
        for line in config.get("environment", []):
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

        for opt in config.get("gst", {}).get("options", []):
            if "--gst-plugin-path" in opt:
                env_vars["GST_PLUGIN_PATH"] = opt.split("=")[-1].strip("'\"")
            if "LD_LIBRARY_PATH" in opt:
                env_vars["LD_LIBRARY_PATH"] = opt.split("=")[-1].strip("'\"")


        dot_path = generate_dot_from_pipeline(
            gst_string=pipeline_str,
            output_path='/tmp',
            output_name="analyzed",
            env_vars=env_vars
        )

        return send_file(dot_path, mimetype="text/vnd.graphviz", as_attachment=True, download_name="pipeline.dot")

    except Exception as e:
        logging.exception("Failed to analyze GStreamer pipeline")
        return jsonify({"error": str(e)}), 500

MAX_LOG_LINES = 10000
MAX_READ_SIZE = 256 * 1024

@app.route('/logs/<logname>', methods=["GET"])
def get_log(logname):
    if logname not in ALLOWED_LOGS:
        abort(404, description="Log not found")

    log_file = ALLOWED_LOGS[logname]

    # Strictly handle remote mode
    if is_remote_devkit_configured():
        if not is_remote_devkit_connected():
            return jsonify({"error": "Remote devkit is configured but not connected."}), 503

        remote_path = f"/{LOG_DIR}/{log_file}"
        try:
            content = read_remote_file(remote_path)
            return Response(content, mimetype='text/plain')
        except FileNotFoundError:
            return jsonify({"error": f"{logname} log not found on remote device."}), 404
        except Exception as e:
            return jsonify({"error": f"Remote read failed: {str(e)}"}), 500

    # Local fallback only if remote is NOT configured
    log_path = os.path.join(LOG_DIR, log_file)
    if not os.path.isfile(log_path):
        return jsonify({"error": f"{logname} log not found."}), 404

    try:
        file_size = os.path.getsize(log_path)
        if file_size > MAX_READ_SIZE:
            content = tail_lines(log_path, MAX_LOG_LINES, MAX_READ_SIZE)
        else:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        return Response(content, mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metrics", methods=["GET"])
def get_system_metrics():
    try:
        global current_started_app_name
        if is_remote_devkit_configured():
            if is_remote_devkit_connected():
                return get_remote_metrics(current_started_app_name)
            else:
                return {
                    "cpu_load": '',
                    "memory": {},
                    "mla_allocated_bytes": 0,
                    "disk": {},
                    "pipeline_status": {},
                    "temperature_celsius_avg": 0
                }
        
        # CPU load (1-minute average)
        cpu_percent_total = psutil.cpu_percent(interval=0.1)

        # Memory info
        mem = psutil.virtual_memory()
        memory_usage = {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent
        }

        # MLA memory usage from /dev/simaa-mem
        mla_mem_path = "/dev/simaai-mem" if is_sima_board() else "/tmp/simaai-mem"
        mla_allocated_bytes = None
        try:
            with open(mla_mem_path, "r") as f:
                contents = f.read()
                match = re.search(r"Total allocated size: (0x[0-9a-fA-F]+)", contents)
                if match:
                    mla_allocated_bytes = int(match.group(1), 16)
        except Exception as mla_err:
            logging.warning(f"Could not read MLA memory info: {mla_err}")

        # Disk usage
        try:
            target_path = Path("/data") if is_sima_board() else Path.home()
            disk = psutil.disk_usage(str(target_path))
            disk_usage = {
                "mount": str(target_path),
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        except Exception as disk_err:
            logging.warning(f"Could not read disk usage at {target_path}: {disk_err}")
            disk_usage = None

        # Temperature reading (SIMA board only)
        avg_temp = None
        if is_sima_board() and board_type() == 'davinci':
            try:
                with open("/sys/kernel/temperature_profile", "r") as f:
                    temps = []
                    for line in f:
                        match = re.search(r"Temperature.*is (\d+) C", line)
                        if match:
                            temps.append(int(match.group(1)))
                    if temps:
                        avg_temp = sum(temps) / len(temps)
            except Exception as temp_err:
                logging.warning(f"Could not read temperature: {temp_err}")

        # Get pipeline process status
        process_status = process_manager.get_status()

        return {
            "cpu_load": cpu_percent_total,
            "memory": memory_usage,
            "mla_allocated_bytes": mla_allocated_bytes,
            "disk": disk_usage,
            "pipeline_status": process_status,
            "temperature_celsius_avg": avg_temp
        }

    except Exception as e:
        logging.exception("Failed to retrieve system metrics")
        return {"error": str(e)}, 500

@app.route("/manifest/<app_name>", methods=["GET"])
def get_manifest(app_name):
    manifest_path = Path(f"{MPK_APPS_ROOT}{app_name}/manifest.json")
    if not manifest_path.exists():
        return {"error": f"Manifest not found for app '{app_name}'"}, 404
    try:
        with open(manifest_path, "r") as f:
            data = f.read()
        return jsonify({"app": app_name, "manifest": data})
    except Exception as e:
        logging.exception("Error reading manifest")
        return {"error": str(e)}, 500

@app.route("/manifest/<app_name>", methods=["POST"])
def save_manifest(app_name):
    manifest_path = Path(f"{MPK_APPS_ROOT}{app_name}/manifest.json")
    try:
        manifest_text = request.get_data(as_text=True)
        with open(manifest_path, "w") as f:
            f.write(manifest_text)
        return {"status": "saved", "app": app_name}
    except Exception as e:
        logging.exception("Error saving manifest")
        return {"error": str(e)}, 500

@app.route("/config/<app_name>", methods=["GET"])
def list_config_files(app_name):
    config_dir = Path(f"{MPK_APPS_ROOT}{app_name}/etc")
    if not config_dir.exists() or not config_dir.is_dir():
        return {"error": "Configuration directory not found"}, 404

    files = [f.name for f in config_dir.iterdir() if f.is_file()]
    return jsonify(files)

@app.route("/config/<app_name>/<path:filename>", methods=["GET"])
def get_config_file(app_name, filename):
    config_file = Path(f"{MPK_APPS_ROOT}{app_name}/etc") / filename
    if not config_file.exists() or not config_file.is_file():
        return {"error": f"File {filename} not found"}, 404

    try:
        text = config_file.read_text()
        try:
            content = json.loads(text)
            return jsonify({
                "file": filename,
                "content": content
            })
        except json.JSONDecodeError:
            # Not JSON, return raw text
            return jsonify({
                "file": filename,
                "content": text
            })
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}, 500


@app.route("/config/<app_name>/<path:filename>", methods=["POST"])
def save_config_file(app_name, filename):
    config_file = Path(f"{MPK_APPS_ROOT}{app_name}/etc") / filename
    try:
        content = request.get_data(as_text=True)
        config_file.write_text(content)
        return {"status": "saved", "file": str(config_file)}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}, 500

@app.route('/envinfo', methods=['GET'])
def get_env_info():
    return jsonify({
        'is_sima_board': is_sima_board(),
        'is_remote_devkit_configured': is_remote_devkit_configured()
    })

@app.route('/buildinfo', methods=['GET'])
def get_build_info():
    build_paths = ['/etc/build', '/etc/buildinfo']

    if is_sima_board():
        for path in build_paths:
            try:
                with open(path, 'r') as f:
                    build_text = f.read()
                return jsonify(parse_build_info(build_text))
            except Exception:
                continue  # Try next path
        return jsonify({'error': 'Failed to read local build file'}), 500

    elif is_remote_devkit_configured():
        if is_remote_devkit_connected():
            for path in build_paths:
                try:
                    build_text = read_remote_file(path)
                    build_text = build_text.decode("utf-8", errors="replace")
                    return jsonify(parse_build_info(build_text, remote=True))
                except Exception:
                    continue  # Try next path
            return jsonify({'error': 'Failed to read remote build file'}), 502
        else:
            return jsonify({'error': 'Remote device unreachable'}), 502

    else:
        return jsonify({
            'MACHINE': platform.machine(),
            'SIMA_BUILD_VERSION': platform.platform()
        })

        
def build_tree(path):
    tree = {
        "name": os.path.basename(path),
        "path": str(path),
        "type": "directory",
        "children": []
    }

    try:
        for entry in sorted(os.listdir(path)):
            if entry in EXCLUDED_FOLDERS:
                continue

            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                child_tree = build_tree(full_path)
                if child_tree["children"]:  # Include only non-empty dirs
                    tree["children"].append(child_tree)
            else:
                ext = os.path.splitext(entry)[1].lower()
                if ext not in EXCLUDED_EXTENSIONS:
                    tree["children"].append({
                        "name": entry,
                        "path": str(full_path),
                        "type": "file"
                    })
    except Exception as e:
        tree["error"] = str(e)

    return tree


@app.route("/appsrc", methods=["GET"])
def get_app_structure():
    try:
        if is_remote_devkit_configured():
            if is_remote_devkit_connected():
                return jsonify(build_remote_tree())
            
            return jsonify({"error": "Remote DevKit not connected"}), 502

        if not os.path.exists(MPK_APPS_ROOT):
            return jsonify({"error": "Directory not found"}), 404

        return jsonify(build_tree(MPK_APPS_ROOT))

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve app structure: {str(e)}"}), 500


@app.route("/readfile")
def read_file():
    raw_path = request.args.get("path")
    if not raw_path:
        return abort(400, "Missing 'path' parameter")

    try:
        if is_remote_devkit_configured():
            if is_remote_devkit_connected():
                return read_remote_file(raw_path)
            else:
                return abort(502, "Remote DevKit not connected")

        # Local path access
        real_path = Path(raw_path).resolve()
        if not str(real_path).startswith(str(MPK_APPS_ROOT.resolve())):
            return abort(403)

        with open(real_path, 'r') as f:
            return f.read()

    except Exception as e:
        return str(e), 500
    
@app.route("/writefile", methods=["POST"])
def write_file():
    data = request.get_json()
    path = data.get("path")
    content = data.get("content")

    if not path or content is None:
        return jsonify({"error": "Missing path or content"}), 400

    # Ensure path is within allowed base directory
    abs_path = os.path.abspath(path)
    if is_remote_devkit_configured():
        result = write_remote_file(path, content)
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)
    
    if not abs_path.startswith(os.path.abspath(MPK_APPS_ROOT)):
        return jsonify({"error": "Unauthorized path"}), 403

    # If saving a JSON file, validate JSON content first
    if path.lower().endswith('.json'):
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload/mpk', methods=['POST'])
def upload_mpk():
    def generate():
        yield "Validating uploaded file...\n"

        uploaded_file = request.files.get('file')
        if not uploaded_file or not uploaded_file.filename.endswith('.mpk'):
            yield "❌ Invalid or missing .mpk file.\n"
            return

        # Ensure UPLOAD_ROOT exists
        try:
            os.makedirs(UPLOAD_ROOT, exist_ok=True)
        except Exception as e:
            yield f"❌ Failed to create upload root: {str(e)}\n"
            return

        try:
            temp_dir = tempfile.mkdtemp(dir=UPLOAD_ROOT)
        except Exception as e:
            yield f"❌ Failed to create temp directory: {str(e)}\n"
            return

        mpk_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(mpk_path)
        yield "✓ File saved.\n"

        # Check if we're targeting a remote devkit
        if is_remote_devkit_configured():
            yield "📡 Remote devkit detected. transferring file to the devkit...\n"
            try:
                for line in handle_remote_mpk_upload(mpk_path, '/data/simaai/applications'):
                    yield line
            except Exception as e:
                yield f"❌ Remote upload failed: {str(e)}\n"
            return

        try:
            with zipfile.ZipFile(mpk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            yield "✓ Package extracted.\n"
        except zipfile.BadZipFile:
            yield "❌ Failed to unzip .mpk file.\n"
            return

        def find_file(root, pattern):
            for dirpath, _, files in os.walk(root):
                for name in files:
                    if fnmatch.fnmatch(name, pattern):
                        return os.path.join(dirpath, name)
            return None
        
        # Locate manifest and RPM
        manifest_path = find_file(temp_dir, 'manifest.json')
        rpm_path = find_file(temp_dir, '*.rpm')
        if not manifest_path or not rpm_path:
            yield "❌ Missing manifest.json or installer.rpm.\n"
            return

        yield "Running rpm query...\n"

        try:
            result = subprocess.run(['rpm', '-qpl', rpm_path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=True)

            rpm_files = result.stdout.decode().splitlines()
            pipeline_dir = extract_pipeline_dir(rpm_files, MPK_APPS_ROOT)
            if not pipeline_dir:
                yield "❌ Could not identify install path from RPM.\n"
                return

            print(f"✅ Identified pipeline install dir: {pipeline_dir}")
        except subprocess.CalledProcessError as e:
            yield f"❌ rpm -qpl failed: {e.stderr.decode()}\n"
            return

        try:
            os.makedirs(pipeline_dir, exist_ok=True)
            shutil.copy2(manifest_path, os.path.join(pipeline_dir, 'manifest.json'))
            yield "✓ manifest.json copied.\n"
        except Exception as e:
            yield f"❌ Copy failed: {str(e)}\n"
            return
        
        yield f"✅ Installing to: {pipeline_dir}\n"
        try:
            subprocess.run(['rpm', '-U', '--replacepkgs', rpm_path],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            yield "✓ RPM installed.\n"
        except subprocess.CalledProcessError as e:
            yield f"❌ RPM installation failed: {e.stderr.decode()}\n"
            return

        yield "🎉 Upload completed!\n"

    return Response(stream_with_context(generate()), mimetype='text/plain')


@app.route('/api/media-files', methods=['GET'])
def list_media_files():
    def build_tree(base_path, rel_path=""):
        result = []
        full_path = os.path.join(base_path, rel_path)
        try:
            entries = os.listdir(full_path)

            # Filter out hidden files and macOS metadata
            entries = [
                entry for entry in entries
                if not entry.startswith('.') and not entry.startswith('__MACOSX')
            ]

            # Sort folders first, then files
            entries.sort(key=lambda e: (not os.path.isdir(os.path.join(full_path, e)), e.lower()))

            for entry in entries:
                abs_entry_path = os.path.join(full_path, entry)
                rel_entry_path = os.path.join(rel_path, entry)
                if os.path.isdir(abs_entry_path):
                    result.append({
                        'name': '/' + entry,
                        'path': rel_entry_path,
                        'type': 'folder',
                        'children': build_tree(base_path, rel_entry_path)
                    })
                else:
                    result.append({
                        'name': entry,
                        'path': rel_entry_path,
                        'type': 'file'
                    })
        except Exception as e:
            logging.exception(f"Error reading directory {full_path}: {e}")
        return result

    if not os.path.exists(MEDIA_DIR):
        return jsonify([])

    tree = build_tree(MEDIA_DIR)
    return jsonify(tree)

@app.route('/system/tools')
def check_system_tools():
    tools = {
        'ffmpeg': shutil.which('ffmpeg') is not None,
        'gstreamer': shutil.which('gst-launch-1.0') is not None
    }
    return jsonify(tools)

@app.route('/upload/media', methods=['POST'])
def upload_media():
    def generate():
        yield "Processing the uploaded media file...\n"

        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            yield "❌ No file provided.\n"
            return

        filename = secure_filename(uploaded_file.filename)
        file_ext = filename.lower().rsplit('.', 1)[-1]
        original_path = os.path.join(MEDIA_DIR, filename)

        final_warning = ""  # <-- store final reminder here

        if file_ext in ['zip', 'tar', 'gz', 'tar.gz']:
            base_name = os.path.splitext(os.path.splitext(filename)[0])[0]  # handle .tar.gz
            target_dir = os.path.join(MEDIA_DIR, base_name)
            os.makedirs(target_dir, exist_ok=True)
            temp_path = os.path.join(target_dir, filename)
            uploaded_file.save(temp_path)
            yield f"✓ Saved archive to {temp_path}\n"

            try:
                if filename.endswith('.zip'):
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    yield "✓ ZIP extracted.\n"
                elif filename.endswith('.tar.gz') or filename.endswith('.tar'):
                    with tarfile.open(temp_path, 'r:*') as tar:
                        tar.extractall(path=target_dir)
                    yield "✓ TAR extracted.\n"
                else:
                    yield "❌ Unsupported archive format.\n"
                    return
            except Exception as e:
                yield f"❌ Failed to extract: {str(e)}\n"
                return
            finally:
                os.remove(temp_path)
                yield "✓ Temporary file cleaned up.\n"

        else:
            uploaded_file.save(original_path)
            yield f"✓ File uploaded to {original_path}\n"

            if file_ext == 'mp4':
                # Check if ffmpeg is available
                ffmpeg_check = shutil.which('ffmpeg')
                if not ffmpeg_check:
                    final_warning = (
                        "⚠️ FFMPEG is not installed. "
                        "Video may look jittery during playback. "
                        "Install FFMPEG and re-upload, or process the video offline.\n"
                    )
                else:
                    converted_path = os.path.join(MEDIA_DIR, f"converted_{filename}")
                    cmd = [
                        "ffmpeg", "-y", "-i", original_path,
                        "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
                        "-x264-params", "keyint=30:min-keyint=30:no-scenecut=1",
                        "-b:v", "2M", "-r", "30", "-g", "30", "-bf", "0",
                        "-an", converted_path
                    ]
                    yield "🛠️ Optimizing video, please wait...\n"
                    try:
                        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        os.remove(original_path)
                        os.rename(converted_path, original_path)
                        yield f"✓ Video converted and saved to {original_path}\n"
                    except subprocess.CalledProcessError as e:
                        yield f"❌ FFMPEG conversion failed: {e.stderr.decode(errors='ignore')}\n"

        yield "🎉 Upload completed!\n" + final_warning

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route('/api/delete-media', methods=['POST'])
def delete_media():
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({"error": "Missing 'path' in request"}), 400

    requested_path = data['path']
    full_path = os.path.abspath(os.path.join(MEDIA_DIR, requested_path))

    # Ensure safety: full_path must stay within MEDIA_DIR
    if not full_path.startswith(os.path.abspath(MEDIA_DIR)):
        return jsonify({"error": "Invalid file path"}), 403

    if not os.path.exists(full_path):
        return jsonify({"error": "File or directory not found"}), 404

    try:
        # If deleting a file, clean up any source referencing it
        if os.path.isfile(full_path):
            file_name = os.path.relpath(full_path, MEDIA_DIR)

            # Unassign any source using this file
            sources = load_sources()
            modified = False
            for src in sources:
                if src.get('file') == file_name:
                    src['file'] = ''
                    src['state'] = 'stopped'
                    logging.info(f"Auto-cleared media source index {src['index']} due to deletion of '{file_name}'")
                    modified = True

            if modified:
                save_sources(sources)

            os.remove(full_path)

        else:
            # Optional: recursively check for any assigned file in this folder and clear them
            deleted_folder = os.path.relpath(full_path, MEDIA_DIR)
            sources = load_sources()
            modified = False
            for src in sources:
                assigned_file = src.get('file', '')
                if assigned_file.startswith(deleted_folder + os.sep):
                    src['file'] = ''
                    src['state'] = 'stopped'
                    logging.info(f"Auto-cleared source {src['index']} due to folder deletion '{deleted_folder}'")
                    modified = True

            if modified:
                save_sources(sources)

            shutil.rmtree(full_path)

        return jsonify({"message": "Deleted successfully"}), 200

    except Exception as e:
        logging.exception("Failed to delete media and clean up sources")
        return jsonify({"error": str(e)}), 500

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_DIR, filename)

@app.route('/api/media-info', methods=['POST'])
def media_info():
    data = request.get_json()
    rel_path = data.get("path")

    if not rel_path:
        return jsonify({"error": "Missing path"}), 400

    # Ensure the path is within MEDIA_DIR
    abs_path = os.path.abspath(os.path.join(MEDIA_DIR, rel_path))
    if not abs_path.startswith(os.path.abspath(MEDIA_DIR)) or not os.path.isfile(abs_path):
        return jsonify({"error": "Invalid path"}), 400

    info = {
        "filename": os.path.basename(abs_path),
        "size_bytes": os.path.getsize(abs_path)
    }

    try:
        if abs_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            with Image.open(abs_path) as img:
                info["type"] = "image"
                info["width"], info["height"] = img.size
                info["mode"] = img.mode
                info["format"] = img.format
        else:
            media_info = MediaInfo.parse(abs_path)
            video_track = next((t for t in media_info.tracks if t.track_type == "Video"), None)
            if video_track:
                info.update({
                    "type": "video",
                    "codec": video_track.codec_id or video_track.format,
                    "width": video_track.width,
                    "height": video_track.height,
                    "duration_ms": video_track.duration,
                    "frame_rate": video_track.frame_rate
                })
            else:
                info["type"] = "unknown"
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(info)

def load_sources():
    try:
        if not os.path.exists(MEDIA_SRC_DATA_FILE):
            logging.warning(f"{MEDIA_SRC_DATA_FILE} does not exist. Returning empty list and reset.")
            reset_sources()
            return []
        with open(MEDIA_SRC_DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load sources: {e}")
        return []

def save_sources(sources):
    try:
        with open(MEDIA_SRC_DATA_FILE, 'w') as f:
            json.dump(sources, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save sources: {e}")

def reset_sources():
    """Ensure media_sources.json exists and all sources are in stopped state."""
    sources = []
    if os.path.exists(MEDIA_SRC_DATA_FILE):
        try:
            with open(MEDIA_SRC_DATA_FILE, 'r') as f:
                sources = json.load(f)
            for src in sources:
                src['state'] = 'stopped'
            logging.info("Existing media_sources.json loaded and states reset to 'stopped'.")
        except Exception as e:
            logging.error(f"Failed to load existing sources during reset: {e}")
            sources = []
    
    if not sources or len(sources) != DEFAULT_SOURCE_COUNT:
        sources = [
            {'index': i + 1, 'file': '', 'state': 'stopped'}
            for i in range(DEFAULT_SOURCE_COUNT)
        ]
        logging.info("media_sources.json created with default source entries.")

    try:
        with open(MEDIA_SRC_DATA_FILE, 'w') as f:
            json.dump(sources, f, indent=2)
        logging.info("media_sources.json saved after reset.")
    except Exception as e:
        logging.error(f"Failed to save media_sources.json during reset: {e}")    

ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

@app.route('/mediasrc/videos', methods=['GET'])
def list_video_files():
    try:
        video_files = []
        for root, _, files in os.walk(MEDIA_DIR):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, f)
                    relative_path = os.path.relpath(full_path, MEDIA_DIR)
                    # Use forward slashes for web URLs
                    video_files.append(relative_path.replace(os.path.sep, '/'))

        return jsonify(sorted(video_files)), 200
    except Exception as e:
        logging.error(f"Error scanning media files: {e}")
        return jsonify({'error': 'Failed to list video files'}), 500
    
@app.route('/mediasrc', methods=['GET'])
def get_sources():
    try:
        sources = load_sources()
        return jsonify(sources)
    except Exception as e:
        logging.exception("Error in GET /mediasrc")
        return jsonify({'error': 'Failed to load sources'}), 500

@app.route('/mediasrc/assign', methods=['POST'])
def assign_source():
    try:
        data = request.get_json()
        index = data.get('index')
        file = data.get('file')  # Can be None or empty string for unassignment

        if index is None:
            return jsonify({'error': 'Missing index'}), 400

        sources = load_sources()
        for src in sources:
            if src['index'] == index:
                was_playing = (src['state'] == 'playing')

                if was_playing:
                    logging.info(f"Stopping stream for source {index} before reassigning.")
                    stop_media_stream(index)

                # Assign new file or clear it
                src['file'] = file if file else ''

                # Restart only if it was playing and new file is assigned
                if was_playing and file:
                    file_path = os.path.join(MEDIA_DIR, file)
                    success, error_msg = start_media_stream(index, file_path)
                    if not success:
                        logging.error(f"Failed to restart stream after assigning file: {error_msg}")
                        return jsonify({'error': error_msg}), 500
                    src['state'] = 'playing'
                    logging.info(f"Source {index} reassigned and restarted with '{file}'.")
                else:
                    # Keep the state unchanged if it wasn't playing
                    logging.info(
                        f"Source {index} {'assignment cleared' if not file else f'reassigned to {file}'}. Stream was {'playing' if was_playing else 'not playing'}."
                    )

                save_sources(sources)
                return jsonify({'success': True})

        logging.warning(f"Source index {index} not found in assign")
        return jsonify({'error': 'Source not found'}), 404

    except Exception as e:
        logging.exception("Error in POST /mediasrc/assign")
        return jsonify({'error': 'Internal server error'}), 500

    
@app.route('/mediasrc/start', methods=['POST'])
def start_source():
    try:
        data = request.get_json()
        index = data.get('index')

        if index is None:
            return jsonify({'error': 'Missing index'}), 400

        sources = load_sources()
        for src in sources:
            if src['index'] == index:
                filename = src.get('file')
                if not filename:
                    logging.warning(f"Attempt to start source {index} with no file assigned")
                    return jsonify({'error': 'No file assigned to source'}), 400

                file_path = os.path.join(MEDIA_DIR, filename)

                success, error_msg = start_media_stream(index, file_path)
                if not success:
                    return jsonify({'error': error_msg}), 500

                src['state'] = 'playing'
                save_sources(sources)
                return jsonify({'success': True})

        logging.warning(f"Source index {index} not found in start")
        return jsonify({'error': 'Source not found'}), 404

    except Exception as e:
        logging.exception("Error in POST /mediasrc/start")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/mediasrc/stop', methods=['POST'])
def stop_source():
    try:
        data = request.get_json()
        index = data.get('index')

        if index is None:
            return jsonify({'error': 'Missing index'}), 400

        sources = load_sources()
        for src in sources:
            if src['index'] == index:
                logging.info(f"Stopping source {index}")
                stop_media_stream(index)
                src['state'] = 'stopped'
                save_sources(sources)
                return jsonify({'success': True})

        logging.warning(f"Source index {index} not found in stop")
        return jsonify({'error': 'Source not found'}), 404
    except Exception as e:
        logging.exception("Error in POST /mediasrc/stop")
        return jsonify({'error': 'Internal server error'}), 500

def get_env_from_manifest(app_name):
    manifest = app_manager.get_app_config(app_name)
    if not manifest:
        return {}

    # Find the matching application block
    app_block = next((a for a in manifest.get("applications", []) if a.get("name") == app_name), None)
    if not app_block:
        return {}

    config = app_block.get("configuration", {})
    env_vars = {}

    for line in config.get("environment", []):
        if "=" in line:
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip().strip("'").strip('"')

    return env_vars

@app.route('/gsthelp/<plugin>')
def get_gst_help(plugin):
    app_name = request.args.get("app")

    base_env = os.environ.copy()
    if app_name:
        manifest_env = get_env_from_manifest(app_name)
        base_env.update(manifest_env)

    base_env["PAGER"] = "cat"
    base_env["LESS"] = ""

    # ✅ Remote path
    if is_remote_devkit_configured() and is_remote_devkit_connected():
        exit_code, output = run_remote_gst_inspect(plugin, base_env)
        if exit_code != 0 or "No such element or plugin" in output:
            return f"❌ Plugin '{plugin}' not found or failed to inspect remotely.", 404
        return output

    # ✅ Local path
    try:
        result = subprocess.run(
            ['gst-inspect-1.0', plugin],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
            encoding='utf-8',
            env=base_env
        )
        output = result.stdout.strip()

        if result.returncode != 0 or "No such element or plugin" in output:
            return f"❌ Plugin '{plugin}' not found or failed to inspect.", 404

        return output

    except subprocess.TimeoutExpired:
        return f"❌ Error: gst-inspect took too long — try again later.", 504

    except Exception as e:
        return f"❌ Unexpected server error: {str(e)}", 500


@app.route('/remotedevkit/cfg', methods=['GET'])
def get_remote_devkit_config():
    try:
        if not os.path.exists(CFG_PATH):
            return jsonify({"message": "No configuration found."}), 404

        with open(CFG_PATH, "r") as f:
            config = json.load(f)

        # Optionally mask the root password in the response
        safe_config = config.copy()
        if "remote-devkit" in safe_config and "rootPassword" in safe_config["remote-devkit"]:
            safe_config["remote-devkit"]["rootPassword"] = "••••••••"

        return jsonify(safe_config)

    except Exception as e:
        return jsonify({"message": f"Error reading config: {str(e)}"}), 500


@app.route('/remotedevkit/cfg', methods=['POST'])
def save_remote_devkit_config():
    try:
        data = request.get_json()

        ipaddress = data.get("ip", "").strip()
        port = 22
        if ':' in ipaddress:
            port = int(ipaddress.split(':')[1])
            ipaddress = ipaddress.split(':')[0]

        password = data.get("rootPassword", "")
        

        if not ipaddress or not password and ipaddress != '127.0.0.1':
            return jsonify({"message": "Missing IP or root password"}), 400

        # Test SSH connection
        if ipaddress != '127.0.0.1':
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh.connect(
                    hostname=ipaddress,
                    port=port,
                    username='root',
                    password=password,
                    timeout=5,
                    banner_timeout=5,
                    auth_timeout=5
                )

                # Optionally run a test command to validate login
                stdin, stdout, stderr = ssh.exec_command("echo connected")
                result = stdout.read().decode().strip()

                ssh.close()

                if result != "connected":
                    return jsonify({"message": "SSH login failed or unexpected response."}), 502

            except Exception as ssh_error:
                return jsonify({"message": f"SSH connection failed: {str(ssh_error)}"}), 502

        # Save config
        config = {
            "remote-devkit": {
                "ip": ipaddress,
                "port": port,
                "rootPassword": password
            }
        }

        with open(CFG_PATH, "w") as f:
            json.dump(config, f, indent=2)

        return jsonify({"message": "✅ SSH test succeeded and configuration saved."})

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route('/server-ip')
def get_server_ip():
    try:
        # Check if the IP is provided via environment variable
        container_ip = os.getenv("CONTAINER_HOST_IP")
        if container_ip:
            return jsonify({'ip': container_ip})

        # Fall back to devkit config
        if not is_remote_devkit_configured():
            return jsonify({'ip': '127.0.0.1'})

        remote_ip = get_remote_devkit_ip()
        remote_port = 22

        # Determine the local IP used to reach the remote devkit
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remote_ip, remote_port))
        local_ip = s.getsockname()[0]
        s.close()

        return jsonify({'ip': local_ip})

    except Exception:
        return jsonify({'ip': '127.0.0.1'})

@app.route("/")
def index():
    return render_template("framework.html")

def main():
    parser = argparse.ArgumentParser(description="Start the Optiview server.")
    parser.add_argument("--port", type=int, default=9900, help="Port to run the server on (default: 9900)")
    args = parser.parse_args()
    port = args.port

    # ensure_dependencies_installed()
    ssl_context = check_and_generate_self_signed_cert()
    start_processes(ssl_context)
    reset_sources()

    # Register cleanup on exit
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)

    local_ip = get_lan_ip()
    print("\n" + "="*160)
    print("🚀  SiMa OptiView server is starting...")
    print(f"🌐  Access the server at: \033[1mhttps://{local_ip}:{port}\033[0m")
    print("📎  Make sure to accept the self-signed certificate in your browser.")
    print("📎  To stop OptiView, press `Ctrl + C`")
    print("="*160 + "\n")

    # Start Flask server
    app.run(host="0.0.0.0", port=port, ssl_context=ssl_context)

if __name__ == "__main__":
    main()