"""
Generate questions based on processed markdown chunks.
Generated Q/A pairs are used to finetune embedding model.
"""

import json
from pathlib import Path
from typing import Any

from chATLAS_Embed.finetune.openai_client import OpenAIClient

# Prompt template for generating questions from chunks
QUESTION_GENERATION_PROMPT = """Objective: Generate high-quality Question/Answer pairs from the provided text chunk for the purpose of fine-tuning an embedding model for a RAG application used by particle physics researchers.
Context: The text chunk and its associated metadata below are from documentation used by particle physics researchers.

------------
{chunk_text}
------------

Instructions:
Based only on the text and metadata provided in the context above, generate up to 3 simple, atomic questions that a particle physics researcher might ask. Use the metadata to make the questions as specific as possible. Only generate questions if the text contains enough substantive information to formulate high-quality, answerable questions. If the text is not suitable for creating quality questions (e.g., it's just a list of links, a code snippet without explanation, or lacks substantive information), generate fewer questions or none at all. Prioritize quality over quantity - it's better to generate 1-2 excellent questions than 3 mediocre ones.

Generate questions for one of these types of researchers:
- Students: Asking conceptual questions to understand basics. (e.g., "What is X used for?")
- Researchers/Engineers: Asking practical questions about applications and how to perform tasks. (e.g., "How can I do Y with Z?")
- Senior Experts: Asking strategic questions about capabilities and broader implications. (e.g., "What are the advantages of system A over B?")

Question Requirements:
- Suitability: The text chunk must contain enough information to form meaningful questions and their corresponding answers. If it does not, generate fewer questions or none at all.
- Quality over Quantity: Only generate multiple questions if each one adds unique value and can be clearly answered from the text.
- Diversity: When generating multiple questions, ensure they cover different aspects of the content (e.g., one about purpose, one about usage, one about technical details).
- Simplicity: Each question must be atomic, asking for only one piece of information. It should not contain conjunctions like "and" or be a list of questions in one sentence.
- Answerability: The answer to the question must be present in the provided text chunk.
- Realism: The question should sound like a natural query from a researcher, not an automated or generic one.
- Relevance: The question should focus on topics relevant to particle physics, CERN, or the ATLAS experiment when the text allows.

- CRITICAL - COMPLETE INDEPENDENCE FROM CONTEXT: This is the most important rule. When generating questions, pretend you have never seen the provided chunk. The question must make complete sense to someone who has no access to the original text. 

    Why this matters: These questions will be used by researchers who don't have the original document in front of them. If your question contains words like "this", "these", "the above", or "as described", it becomes meaningless without the context.

    FORBIDDEN context references include:
    - "this/these/that/those" + any noun (this repository, these pages, that file, this context)  
    - "the above/below" (the above code, the steps below)
    - "mentioned/described/shown" (as mentioned, described here)
    - "the text/document/page/section"
    - Generic references like "the repository" or "the file" or "this context"

    Instead, use SPECIFIC INFORMATION from the metadata or context to make questions self-contained:
    - Bad: "Which repositories should be cloned in this step?" -> Good: "Which repositories should be cloned when setting up the taucp-boom project?"
    - Bad: "What is the subject of these pages?" -> Good: "What is the subject of the CERN Beam Performance Tracking documentation?"

Output Format:
Provide the output as a JSON list. If suitable questions are generated, the list will contain 1-3 objects, each with a "question" key. If no suitable questions can be generated, provide an empty list. Generate fewer questions if the chunk doesn't support multiple high-quality questions.

Example for a chunk with multiple good questions:

```
[
    {{"question": "..."}},
    {{"question": "..."}},
    {{"question": "..."}}
]
```

Example for a chunk with limited content:

```
[
    {{"question": "..."}}
]
```

Example for an unsuitable chunk:

```
[]
```
"""


def format_chunk(project: dict, file: dict, chunk: dict) -> str:
    # Format chunk text with metadata included
    return f"GitLab Project Path: {project['path']}\nFile path: {file['path']}\nChunk text: {chunk['text']}"


def get_chunks(project: dict):
    """
    Process projects data into formatted chunks using a generator for memory efficiency.

    Args:
        data: List of project data dictionaries

    Yields:
        Formatted chunk dictionary with repo_path, file_path, and chunk_text
    """
    for file in project["markdown_files"]:
        for chunk in file["nodes"]:
            yield format_chunk(project, file, chunk)


def generate_questions_from_chunk(chunk_text: str, client: OpenAIClient) -> list[dict[str, str]]:
    """
    Generate questions that can be answered by the given chunk using OpenAI's API.

    Args:
        chunk_text: The text chunk to generate questions for (includes metadata)
        client: OpenAI client instance

    Returns:
        List of dictionaries with 'question' and 'answer' keys
    """
    return client.generate_questions(chunk_text=chunk_text, prompt_template=QUESTION_GENERATION_PROMPT)


def generate_qa_entries(
    chunks: list[dict[str, Any]], client: OpenAIClient
) -> Any:  # Generator[dict[str, Any], None, None]
    """
    Generate Q&A entries from chunks using a generator for memory efficiency.

    Args:
        chunks: List of chunk dictionaries with 'chunk_text' key
        client: OpenAI client instance

    Yields:
        Dictionary containing Q&A entry with metadata
    """
    for i, chunk in enumerate(chunks):
        try:
            print(f"Processing chunk {i + 1}/{len(chunks)}...")
            questions = generate_questions_from_chunk(chunk["chunk_text"], client=client)

            # Handle case where no questions are generated (empty list)
            if not questions:
                print(f"No suitable questions generated for chunk {i + 1} (chunk not suitable for Q&A)")
                continue

            for question_data in questions:
                qa_entry = {
                    "question": question_data["question"],
                    "answer": chunk["chunk_text"],
                    "repo_path": chunk.get("repo_path", ""),
                    "file_path": chunk.get("file_path", ""),
                    "chunk_index": i,
                }
                yield qa_entry

        except Exception as e:
            print(f"Error processing chunk {i + 1}: {e!s}")
            continue


def generate_qa_dataset(
    chunks: list[dict[str, Any]],
    client: OpenAIClient,
    output_file: str | None = None,
) -> list[dict[str, Any]]:
    """
    Generate a Q&A dataset from a list of chunks.

    Args:
        chunks: List of chunk dictionaries with 'chunk_text' key
        client: OpenAI client instance
        output_file: Optional file path to save the dataset

    Returns:
        List of Q&A pairs with metadata
    """
    # Use generator for memory efficiency
    qa_dataset = []

    if output_file:
        # If saving to file, write incrementally to save memory
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("[\n")
            first_entry = True

            for qa_entry in generate_qa_entries(chunks, client=client):
                if not first_entry:
                    f.write(",\n")
                else:
                    first_entry = False

                json.dump(qa_entry, f, indent=2, ensure_ascii=False)
                qa_dataset.append(qa_entry)

            f.write("\n]")
        print(f"Dataset saved to {output_file}")
    else:
        # If not saving to file, collect all entries
        qa_dataset = list(generate_qa_entries(chunks, client=client))

    return qa_dataset


if __name__ == "__main__":
    # Load the data
    fname = "/Users/sam/work/atlas/chatlas/chatlas-packages/chATLAS_Scrape/process_chunked.json"
    path = Path(fname)

    with path.open() as f:
        data = json.load(f)

    # Create OpenAI client once for reuse
    client = OpenAIClient()

    # count how many chunks there are in total
    total_chunks = len([chunk for project in data for chunk in get_chunks(project)])
    print(f"Total chunks to process: {total_chunks}")

    # Process chunks using simplified loop
    for project in data:
        for chunk in get_chunks(project):
            print("-" * 50)
            print("Chunk:")
            print(chunk)
            print("-" * 50)
            print("Generated questions:")
            questions = generate_questions_from_chunk(chunk, client=client)
            if questions:
                print(f"Generated {len(questions)} questions:")
                for q in questions:
                    print(f"Q: {q['question']}")
            else:
                print("No suitable questions generated for this chunk.")
            print("-" * 50)
            break
