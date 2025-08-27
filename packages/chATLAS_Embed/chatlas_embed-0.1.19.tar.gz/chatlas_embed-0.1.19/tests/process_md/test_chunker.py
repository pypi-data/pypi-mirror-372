from pathlib import Path

from chATLAS_Embed.process_md import analyse_chunks, chunker

OUT_DIR = Path(__file__).parent / "test_output"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def test_chunker():
    in_path = Path(__file__).parent / "test_contents.json"
    out_path = OUT_DIR / "test_contents_chunked.json"
    chunker.main(args=["--input", str(in_path), "--output", str(out_path)])
    assert out_path.exists(), "Chunked markdown content file should be created"

    analyse_chunks.main(args=["--input", str(out_path)])
