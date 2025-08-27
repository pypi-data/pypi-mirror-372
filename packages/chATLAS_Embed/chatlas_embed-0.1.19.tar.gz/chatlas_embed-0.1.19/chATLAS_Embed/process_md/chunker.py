import argparse
import json
import statistics
from pathlib import Path

from bs4 import BeautifulSoup

from chATLAS_Embed.process_md.html_utils import remove_html_from_markdown
from chATLAS_Embed.process_md.preprocess import preprocess_markdown
from chATLAS_Embed.process_md.split_text import split_text_recursive

# ...existing code...


# ...existing code...


def file_filter(project_path: str, file_path: str, content: str) -> bool:
    """
    Filter function to determine if a file should be processed.

    Args:
        project_path: The path of the project
        file_path: The path of the file within the project
        content: The content of the file to be processed

    Returns:
        True if the file should be processed, False otherwise
    """
    if not file_path:
        return False

    if not content:
        return False

    if len(content) < 100 or len(content) > 100_000:
        return False

    return True


def preprocess_project(project: dict) -> dict:
    """
    Process a project by filtering and preprocessing its markdown files.
    """
    out_files = []
    for file in project["markdown_files"]:
        if not file_filter(project["path"], file["path"], file["content"]):
            continue
        processed_content, placeholders = preprocess_markdown(file["content"])
        if len(processed_content) < 100:
            continue
        file["content"] = processed_content
        file["placeholders"] = placeholders
        out_files.append(file)
    project["markdown_files"] = out_files
    return project


def chunk_project(project: dict, max_chunk_length: int, min_chunk_length: int = 200) -> list[int]:
    """
    Chunk a project's markdown files using custom recursive text splitting.

    Args:
        project: A dictionary representing the project with markdown files.
        max_chunk_length: Maximum allowed length for chunks.
        min_chunk_length: Minimum allowed length for chunks. Chunks shorter than this will be filtered out.

    Returns:
        List of chunk lengths.
    """
    chunk_lengths = []
    for file in project["markdown_files"]:
        split_texts = split_text_recursive(file["content"], max_chunk_length, min_chunk_length)
        # Filter out chunks that are shorter than the minimum length
        split_texts = [chunk for chunk in split_texts if len(chunk) >= min_chunk_length]

        final_nodes = []
        content = file["content"]
        offset = 0
        total_chunks = len(split_texts)
        file["total_chunks"] = total_chunks
        for i, split_text in enumerate(split_texts):
            # Find start and stop index for this chunk in the original content
            start_index = content.find(split_text, offset)
            if start_index == -1:
                start_index = offset  # fallback if not found
            stop_index = start_index + len(split_text)
            offset = stop_index
            chunk_lengths.append(len(split_text))
            node = {
                "text": split_text,
                "metadata": {
                    "chunk_index": i,
                    "start_index": start_index,
                    "stop_index": stop_index,
                },
            }
            final_nodes.append(node)
        file["nodes"] = final_nodes
    return chunk_lengths


def main(args=None):
    parser = argparse.ArgumentParser(description="Process and chunk markdown files.")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("-o", "--output", default="process_chunked.json", help="Output file path")
    parser.add_argument(
        "--max-chunk-length",
        type=int,
        default=1500,
        help="Maximum length for chunks. If specified, chunks exceeding this length will be split by paragraphs.",
    )
    parser.add_argument(
        "--min-chunk-length",
        type=int,
        default=200,
        help="Minimum length for chunks. Chunks shorter than this will be filtered out.",
    )
    parsed_args = parser.parse_args(args)

    path = Path(parsed_args.input)

    # check if the path exists
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist.")

    # read json file
    with path.open("r", encoding="utf-8") as file:
        projects = json.load(file)

    # process each project
    num_chunks = 0
    all_chunk_lengths = []
    for i, project in enumerate(projects):
        print(f"Processing project {i + 1}/{len(projects)}: {project['path']}")
        preprocess_project(project)
        chunk_lengths = chunk_project(project, parsed_args.max_chunk_length, parsed_args.min_chunk_length)
        all_chunk_lengths.extend(chunk_lengths)
        num_chunks += sum(len(file.get("nodes", [])) for file in project["markdown_files"])

    # write json file
    output_path = Path(parsed_args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(projects, file, indent=4, ensure_ascii=False)

    print(f"Processed projects saved to {output_path}")
    print(f"Total number of chunks created: {num_chunks}")

    # Print chunk statistics
    if all_chunk_lengths:
        print("\nChunk Length Statistics:")
        print(f"  Mean length: {statistics.mean(all_chunk_lengths):.1f} characters")
        print(f"  Median length: {statistics.median(all_chunk_lengths)} characters")
        print(f"  Minimum length: {min(all_chunk_lengths)} characters")
        print(f"  Maximum length: {max(all_chunk_lengths)} characters")
    else:
        print("No chunks were created.")


if __name__ == "__main__":
    main()
