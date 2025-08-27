import argparse
import json

import matplotlib.pyplot as plt


def main(args=None):
    parser = argparse.ArgumentParser(description="Analyze chunked markdown projects")
    parser.add_argument("--input", required=True, help="Path to chunked JSON file")
    args = parser.parse_args(args)

    with open(args.input, encoding="utf-8") as f:
        projects = json.load(f)

    file_lengths = []
    chunk_lengths = []

    for project in projects:
        for file in project.get("markdown_files", []):
            content = file.get("content", "")
            file_lengths.append(len(content))
            for node in file.get("nodes", []):
                chunk_text = node.get("text", "")
                chunk_lengths.append(len(chunk_text))

    plt.figure(figsize=(10, 4))
    plt.hist(file_lengths, bins=50, color="skyblue", edgecolor="black", log=True)
    plt.title("Histogram of File Lengths")
    plt.xlabel("File Length (characters)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("file_lengths_histogram.png")
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.hist(chunk_lengths, bins=50, color="salmon", edgecolor="black", log=True)
    plt.title("Histogram of Chunk Lengths")
    plt.xlabel("Chunk Length (characters)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("chunk_lengths_histogram.png")
    plt.close()


if __name__ == "__main__":
    main()
