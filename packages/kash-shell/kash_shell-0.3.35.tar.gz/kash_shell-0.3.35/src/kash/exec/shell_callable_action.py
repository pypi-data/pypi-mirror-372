from funlog import log_tallies

from kash.config.env_settings import KashEnv
from kash.config.logger import get_logger
from kash.config.text_styles import COLOR_ERROR
from kash.config.unified_live import get_unified_live
from kash.exec.action_exec import run_action_with_shell_context
from kash.exec.history import record_command
from kash.exec_model.commands_model import Command
from kash.exec_model.shell_model import ShellResult
from kash.help.help_printing import print_action_help
from kash.model.actions_model import Action
from kash.model.params_model import RawParamValues
from kash.shell.output.shell_output import PrintHooks
from kash.shell.utils.exception_printing import summarize_traceback
from kash.utils.common.parse_shell_args import parse_shell_args
from kash.utils.errors import get_nonfatal_exceptions

log = get_logger(__name__)


class ShellCallableAction:
    """
    Wraps an Action for use in the shell, adding shell-specific options,
    parsing shell args, and adding console logging.
    """

    def __init__(self, action_cls: type[Action]):
        self.action_cls = action_cls
        self.__name__ = action_cls.name
        self.__doc__ = action_cls.description

    def __call__(self, args: list[str]) -> ShellResult | None:
        from kash.commands.help import help_commands

        log.debug("ShellCallableAction: %s: %s", self.action_cls.name, args)

        try:
            action_cls = self.action_cls
            PrintHooks.before_shell_action_run()

            shell_args = parse_shell_args(args)

            # We will instantiate the action later but we create an unconfigured
            # instance for help/info.
            action = action_cls.create(None)
            if shell_args.show_help:
                print_action_help(action, verbose=True)
                return ShellResult()
            elif shell_args.options.get("show_source", False):
                return help_commands.source_code(action_cls.name)

            # Handle --rerun and --refetch options at action invocation time.
            rerun = bool(shell_args.options.get("rerun", False))
            refetch = bool(shell_args.options.get("refetch", False))
            no_format = bool(shell_args.options.get("no_format", False))

            log.info("Action shell args: %s", shell_args)
            explicit_values = RawParamValues(shell_args.options)
            if not action.interactive_input and not action.live_output:
                with get_unified_live().status(f"Running action {action.name}…"):
                    result = run_action_with_shell_context(
                        action_cls,
                        explicit_values,
                        *shell_args.args,
                        rerun=rerun,
                        refetch=refetch,
                        no_format=no_format,
                    )
            else:
                result = run_action_with_shell_context(
                    action_cls, explicit_values, *shell_args.args, rerun=rerun, refetch=refetch
                )
            # We don't return the result to keep the xonsh shell output clean.
        except get_nonfatal_exceptions() as e:
            PrintHooks.nonfatal_exception()
            log.error(f"[{COLOR_ERROR}]Action error:[/{COLOR_ERROR}] %s", summarize_traceback(e))
            log.info("Action error details: %s", e, exc_info=True)
            return ShellResult(exception=e)
        except Exception as e:
            # Log here while we are in the true call stack (not inside the xonsh call stack).
            log.error(
                "Action error: %s", e, exc_info=KashEnv.KASH_SHOW_TRACEBACK.read_bool(default=True)
            )
            raise
        finally:
            log_tallies(level="warning", if_slower_than=10.0)
            # output_separator()

        # The handling of the output can be overridden by the action, but by default just show
        # the selection and suggested actions.
        if result.shell_result:
            shell_result = result.shell_result
        else:
            shell_result = ShellResult(
                show_selection=True,
                suggest_actions=True,
            )

        record_command(Command.assemble(action, args))

        PrintHooks.after_shell_action_run()

        return shell_result

    def __repr__(self):
        return f"ShellCallableAction({self.action_cls.name})"
