# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/Document.py`
"""Document data structure for chATLAS_Embed."""

import json
from dataclasses import Field, dataclass, field
from enum import Enum
from typing import Any


class DocumentSource(str, Enum):
    """Enumeration of document source types."""

    TWIKI = "twiki"
    CDS = "CDS"
    INDICO = "Indico"
    ATLAS_TALK = "AtlasTalk"
    MKDOCS = "MkDocs"
    GITLAB_MARKDOWN = "GitLabMarkdown"


@dataclass
class Document:
    """
    Represents a base document with its page_content and metadata.

    Attributes:
        page_content: Content of the page.
        source: The source type of the document.
        name: Name/title of the document.
        url: URL of the document.
        metadata: Additional metadata for the document.
        id: ID for the document. Optional, can be set later.
        parent_id: Parent ID if this document has a parent in a hierarchical vector store.
    """

    page_content: str
    source: DocumentSource
    name: str
    url: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str | None = None
    parent_id: str | None = None

    def to_dict(self) -> dict:
        out = {
            "type": self.source.value,  # TODO: change to source everywhere (type should be instead txt, md, pdf, etc)
            "name": self.name,
            "url": self.url,
            "id": self.id,
            "parent_id": self.parent_id,
        }
        overlap = set(self.metadata.keys()) & set(out.keys())
        assert not overlap, f"Metadata keys collide with document fields: {overlap}"
        return {**self.metadata, **out}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_parent(cls, parent_doc: "Document", page_content: str, metadata: dict | None = None) -> "Document":
        if metadata is None:
            metadata = {}

        metadata = {**parent_doc.metadata, **metadata}
        return cls(
            page_content=page_content,
            source=parent_doc.source,
            name=parent_doc.name,
            url=parent_doc.url,
            metadata=metadata,
            parent_id=parent_doc.parent_id,
        )
