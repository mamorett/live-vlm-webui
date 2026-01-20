import os
import sys
import json

file_dir = "src/live_vlm_webui"
config_json_path = os.path.join(file_dir, "config.json")
print(f"Checking config at: {config_json_path}")
print(f"Exists: {os.path.exists(config_json_path)}")
if os.path.exists(config_json_path):
    print("Content valid JSON:", end=" ")
    try:
        with open(config_json_path, 'r') as f:
            data = json.load(f)
            print("Yes")
            print("rtsp_cameras in data:", "rtsp_cameras" in data)
            print("rtsp_cameras count:", len(data.get("rtsp_cameras", [])))
    except Exception as e:
        print(f"No ({e})")
