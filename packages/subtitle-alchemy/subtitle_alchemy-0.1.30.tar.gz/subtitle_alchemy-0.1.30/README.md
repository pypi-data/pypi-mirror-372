# Subtitle Alchemy

**Subtitle Alchemy** is a Python-based tool that automates subtitle generation for audio and video content using the [FunASR](https://github.com/modelscope/FunASR) Speech-to-Text (STT) model, along with a feature that aligns a pre-written transcript with the audio track for accurate subtitling.

## Features

- **Automatic Subtitle Creation**: Generates subtitles from audio/video using FunASR's STT.
- **Transcript Matching (文稿匹配)**: Aligns manually prepared transcripts with audio for precise subtitle timing.

## Installation

You can install via pip:

```bash
pip install -U subtitle-alchemy
```

Or install from source:

```bash
git clone https://github.com/ppmzhang2/subtitle-alchemy && cd subtitle-alchemy
pip install -e .
```

## Usage

Transcribe an audio or video and save the sketch. The output will be an `npz` file saved in the specified directory with the same base name as the input file:

```bash
subalch transcribe path_to_your_media output_dir --hotword "热词"
```

Generate the subtitle from the sketch. The output will be saved in the specified directory with the same base name as the input file. The `--form` option allows you to specify the output format (e.g., `srt`, `ass`, `vtt`, etc.), and the `--threshold` option sets the minimum silence duration (in milliseconds) to split the subtitles:

```bash
subalch generate path_to_sketch.npz output_dir --form srt --threshold 500
```

For transcript alignment, simply provide the path to the sketch and the transcript file:

```bash
subalch align path_to_sketch.npz path_to_transcript --form srt --threshold 500
```

## Dependencies

- Python 3.11+

## Contributing

Pull requests are welcome! For major changes, please open an issue to discuss what you'd like to change.

## License

[MIT](LICENSE)
