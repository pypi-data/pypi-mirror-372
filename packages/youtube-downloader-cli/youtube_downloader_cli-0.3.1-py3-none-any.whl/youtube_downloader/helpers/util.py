import json
import os
import subprocess
import unicodedata
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Any

from click import ClickException
from pytubefix import Playlist, Stream, YouTube
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    FileSizeColumn,
    GetTimeCallable,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TotalFileSizeColumn,
)
from rich.table import Column
from rich.text import Text

APPDATA = Path("~/.local/share/youtube-downloader-cli/").expanduser()
# TODO: change NO_WORKER to a function to only evaluate on demand
try:
    # TODO: separte into more steps and add logging
    NO_WORKER = int(os.environ.get("YTDL_WORKERS", 4))
except ValueError:
    NO_WORKER = 4


class CustomProgress(Progress):
    def __init__(
        self,
        *columns: str | ProgressColumn,
        console: Console | None = None,
        auto_refresh: bool = True,
        refresh_per_second: float = 10,
        speed_estimate_period: float = 30,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        get_time: GetTimeCallable | None = None,
        disable: bool = False,
        expand: bool = False,
    ) -> None:
        super().__init__(
            *columns,
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_time=get_time,
            disable=disable,
            expand=expand,
        )
        self.task_ids_mapping: dict[str, int] = dict()

    def custom_add_task(
        self,
        title: str,
        description: str,
        start: bool = True,
        total: float | None = 100,
        completed: int = 0,
        visible: bool = True,
        **fields: Any,
    ) -> TaskID:
        task_id = self.add_task(description, start, total, completed, visible, **fields)
        self.task_ids_mapping[title] = task_id
        return task_id

    def update_mapping(self, title: str, task_id: int) -> None:
        self.task_ids_mapping[title] = task_id


progress: CustomProgress = CustomProgress(
    SpinnerColumn(),
    TextColumn(
        "[progress.description]{task.description}",
        table_column=Column(width=30, overflow="ellipsis", no_wrap=True),
    ),
    BarColumn(bar_width=50, style="red", complete_style="green"),
    TextColumn(" - ", style="bar.back"),
    TaskProgressColumn(),
    TextColumn(" - ", style="bar.back"),
    FileSizeColumn(),
    TextColumn("/", style="green"),
    TotalFileSizeColumn(),
    transient=True,
    refresh_per_second=100,
)

progress2: Progress = Progress(
    SpinnerColumn(),
    TextColumn(
        "[progress.description]{task.description}",
        table_column=Column(width=30, overflow="ellipsis", no_wrap=True),
    ),
    BarColumn(bar_width=50, style="red", complete_style="green"),
    TaskProgressColumn(),
    transient=True,
    refresh_per_second=100,
)


def progress_update(stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
    global progress
    task_id = progress.task_ids_mapping.get(stream.title)
    progress.update(task_id, advance=len(chunk))


def complete(stream: Stream, filepath: str) -> None:
    file = Path(filepath)
    task_id = progress.task_ids_mapping.get(stream.title)

    with progress._lock:
        if progress._tasks[task_id].finished:
            if file.stem not in ["ain", "vin"]:
                progress.console.print(
                    f"[green]Successfully downloaded [/green][purple]{file.name} "
                )
            progress.remove_task(task_id)


def download(stream: Stream, save_dir: Path, filename: str, **kwargs: Any) -> None:
    stream.download(filename=filename, output_path=save_dir)


def error_exit(_exception: Exception) -> None:
    raise ClickException(f"{type(_exception).__name__} : {_exception}")


def getDefaultTitle(y: YouTube | Stream | Playlist, subtype: str = "mp4") -> str:
    """
    Create safe file name by removing special character
    from YouTube video title
    """

    # TODO: add logging
    if isinstance(y, Playlist):
        return f"Playlist {y.title}"

    if isinstance(y, YouTube):
        title = (
            y.vid_info.get("microformat", {})
            .get("playerMicroformatRenderer", {})
            .get("title", {})
            .get("simpleText", None)
            or y.title
        ) + f".{subtype}"

    if isinstance(y, Stream):
        title = y.default_filename

    return title.translate(
        {
            ord(x): ""
            for x in title
            if unicodedata.category(x)[0] not in "LN" and x not in "_-()[]! ."
        }
    )


def check_ffmpeg() -> bool:
    """
    Check if ffmpeg is available.
    return True if ffmpeg is present, False otherwise
    """

    try:
        subprocess.check_call(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        progress.console.print("[yellow]ffmpeg is not available")
        return False


def ffmpeg_merge(audio: Path, video: Path, out: Path) -> bool:
    try:
        # fmt: off
        subprocess.check_output(
            [
                "ffmpeg", "-y",
                "-i", str(audio.resolve()),
                "-i", str(video.resolve()),
                "-c", "copy",
                "-loglevel", "warning",
                str(out.resolve()),
            ],
            stderr=subprocess.STDOUT,
        )
        # fmt: on
        return True
    except subprocess.CalledProcessError as e:
        panel = Panel(
            Group(
                Text.assemble(("failed to merge ", "default"), (out.name, "purple")),
                Panel(
                    e.output.decode().strip(),
                    title="[red]error",
                    title_align="left",
                    border_style="red",
                ),
            ),
            title="[red]error using ffmpeg",
            title_align="left",
            border_style="red",
        )
        progress.console.print(panel)
        return False


def download_video_wffmpeg(
    audio_stream: Stream, video_stream: Stream, save_dir: Path, filename: str, **kwargs: Any
) -> None:
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        audio_file = Path(tmpdir) / f"ain.{audio_stream.subtype}"
        video_file = Path(tmpdir) / f"vin.{video_stream.subtype}"

        download(audio_stream, Path(tmpdir), audio_file.name, **kwargs)
        download(video_stream, Path(tmpdir), video_file.name, **kwargs)

        if ffmpeg_merge(audio_file, video_file, save_dir / filename):
            progress.console.print(f"[green]Successfully downloaded [/green][purple]{filename}")


def wait(sec: float) -> None:
    sleep(sec)


class YouTubeMetadataCache:
    def __init__(self, p: Path) -> None:
        if not p.exists():
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
            p.touch()
        self._filepath = p
        self._loaded = False

    @property
    def urls(self) -> list[str]:
        if (not self._loaded) or (not hasattr(self, "_urls")):
            self._load()
            self._urls = [url for url in self._json.keys()]
        return self._urls

    @property
    def titles(self) -> dict:
        if (not self._loaded) or (not hasattr(self, "_titles")):
            self._load()
            self._titles = {url: self._json.get(url, {}).get("title", "") for url in self._json}

        return self._titles

    def _load(self) -> None:
        if not self._loaded:
            self._cache = self._filepath.read_bytes()
            if self._cache:
                self._json = json.loads(self._cache)
            else:
                self._json = {}
            self._loaded = True

    def add_title(self, url: str, title: str) -> None:
        if not self._loaded:
            self._load()
        self._json[url] = {}
        self._json[url]["title"] = title
        if not hasattr(self, "_titles"):
            self._titles = {}
        # TODO: add logging
        self._titles[url] = title

    def _store(self) -> None:
        if not self._loaded:
            return

        self._filepath.write_text(json.dumps(self._json))

    def __enter__(self):  # noqa: ANN204
        if not self._loaded:
            self._load()
        return self

    def __exit__(self, ext, val, tb) -> None:  # noqa: ANN001
        self._store()


metadata = YouTubeMetadataCache(APPDATA / "metadata")
