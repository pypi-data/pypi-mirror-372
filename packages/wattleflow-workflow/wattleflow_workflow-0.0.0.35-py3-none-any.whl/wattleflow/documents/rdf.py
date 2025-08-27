# Module Name: documents/rdf.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains Rdf Document class.

from logging import NOTSET, Handler
from typing import Dict, Optional
from wattleflow.concrete import Document


class RDFDocument(Document[Dict]):
    def __init__(
        self,
        content: Dict,
        filename: str,
        level: int = NOTSET,
        handler: Optional[Handler] = None,
    ):
        Document.__init__(self, content=content, level=level, handler=handler)
        self.update_metadata(key="filename", value=filename)

    @property
    def filename(self) -> str:
        return str(self.metadata.get("filename", ""))

    @property
    def size(self) -> int:
        if self.content is None:
            return 0

        return len(self.content)
