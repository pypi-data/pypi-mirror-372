from dataclasses import replace
from typing import Unpack

from chopdiff.docs import DiffFilter, TextDoc
from chopdiff.transforms import WindowSettings, filtered_transform
from clideps.env_vars.dotenv_utils import load_dotenv_paths
from flowmark import fill_markdown

from kash.config.logger import get_logger
from kash.config.settings import global_settings
from kash.llm_utils import LLMName
from kash.llm_utils.fuzzy_parsing import strip_markdown_fence
from kash.llm_utils.llm_completion import llm_template_completion
from kash.llm_utils.llm_messages import Message, MessageTemplate
from kash.model.actions_model import LLMOptions
from kash.model.items_model import Item, ItemType, ItemUpdateOptions
from kash.utils.errors import InvalidInput
from kash.utils.file_utils.file_formats_model import Format
from kash.utils.text_handling.doc_normalization import normalize_formatting

log = get_logger(__name__)


def windowed_llm_transform(
    model: LLMName,
    system_message: Message,
    template: MessageTemplate,
    input: str,
    windowing: WindowSettings | None,
    diff_filter: DiffFilter | None = None,
    check_no_results: bool = True,
) -> TextDoc:
    def doc_transform(input_doc: TextDoc) -> TextDoc:
        return TextDoc.from_text(
            # XXX We normalize the Markdown before parsing as a text doc in particular because we
            # want bulleted list items to be separate paragraphs.
            fill_markdown(
                llm_template_completion(
                    model,
                    system_message=system_message,
                    input=input_doc.reassemble(),
                    body_template=template,
                    check_no_results=check_no_results,
                ).content
            )
        )

    result_doc = filtered_transform(TextDoc.from_text(input), doc_transform, windowing, diff_filter)
    return result_doc


def llm_transform_str(options: LLMOptions, input_str: str, check_no_results: bool = True) -> str:
    load_dotenv_paths(True, True, global_settings().system_config_dir)

    if options.windowing and options.windowing.size:
        log.message(
            "Running LLM `%s` sliding transform for %s: %s",
            options.model,
            options.op_name,
            options.windowing,
        )

        result_str = windowed_llm_transform(
            options.model,
            options.system_message,
            options.body_template,
            input_str,
            options.windowing,
            diff_filter=options.diff_filter,
        ).reassemble()
    else:
        log.info(
            "Running simple LLM transform action %s with model %s",
            options.op_name,
            options.model.litellm_name,
        )

        result_str = llm_template_completion(
            options.model,
            system_message=options.system_message,
            body_template=options.body_template,
            input=input_str,
            check_no_results=check_no_results,
        ).content

    return result_str


def llm_transform_item(
    item: Item,
    model: LLMName | None = None,
    *,
    normalize: bool = True,
    strip_fence: bool = True,
    check_no_results: bool = True,
    **updates: Unpack[ItemUpdateOptions],
) -> Item:
    """
    Main function for running an LLM action on an item.
    Requires the action context on the item to specify all the LLM options.
    Model may be overridden by an explicit model parameter.
    Also by default cleans up and normalizes output as Markdown.
    """
    # Default to Markdown docs.
    if "format" not in updates:
        updates["format"] = Format.markdown
    if "type" not in updates:
        updates["type"] = ItemType.doc
    if "body" not in updates:
        updates["body"] = None

    if not item.context:
        raise InvalidInput(f"LLM actions expect a context on input item: {item}")
    action = item.context.action
    if not item.body:
        raise InvalidInput(f"LLM actions expect a body: {action.name} on {item}")

    llm_options = action.llm_options
    if model:
        llm_options = replace(llm_options, model=model)

    log.message("LLM transform from action `%s` on item: %s", action.name, item)
    log.message("LLM options: %s", action.llm_options)

    result_item = item.derived_copy(**updates)
    result_str = llm_transform_str(llm_options, item.body, check_no_results=check_no_results)
    if strip_fence:
        result_str = strip_markdown_fence(result_str)
    if normalize:
        result_str = normalize_formatting(result_str, format=updates["format"])

    result_item.body = result_str
    return result_item
