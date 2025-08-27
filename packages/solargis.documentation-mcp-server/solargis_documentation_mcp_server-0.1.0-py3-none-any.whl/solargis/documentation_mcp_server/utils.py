import markdownify


def to_markdown(html: str) -> str:
    try:
        content = markdownify.markdownify(
            html=html,
            heading_style=markdownify.ATX,
            autolinks=True,
            default_title=True,
            escape_asterisks=True,
            escape_underscores=True,
            newline_style=markdownify.SPACES,
        )

        if not content:
            return "<e>Page failed to be simplified from HTML</e>"

        return content
    except Exception as e:
        return f"<e>Error converting HTML to Markdown: {str(e)}</e>"


def paginate_documentation_result(
    url: str,
    content: str,
    start_index: int,
    max_length: int,
) -> str:
    """Paginate documentation result with pagination information.

    Args:
        url: Documentation URL
        content: Content to paginate
        start_index: Start index for pagination
        max_length: Maximum content length

    Returns:
        Paginated documentation result
    """
    original_length = len(content)

    if start_index >= original_length:
        return f"Solargis documentation from {url}:\n\n<e>No more content available.</e>"

    end_index = min(start_index + max_length, original_length)
    truncated_content = content[start_index:end_index]

    if not truncated_content:
        return f"Solargis documentation from {url}:\n\n<e>No more content available.</e>"

    actual_content_length = len(truncated_content)
    remaining_content = original_length - (start_index + actual_content_length)

    result = f"Solargis documentation from {url}:\n\n{truncated_content}"

    if remaining_content > 0:
        next_start = start_index + actual_content_length
        result = f"{result}\n\n<e>Content truncated. Call the read_documentation tool with start_index={next_start} to get more content.</e>"

    return result
