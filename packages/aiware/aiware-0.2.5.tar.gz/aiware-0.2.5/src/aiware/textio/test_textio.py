import json
import os
import logging
from pathlib import Path
import pytest
from aiware.textio.textio import ParserConfig, TextIO, inspect  # your Python bindings
from aiware.aion import aion  # assuming this exists in your py env

log = logging.getLogger(__name__)

def _to_pig_latin(sentence: str) -> str:
    def convert_word(word):
        vowels = "aeiouAEIOU"
        if word[0] in vowels:
            return word + "yay"
        else:
            # Find the index of the first vowel
            for i, letter in enumerate(word):
                if letter in vowels:
                    return word[i:] + word[:i] + "ay"
            return word + "ay"  # No vowels case
    # Split the sentence into words, convert, then join back
    return ' '.join(convert_word(word) for word in sentence.split())

TESTDATA_DIR = Path(__file__).parent / "testdata"

@pytest.mark.parametrize("file,encoding,parser", [
    ("encoding-utf-8.txt", "utf-8", "plaintext"),
    ("encoding-utf-8-bom.txt", "utf-8", "plaintext"),
    ("encoding-utf-16le.txt", "utf-16le", "plaintext"),
    ("encoding-utf-16be.txt", "utf-16be", "plaintext"),
    # ("test.ttml", "utf-8", "ttml"),
    ("text.aion", "utf-8", "aion-text"),
    ("text-no-contract.aion", "utf-8", "aion-text"),
    ("object.aion", "utf-8", "aion-object"),
    ("object-series.aion", "utf-8", "aion-object"),
    ("object-no-contract.aion", "utf-8", "aion-object"),
    ("transcript.aion", "utf-8", "aion-transcript"),
    ("transcript-no-contract.aion", "utf-8", "aion-transcript"),
    ("transcript-lattice.aion", "utf-8", "aion-transcript"),
])
def test_encoding_and_parser_detection(file, encoding, parser):
    tf = TextIO.from_filepath(TESTDATA_DIR / file)
    assert tf.encoding == encoding
    assert tf.parser_name == parser


@pytest.mark.parametrize("file,encoding,mime", [
    # ("test.ttml", "utf-8", "text/xml"),
    # ("test.html", "utf-8", "text/html"),
])
def test_encoding_inspection(file, encoding, mime):
    tf = inspect(TESTDATA_DIR / file)
    log.info(tf)
    assert tf.encoding == encoding
    assert tf.mime == mime


@pytest.mark.parametrize("file,converter,compare", [
    # ("test.ttml", "aion-transcript", "test-ttml-to-aion-transcript.aion"),
    # ("transcript.aion", "ttml", "transcript-aion-to-ttml.ttml"),
])
def test_conversion(file, converter, compare):
    tf = TextIO.from_filepath(TESTDATA_DIR / file)

    output = tf.convert(converter)

    with open(TESTDATA_DIR / "output/{compare}", "r", encoding="utf-8") as f:
        expected = f.read()
    assert output.decode("utf-8") == expected


def test_aion():
    tf = TextIO.from_filepath(TESTDATA_DIR / "text-series.aion")

    for line in tf.get_extracted_text():
        try:
            pl = _to_pig_latin(line.__str__())
            line.modify_str(pl)
        except Exception:
            pass

    tf.set_language("pl")

    rebuild = tf.rebuild()
    with open(TESTDATA_DIR / "output/test-aion.aion", "r", encoding="utf-8") as f:
        expected = f.read()
    assert rebuild.decode("utf-8") == expected

    tf.configure(ParserConfig(chunkSize=25))
    for line in tf.get_translation_chunks():
        line.modify_str(line.__str__() + "!")

    rebuild = tf.rebuild()
    with open(TESTDATA_DIR / "output/test-aion2.aion", "r", encoding="utf-8") as f:
        expected = f.read()
    assert rebuild.decode("utf-8") == expected

    aion_format = tf.get_aion()
    assert isinstance(aion_format, aion.Aion)


def test_sentences():
    tf = TextIO.from_filepath(TESTDATA_DIR / "transcript-from-engine.aion")

    sentences = tf.get_sentences()
    assert len(sentences) == 3

    et = tf.extracted_text
    assert len(et) == 3


# def test_raw_chunks():
#     tf = TextIO.from_filepath(TESTDATA_DIR / "generic.txt")

#     tf.configure(ParserConfig(chunkSize=1024))
#     chunks = tf.get_raw_chunks()
#     assert len(chunks) == 6

#     tf2 = TextIO.from_filepath(TESTDATA_DIR / "generic-words.txt")

#     tf2.configure(ParserConfig(chunkSize=50))
#     for line in tf2.get_extracted_text():
#         try:
#             pl = _to_pig_latin(line.__str__())
#             line.modify_str(pl)
#         except Exception:
#             pass

#     chunks2 = tf2.get_raw_chunks()
#     assert len(chunks2) == 145
