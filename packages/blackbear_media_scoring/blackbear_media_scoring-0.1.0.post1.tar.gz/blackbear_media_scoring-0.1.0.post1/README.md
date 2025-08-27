# BlackBear Media Scoring
Scoring video, audio, or text based on categories.

## Project Initialization

To set up this project on a new device, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:iak-id/blackbear-media-scoring.git
    cd blackbear-media-scoring
    ```

2.  **Install dependencies:**
    This project uses `poetry` for dependency management. If you don't have `poetry` installed, you can install it by following the instructions on its official website (https://python-poetry.org/docs/#installation).

    Once `poetry` is installed, install the project dependencies:
    ```bash
    poetry install
    ```

3.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```

    ### Setting up API Keys

    To use the different AI models, you need to set up the corresponding API keys as environment variables:
 
    *   **Gemini**: Set `GEMINI_API_KEY` to your Gemini API key.
    *   **OpenRouter**: Set `OPENROUTER_API_KEY` to your OpenRouter API key.

    For the OpenRouter provider, you can also set specific models for image and audio processing:

    *   **OPENROUTER_IMAGE_EXTRACTOR_MODEL**: Set to the OpenRouter model you want to use for image processing (default: `google/gemini-2.5-flash-lite`).
    *   **OPENROUTER_AUDIO_EXTRACTOR_MODEL**: Set to the OpenRouter model you want to use for audio processing (default: `google/gemini-2.5-flash-lite`).
    *   **OPENROUTER_ASSESSOR_EXTRACTOR_MODEL**: Set to the OpenRouter model you want to use for assessing the extracted media (default: `google/gemini-2.5-flash-lite`).

    You can set these environment variables in your shell or create a `.env` file in the project root directory:

    ```bash
    GEMINI_API_KEY=your-gemini-api-key
    OPENROUTER_API_KEY=your-openrouter-api-key
    OPENROUTER_IMAGE_EXTRACTOR_MODEL=your-image-model
    OPENROUTER_AUDIO_EXTRACTOR_MODEL=your-audio-model
    OPENROUTER_ASSESSOR_EXTRACTOR_MODEL=your-assessor-model
    ```


## Usage

### Running All Services Simultaneously

To run the entire pipeline (download, extract, and assess) for a YouTube video:

```bash
poetry run python -m blackbear_media_scoring <youtube_url> [--type video|audio] [--start HH:MM:SS] [--end HH:MM:SS]
```

*   `<youtube_url>`: The YouTube video URL.
*   `--type video|audio`: Optional. Type of media to download (default: `video`).
*   `--start HH:MM:SS`: Optional. Start time of the video segment (e.g., `00:01:30` or `90`).
*   `--end HH:MM:SS`: Optional. End time of the video segment (e.g., `00:02:00` or `120`).

**Example:**
```bash
poetry run python -m blackbear_media_scoring "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start "00:00:10" --end "00:00:20" --type video
```

You can also run each service independently.

### Running Individual Services

#### Downloader

Download a YouTube video or a segment of it:

```bash
poetry run python -m blackbear_media_scoring.downloader <youtube_url> [-s <start_time>] [-e <end_time>] [-o <output_dir>] [--debug] [--verbose]
```

*   `<youtube_url>`: The URL of the YouTube video to download.
*   `-s <start_time>`: Optional. Start time of the segment (e.g., `00:01:30` or `90`).
*   `-e <end_time>`: Optional. End time of the segment (e.g., `00:02:00` or `120`).
*   `-o <output_dir>`: Optional. Directory to save the downloaded file (default: `output`).
*   `--debug`: Optional. Enable debug output for `yt-dlp`.
*   `--verbose`: Optional. If false, then only print the absolute path of the downloaded file to stdout.

**Example:**
```bash
poetry run python -m blackbear_media_scoring.downloader "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s "00:00:10" -e "00:00:20"
```

#### Extractor

Extract a description from a video, image, or audio file:

```bash
poetry run python -m blackbear_media_scoring.extractor <media_path> [--model <model_name>] [--image-model <model_name>] [--audio-model <model_name>] [--media-type video|image|audio]
```

*   `<media_path>`: Path to the media file to describe.
*   `--model <model_name>`: Optional. The AI model to use for extraction (default: `gemini`). Supported models: `gemini`, `openrouter`.
*   `--image-model <model_name>`: Optional. The AI model to use for image extraction (default: value of `--model`).
*   `--audio-model <model_name>`: Optional. The AI model to use for audio extraction (default: value of `--model`).
*   `--media-type video|image|audio`: Optional. Type of media to process (default: `video`).

When `--media-type` is `video`, the video is processed as a whole.
When `--media-type` is `image`, frames are extracted from the video and processed as images.
When `--media-type` is `audio`, audio is extracted from the video and processed as audio.

**Examples:**
```bash
poetry run python -m blackbear_media_scoring.extractor "output/my_video.mp4" --model gemini
```

**Example with OpenRouter:**
```bash
OPENROUTER_API_KEY="your-api-key" poetry run python -m blackbear_media_scoring.extractor "output/my_video.mp4" --model openrouter
```

**Example with different models for image and audio:**
```bash
OPENROUTER_API_KEY="your-api-key" GEMINI_API_KEY="your-gemini-api-key" poetry run python -m blackbear_media_scoring.extractor "output/my_video.mp4" --model openrouter --image-model gemini --audio-model gemini --media-type video
```

**Example for image processing (extracts frames from video):**
```bash
GEMINI_API_KEY="your-gemini-api-key" poetry run python -m blackbear_media_scoring.extractor "output/my_video.mp4" --model gemini --media-type image
```

**Example for audio processing (extracts audio from video):**
```bash
OPENROUTER_API_KEY="your-api-key" poetry run python -m blackbear_media_scoring.extractor "output/my_video.mp4" --model openrouter --media-type audio
```

#### Assessor

Assess text content for sensitive material:

```bash
poetry run python -m blackbear_media_scoring.assesor "<text_to_assess>" [--model <model_name>]
```

*   `<text_to_assess>`: The text content to be scored.
*   `--model <model_name>`: Optional. The LLM model to use for assessment (default: `gemini`).

**Example:**
```bash
poetry run python -m blackbear_media_scoring.assesor "This is a test text about a cat playing with a ball."
```

