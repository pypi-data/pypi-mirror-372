from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import Field as DataclassField
from dataclasses import field, replace
from enum import Enum
from textwrap import dedent
from typing import Any, TypeVar, cast

from chopdiff.docs import DiffFilter
from chopdiff.transforms import WINDOW_NONE, WindowSettings
from flowmark import fill_text
from prettyfmt import abbrev_obj, fmt_lines
from pydantic.dataclasses import dataclass, rebuild_dataclass
from pydantic.json_schema import JsonSchemaValue
from strif import StringTemplate
from typing_extensions import override

from kash.config.logger import get_logger
from kash.exec_model.args_model import NO_ARGS, ONE_ARG, ArgCount, ArgType, Signature
from kash.exec_model.shell_model import ShellResult
from kash.llm_utils import LLM, LLMName
from kash.llm_utils.llm_messages import Message, MessageTemplate
from kash.model.exec_model import ActionContext, ExecContext
from kash.model.items_model import UNTITLED, Format, Item, ItemType
from kash.model.params_model import (
    ALL_COMMON_PARAMS,
    COMMON_SHELL_PARAMS,
    RUNTIME_ACTION_PARAMS,
    Param,
    ParamDeclarations,
    TypedParamValues,
)
from kash.model.paths_model import StorePath
from kash.model.preconditions_model import Precondition
from kash.utils.common.parse_key_vals import format_key_value
from kash.utils.common.type_utils import not_none
from kash.utils.errors import InvalidDefinition, InvalidInput

log = get_logger(__name__)


class TitleTemplate(StringTemplate):
    """A template for a title."""

    def __init__(self, template: str):
        super().__init__(template.strip(), allowed_fields=["title", "action_name"])


@dataclass(frozen=True)
class ActionInput:
    """
    Input to an action.
    """

    items: list[Item]

    @staticmethod
    def empty() -> ActionInput:
        """An empty input, for when an action processes no items."""
        return ActionInput(items=[])

    # XXX For convenience, we have the ability to include the context on each item
    # (this helps soper-item functions don't have to take context args everywhere).
    # TODO: Probably better to move this to a context var.
    def set_context(self, context: ActionContext) -> None:
        for item in self.items:
            item.context = context

    def clear_context(self) -> None:
        for item in self.items:
            item.context = None


class PathOpType(Enum):
    archive = "archive"
    select = "select"


@dataclass(frozen=True)
class PathOp:
    """
    An operation on a path.
    """

    store_path: StorePath
    op: PathOpType


@dataclass
class ActionResult:
    """
    Results from an action, including all items it produced as well as some hints
    about how to handle the result items.
    """

    items: list[Item]
    """Results from this action. Most often, just a single item."""

    replaces_input: bool = False
    """If True, a hint to archive the input items."""

    overwrite: bool = False
    """If True, will not pick unique output paths to save to, overwriting existing files of the same name."""

    skip_duplicates: bool = False
    """If True, do not save duplicate items (based on identity)."""

    path_ops: list[PathOp] | None = None
    """If specified, operations to perform on specific paths, such as selecting items."""

    shell_result: ShellResult | None = None
    """Customize control of how the action's result is displayed in the shell."""

    def get_by_format(self, *formats: Format) -> Item:
        """Convenience method to get an item for actions that return multiple formats."""
        return next(item for item in self.items if item.format in formats)

    def has_hints(self) -> bool:
        return bool(
            self.replaces_input or self.skip_duplicates or self.path_ops or self.shell_result
        )

    def set_context(self, context: ActionContext) -> None:
        for item in self.items:
            item.context = context

    def clear_context(self):
        for item in self.items:
            item.context = None

    def __repr__(self):
        return abbrev_obj(self, field_max_len=80)


T = TypeVar("T")


class ParamSource(Enum):
    """
    Parameter values can be explicitly set at call time, filled in by a function
    default (for actions defined as decorated functions), filled in from the workspace,
    or filled in with a global default.
    """

    explicit = "explicit"
    function_default = "function_default"
    workspace = "workspace"
    global_default = "global_default"

    @property
    def is_explicit(self) -> bool:
        return self in (ParamSource.explicit, ParamSource.function_default)


LLM_OPTION_PARAMS = ["model", "system_message", "body_template"]
"""
These action parameters are mirrored into the LLM options.
"""


@dataclass(frozen=True)
class LLMOptions:
    """
    Options for an LLM request or transformation.
    """

    op_name: str | None = None
    model: LLMName = LLM.default_standard
    system_message: Message = Message("")
    body_template: MessageTemplate = MessageTemplate("{body}")
    windowing: WindowSettings = WINDOW_NONE
    diff_filter: DiffFilter | None = None

    def updated_with(self, param_name: str, value: Any) -> LLMOptions:
        """Update option from an action parameter."""
        if param_name in LLM_OPTION_PARAMS:
            assert hasattr(self, param_name)
            return replace(self, **{param_name: value})
        return self

    def __repr__(self):
        return abbrev_obj(self, field_max_len=80)


@dataclass
class Action(ABC):
    """
    The base class for Actions, which are arbitrary operations that can be performed
    on `Items`.

    At the basic level, an `Action` simply represents an operation that takes zero or
    `Items` and produces output `Items`. The `Action` holds other hints and settings
    that make it useful directly in code or as a shell or UI-invocable operation.
    Usually, you want to create and register an `Action` via the `@kash_action`
    decorator on a Python function.

    In addition to inputs, an action has parameters and default values already built
    in. These are defined at the class level but actions are instantiated with final
    values filled in before being run.

    Use `cls.create()` to instantiate an action. This allows parameters to be further
    overridden safely with overrides (e.g. from a function or command line parameter or
    a workspace setting). Basic info like docstrings and `name` are available on the
    class, but to get full info on an action you need to look at the `Action` instance.

    Note action parameter values can be set in several places. Statically, they may be
    set as defaults at the class level (since an `Action` is a dataclass) or as formal
    parameters to a decorated function that gets converted into an `Action` class.
    At runtime, they can be overridden via explicit values (to the function or as an
    option on the command line, for example) or workspace settings.
    These are filled in by creating an `Action` instance via `cls.create()`.
    """

    name: str = ""
    """
    The name of the action. Should be in lower_snake_case.
    """

    description: str = ""
    """
    A description of the action, in a few sentences.
    """

    cacheable: bool = True
    """
    If True, the action execution may be skipped if the output is already present.
    """

    precondition: Precondition = Precondition.always
    """
    A precondition that must apply to all inputs to this action. Helps select whether
    an action is applicable to an item.
    """

    arg_type: ArgType = ArgType.Locator
    """
    The type of the arguments.
    """

    expected_args: ArgCount = ONE_ARG
    """
    The expected number of arguments. When an action is run per-item, this should
    be ONE_ARG.
    """

    output_type: ItemType | None = None
    """
    The type of the output item(s). If an action returns multiple output types,
    this will be the output type of the first output.
    This is mainly used for preassembly for the cache check if an output already exists.
    None means to use the input type.
    """

    output_format: Format | None = None
    """
    The format of the output item(s). The default is to assume it is the same
    format as the input. If an action returns multiple output formats,
    this will be the format of the first output.
    This is mainly used for preassembly for the cache check if an output already exists.
    """

    expected_outputs: ArgCount = ONE_ARG
    """
    The number of outputs expected from this action.
    """

    params: ParamDeclarations = ()
    """
    Declared parameters relevant to this action, which are settable when the action is invoked.
    These can be new parameters defined in a subclass, or more commonly, an existing
    common parameter (like `model` or `query`) that is shared by several actions.
    """

    param_source: dict[str, ParamSource] = field(default_factory=dict)
    """
    For each parameter, the source of its value. The actual value is a field.
    Useful for logs/debugging.
    """

    run_per_item: bool = False
    """
    Normally, an action runs on all input items at once. If True, run the action separately
    for each input item, each time on a single item.
    """

    uses_selection: bool = True
    """
    The normal behavior is that an action can be run without arguments and it will
    fall back to the current selection for its input arguments.
    """

    interactive_input: bool = False
    """
    Does this action ask for input interactively?
    """

    live_output: bool = False
    """
    Does this action have live output (e.g., progress bars, spinners)?
    If True, the shell should not show its own status spinner.
    """

    mcp_tool: bool = False
    """
    If True, this action is published as an MCP tool.
    """

    title_template: TitleTemplate = TitleTemplate("{title}")
    """
    A template for the title of the output item, based on its primary input.
    """

    llm_options: LLMOptions = field(default_factory=LLMOptions)
    """
    Options for LLM operations.
    """

    @classmethod
    def create(
        cls: type[Action],
        explicit_param_values: TypedParamValues | None,
        ctx_param_values: TypedParamValues | None = None,
    ):
        """
        Instantiate the action for use, optionally with overridden parameters.
        Explicit parameters are set and must apply to the action.
        Contextual parameters are filled in if they match and a parameter hasn't
        already been set.
        """
        instance = cls()
        if explicit_param_values:
            instance._update_param_values(
                explicit_param_values, ParamSource.explicit, strict=True, overwrite=True
            )
        if ctx_param_values:
            instance._update_param_values(
                ctx_param_values, ParamSource.workspace, strict=False, overwrite=False
            )
        return instance

    def __post_init__(self):
        self.description = fill_text(dedent(self.description).strip())
        # Enforce obvious consistency on arg constraints so these args can be omitted.
        if self.run_per_item:
            self.expected_args = ONE_ARG
        # If the action has no inputs, it must ignore the selection.
        if self.expected_args == NO_ARGS:
            self.uses_selection = False

        self.validate_sanity()

    def validate_sanity(self):
        """
        Declaration sanity checks.
        """
        if not self.name:
            raise InvalidDefinition("Action must have a name")

        for param in self.params:
            if not self.has_param(param.name):
                raise InvalidDefinition(
                    f"Action `{self.name}` has parameter `{param.name}` declared in `params` but no corresponding field defined"
                )

    def validate_params_present(self):
        """
        Runtime validation for parameters.
        """
        for param in self.params:
            if param.is_explicit and not not_none(self.param_source.get(param.name)).is_explicit:
                raise InvalidInput(
                    f"Action `{self.name}` requires explicit parameter `{param.name}` but it was not provided"
                )

    def validate_args(self, nargs: int) -> None:
        """
        Runtime validation for arguments.
        """
        self.validate_sanity()

        if self.run_per_item:
            if nargs < 1:
                log.warning("Running action `%s` for each input but got no inputs", self.name)
            return

        if nargs != 0 and self.expected_args == NO_ARGS:
            raise InvalidInput(f"Action `{self.name}` does not expect any arguments")
        if nargs != 1 and self.expected_args == ONE_ARG:
            raise InvalidInput(f"Action `{self.name}` expects exactly one argument")
        if self.expected_args.max_args is not None and nargs > self.expected_args.max_args:
            raise InvalidInput(
                f"Action `{self.name}` expects at most {self.expected_args.max_args} arguments"
            )
        if self.expected_args.min_args is not None and nargs < self.expected_args.min_args:
            raise InvalidInput(
                f"Action `{self.name}` expects at least {self.expected_args.min_args} arguments"
            )

    def validate_precondition(self, input: ActionInput) -> None:
        if self.precondition:
            for item in input.items:
                self.precondition.check(item, f"action `{self.name}`")

    def signature(self) -> Signature:
        return Signature(self.arg_type, self.expected_args)

    # It seems useful to keep parameters as fields on the action instance itself,
    # instead of encapsulated, in case we want to declare them in explicit dataclass
    # fields in subclasses of Action.

    def has_param(self, param_name: str) -> bool:
        return hasattr(self, param_name)

    def get_param(self, param_name: str) -> Any:
        return getattr(self, param_name)

    def set_param(self, param_name: str, value: Any, source: ParamSource) -> None:
        setattr(self, param_name, value)
        self.param_source[param_name] = source
        # Update corresponding LLM option if appropriate.
        self.llm_options = self.llm_options.updated_with(param_name, value)

    @property
    def shell_params(self) -> list[Param]:
        """
        List of parameters that are relevant to shell usage.
        """
        return (
            list(self.params)
            + list(RUNTIME_ACTION_PARAMS.values())
            + list(COMMON_SHELL_PARAMS.values())
        )

    def param_value_summary(self) -> dict[str, str]:
        """
        Readable, serializable summary of the action's non-default parameters, to include in
        logs or metadata.
        """

        def stringify(value: Any) -> str:
            if isinstance(value, Enum):
                return value.name
            return str(value)

        changed_params: dict[str, Any] = {}
        for param in self.params:
            if self.has_param(param.name):
                value = self.get_param(param.name)
                if value:
                    changed_params[param.name] = stringify(value)
        return changed_params

    def param_value_summary_str(self) -> str:
        return ", ".join(
            [format_key_value(name, value) for name, value in self.param_value_summary().items()]
        )

    def _field_info(self, param_name: str) -> DataclassField | None:
        return next(
            (f for f in self.__dataclass_fields__.values() if f.name == param_name),
            None,
        )

    def _update_param_values(
        self,
        new_values: TypedParamValues,
        param_source: ParamSource,
        strict: bool,
        overwrite: bool,
    ) -> None:
        """
        Update the action with the additional parameter values.

        If `strict` is True, raise an error for unknown parameters, which we want to refuse
        for params set on the command line, but tolerate for params from workspace etc.

        Unless `overwrite` is True, do not overwrite existing parameter values.
        """
        action_param_names = [param.name for param in self.params]

        overrides: list[str] = []
        for param_name, value in new_values.values.items():
            # Sanity checks.
            if param_name not in ALL_COMMON_PARAMS and param_name not in action_param_names:
                if strict:
                    raise InvalidInput(
                        f"Unknown override param for action `{self.name}`: {param_name}"
                    )
                else:
                    log.warning(
                        "Ignoring inapplicable override param for action `%s`: %s",
                        self.name,
                        param_name,
                    )
                    continue

            # Look up the param info.
            param = next((p for p in self.params if p.name == param_name), None)

            # Set the field value on this action if the param applies to this action.
            if param:
                # Sanity check that the field type matches the param type.
                field_info = self._field_info(param_name)
                if field_info and not issubclass(cast(type, field_info.type), param.type):
                    log.warning(
                        "Parameter `%s` has field type %s in action `%s` but expected type %s",
                        param_name,
                        field_info.type,
                        self.name,
                        param.type,
                    )

                if not self.has_param(param_name) or overwrite:
                    self.set_param(param_name, value, param_source)
                    overrides.append(format_key_value(param_name, value))
                else:
                    log.info(
                        "Not overwriting existing parameter: keeping %s instead of %s",
                        format_key_value(param_name, self.get_param(param_name)),
                        format_key_value(param_name, value),
                    )
            else:
                log.info("Ignoring parameter for action `%s`: `%s`", self.name, param_name)

        if overrides:
            log.info(
                "Overriding parameters for action `%s`:\n%s",
                self.name,
                fmt_lines(overrides),
            )

    def format_title(self, prev_title: str | None) -> str:
        """
        Format the title for an output item of this action.
        """
        prev_title = prev_title or UNTITLED
        if self.title_template:
            return self.title_template.format(title=prev_title, action_name=self.name)
        else:
            return prev_title

    def preassemble_result(self, context: ActionContext) -> ActionResult | None:
        """
        Actions can have a separate preliminary step to pre-assemble outputs. This allows
        us to determine the title and types for the output items and check if they were
        already generated before running slow or expensive actions.

        For now, this only applies to actions with a single output, when `self.cacheable`
        is True.
        """
        can_preassemble = self.cacheable and self.expected_outputs == ONE_ARG
        log.info(
            "Preassemble check for `%s`: can_preassemble=%s (expected_outputs=%s, cacheable=%s)",
            self.name,
            can_preassemble,
            self.expected_outputs,
            self.cacheable,
        )
        if can_preassemble:
            # Using first input to determine the output title.
            primary_input = context.action_input.items[0]
            # In this case we only expect one output, of the type specified by the action.
            output_type = context.action.output_type or primary_input.type
            if not output_type:
                log.warning(
                    "No output type specified for action `%s`, using `doc` for preassembly",
                    self.name,
                )
                output_type = ItemType.doc
            primary_output = primary_input.derived_copy(context, 0, type=output_type)
            log.info("Preassembled output: source %s, %s", primary_output.source, primary_output)
            return ActionResult([primary_output])
        else:
            # Caching disabled.
            return None

    def tool_json_schema(self) -> JsonSchemaValue:
        """
        Generate a JSON schema for this action in MCP tool schema format.
        """
        # Create the base schema
        input_schema: JsonSchemaValue = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        # Add input items schema with constraints from ArgCount.
        # TODO: Perhaps better to simplify the schema and remove the array for exactly one arg?
        if self.expected_args != NO_ARGS:
            items_schema: JsonSchemaValue = {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "A URL or S3 URL or a workspace file path, e.g. https://example.com/some/file/path or s3://somebucket/some/file/path or some/file/path",
                },
                "description": f"A list of paths or URLs of input items ({self.expected_args.as_str()}). Use an array of length one for a single input.",
            }

            # Set min/max items.
            if self.expected_args.min_args is not None:
                items_schema["minItems"] = self.expected_args.min_args
            if self.expected_args.max_args is not None:
                items_schema["maxItems"] = self.expected_args.max_args

            input_schema["properties"]["items"] = items_schema
            if self.expected_args.min_args and self.expected_args.min_args > 0:
                input_schema["required"].append("items")

        # Add parameters schema.
        for param in self.params:
            param_schema = param.json_schema()
            input_schema["properties"][param.name] = param_schema
            # Only explicit parameters are required in the tool schema.
            if param.is_explicit:
                input_schema["required"].append(param.name)

        return input_schema

    @abstractmethod
    def run(self, input: ActionInput, context: ActionContext) -> ActionResult:
        pass

    def __repr__(self):
        return abbrev_obj(self)


@dataclass
class PerItemAction(Action, ABC):
    """
    Abstract base class for an action that processes one input item and returns
    one output item.

    Note that this action can be invoked on many input items, but the run method
    itself must expect exactly one input item and the executor will run it for each
    input.
    """

    expected_args: ArgCount = ONE_ARG

    run_per_item: bool = True

    def __post_init__(self):
        super().__post_init__()

    @override
    def run(self, input: ActionInput, context: ActionContext) -> ActionResult:
        log.info("Running action `%s` per-item.", self.name)
        for item in input.items:
            item.context = context
        return ActionResult(items=[self.run_item(input.items[0])])

    @abstractmethod
    def run_item(self, item: Item) -> Item:
        """
        Override with item processing.
        """


# Handle circular dependency in Python dataclasses.
rebuild_dataclass(Item)  # pyright: ignore
rebuild_dataclass(ExecContext)  # pyright: ignore
rebuild_dataclass(ActionContext)  # pyright: ignore
