import json
import pytest
from pathlib import Path

from aiware.textio.filetypes.aion.aion import AbstractAionParser, AionObjectParser, AionTextParser, AionTranscriptParser, content_to_aion

TESTDATA_DIR = Path(__file__).parent.parent.parent / "testdata"


@pytest.mark.parametrize("name,testfile,parser_cls", [
    ("AionText", "text.aion", AionTextParser),
    ("AionText (Series)", "text-series.aion", AionTextParser),
    ("AionObject", "object.aion", AionObjectParser),
    ("AionObject (Series)", "object-series.aion", AionObjectParser),
    ("AionTranscript", "transcript.aion", AionTranscriptParser),
    ("AionTranscript2", "transcript-from-engine.aion", AionTranscriptParser),
])
def test_aion_parsers(name, testfile, parser_cls: type[AbstractAionParser]):
    test_path = TESTDATA_DIR / testfile
    content = test_path.read_bytes()

    # Check if parser recognizes file
    assert parser_cls.is_a(content), f"{name}: Failed to detect an Aion file"

    parser = parser_cls()

    # Convert input to Aion
    aion = content_to_aion(content)
    assert aion is not None, f"{name}: Failed to unmarshal Aion file"

    # Run Extract
    extract = parser.extract(content)
    assert extract is not None, f"{name}: Failed to extract from Aion file"

    # Run Rebuild with original content
    rebuild = parser.rebuild(content, extract)
    assert rebuild is not None, f"{name}: Failed to rebuild Aion file"

    # Run Rebuild with no content (new Aion)
    rebuild_new = parser.rebuild(b"", extract)
    assert rebuild_new is not None, f"{name}: Failed to rebuild from empty content"

    # Parse rebuilt object back to Aion
    rebuilt = content_to_aion(rebuild)
    assert rebuilt == aion, f"{name}: Rebuilt AION does not match original"
