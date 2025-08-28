from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec_model.args_model import ONE_OR_MORE_ARGS
from kash.model import ActionInput, ActionResult, Param
from kash.utils.errors import InvalidInput
from kash.web_gen import tabbed_webpage

log = get_logger(__name__)


@kash_action(
    expected_args=ONE_OR_MORE_ARGS,
    params=(
        Param(
            name="clean_headings",
            type=bool,
            description="Use an LLM to clean up headings.",
        ),
    ),
)
def tabbed_webpage_config(input: ActionInput, clean_headings: bool = False) -> ActionResult:
    """
    Set up a web page config with optional tabs for each page of content. Uses first item as the page title.
    """
    for item in input.items:
        if not item.body:
            raise InvalidInput(f"Item must have a body: {item}")

    config_item = tabbed_webpage.tabbed_webpage_config(input.items, clean_headings)

    return ActionResult([config_item])
