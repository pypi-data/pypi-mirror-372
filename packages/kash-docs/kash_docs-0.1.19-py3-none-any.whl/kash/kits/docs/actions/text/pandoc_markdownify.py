from strif import temp_output_file

from kash.exec import kash_action
from kash.exec.preconditions import is_doc_resource
from kash.model import Format, Item, ItemType
from kash.utils.errors import InvalidInput
from kash.workspaces.workspaces import current_ws


@kash_action(precondition=is_doc_resource)
def pandoc_markdownify(item: Item) -> Item:
    """
    Convert docs to markdown using Pandoc.
    """
    # Soft dep since we're not using pandoc currently.
    try:
        import pypandoc  # pyright: ignore[reportMissingImports]
    except ImportError:
        raise ImportError(
            "This action requires pandoc to be installed! Add pypandoc-binary>=1.15 to project deps."
        )

    if not item.store_path:
        raise InvalidInput(f"Missing store path for item: {item}")

    ws = current_ws()
    doc_path = ws.base_dir / item.store_path
    with temp_output_file("pandoc_output", suffix=".md") as (_fd, tmp_path):
        pypandoc.convert_file(doc_path, to="markdown", outputfile=tmp_path)
        markdown_content = tmp_path.read_text()
    output_item = item.derived_copy(
        type=ItemType.doc, format=Format.markdown, body=markdown_content
    )

    return output_item
