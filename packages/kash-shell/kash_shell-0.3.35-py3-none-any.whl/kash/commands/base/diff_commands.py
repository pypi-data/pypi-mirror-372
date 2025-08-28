from pathlib import Path

from kash.commands.base.show_command import show
from kash.commands.workspace.selection_commands import select
from kash.config.logger import get_logger
from kash.exec import import_locator_args, kash_command
from kash.exec_model.shell_model import ShellResult
from kash.model.items_model import Item, ItemRelations, ItemType
from kash.model.paths_model import StorePath
from kash.shell.output.shell_output import Wrap, cprint
from kash.utils.errors import ContentError, InvalidInput, InvalidOperation
from kash.utils.file_utils.file_formats_model import Format
from kash.utils.text_handling.unified_diffs import unified_diff, unified_diff_files
from kash.workspaces import current_ws

log = get_logger(__name__)


def unified_diff_items(from_item: Item, to_item: Item, strict: bool = True) -> Item:
    """
    Generate a unified diff between two items. If `strict` is true, will raise
    an error if the items are of different formats.
    """
    if not from_item.body and not to_item.body:
        raise ContentError(f"No body to diff for {from_item} and {to_item}")
    if not from_item.store_path or not to_item.store_path:
        raise ContentError("No store path on items; save before diffing")
    diff_items = [item for item in [from_item, to_item] if item.format == Format.diff]
    if len(diff_items) == 1:
        raise ContentError(
            f"Cannot compare diffs to non-diffs: {from_item.format}, {to_item.format}"
        )
    if len(diff_items) > 0 or from_item.format != to_item.format:
        msg = f"Diffing items of incompatible format: {from_item.format}, {to_item.format}"
        if strict:
            raise ContentError(msg)
        else:
            log.warning("%s", msg)

    from_path, to_path = StorePath(from_item.store_path), StorePath(to_item.store_path)

    diff = unified_diff(from_item.body, to_item.body, str(from_path), str(to_path))

    return Item(
        type=ItemType.doc,
        title=f"Diff of {from_path} and {to_path}",
        format=Format.diff,
        relations=ItemRelations(diff_of=[from_path, to_path]),
        body=diff.patch_text,
    )


@kash_command
def diff_items(*paths: str, force: bool = False) -> ShellResult:
    """
    Show the unified diff between the given files. It's often helpful to treat diffs
    as items themselves, so this works on items. Items are imported as usual into the
    global workspace if they are not already in the store.

    Args:
        stat: Only show the diffstat summary.
        force: If true, will run the diff even if the items are of different formats.
    """
    ws = current_ws()
    if len(paths) == 2:
        [path1, path2] = paths
    elif len(paths) == 0:
        try:
            last_selections = ws.selections.previous_n(2, expected_size=1)
        except InvalidOperation:
            raise InvalidInput(
                "Need two selections of single files in history or exactly two paths to diff"
            )
        [path1] = last_selections[0].paths
        [path2] = last_selections[1].paths
    else:
        raise InvalidInput("Provide zero paths (to use selections) or two paths to diff")

    [store_path1, store_path2] = import_locator_args(path1, path2)
    item1, item2 = ws.load(store_path1), ws.load(store_path2)

    diff_item = unified_diff_items(item1, item2, strict=not force)
    diff_store_path = ws.save(diff_item, as_tmp=False)
    select(diff_store_path)
    return ShellResult(show_selection=True)


@kash_command
def diff_files(*paths: str, diffstat: bool = False, save: bool = False) -> ShellResult:
    """
    Show the unified diff between the given files. This works on any files, not
    just items, so helpful for quick analysis without importing the files.

    Args:
        diffstat: Only show the diffstat summary.
        save: Save the diff as an item in the store.
    """
    if len(paths) == 2:
        [path1, path2] = paths
    elif len(paths) == 0:
        # If nothing args given, user probably wants diff_items on selections.
        return diff_items()
    else:
        raise InvalidInput("Provide zero paths (to use selections) or two paths to diff")

    path1, path2 = Path(path1), Path(path2)
    diff = unified_diff_files(path1, path2)

    if diffstat:
        cprint(diff.diffstat, text_wrap=Wrap.NONE)
        return ShellResult(show_selection=False)
    else:
        diff_item = Item(
            type=ItemType.doc,
            title=f"Diff of {path1.name} and {path2.name}",
            format=Format.diff,
            body=diff.patch_text,
        )
        ws = current_ws()
        if save:
            diff_store_path = ws.save(diff_item, as_tmp=False)
            select(diff_store_path)
            return ShellResult(show_selection=True)
        else:
            diff_store_path = ws.save(diff_item, as_tmp=True)
            show(diff_store_path)
            return ShellResult(show_selection=False)
