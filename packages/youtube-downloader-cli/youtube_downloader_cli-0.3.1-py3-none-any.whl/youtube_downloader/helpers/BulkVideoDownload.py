from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

from pytubefix import Playlist
from pytubefix.exceptions import PytubeFixError as PytubeError

from youtube_downloader.helpers.DownloadVideo import (
    initialize as init_one,
)
from youtube_downloader.helpers.DownloadVideo import (
    initialize_wffmpeg as init_one_ffmpeg,
)
from youtube_downloader.helpers.util import (
    NO_WORKER,
    check_ffmpeg,
    error_exit,
    getDefaultTitle,
    metadata,
    progress,
    wait,
)
from youtube_downloader.helpers.util import (
    download as download_one,
)
from youtube_downloader.helpers.util import (
    download_video_wffmpeg as download_one_ffmpeg,
)


def initialize(url: str) -> Iterable[str]:
    try:
        playlist = Playlist(url, client="WEB")
        # TODO: add logging
        metadata.add_title(url, Path(getDefaultTitle(playlist)).stem)
        return playlist.video_urls
    except (URLError, HTTPError) as err:
        progress.console.print(
            "error connecting to YouTube. possible problem: [yellow]invalid url[/yellow] or [yellow]internet connection[/yellow]"
        )
        error_exit(err)
    except PytubeError as err:
        error_exit(err)


def download(urls: Iterable[str], save_dir: Path, **kwargs: Any) -> None:
    def run(url: str, **kwargs: Any) -> None:
        task_id = progress.custom_add_task(
            title=url,
            description="Downloading ...",
            total=0,
            completed=0,
        )
        stream, defaultTitle = init_one(url, **kwargs)
        progress.update(task_id, description=stream.title, total=stream.filesize)
        progress.update_mapping(stream.title, task_id)
        print(f"Downloading resolution {stream.resolution} for {defaultTitle}")
        download_one(stream, save_dir, defaultTitle, **kwargs)

    with progress:
        with ThreadPoolExecutor(max_workers=NO_WORKER) as pool:
            for url in urls:
                pool.submit(run, url, **kwargs)
                wait(0.5)


def download_wffmpeg(videos: Iterable[str], save_dir: Path, **kwargs: Any) -> None:
    def run(url: str, **kwargs: Any) -> None:
        task_id = progress.custom_add_task(
            title=url,
            description="Downloading ...",
            total=0,
            completed=0,
        )
        audio_stream, video_stream, defaultTitle = init_one_ffmpeg(url, **kwargs)
        if not save_dir.joinpath(defaultTitle).exists():
            print(f"+ Downloading resolution {video_stream.resolution} for {defaultTitle}")
            progress.update(
                task_id,
                description=defaultTitle,
                total=audio_stream.filesize + video_stream.filesize,
                completed=0,
            )
            progress.update_mapping(audio_stream.title, task_id)
            progress.update_mapping(video_stream.title, task_id)
            download_one_ffmpeg(audio_stream, video_stream, save_dir, defaultTitle, **kwargs)
        else:
            progress.remove_task(task_id)

    with progress:
        with ThreadPoolExecutor(max_workers=NO_WORKER) as pool:
            for video in videos:
                pool.submit(run, video, **kwargs)
                wait(0.5)


def get_videos(url: str, save_dir: Path, **kwargs: Any) -> None:
    with metadata:
        videos = initialize(url)
        if not check_ffmpeg():
            download(videos, save_dir, **kwargs)
        else:
            download_wffmpeg(videos, save_dir, **kwargs)


if __name__ == "__main__":
    pass
