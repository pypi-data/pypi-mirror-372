from typing import Optional
from aiware.textio.filetypes.parser import ExtractedText, FiletypeParser


class PlaintextParser(FiletypeParser):
    @classmethod
    def is_a(cls, content: bytes) -> bool:
        """
        Yes it is.
        For most filetype parsers, it is NOT appropriate to just return true.
        But in the case of plaintext, we can just trust that if we reached this
        point, we are most likely end-of-road in attempting to discover more complex
        file types, so we can just treat this as plain text.
        """
        return True

    def extract(self, content: bytes) -> list[ExtractedText]:
        """
        Extract - The parse function is called inside the main TextIO.Extract() function
        and returns extracted text and an index used to rebuild that Data.
        For plaintext files, this is always going to be the entire content of the file.
        """
        return [
            ExtractedText(
		        text=content,
		        index=[0],
            )
        ]

    def rebuild(self, content: Optional[bytes], extracted: list[ExtractedText]) -> bytes:
        """
        Rebuild - To rebuild, we will always just return the entire contents of the file.
        In a more complex filetype, the content provided will be used to rebuild against.
        Or if content is empty, a new file is being created (convert)
        """
        resp: bytearray = bytearray()
        for i, v in enumerate(extracted):
            text = v.text
            if v.modified and len(v.modified) > 0:
                text = v.modified
            if i > 0:
                resp.extend(b"\n")
            resp.extend(text)
        return bytes(resp)

    def set_language(self, lang: str):
        self.language = lang
