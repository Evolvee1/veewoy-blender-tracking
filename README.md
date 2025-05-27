# Blender 2D Grease Pencil Animation Plugin

This project is a Blender add-on and supporting toolkit for creating 2D Grease Pencil animations driven by video/camera input (for pose estimation) and audio (for lipsync). It leverages state-of-the-art frameworks for pose extraction, speech-to-text, and phoneme alignment.

## Project Structure

```
veewoy-blender-tracking/
│
├── blender_addon/         # Blender add-on Python code (UI, animation logic)
│   ├── __init__.py
│   ├── operators.py
│   ├── panels.py
│   └── utils.py
│
├── external_tools/        # Scripts for pose estimation and audio processing
│   ├── pose_estimation.py   # Uses MediaPipe to extract keypoints from video/camera
│   ├── audio_transcribe.py  # Uses Whisper to transcribe audio
│   ├── phoneme_align.py     # Uses Gentle to align phonemes
│   └── requirements.txt     # Python dependencies for external tools
│
├── data/                  # Intermediate data (keypoints, phonemes, etc.)
│   ├── keypoints.json
│   ├── transcript.txt
│   └── phonemes.json
│
├── requirements.txt       # Top-level requirements (Blender add-on, etc.)
└── README.md
```

## Frameworks & Libraries

- **Pose Estimation:** [MediaPipe](https://google.github.io/mediapipe/) (Python)
- **Audio Transcription:** [OpenAI Whisper](https://github.com/openai/whisper) (Python)
- **Phoneme Alignment:** [Gentle](https://github.com/lowerquality/gentle) (Python)
- **Blender Add-on:** [Blender Python API](https://docs.blender.org/api/current/)

## Overview
- The Blender add-on provides a UI for importing video/audio, running analysis, and animating Grease Pencil objects.
- External Python scripts process video/audio and output data files (JSON/CSV) for the add-on to consume.
- Data is exchanged via the `data/` directory.

## Setup
- See `external_tools/requirements.txt` for installing pose/audio dependencies.
- Install the Blender add-on from the `blender_addon/` directory.