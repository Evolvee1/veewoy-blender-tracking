# utils.py
# Utility functions for the Blender add-on. 
# Requires: websocket-client (pip install websocket-client)

import json
import bpy


def load_keypoints_json(filepath):
    """Load pose keypoints from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_phonemes_json(filepath):
    """Load phoneme timings from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data 