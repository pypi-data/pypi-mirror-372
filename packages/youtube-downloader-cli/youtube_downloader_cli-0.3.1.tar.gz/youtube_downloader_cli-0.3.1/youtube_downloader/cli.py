import io
from collections.abc import Callable, Iterable
from pathlib import Path
from urllib.parse import urlparse

import click
import pyperclip
import questionary
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import CompleteEvent, Completer, Completion, DeduplicateCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory, History
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.markdown import Markdown
from rich.theme import Theme

from youtube_downloader import __version__, scriptDir
from youtube_downloader.helpers import (
    APPDATA,
    YouTubeMetadataCache,
    error_exit,
    get_audio,
    get_audios,
    get_video,
    get_video_srt,
    get_videos,
    metadata,
)


def url_validate(url: str) -> bool | str:
    if urlparse(url).netloc.endswith("youtube.com") or (len(url) == 0):
        return True
    else:
        return "Please enter a YouTube URL"


# fmt: off
main_opts: dict[str, Callable[[str, Path], None]] = {
    "1. Download audio only "           : get_audio,
    "2. Download video "                : get_video,
    "3. Download video with caption "   : get_video_srt,
    "4. Download audios from playlist " : get_audios,
    "5. Download videos from playlist " : get_videos,
}
# fmt: on

# fmt: off
res_opts: dict[str, int] = {
    "SD - 480p"      : 480,
    "HD - 720p"      : 720,
    "FullHD - 1080p" : 1080,
    "QHD - 1440p"    : 1440,
    "4K - 2160p"     : 2160,
    "best"           : -1,
}
# fmt: on


class HistoryCompleter(Completer):
    def __init__(self, history: History, metadata: YouTubeMetadataCache) -> None:
        self.history = history
        self.metadata = metadata
        self._merged_data = sorted(
            (
                *history.load_history_strings(),
                *metadata.urls,
            ),
            key=lambda x: metadata.titles.get(x, "unknown"),
        )

    def get_completions(self, document: Document, event: CompleteEvent) -> Iterable[Completion]:
        text = document.text
        for item in self._merged_data:
            if text in item:
                yield Completion(
                    text=item,
                    start_position=-len(text),
                    display_meta=self.metadata.titles.get(item, "unknown"),
                )


url_hist_path = APPDATA / "url_history"
url_hist = FileHistory(url_hist_path)
save_hist_path = APPDATA / "save_history"
save_hist = FileHistory(save_hist_path)

if scriptDir.joinpath("README").exists():
    README_MD = scriptDir.joinpath("README").read_text()
else:
    README_MD = scriptDir.parent.joinpath("README.md").read_text()

USAGE_MARKUP = """
SAMPLE : Provide inputs as per steps below
    [not underline green]STEP 1[/not underline green] : Please enter YouTube URL that you want to download from
      Ex: [bold]? Enter YouTube URL: [yellow]https://youtube.com/?v=example1[/yellow][/bold]

    [not underline green]STEP 2[/not underline green] : Select action
      Ex: [bold]? What do you want to download ? (Use arrow keys)
          [not underline white]1. Download audio only [/not underline white]
        » [not underline reverse white]2. Download video [/not underline reverse white] 
          [not underline white]3. Download video with caption [/not underline white]
          [not underline white]4. Download audios from playlist [/not underline white]
          [not underline white]5. Download videos from playlist [/not underline white]
        [/bold]

    Option 2 selected:
      Ex: [bold]? What do you want to download ? [not underline yellow]2. Download video[/not underline yellow][/bold]

    [not underline green]STEP 3[/not underline green] : Choose save location
      Ex: [bold]? Where do you want to save ? [yellow]~/Videos/[/yellow][/bold]

    [not underline green]STEP 4[/not underline green] : If option 2, 3, or 5 is chosen in Step 2, please select a preferred resolution for video downloading.
      Ex: [bold]? What is your prefered resolution ? (Use arrow keys)
          [white]SD - 480p[/white]
          [white]HD - 720p[/white]
        » [reverse white]FullHD - 1080p[/reverse white]
          [white]QHD - 1440p[/white]
          [white]4K - 2160p[/white]
          [white]best[/white][/bold]

    [not underline green]STEP 5[/not underline green] : If option 3 is chosen in STEP 2, select captions to download here
      Ex: [bold]? Select captions to download (Use arrow keys to move, <space> to select, <a> to toggle, <i> to invert)
            » [reverse white]● en ---- English[/reverse white]
              [white]○ ja ---- Japanese[/white]
              [white]○ ko ---- Korean[/white][/bold]

"""

CMD_HELP_MARKUP = "[italic green]Run without option to start the app[/italic green]"


HelpTheme = Theme(
    styles={
        "repr.switch": "blue",
        "repr.option": "green",
        "repr.number": "bright_blue underline",
        "repr.tag_name": "default",
        "rule.line": "bold yellow",
        "markdown.hr": "bold yellow",
        "markdown.h2": "reverse",
        "markdown.h3": "underline",
    }
)


class RichCommandHighlighter(ReprHighlighter):
    highlights = (
        *ReprHighlighter.highlights,
        r"(^|\W)(?P<switch>\-\w+)(?![a-zA-Z0-9])",
        r"(^|\W)(?P<option>\-\-[\w\-]+)(?![a-zA-Z0-9])",
    )


class RichFormatter(click.HelpFormatter):
    def __init__(
        self,
        indent_increment: int = 2,
        width: int | None = None,
        max_width: int | None = None,
    ) -> None:
        super().__init__(indent_increment, width, max_width)
        self.buffer = io.StringIO()
        self.console = Console(
            file=self.buffer,
            force_terminal=True,
            highlighter=RichCommandHighlighter(),
            theme=HelpTheme,
        )

    def write(self, string: str) -> None:
        self.console.print(string, end="")

    def getvalue(self) -> str:
        return self.buffer.getvalue()

    def write_usage(self, prog: str, args: str = "", prefix: str | None = None) -> None:
        super().write_usage(prog, args, prefix=(prefix or "USAGE : "))


class RichHelpCmd(click.Command):
    def get_help(self, ctx: click.Context) -> str:
        formatter = RichFormatter(width=ctx.terminal_width, max_width=ctx.max_content_width)
        self.format_help(ctx, formatter)
        return formatter.getvalue().rstrip("\n")

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        formatter.write(
            "[bold]youtube-downloader-cli :penguin: CLI APP to download from YouTube[/bold]\n"
        )

        formatter.write_paragraph()
        self.format_usage(ctx, formatter)
        formatter.write(self.help)

        formatter.write_paragraph()
        self.format_options(ctx, formatter)


@click.command(cls=RichHelpCmd, help=CMD_HELP_MARKUP, no_args_is_help=False)
@click.help_option("-h", "--help", is_flag=True, is_eager=True)
@click.option("-v", "--version", is_flag=True, is_eager=True, help="Show version and exit.")
@click.option("-m", "--manual", is_flag=True, is_eager=True, help="Show manual page and exit.")
@click.pass_context
def main(ctx: click.Context, version: bool, manual: bool) -> None:
    if version:
        print(f"youtube-downloader-cli v{__version__}")
        return

    if manual:
        console = Console(
            force_terminal=True,
            highlighter=RichCommandHighlighter(),
            theme=HelpTheme,
        )

        console.print(Markdown(README_MD))
        console.rule()
        print(main.get_help(ctx))
        console.print(USAGE_MARKUP.rstrip())

        return

    if not APPDATA.exists():
        APPDATA.mkdir(parents=True)
    if not url_hist_path.exists():
        url_hist_path.touch()
    if not save_hist_path.exists():
        save_hist_path.touch()

    # Get URL from clipboard if available
    if not pyperclip.is_available():
        txt = pyperclip.paste()
        if url_validate(txt) is not True:
            txt = ""
    else:
        txt = ""

    # Get user inputs (URL, action, save location)
    answers = questionary.form(
        url=questionary.text(
            message="Enter YouTube URL:",
            bottom_toolbar="Use <tab> for history",
            default=txt,
            validate=url_validate,
            enable_history_search=False,
            history=url_hist,
            auto_suggest=AutoSuggestFromHistory(),
            completer=DeduplicateCompleter(HistoryCompleter(url_hist, metadata)),
            complete_style=CompleteStyle.MULTI_COLUMN,
        ),
        opt=questionary.select(message="What do you want to download ?", choices=main_opts),
        loc=questionary.path(
            message="Where do you want to save ?",
            bottom_toolbar="Use <up> & <down> for history",
            default=str(Path.cwd()),
            only_directories=True,
            validate=lambda p: (
                True if Path(p).expanduser().is_dir() else "Please enter path to a directory"
            ),
            enable_history_search=False,
            history=save_hist,
            auto_suggest=AutoSuggestFromHistory(),
        ),
    ).ask()

    # If user cancelled, stop executing
    if not answers:
        return

    save_dir = Path(answers.get("loc")).expanduser().resolve()
    url = answers.get("url")
    opt = answers.get("opt")

    if int(opt[0]) in (2, 3, 5):
        # If downloading video
        res_opt = questionary.select(
            message="What is your prefered resolution ?",
            choices=list(res_opts.keys()),
            default="FullHD - 1080p",
        ).ask()

        if not res_opt:
            return

        max_res = res_opts.get(res_opt)
    else:
        # If downloading audio
        max_res = -1

    try:
        main_opts.get(opt)(url, save_dir, max_res=max_res)
    except Exception as e:
        error_exit(e)


if __name__ == "__main__":
    main()
