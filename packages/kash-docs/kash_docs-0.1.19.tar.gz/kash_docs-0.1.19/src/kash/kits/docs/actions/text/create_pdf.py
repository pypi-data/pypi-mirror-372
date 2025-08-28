from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_html_compatible_body
from kash.kits.docs.doc_formats.pdf_output import html_to_pdf
from kash.model import FileExt, Format, Item, ItemType, Param
from kash.utils.common.format_utils import fmt_loc
from kash.utils.errors import InvalidInput
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_action(
    precondition=has_html_compatible_body,
    params=(Param("save_html", "Also save the HTML for generating the PDF.", type=bool),),
    mcp_tool=True,
)
def create_pdf(item: Item, save_html: bool = False) -> Item:
    """
    Create a PDF from text or Markdown.
    """
    if not item.body:
        raise InvalidInput(f"Item must have a body: {item}")

    pdf_item = item.derived_copy(type=ItemType.export, format=Format.pdf, file_ext=FileExt.pdf)
    target_pdf_path = current_ws().assign_store_path(pdf_item)
    log.message("Will save PDF to: %s", fmt_loc(target_pdf_path))

    ws = current_ws()
    if save_html:
        html_item = item.derived_copy(
            type=ItemType.export, format=Format.html, file_ext=FileExt.html
        )
        target_html_path = ws.assign_store_path(html_item)
        log.message("Will save HTML to: %s", fmt_loc(target_html_path))
    else:
        target_html_path = None

    html = item.body_as_html()

    # Add directly to the store and indicate that we've saved it.
    html_to_pdf(html, target_pdf_path, title=item.title, html_out_path=target_html_path)
    pdf_item.mark_as_saved(target_pdf_path)

    return pdf_item
