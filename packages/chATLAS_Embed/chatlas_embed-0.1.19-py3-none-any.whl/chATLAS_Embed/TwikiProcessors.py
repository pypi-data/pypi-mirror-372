#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/TwikiProcessors.py`

"""
Implementations for loading and processing Twiki documents:

TWikiTextDocument - Dataclass: Base Twiki Document dataclass
TWikiTextProcessor - Processes Twiki text files into standard Document Dataclass
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TWikiTextDocument:
    """Represents a TWiki document from text file."""

    content: str
    url: str
    last_modification: str
    parent_structure: str
    name: str
    html_path: str


class TWikiTextProcessor:
    """Processes TWiki text files into structured documents."""

    @staticmethod
    def read_twiki_text(file_path: Path) -> TWikiTextDocument:
        with open(file_path, encoding="utf-8") as f:
            # Skip first line
            f.readline()
            # Read metadata
            url = f.readline().strip()
            f.readline()  # Skip empty line
            last_modification = f.readline().strip()
            f.readline()  # Skip empty line

            # Read parent structure
            parent_structure = ""
            timeout_count = 0
            while True:
                line = f.readline()
                if "HEADERS" in line or timeout_count > 10:
                    break
                timeout_count += 1
                parent_structure += line

            # Put last modification in correct form
            last_modification = datetime.strptime(last_modification, "%Y-%m")
            last_modification = str(last_modification.strftime("%d-%m-%Y"))

            # Read page_content
            content = f.read()

            return TWikiTextDocument(
                content=content,
                url=url,
                last_modification=last_modification,
                parent_structure=parent_structure,
                name=file_path.stem,
                html_path=str(file_path).replace("/text/", "/html/").replace(".txt", ".html"),
            )
