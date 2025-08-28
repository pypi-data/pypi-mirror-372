from kash.config.logger import get_logger
from kash.config.text_styles import STYLE_HINT
from kash.exec import assemble_path_args, kash_command
from kash.exec_model.shell_model import ShellResult
from kash.model.paths_model import StorePath
from kash.shell.output.shell_output import cprint
from kash.shell.utils.native_utils import ViewMode, terminal_show_image, view_file_native
from kash.utils.errors import InvalidInput, InvalidState
from kash.web_content.file_cache_utils import cache_file
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_command
def show(
    path: str | None = None,
    console: bool = False,
    native: bool = False,
    thumbnail: bool = False,
    browser: bool = False,
    plain: bool = False,
    noselect: bool = False,
) -> ShellResult:
    """
    Show the contents of a file if one is given, or the first file if multiple files
    are selected. Will try to use native apps or web browser to display the file if
    appropriate, and otherwise display the file in the console.

    Will use `bat` if available to show files in the console, including syntax
    highlighting and git diffs.

    Args:
        console: Force display to console (not browser or native apps).
        native: Force display with a native app (depending on your system configuration).
        thumbnail: If there is a thumbnail image, show it too.
        browser: Force display with your default web browser.
        plain: Use plain view in the console (this is `bat`'s `plain` style).
        noselect: Disable default behavior where `show` also will `select` the file.
    """
    view_mode = (
        ViewMode.console
        if console or plain
        else ViewMode.browser
        if browser
        else ViewMode.native
        if native
        else ViewMode.auto
    )
    try:
        input_paths = assemble_path_args(path)
        input_path = input_paths[0]

        if isinstance(input_path, StorePath):
            ws = current_ws()
            if input_path.is_file():
                # Optionally, if we can inline display the image (like in kitty) above the text representation, do that.
                item = ws.load(input_path)
                if thumbnail and item.thumbnail_url:
                    try:
                        local_path = cache_file(item.thumbnail_url).content.path
                        terminal_show_image(local_path)
                    except Exception as e:
                        log.info("Had trouble showing thumbnail image (will skip): %s", e)
                        cprint(f"[Image: {item.thumbnail_url}]", style=STYLE_HINT)

            view_file_native(ws.base_dir / input_path, view_mode=view_mode, plain=plain)
        else:
            view_file_native(input_path, view_mode=view_mode, plain=plain)
        if not noselect:
            from kash.commands.workspace.selection_commands import select

            if isinstance(input_path, StorePath):
                select(input_path)
            return ShellResult(show_selection=True)
    except (InvalidInput, InvalidState):
        if path:
            # If path is absolute or we couldbn't get a selection, just show the file.
            view_file_native(path, view_mode=view_mode)
        else:
            raise InvalidInput("No selection")

    return ShellResult(show_selection=False)
