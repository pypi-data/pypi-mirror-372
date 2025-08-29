# YouTube Downloader

<!-- markdownlint-disable MD013 -->
<!-- markdownlint-configure-file {"ol-prefix": { "style": "ordered" } } -->

1. YouTube Video download
   - From a video or from a playlist
   - Download caption option available
   - Selectable resolution

2. YouTube Audio download
   - From a video or from a playlist

## Installation & Upgrade

1. To install
   - Using `pip`

     ```console
     pip install youtube-downloader-cli
     ```

   - Using `uv`

     ```console
     uv tool install youtube-downloader-cli
     ```

   - Using `uvx` to use this tool directly without install

     ```console
     uvx youtube-downloader-cli
     ```

2. To upgrade

   - Using `pip`

     ```console
     pip install --upgrade youtube-downloader-cli
     ```

   - Using `uv`

     ```console
     uv tool install --upgrade --reinstall youtube-downloader-cli
     ```

   - Using `uvx`

     ```console
     uvx youtube-downloader-cli@latest
     ```

## CLI Application

### Step 1. Enter YouTube video URL (auto-detect from clipboard)

### Step 2. Choose options

Available options:

  ```text
  1. Download audio only 
  2. Download video 
  3. Download video with caption 
  4. Download audios from playlist
  5. Download videos from playlist
  ```

### Step 3. Choose a directory to save file(s)

### Step 4. Choose preferred resolution for video downloading

If option 2, 3, or 5 is chosen in ***Step 2***, please select a preferred resolution for video downloading.

Available options:

  ```text
  SD - 480p
  HD - 720p
  FullHD - 1080p
  QHD - 1440p
  4K - 2160p
  best
  ```

Video with highest resolution, but not higher than user's choice (unless '**best**' is chosen), will be downloaded.

### Step 5. Choose captions to download

If option 3 is chosen in ***Step 2***, please select which caption(s) to be downloaded. User will only be prompted if more than one caption is available for selected video.

> [!Note]
> If PyTubeFix failed to connect to YouTube, it may need to be upgraded to the newest version.
>
> Using `pip`: `pip install --upgrade pytubefix`.
>
> Or using `uv`: `uv install --upgrade --reinstall youtube-downloader-cli`.

<!-- markdownlint-disable-line MD028 -->

> [!Tip]
> When downloading from a playlist (Option 4 & 5), videos/audios will be downloaded in parallel. Maximum number of parallel downloads could be set via environment variable `YTDL_WORKERS` (default is 4).

## Dependencies

1. For CLI Application

   - pyperclip
   - pytubefix
   - questionary
   - rich

2. Of `pytubefix`
   NodeJS is used for POTOKEN generation by `pytubefix`. If NodeJS is not available, POTOKEN will be skipped, may result in YouTube denying `pytubefix`'s requests.

3. FFMPEG

   Progressive stream (both audio & video in one file) in YouTube has lower resolution. If `ffmpeg` is available, high resolution video & audio will be downloaded separately, then merges using `ffmpeg`.

   If `ffmpeg` is not available in $PATH, progressive stream will be downloaded.
