from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

from pytubefix import Stream, YouTube
from pytubefix.exceptions import PytubeFixError as PytubeError

from youtube_downloader.helpers.util import (
    complete,
    download,
    error_exit,
    getDefaultTitle,
    metadata,
    progress,
    progress_update,
)


def initialize(url: str, **kwargs: Any) -> tuple[Stream, str]:
    try:
        yt = YouTube(
            url=url,
            client="WEB",
            on_complete_callback=complete,
            on_progress_callback=progress_update,
        )
        stream = yt.streams.get_audio_only()
        defaultTitle = getDefaultTitle(
            yt, subtype=Path(stream.default_filename).suffix.removeprefix(".")
        )
        metadata.add_title(url, Path(defaultTitle).stem)

        return stream, defaultTitle
    except (URLError, HTTPError) as err:
        progress.console.print(
            "error connecting to YouTube. possible problem: [yellow]invalid url[/yellow] or [yellow]internet connection[/yellow]"
        )
        error_exit(err)
    except PytubeError as err:
        error_exit(err)


def get_audio(url: str, save_dir: Path, **kwargs: Any) -> None:
    with progress, metadata:
        task_id = progress.custom_add_task(title=url, description="Downloading", start=False)
        stream, defaultTitle = initialize(url, **kwargs)
        progress.start_task(task_id)
        progress.update(task_id, description=defaultTitle, total=stream.filesize, completed=0)
        progress.update_mapping(stream.title, task_id)
        # print(f"Downloading {defaultTitle}")
        download(stream, save_dir, defaultTitle, **kwargs)


if __name__ == "__main__":
    pass
