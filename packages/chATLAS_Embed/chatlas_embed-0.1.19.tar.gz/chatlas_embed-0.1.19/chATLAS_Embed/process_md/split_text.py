import re


def split_text_recursive(text: str, max_length: int, min_length: int = 200) -> list[str]:
    """
    Recursively split text into chunks with a cleaner approach.

    Strategy:
    1. Split by markdown sections (headers starting with #) if chunk is too long
    2. Split by paragraphs (double newlines) if chunk is still too long
    3. Split by newlines if chunk is still too long
    4. Split by sentences if chunk is still too long
    5. Recombine small chunks at the end

    Args:
        text: The text to split
        max_length: Maximum allowed length for a chunk
        min_length: Minimum preferred length for chunks (used in recombining)

    Returns:
        List of text chunks optimally sized
    """
    if len(text) <= max_length:
        return [text]

    # Try splitting by markdown sections first
    chunks = _split_by_markdown_sections(text, max_length)

    # If any chunks are still too long, split by paragraphs (double newlines)
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            final_chunks.append(chunk)
        else:
            paragraph_chunks = _split_by_separator(chunk, "\n\n", max_length)

            # If still too long, split by newlines
            for paragraph_chunk in paragraph_chunks:
                if len(paragraph_chunk) <= max_length:
                    final_chunks.append(paragraph_chunk)
                else:
                    newline_chunks = _split_by_separator(paragraph_chunk, "\n", max_length)

                    # If still too long, split by sentences
                    for newline_chunk in newline_chunks:
                        if len(newline_chunk) <= max_length:
                            final_chunks.append(newline_chunk)
                        else:
                            sentence_chunks = _split_by_sentences(newline_chunk, max_length)
                            final_chunks.extend(sentence_chunks)

    # Recombine small chunks
    return _recombine_small_chunks(final_chunks, max_length, min_length)


def _split_by_markdown_sections(text: str, max_length: int) -> list[str]:
    """
    Split text by markdown sections (headers starting with #), respecting max_length.

    Args:
        text: Text to split
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]

    # Split text into lines to identify markdown headers
    lines = text.split("\n")
    chunks = []
    current_chunk_lines = []

    for line in lines:
        # Check if this is a major section header (starts with single #)
        is_major_header = line.strip().startswith("# ") and not line.strip().startswith("## ")

        # If we encounter a major header and already have content, check if we should start a new chunk
        if is_major_header and current_chunk_lines:
            current_chunk = "\n".join(current_chunk_lines)
            # Only force a split at headers if the current chunk is reasonably sized
            # This prevents creating many tiny chunks when max_length is large
            if len(current_chunk) >= max_length * 0.3:  # At least 30% of max_length
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk_lines = [line]
            else:
                # Current chunk is too small, continue building it
                current_chunk_lines.append(line)
        else:
            # For non-major headers or regular lines, add to current chunk
            current_chunk_lines.append(line)

            # Check if current chunk is getting too long
            current_chunk = "\n".join(current_chunk_lines)
            if len(current_chunk) > max_length and len(current_chunk_lines) > 1:
                # If we have multiple lines, try to find a good split point
                split_point = len(current_chunk_lines) - 1

                # Look for a header to split at (prefer splitting before headers)
                for j in range(len(current_chunk_lines) - 1, 0, -1):
                    if current_chunk_lines[j].strip().startswith("#"):
                        split_point = j
                        break

                # Save the chunk up to the split point
                if split_point > 0:
                    lines_to_save = current_chunk_lines[:split_point]
                    chunk_to_save = "\n".join(lines_to_save)
                    if chunk_to_save.strip():
                        chunks.append(chunk_to_save.strip())
                    current_chunk_lines = current_chunk_lines[split_point:]
                else:
                    # Can't find good split point, split before last line
                    lines_to_save = current_chunk_lines[:-1]
                    if lines_to_save:
                        chunk_to_save = "\n".join(lines_to_save)
                        if chunk_to_save.strip():
                            chunks.append(chunk_to_save.strip())
                    current_chunk_lines = [current_chunk_lines[-1]]

    # Add the final chunk
    if current_chunk_lines:
        final_chunk = "\n".join(current_chunk_lines)
        if final_chunk.strip():
            chunks.append(final_chunk.strip())

    return chunks


def _split_by_separator(text: str, separator: str, max_length: int) -> list[str]:
    """
    Split text by a given separator, respecting max_length.

    Args:
        text: Text to split
        separator: Separator to split by
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]

    parts = text.split(separator)
    chunks = []
    current_chunk = ""

    for part in parts:
        # Calculate the length if we add this part
        potential_length = len(current_chunk) + len(separator) + len(part) if current_chunk else len(part)

        if current_chunk and potential_length > max_length:
            # Current chunk would be too long, save it and start new one
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = part
        elif current_chunk:
            # Add to current chunk
            current_chunk += separator + part
        else:
            # First part
            current_chunk = part

    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _split_by_sentences(text: str, max_length: int) -> list[str]:
    """
    Split text by sentences, respecting max_length.

    Args:
        text: Text to split
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]

    # Simple sentence splitting regex - looks for sentence endings followed by whitespace
    sentence_pattern = r"(?<=[.!?])\s+"
    sentences = re.split(sentence_pattern, text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Calculate potential length
        potential_length = len(current_chunk) + len(sentence) + 1 if current_chunk else len(sentence)

        if current_chunk and potential_length > max_length:
            # Save current chunk and start new one
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        elif current_chunk:
            # Add to current chunk
            current_chunk += " " + sentence
        else:
            # First sentence
            current_chunk = sentence

    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If individual sentences are still too long, we'll have to truncate or split by words
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            final_chunks.append(chunk)
        else:
            # Last resort: split by words
            word_chunks = _split_by_words(chunk, max_length)
            final_chunks.extend(word_chunks)

    return final_chunks


def _split_by_words(text: str, max_length: int) -> list[str]:
    """
    Split text by words as a last resort when sentences are too long.

    Args:
        text: Text to split
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]

    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        # Calculate potential length
        potential_length = len(current_chunk) + len(word) + 1 if current_chunk else len(word)

        if current_chunk and potential_length > max_length:
            # Save current chunk and start new one
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = word
        elif current_chunk:
            # Add to current chunk
            current_chunk += " " + word
        else:
            # First word
            current_chunk = word

    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _recombine_small_chunks(chunks: list[str], max_length: int, min_length: int) -> list[str]:
    """
    Recombine small chunks to optimize chunk sizes.

    Args:
        chunks: List of text chunks
        max_length: Maximum allowed chunk length
        min_length: Minimum preferred chunk length

    Returns:
        List of optimized chunks
    """
    if not chunks:
        return []

    recombined = []
    current_chunk = ""

    for chunk in chunks:
        # Calculate potential length if we combine
        potential_length = len(current_chunk) + len(chunk) + 2 if current_chunk else len(chunk)  # +2 for separator

        if not current_chunk:
            # First chunk
            current_chunk = chunk
        elif potential_length <= max_length:
            # Can combine safely
            current_chunk += "\n\n" + chunk
        else:
            # Would exceed max_length, save current and start new
            if current_chunk.strip():
                recombined.append(current_chunk.strip())
            current_chunk = chunk

    # Add the last chunk
    if current_chunk.strip():
        recombined.append(current_chunk.strip())

    return recombined
