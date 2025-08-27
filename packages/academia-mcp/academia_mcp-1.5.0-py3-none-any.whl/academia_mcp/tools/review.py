import base64
from io import BytesIO
from pathlib import Path

from academia_mcp.pdf import parse_pdf_file_to_images
from academia_mcp.llm import llm_acall, ChatMessage
from academia_mcp.files import get_workspace_dir


PROMPT = """
Find problems with the paper formatiing.
"""


async def review_pdf(pdf_filename: str) -> str:
    """
    Review a pdf file.

    Args:
        pdf_path: The path to the pdf file.
    """
    pdf_filename_path = Path(pdf_filename)
    if not pdf_filename_path.exists():
        pdf_filename_path = Path(get_workspace_dir()) / pdf_filename

    images = parse_pdf_file_to_images(pdf_filename_path)
    content_parts = []
    for image in images:
        buffer_io = BytesIO()
        image.save(buffer_io, format="PNG")
        img_bytes = buffer_io.getvalue()
        image_base64 = base64.b64encode(img_bytes).decode("utf-8")
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"},
        }
        content_parts.append(image_content)

    content_parts.append(
        {
            "type": "text",
            "text": "Please review the paper and provide a summary of its content.",
        }
    )
    llm_response = await llm_acall(
        model_name="gpt-4o",
        messages=[
            ChatMessage(role="user", content=content_parts),
        ],
    )
    return llm_response.strip()
