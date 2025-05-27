# audio_transcribe.py
# Transcribes audio using OpenAI Whisper.

import argparse
import whisper
import os
import json


def transcribe_audio(audio_path, transcript_txt_path, transcript_json_path, model_size="base"):
    """
    Transcribe audio using OpenAI Whisper and save transcript as .txt and .json (with word-level timestamps).
    """
    model = whisper.load_model(model_size)
    print(f"Transcribing {audio_path} with Whisper model '{model_size}'...")
    result = model.transcribe(audio_path, word_timestamps=True)

    # Save plain text transcript (for Gentle)
    with open(transcript_txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(result["text"].strip() + "\n")
    print(f"Transcript saved to {transcript_txt_path}")

    # Save full JSON (for reference/future use)
    with open(transcript_json_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=2)
    print(f"Full transcript with timestamps saved to {transcript_json_path}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper.")
    parser.add_argument("--audio", required=True, help="Path to audio file (wav, mp3, etc.)")
    parser.add_argument("--txt", default="transcript.txt", help="Output plain text transcript file")
    parser.add_argument("--json", default="transcript.json", help="Output JSON transcript file")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large)")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Audio file not found: {args.audio}")
        return

    transcribe_audio(args.audio, args.txt, args.json, args.model)


if __name__ == "__main__":
    main() 