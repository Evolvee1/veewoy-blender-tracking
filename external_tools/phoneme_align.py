# phoneme_align.py
# Aligns phonemes to transcript/audio using Gentle.

import argparse
import subprocess
import json
import os

# Path to Gentle's align.py or Docker image (update as needed)
GENTLE_ALIGN_SCRIPT = "gentle/align.py"  # Update this path if needed


def run_gentle(audio_path, transcript_path, output_json_path):
    """
    Run Gentle forced aligner on the given audio and transcript, outputting phoneme timings to a JSON file.
    """
    # Example: python gentle/align.py audio.wav transcript.txt > aligned.json
    cmd = [
        "python", GENTLE_ALIGN_SCRIPT,
        audio_path,
        transcript_path
    ]
    print(f"Running Gentle: {' '.join(cmd)}")
    with open(output_json_path, "w", encoding="utf-8") as outfile:
        subprocess.run(cmd, stdout=outfile, check=True)
    print(f"Alignment complete. Output: {output_json_path}")


def main():
    parser = argparse.ArgumentParser(description="Align phonemes to audio using Gentle.")
    parser.add_argument("--audio", required=True, help="Path to audio file (wav)")
    parser.add_argument("--transcript", required=True, help="Path to transcript file (txt)")
    parser.add_argument("--output", default="phonemes.json", help="Output JSON file for phoneme timings")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Audio file not found: {args.audio}")
        return
    if not os.path.exists(args.transcript):
        print(f"Transcript file not found: {args.transcript}")
        return

    run_gentle(args.audio, args.transcript, args.output)


if __name__ == "__main__":
    main() 