import time
from dataclasses import dataclass, replace
from pathlib import Path

from prettyfmt import fmt_lines, fmt_path, plural

from kash.config.logger import get_logger
from kash.config.text_styles import (
    EMOJI_SKIP,
    EMOJI_START,
    EMOJI_SUCCESS,
    EMOJI_TIMING,
)
from kash.exec.preconditions import is_url_resource
from kash.exec.resolve_args import assemble_action_args
from kash.exec_model.args_model import CommandArg
from kash.file_storage.file_store import FileStore
from kash.model.actions_model import (
    NO_ARGS,
    Action,
    ActionInput,
    ActionResult,
    ExecContext,
    PathOpType,
)
from kash.model.exec_model import ActionContext, RuntimeSettings
from kash.model.items_model import Item, State
from kash.model.operations_model import Input, Operation, Source
from kash.model.params_model import ALL_COMMON_PARAMS, GLOBAL_PARAMS, RawParamValues
from kash.model.paths_model import StorePath
from kash.shell.output.shell_output import PrintHooks
from kash.utils.common.s3_utils import get_s3_parent_folder, s3_sync_to_folder
from kash.utils.common.task_stack import task_stack
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import Url, is_s3_url
from kash.utils.errors import ContentError, InvalidOutput, get_nonfatal_exceptions
from kash.workspaces import Selection, current_ws

log = get_logger(__name__)


def prepare_action_input(*input_args: CommandArg, refetch: bool = False) -> ActionInput:
    """
    Prepare input args, which may be URLs or paths, into items that correspond to
    URL or file resources, either finding them in the workspace or importing them.
    Also fetches metadata for URLs if they don't already have title and description.
    Automatically imports any URLs and copies any sidematter-format files (metadata/assets).
    """
    from kash.exec.fetch_url_items import fetch_url_item_content

    ws = current_ws()

    # Ensure input items are already saved in the workspace and load the corresponding items.
    # This also imports any URLs.
    input_items = [ws.import_and_load(arg, with_sidematter=True) for arg in input_args]

    # URLs should have metadata like a title and be valid, so we fetch them.
    if input_items:
        log.message("Assembling metadata for input items:\n%s", fmt_lines(input_items))
        input_items = [
            fetch_url_item_content(item, refetch=refetch).item if is_url_resource(item) else item
            for item in input_items
        ]

    return ActionInput(input_items)


def validate_action_input(
    context: ExecContext, ws: FileStore, action: Action, action_input: ActionInput
) -> Operation:
    """
    Validate an action input, ensuring the right number of args, all explicit params are filled,
    and the precondition holds and return an `Operation` that describes what will happen.
    For flexibility, we don't require the items to be saved (have a store path).
    """
    input_items = action_input.items
    # Validations:
    # Ensure we have the right number of args.
    action.validate_args(len(input_items))
    # Ensure all explicit parameters are filled in.
    action.validate_params_present()
    # Validate the precondition holds on the inputs.
    action.validate_precondition(action_input)

    # Now make a note of the the operation we will perform.
    # If the inputs are paths, record the input paths, including hashes.
    def input_for(item: Item) -> Input:
        if item.store_path:
            return Input(StorePath(item.store_path), ws.hash(StorePath(item.store_path)))
        else:
            return Input(path=None, source_info="unsaved")

    inputs = [input_for(item) for item in input_items]

    # Add any non-default runtime options into the options summary.
    options = {**action.param_value_summary(), **context.settings.non_default_options}
    operation = Operation(action.name, inputs, options)

    return operation


def log_action(action: Action, action_input: ActionInput, operation: Operation):
    """
    Log the action and the operation we are about to run.
    """
    PrintHooks.before_log_action_run()
    log.message("%s Action: `%s`", EMOJI_START, action.name)
    log.info("Running: `%s`", operation.command_line(with_options=True))
    if len(action.param_value_summary()) > 0:
        log.message("Parameters: %s", action.param_value_summary_str())
    log.info("Operation is: %s", operation)
    log.info("Input items are:\n%s", fmt_lines(action_input.items))


def check_for_existing_result(context: ActionContext) -> ActionResult | None:
    """
    Check if we already have the results for this operation (same action and inputs)
    If so return it, unless rerun is requested, in which case we just log that the results
    already exist.
    """
    action = context.action
    settings = context.settings
    ws = settings.workspace
    rerun = settings.rerun

    existing_result = None

    # Check if a previous run already produced the result.
    # To do this we preassemble outputs.
    preassembled_result = action.preassemble_result(context)
    if preassembled_result:
        # Check if these items already exist, with last_operation matching action and input fingerprints.
        already_present = [ws.find_by_id(item) for item in preassembled_result.items]
        all_present = all(already_present)
        log.info(
            "Rerun check: all_present=%s with these items already present:\n%s",
            all_present,
            fmt_lines(already_present),
        )
        if all_present:
            if rerun:
                log.message("All outputs already exist but running anyway since rerun requested.")
            else:
                log.message(
                    "All outputs already exist! Skipping action (use --rerun to force run).",
                )
                existing_items = [ws.load(not_none(store_path)) for store_path in already_present]
                existing_result = ActionResult(existing_items)
    else:
        log.info(
            "Rerun check: Will run since `%s` has no rerun check (no preassembly).",
            action.name,
        )

    return existing_result


def run_action_operation(
    context: ActionContext,
    action_input: ActionInput,
    operation: Operation,
) -> ActionResult:
    """
    Run an action with final execution context and resolved inputs. Handles only execution,
    adding operation history to the item metadata, and logging. Does not save.
    """
    start_time = time.time()

    # Run the action.
    action = context.action
    settings = context.settings
    if action.run_per_item:
        result = _run_for_each_item(context, action_input)
    else:
        result = action.run(action_input, context)

    if not result:
        raise InvalidOutput(f"Action `{action.name}` did not return any results")

    # Record the operation and add to the history of each item.
    for i, item in enumerate(result.items):
        # A per-item action should be recorded as if it ran on each item individually.
        if action.run_per_item:
            this_op = replace(operation, arguments=[operation.arguments[i]])
        else:
            this_op = operation
        item.update_source(Source(operation=this_op, output_num=i, cacheable=action.cacheable))

    # Override the state if appropriate (this handles marking items as transient).
    if settings.override_state:
        for item in result.items:
            item.state = settings.override_state

    log.info("Action `%s` result: %s", action.name, result)

    elapsed = time.time() - start_time
    if elapsed > 1.0:
        log.message("%s Action `%s` took %.1fs.", EMOJI_TIMING, action.name, elapsed)

    return result


class SkipItem(Exception):
    """
    Raise this exception in an action function body to skip the current item.
    """


def _run_for_each_item(context: ActionContext, input: ActionInput) -> ActionResult:
    """
    Helper to process each input item. If non-fatal errors are encountered on any item,
    they are reported and processing continues with the next item.
    """
    action = context.action
    items = input.items
    log.info("Running action `%s` for each input on %s items", action.name, len(items))

    def run_item(item: Item) -> Item:
        # Should have already validated arg counts by now.
        result = action.run(ActionInput([item]), context)
        if result.has_hints():
            log.warning(
                "Ignoring result hints for action `%s` when running on multiple items"
                " (consider setting run_per_item=False): %s",
                action.name,
                result,
            )
        return result.items[0]

    with task_stack().context(action.name, len(items), "item") as ts:
        result_items: list[Item] = []
        errors: list[Exception] = []
        multiple_inputs = len(items) > 1

        for i, item in enumerate(items):
            log.message(
                "Action `%s` input item %d/%d:\n%s",
                action.name,
                i + 1,
                len(items),
                fmt_lines([item]),
            )
            had_error = False
            try:
                result_item = run_item(item)
                result_items.append(result_item)
            except SkipItem:
                log.info("Caught SkipItem exception, skipping run on this item")
                result_items.append(item)
                continue
            except get_nonfatal_exceptions() as e:
                errors.append(e)
                had_error = True

                if multiple_inputs:
                    log.error(
                        "Error processing item; continuing with others: %s: %s",
                        e,
                        item,
                    )
                else:
                    # If there's only one input, fail fast.
                    raise e
            finally:
                ts.next(last_had_error=had_error)

    if errors:
        log.error(
            "%s %s occurred while processing items. See above!",
            len(errors),
            plural("error", len(errors)),
        )

    if len(result_items) < 1:
        raise ContentError(f"Action `{action.name}` returned no items")

    return ActionResult(result_items)


def save_action_result(
    ws: FileStore,
    result: ActionResult,
    action_input: ActionInput,
    *,
    as_tmp: bool = False,
    no_format: bool = False,
) -> tuple[list[StorePath], list[StorePath]]:
    """
    Save the result of an action to the workspace. Handles skipping duplicates and
    archiving old inputs, if appropriate, based on hints in the ActionResult.
    """
    # If an action returned an external path, we should confirm it exists or it is probably
    # a bug in the action.
    for item in result.items:
        if item.external_path and not Path(item.external_path).exists():
            raise InvalidOutput(
                f"External path returned by action does not exist: {fmt_path(item.external_path)}"
            )

    input_items = action_input.items

    skipped_paths = []
    for item in result.items:
        if result.skip_duplicates:
            store_path = ws.find_by_id(item)
            if store_path:
                skipped_paths.append(store_path)
                continue

        ws.save(item, overwrite=result.overwrite, as_tmp=as_tmp, no_format=no_format)

    if skipped_paths:
        log.message(
            "Skipped saving %s items already saved:\n%s",
            len(skipped_paths),
            fmt_lines(skipped_paths),
        )

    unsaved_items = [item for item in input_items if not item.store_path]
    input_store_paths = [StorePath(item.store_path) for item in input_items if item.store_path]
    result_store_paths = [StorePath(item.store_path) for item in result.items if item.store_path]
    old_inputs = sorted(set(input_store_paths) - set(result_store_paths))
    if unsaved_items:
        log.info("unsaved_items:\n%s", fmt_lines(unsaved_items))
    log.info("result_store_paths:\n%s", fmt_lines(result_store_paths))
    if old_inputs:
        log.info("old_inputs:\n%s", fmt_lines(old_inputs))

    # If there is a hint that the action replaces the input, archive any inputs that are not in the result.
    archived_store_paths: list[StorePath] = []
    if result.replaces_input and input_items:
        for input_store_path in old_inputs:
            # Note some outputs may be missing if replace_input was used.
            ws.archive(input_store_path, missing_ok=True)
        log.message(
            "Archived old input items since action replaces input: %s",
            fmt_lines(old_inputs),
        )
        archived_store_paths.extend(old_inputs)

    return result_store_paths, archived_store_paths


@dataclass(frozen=True)
class ResultWithPaths:
    """
    Result of an action, including the store paths of any S3 items created.
    """

    result: ActionResult
    result_paths: list[StorePath]
    archived_paths: list[StorePath]
    s3_paths: list[Url]


def run_action_with_caching(
    exec_context: ExecContext, action_input: ActionInput
) -> ResultWithPaths:
    """
    Run an action, including validation, only rerunning if `rerun` requested or
    result is not already present. Returns the result, the store paths of the
    result items, and the store paths of any archived items.

    Also handles optional S3 syncing if the input was from S3.

    Note: Mutates the input but only to add `context` to each item.
    """
    action = exec_context.action
    settings = exec_context.settings
    ws = settings.workspace

    # If the input is from S3, we note the parent folder to copy the output back to.
    s3_parent_folder = None
    if exec_context.settings.sync_to_s3 and action_input.items and action_input.items[0].url:
        url = action_input.items[0].url
        if url and is_s3_url(url):
            s3_parent_folder = get_s3_parent_folder(url)

    # Assemble the operation and validate the action input.
    operation = validate_action_input(exec_context, ws, action, action_input)

    # Log what we're about to run.
    log_action(action, action_input, operation)

    # Consolidate all the context.
    context = ActionContext(
        exec_context=exec_context, operation=operation, action_input=action_input
    )

    try:
        # Hack to add the context to each item.
        # We do this before cache preassemble check.
        action_input.set_context(context)

        # Check if a previous run already produced the result.
        existing_result = check_for_existing_result(context)

        if existing_result and not settings.rerun:
            # Use the cached result.
            result = existing_result
            result_store_paths = [StorePath(not_none(item.store_path)) for item in result.items]
            archived_store_paths = []

            PrintHooks.before_done_message()
            log.message(
                "%s Skipped: `%s` completed with %s %s",
                EMOJI_SKIP,
                action.name,
                len(result.items),
                plural("item", len(result.items)),
            )
        else:
            # Run it!
            result = run_action_operation(context, action_input, operation)
            result_store_paths, archived_store_paths = save_action_result(
                ws,
                result,
                action_input,
                as_tmp=settings.tmp_output,
                no_format=settings.no_format,
            )

            PrintHooks.before_done_message()
            log.message(
                "%s Action: `%s` completed with %s %s",
                EMOJI_SUCCESS,
                action.name,
                len(result.items),
                plural("item", len(result.items)),
            )
    finally:
        action_input.clear_context()

    # If the action created an S3 item, we copy it back to the same S3 parent folder.
    # Only do this for the first result, for simplicity.
    s3_urls: list[Url] = []
    if s3_parent_folder and len(result_store_paths) > 0:
        log.warning(
            "Source was an S3 path so syncing result S3: %s -> %s",
            result_store_paths[0],
            s3_parent_folder,
        )
        s3_urls = s3_sync_to_folder(
            result_store_paths[0], s3_parent_folder, include_sidematter=True
        )
        log.message("Synced result to S3:\n%s", fmt_lines(s3_urls))

    return ResultWithPaths(
        result=result,
        result_paths=result_store_paths,
        archived_paths=archived_store_paths,
        s3_paths=s3_urls,
    )


def run_action_with_shell_context(
    action_spec: str | type[Action],
    explicit_param_values: RawParamValues,
    *provided_args: str,
    rerun: bool = False,
    refetch: bool = False,
    override_state: State | None = None,
    tmp_output: bool = False,
    no_format: bool = False,
    internal_call: bool = False,
) -> ActionResult:
    """
    Main function to run an action from the shell. Wraps `run_action_if_needed` to
    handle assembling parameters and arguments from the provided (unparsed)
    parameters and arguments. Handles selection and shell handling of the result.
    Uses the current workspace.
    """
    from kash.exec.action_registry import look_up_action_class

    if isinstance(action_spec, str):
        action_cls = look_up_action_class(action_spec)
    else:
        action_cls = action_spec

    # Context for shell calls is the current workspace.
    ws = current_ws()

    # Get the current workspace params.
    ws_params = ws.params.get_raw_values()

    # Have to instantiate the action to be sure we get the final declared params.
    declared_params = {p.name: p for p in action_cls.create(None).params}
    explicit_parsed = explicit_param_values.parse_all({**ALL_COMMON_PARAMS, **declared_params})

    ws_parsed = ws_params.parse_all(GLOBAL_PARAMS)

    # Create the action with all explicit parameters in place.
    action = action_cls.create(explicit_parsed, ws_parsed)
    action_name = action.name

    # Execution context. This is fixed for the duration of the action.
    settings = RuntimeSettings(
        workspace_dir=ws.base_dir,
        rerun=rerun,
        refetch=refetch,
        override_state=override_state,
        tmp_output=tmp_output,
        no_format=no_format,
    )
    context = ExecContext(action, settings)

    # Collect args from the provided args or otherwise the current selection.
    args, from_selection = assemble_action_args(*provided_args, use_selection=action.uses_selection)

    # As a special case for convenience, if the action expects no args, ignore any pre-selected inputs.
    if action.expected_args == NO_ARGS and from_selection:
        log.message(
            "Not using current selection since action `%s` expects no args.",
            action_name,
        )
        args.clear()

    if args:
        source_str = "provided args" if provided_args else "selection"
        log.message(
            "Using %s as inputs to action `%s`:\n%s",
            source_str,
            action_name,
            fmt_lines(args),
        )

    # Get items for each input arg.
    input = prepare_action_input(*args, refetch=refetch)

    # Finally, run the action.
    result_with_paths = run_action_with_caching(context, input)
    result = result_with_paths.result
    result_store_paths = result_with_paths.result_paths
    archived_store_paths = result_with_paths.archived_paths

    # Implement any path operations from the output and/or select the final output
    if not internal_call:
        if result.path_ops:
            path_ops = [
                path_op
                for path_op in result.path_ops
                if path_op.store_path not in archived_store_paths
            ]

            path_op_archive = [
                path_op.store_path for path_op in path_ops if path_op.op == PathOpType.archive
            ]
            if path_op_archive:
                log.message("Archiving %s items based on action result.", len(path_op_archive))
                for store_path in path_op_archive:
                    ws.archive(store_path, missing_ok=True)

            path_op_selection = [
                path_op.store_path for path_op in path_ops if path_op.op == PathOpType.select
            ]
            if path_op_selection:
                log.message("Selecting %s items based on action result.", len(path_op_selection))
                ws.selections.push(Selection(paths=path_op_selection))
        else:
            # Otherwise if no path_ops returned, default behavior is to select the final
            # outputs (omitting any that were archived).
            final_outputs = sorted(set(result_store_paths) - set(archived_store_paths))
            log.info("final_outputs:\n%s", fmt_lines(final_outputs))
            ws.selections.push(Selection(paths=final_outputs))

    return result
