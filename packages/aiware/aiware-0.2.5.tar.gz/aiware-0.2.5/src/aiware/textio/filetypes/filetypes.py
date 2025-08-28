import logging
import mimetypes
from typing import Any, Optional, Tuple

import magic
from pydantic import BaseModel

from aiware.textio.filetypes.parser import FiletypeParser
from aiware.textio.filetypes.registry import ExtensionsMap, Registry, SupportedTypes

class DetectedFiletype(BaseModel):
    mime: str
    """Detected MIME type"""

    encoding: str
    """Detected charset encoding"""

    extension: str
    """File extension"""

    parser: Optional[str] = None
    """Parser name (if detected)"""


def is_supported(content_type: str) -> bool:
    return content_type in SupportedTypes.types

def get_parser_from_extension(content: bytes, extension: str) -> Optional[Tuple[FiletypeParser, str]]:
    """Return (parser, parser_name) given an extension."""
    
    try:
        parsers = ExtensionsMap.extensions[extension]
    except KeyError:
        return None
    
    # if we have an extension mapping, we can directly map it to parsers
    for parser in parsers:
        # Check Registry to see if the parser is defined (it should be, but error handling is nice)
        # Parsers are part of the filetypes package in this repo and when a new filetype is added
        if parser_type := Registry.parsers.get(parser):
            # Call the is_a() method on the parser to check if it's correct
            if parser_type.is_a(content):
                # If we get a successful match, use that parser.
                return parser_type(), parser
            
    return None


def get_parser_from_content_type(content: bytes, content_type: str) -> Optional[Tuple[FiletypeParser, str]]:
    """Return (parser, parser_name) given a MIME type."""
    
    try:
        parsers = SupportedTypes.types[content_type]
    except KeyError:
        return None
    
    # We don't seem to have an extension map, so we need to check all parsers
	# based on the mimetype -- Now lets see if we can use any of the defined parsers.
    for parser in parsers:
        # Check Registry to see if the parser is defined (it should be, but error handling is nice)
        # Parsers are part of the filetypes package in this repo and when a new filetype is added
        if parser_type := Registry.parsers.get(parser):
            # Call the is_a() method on the parser to check if it's correct
            if parser_type.is_a(content):
                # If we get a successful match, use that parser.
                return parser_type(), parser
            
    return None


def detect(content: bytes, extension: str) -> Tuple[DetectedFiletype, Optional[FiletypeParser]]:
    """
    Detect the MIME type, encoding, and parser for the given content and extension.

    Mirrors the Go function:
        func Detect(content []byte, extension string) (DetectedFiletype, FiletypeParser, error)
    """
    # Detect the mimetype of content and its charset
    # Python's built-in `mimetypes` is weak compared to Go's mimetype lib;
    # you may want to replace with `python-magic` for real detection.
    mime = magic.Magic(mime=True)
    mime_encoding = magic.Magic(mime_encoding=True)

    mtype = mime.from_buffer(content)
    encoding = mime_encoding.from_buffer(content)

    if encoding == "us-ascii" or len(encoding) == 0 or encoding == "unknown":
        encoding = "utf-8"

    content_type = mtype

    # Detect extension if it's not passed
    if not extension:
        guessed_ext = mimetypes.guess_extension(content_type)
        extension = guessed_ext.lstrip(".") if guessed_ext else ""

    dft = DetectedFiletype(
        mime=content_type,
        encoding=encoding,
        extension=extension,
    )

    ftp: Optional[FiletypeParser] = None

    # check if our MIME is in our SupportedTypes list
    if is_supported(content_type):
        # base content type supported
        ftp, dft.parser = get_parser_from_extension(content, extension) or (None, None)
        if not dft.parser:
            # If we don't have an extension, let's check the content type
            ftp, dft.parser = get_parser_from_content_type(content, content_type) or (None, None)
    else:
        # Not supported? Let's check its parent
        parent_type = content_type.split("/")[0] + "/*"
        if is_supported(parent_type):
            ftp, dft.parser = get_parser_from_content_type(content, parent_type) or (None, None)
            if dft.parser:
                print(
                    f"WARNING: Original parser not found, but found a parent parser to use {dft.parser}"
                )
                print("This is not ideal, but may provide usable results.")

    if not dft.parser:
        # Check if output appears to be unsupported AION from another engine, and throw a special error in that case
        if content_type == "application/json":
            text = content.decode(errors="ignore")
            if all(key in text for key in ["taskId", "internalTaskId", "sourceEngineId"]):
                raise ValueError("unsupported AION Detected")

        raise ValueError(f"{content_type} is not a supported file type")

    return dft, ftp
