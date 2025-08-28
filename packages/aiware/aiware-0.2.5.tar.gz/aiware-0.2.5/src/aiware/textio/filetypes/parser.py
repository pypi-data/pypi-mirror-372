

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

from pydantic import BaseModel, Field

class FiletypeParserExpectations(BaseModel):
	build_sentences: Optional[bool]

class ExtractedText(BaseModel):
    text: bytes = Field(alias="text")
    """Original extracted text"""

    modified: Optional[bytes] = Field(alias="modified", default=None)
    """Modified Text, stored separate incase this helps a parser"""

    index: list[int] = Field(alias="index")
    """Index (or Indexes) of the text in the original file"""

    start_time: Optional[timedelta] = Field(alias="startTime", default=None)
    """If dealing with timed data, this is the start time of the text"""

    end_time: Optional[timedelta] = Field(alias="endTime", default=None)
    """If dealing with timed data, this is the end time of the text"""

    extracted_from: Optional[dict[str, object]] = Field(alias="extractedFrom", default=None)
    """Optionally, the interface that the text was extracted from"""

    def __str__(self):
        return str(self.text, "utf8")

    def modify(self, modified: bytes):
        self.modified = modified

    def bytes(self):
        return self.text

    def modify_str(self, modified: str):
        self.modify(bytes(modified, 'utf-8'))


class FiletypeParser(ABC):
    language: Optional[str] = None

    @classmethod
    @abstractmethod
    def is_a(cls, content: bytes) -> bool:
        raise NotImplementedError
    
    def expectations(self) -> FiletypeParserExpectations:
        return FiletypeParserExpectations(
            build_sentences=False
        )

    @abstractmethod
    def extract(self, content: bytes) -> list[ExtractedText]:
        raise NotImplementedError

    @abstractmethod
    def rebuild(self, content: Optional[bytes], extracted: list[ExtractedText]) -> bytes:
        raise NotImplementedError
