import json
import pytest
from pathlib import Path

from aiware.textio.filetypes.aion.aion import AbstractAionParser, AionObjectParser, AionTextParser, AionTranscriptParser, content_to_aion
from aiware.textio.filetypes.plaintext.plaintext import PlaintextParser

TESTDATA_DIR = Path(__file__).parent.parent.parent / "testdata"


def test_plaintext_parser():
    test_path = TESTDATA_DIR / "generic.txt"
    content = test_path.read_bytes()

    parser_cls = PlaintextParser

    # Check if parser recognizes file
    assert parser_cls.is_a(content), "Failed to detect plain text file"

    parser = parser_cls()

    # Run Extract
    extract = parser.extract(content)
    assert extract is not None, "Failed to extract from plain text file"

    # Run Rebuild method
    rebuild = parser.rebuild(content, extract)
    assert rebuild is not None, "Failed to rebuild plain text file"

    # compare
    assert content == rebuild, "Rebuilt file does not match original"
