from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
import html
import json
import logging
from pathlib import Path
import re
from typing import Callable, List, Optional, Self, cast
from pydantic import BaseModel, Field

from aiware.aion.aion import Aion
from aiware.textio.filetypes.parser import ExtractedText, FiletypeParser
from aiware.textio.filetypes.filetypes import DetectedFiletype, detect
from aiware.textio.filetypes.registry import Registry
from aiware.textio.helpers import (
    MB,
    cleanup_sentence,
    convert_to_utf8,
    get_extension_from_path,
    has_sentence_delimiter,
    split_by_byte_size,
    split_sentence_into_fragments,
    split_sentences,
)


class ChunkMarkerConfig(BaseModel):
    start: str = Field(alias="start")
    """Start marker"""

    end: str = Field(alias="end")
    """End marker"""

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
        "protected_namespaces": (),
    }
    
@dataclass
class TextIO:
    mime: str
    """mime type of the file"""

    encoding: str
    """charset of the file"""

    extension: str
    """extension of the file"""

    parser_name: str
    """filetype of the file"""

    parser: FiletypeParser
    """the parser for the file"""

    parser_config: "ParserConfig"
    """config for the parser"""

    content: bytes
    """original content of the file"""

    rebuilt_content: bytes
    """rebuilt content of the file"""

    extracted_text: list[ExtractedText]
    """extracted text from the file"""

    translation_chunks: list[ExtractedText]
    """chunks created for translation"""

    language: Optional[str]
    """language of AION output if we generate some"""

    plain_text: Optional[bytes]
    """plain text output of the file"""

    @classmethod
    def from_bytes(cls, content: bytes, extension: str) -> Self:
        logging.info("TextIO Version: %s", TEXTIO_VERSION)
        logging.info("TextIO Initialized - Content Size: %d", len(content))

        try:
            dft, parser = detect(content, extension)
        except Exception as e:
            raise e

        if not dft.parser or not parser:
            raise ValueError(f"No parser found for filetype: {dft}")

        logging.debug(dft)

        # Verify the content is UTF-8 encoded
        content = convert_to_utf8(content, dft.encoding)

        return cls(
            mime=dft.mime,
            extension=dft.extension,
            encoding=dft.encoding,
            parser_name=dft.parser,
            parser=parser,
            content=bytes(content),
            parser_config=default_parser_config,
            rebuilt_content=bytes(),
            extracted_text=[],
            translation_chunks=[],
            language=None,
            plain_text=None,
        )

    @staticmethod
    def from_filepath(filepath: str | Path) -> "TextIO":
        try:
            with open(filepath, "rb") as f:
                content = f.read()
        except OSError as e:
            raise e

        logging.info("Initializing TextIO with %s", filepath)

        extension = get_extension_from_path(filepath.__str__())
        return TextIO.from_bytes(content, extension)

    #     _____                __  _
    #    / ____|              / _|(_)
    #   | |      ___   _ __  | |_  _   __ _
    #   | |     / _ \ | '_ \ |  _|| | / _` |
    #   | |____| (_) || | | || |  | || (_| |
    #    \_____|\___/ |_| |_||_|  |_| \__, |
    #                                  __/ |
    #                                 |___/
    #
    # Functions related to configuration of the library

    def configure(self, config: "ParserConfig") -> None:
        """
        Update parser_config with values from config, similar to Go's mergo.Merge with override.
        """
        # Merge with override: copy values from config if provided
        self.parser_config = self.parser_config.copy(
            update=config.dict(exclude_unset=True)
        )

        # Don't let chunks be too small
        if self.parser_config.chunk_size < 50:
            logging.warning("Chunk size is too small! Raising to 50")
            self.parser_config.chunk_size = 50

        # Check if ChunkMarkers are set
        if (
            not self.parser_config.chunk_markers.start
            or not self.parser_config.chunk_markers.end
        ):
            logging.warning("ChunkMarkers are not set! Using defaults")
            self.parser_config.chunk_markers = deepcopy(
                default_parser_config.chunk_markers
            )

        # Ensure start and end markers are not the same
        if (
            self.parser_config.chunk_markers.start
            == self.parser_config.chunk_markers.end
        ):
            logging.warning("ChunkMarkers are the same! Using defaults")
            self.parser_config.chunk_markers = deepcopy(
                default_parser_config.chunk_markers
            )

        # Mergo does a terrible job with bools: check manually
        if config.raw_chunk_config and not config.raw_chunk_config.clean_plain_text:
            self.parser_config.raw_chunk_config.clean_plain_text = False
        if config.raw_chunk_config and not config.raw_chunk_config.trim_sentences:
            self.parser_config.raw_chunk_config.trim_sentences = False

        # Escape emojis override
        if config.escape_emojis:
            self.parser_config.escape_emojis = True

        logging.debug(
            "TextIO Configuration Updated: %s", self.parser_config.model_dump_json(indent=2)
        )

    def get_expectations(self):
        return self.parser.expectations()
    
    def set_language(self, lang: str):
        self.parser.language = lang
        self.language = lang
    
    #    ______        _                      _
    #   |  ____|      | |                    | |
    #   | |__   __  __| |_  _ __  __ _   ___ | |_
    #   |  __|  \ \/ /| __|| '__|/ _` | / __|| __|
    #   | |____  >  < | |_ | |  | (_| || (__ | |_
    #   |______|/_/\_\ \__||_|   \__,_| \___| \__|
    #
    #   Functions related to the extraction of text from a document

    def extract(self):
        """
        Run the extract method on a file, and perform any expectation-based modifications.
        """
        logging.debug(f"Extracting Text from File using Parser: {self.parser_name}")

        try:
            extracted_text = self.parser.extract(self.content)
        except Exception as err:
            logging.error("Error extracting text from file", exc_info=err)
            extracted_text = []
            raise err

        self.extracted_text = extracted_text

        # If a file type expects sentences to be built.
        # This is helpful for transcription where the data is word-by-word
        if self.get_expectations().build_sentences:
            self.build_sentences_from_extracted_text()

    def extract_if_empty(self):
        """
        If we have no extracted text objects, run the extract method.
        """
        logging.debug(f"Extract If Empty for Parser: {self.parser_name}")
        if not self.extracted_text:
            self.extract()

    def get_extracted_text(self) -> list[ExtractedText]:
        """
        Returns pointers to our Extracted Text Objects (to be modified before a rebuild).
        """
        logging.debug("Getting Extracted Text")
        self.extract_if_empty()

        # In Python, objects are reference types, so this is simpler than Go pointers
        return list(self.extracted_text) if self.extracted_text else []

    def build_sentences_from_extracted_text(self):
        """
        Modify our extracted text to groups of sentences.
        This will break rebuildability of the file. Parsers
        that specifically set this expectation (like aion-transcript)
        should be setup to rebuild new objects vs updating old ones.
        """

        # @TODO: I'd like this to also take multiple sentences in a single ExtractedText node and break them out into multiple.
        # for use in conversion processes -- Could also be reused in the GetRawOutput function.

        self.extract_if_empty()
        logging.debug("Grouping Extracted Text into Sentences")

        # We need to build sentences from our extracted text
        start_time: Optional[timedelta] = None
        sentence_start_index = 0
        sentence: bytes = b""

        etc: list[Optional[ExtractedText]] = list(self.extracted_text[:])

        for i, et in enumerate(self.extracted_text):
            # If this is the first sentence, we need to set the start time
            if et.start_time and et.start_time != 0 and not start_time:
                start_time = et.start_time

            text = et.text + b" "
            sentence += text

            if has_sentence_delimiter(et.text):
                # Time to end this sentence.
                # Lets replace all of our ExtractedText with a new one
                # with the sentence we just built
                new_et = ExtractedText(
                    index=[sentence_start_index],
                    text=cleanup_sentence(sentence),
                    startTime=start_time,
                    endTime=et.end_time,
                )

                empty: list[Optional[ExtractedText]] = [None] * (
                    i - sentence_start_index + 1
                )
                empty[0] = new_et
                etc[sentence_start_index : i + 1] = empty

                start_time = None
                sentence = b""
                sentence_start_index = i + 1

        self.extracted_text = [b for b in etc if b is not None and b.text is not None]

    #    _____        _             _  _      _
    #   |  __ \      | |           (_)| |    | |
    #   | |__) | ___ | |__   _   _  _ | |  __| |
    #   |  _  / / _ \| '_ \ | | | || || | / _` |
    #   | | \ \|  __/| |_) || |_| || || || (_| |
    #   |_|  \_\\___||_.__/  \__,_||_||_| \__,_|
    #
    #    Functions related to the rebuilding of our original file format
    #		after it has been modified.

    def prebuild(self) -> None:
        """Before a rebuild or a convert"""
        # Sometimes we might be converting and never explicitly called extract
        self.extract_if_empty()

        if len(self.translation_chunks) > 0:
            self.modify_from_translation_chunks()

    def rebuild(self) -> bytes:
        """Call internal parser rebuild function and return the rebuilt text"""
        logging.debug("Rebuilding Extracted Text into File")

        self.prebuild()
        self.unstash_emoji()  # unstash emoji if enabled on rebuild
        try:
            rebuilt = self.parser.rebuild(self.content, self.extracted_text)
        except Exception as err:
            logging.error("Error Rebuilding Extracted Text", exc_info=err)
            rebuilt = b""

        self.rebuilt_content = rebuilt
        return rebuilt

    # Return rebuilt, and rebuild if it doesn't exist
    def get_rebuilt(self) -> bytes:
        if self.rebuilt_content is None:
            return self.rebuild()
        return self.rebuilt_content
    
    #     _____                                _
    #    / ____|                              | |
    #   | |      ___   _ __ __   __ ___  _ __ | |_
    #   | |     / _ \ | '_ \\ \ / // _ \| '__|| __|
    #   | |____| (_) || | | |\ V /|  __/| |   | |_
    #    \_____|\___/ |_| |_| \_/  \___||_|    \__|
    #
    #   Functions related to converting to an alternate format

    # Handle conversion to another file format.
    # We just assume your not trying to do something stupid.
    # Convert works by passing an empty content arg to Rebuild, and each parser
    # is expected to know how to handle an empty content argument.
    
    def convert(self, to: str) -> bytes:
        """
        Convert the extracted text to another parser type.
        """
        logging.debug("Converting File Type from '%s' to '%s'", self.parser_name, to)
        self.prebuild()

        if to == self.parser_name:
            # Converting to yourself is silly, but here
            return self.get_rebuilt()

        parser_name = ""
        if to in Registry.parsers:
            parser_name = to

        # @TODO: Could detect parser by MIME/type strings, e.g. Convert("text/plain")

        if parser_name:
            logging.debug("Found Parser to Use: %s", parser_name)
            # Create a new parser instance
            conversion_parser: FiletypeParser = Registry.parsers[parser_name]()
            return conversion_parser.rebuild(None, self.extracted_text)
        else:
            err = Exception(f"No parser found for: {to}")
            logging.error(err)
            raise err

    def is_aion(self) -> bool:
        """
        Check if the parser name indicates an AION file.
        """
        return "aion" in self.parser_name.lower()

    def get_aion(self) -> Aion:
        """
        Return the parsed AION object from RebuiltContent.
        """
        if self.is_aion():
            a = Aion(**json.loads(self.rebuilt_content or b"{}"))
            if not getattr(a, "language", None):
                a.language = self.language
            return a
        else:
            raise Exception("Not an AION file")

    #    _______                       _         _    _
    #   |__   __|                     | |       | |  (_)
    #      | | _ __  __ _  _ __   ___ | |  __ _ | |_  _   ___   _ __
    #      | || '__|/ _` || '_ \ / __|| | / _` || __|| | / _ \ | '_ \
    #      | || |  | (_| || | | |\__ \| || (_| || |_ | || (_) || | | |
    #      |_||_|   \__,_||_| |_||___/|_| \__,_| \__||_| \___/ |_| |_|
    #
    #   Functions for building payloads useful for translation engines
    #   and decoding those payloads back into ExtractedText objects.

    def get_translation_chunks(self) -> List[ExtractedText]:
        logging.debug("Getting Translatable Chunks")
        self.extract_if_empty()

        translation_chunks: List[ExtractedText] = []
        chunks: List[bytes] = []
        chunk: bytes = b""

        for i, extracted in enumerate(self.extracted_text):
            use_text = extracted.text
            text = make_line(use_text, i, self)

            # Preserve line breaks if placeholder differs
            if self.parser_config.line_break_placeholder != "\n":
                text = text.replace(
                    b"\n", self.parser_config.line_break_placeholder.encode("utf-8")
                )

            if len(text) > self.parser_config.chunk_size:
                if chunk:
                    chunks.append(chunk)
                    chunk = b""
                split = split_by_byte_size(text, self.parser_config.chunk_size)
                chunks.extend(split)
            else:
                if len(chunk) + len(text) > self.parser_config.chunk_size:
                    chunks.append(chunk)
                    chunk = b""
                chunk += text

        if chunk:
            chunks.append(chunk)

        # Wrap in ExtractedText
        for i, ch in enumerate(chunks):
            if ch:
                translation_chunks.append(ExtractedText(text=ch, index=[i]))

        logging.debug("TextIO Translatable Chunks count=%d", len(translation_chunks))
        self.translation_chunks = translation_chunks
        self.stash_emoji()

        return self.translation_chunks

    def modify_from_translation_chunks(self):
        logging.debug("Modifying ExtractedText from translation_chunks")

        buffer = b""
        for chunk in self.translation_chunks:
            text = chunk.modified if chunk.modified is not None else chunk.text
            if text:
                buffer += text

        # Decode HTML entities
        buffer = html.unescape(buffer.decode("utf-8")).encode("utf-8")

        # Restore line breaks
        if self.parser_config.line_break_placeholder != "\n":
            buffer = buffer.replace(
                self.parser_config.line_break_placeholder.encode("utf-8"), b"\n"
            )

        # Split and reconstruct ExtractedText
        start = self.parser_config.chunk_markers.start.encode("utf-8")
        end = self.parser_config.chunk_markers.end.encode("utf-8")

        chunks = buffer.split(start)
        for ch in chunks:
            parts = ch.split(end)
            if len(parts) == 2:
                try:
                    index = int(parts[0].decode("utf-8"))
                    text = parts[1].strip()
                    self.extracted_text[index].modified = text
                except Exception:
                    continue

    #    ______                 _ _
    #   |  ____|               (_|_)
    #   | |__   _ __ ___   ___  _ _
    #   |  __| | '_ ` _ \ / _ \| | |
    #   | |____| | | | | | (_) | | |
    #   |______|_| |_| |_|\___/| |_|
    #                         _/ |
    #                        |__/
    # Some translation services we pass text too may have issues with Emoji.
    # These functions will handle the conversion of Emoji to placeholders in the text before sending it to the service
    # as well as converting the placeholders back to Emoji after the service has returned the translated text.

    def stash_emoji(self):
        """
        Takes the Text in Translated and Extracted chunks and changes them into placeholders
        """
        if not self.parser_config.escape_emojis:
            return

        logging.debug(f"Stashing Emoji With Settings: Markers={self.parser_config.emoji_markers}, regex={self.parser_config.emoji_regex}")

        for et in self.extracted_text:
            et.text = self.stash_emoji_string(et.text.decode('utf-8')).encode('utf-8')

        for tc in self.translation_chunks:
            tc.text = self.stash_emoji_string(tc.text.decode('utf-8')).encode('utf-8')

    def stash_emoji_string(self, input_str: str) -> str:
        emoji_regex = re.compile(self.parser_config.emoji_regex)

        def repl(match: re.Match) -> str:
            r = ord(match.group()[0])
            return f"{self.parser_config.emoji_markers.start}{r}{self.parser_config.emoji_markers.end}"

        return emoji_regex.sub(repl, input_str)

    def unstash_emoji(self):
        """
        Replace the escaped emoji in both Modified and Original text with the actual Emoji
        """
        if not self.parser_config.escape_emojis:
            return

        logging.debug(f"Unstashing Emoji With Settings: Markers={self.parser_config.emoji_markers}, regex={self.parser_config.emoji_regex}")

        for i, et in enumerate(self.extracted_text):
            et.text = self.unstash_emoji_string(et.text.decode('utf-8')).encode('utf-8')
            et.modified = self.unstash_emoji_string(et.modified.decode('utf-8')).encode('utf-8') if et.modified else b""

        for i, tc in enumerate(self.translation_chunks):
            tc.text = self.unstash_emoji_string(tc.text.decode('utf-8')).encode('utf-8')
            tc.modified = self.unstash_emoji_string(tc.modified.decode('utf-8')).encode('utf-8') if tc.modified else b""

    def unstash_emoji_string(self, input_str: str) -> str:
        """
        Helper for UnstashEmoji
        This function can be used to "post-process" the input before it is parsed.
        """
        input_str = self.parser_config.emoji_post_func(input_str)

        re_emoji = re.compile(self.parser_config.emoji_regex)
        test_matches = re_emoji.findall(input_str)
        if not test_matches:
            logging.debug("No escaped entities found")
        else:
            logging.debug(f"Escaped entities found: count={len(test_matches)}")

        def repl(s: str) -> str:
            s = s.removeprefix(self.parser_config.emoji_markers.start)
            s = s.removesuffix(self.parser_config.emoji_markers.end)
            s = s.strip()
            try:
                r = chr(int(s))
                logging.info(f"Unstashing Emoji: s={s}, r={r}")
                return r
            except ValueError:
                return s

        return re_emoji.sub(lambda m: repl(m.group()), input_str)
    
    #    _____                   _____ _                 _
    #   |  __ \                 / ____| |               | |
    #   | |__) |__ ___      __ | |    | |__  _   _ _ __ | | _____
    #   |  _  // _` \ \ /\ / / | |    | '_ \| | | | '_ \| |/ / __|
    #   | | \ \ (_| |\ V  V /  | |____| | | | |_| | | | |   <\__ \
    #   |_|  \_\__,_| \_/\_/    \_____|_| |_|\__,_|_| |_|_|\_\___/

    # Extract the text and dump it all into chunks.
    # No care is made to make sure this text is rebuildable in any way, tho some configuration
    # is available to try and preserve formatting to an extent, if desired.
    # This method is mainly useful for a use case where we don't need to rebuild
    # our original file, but only care about the text that was extracted.
    # This will return the most human readable text possible.
    # @TODO -- This was written before a lot of other helpers -- see if this can leverage other funcs to reduce code duplication

    def get_raw_chunks(self) -> list[bytes]:
        """
        Get raw chunks of the file content.
        """
        logging.debug("Getting Raw Chunks")
        self.extract_if_empty()
        initial = self.get_plain_text()

        logging.debug(f"Initial Raw Text: {initial.decode('utf-8')}")

        chunks = []
        chunk = b""

        # Check if what we created has sentences.
        if has_sentence_delimiter(initial):
            # We are dealing with sentences most likely.
            # Lets try and do our best to preserve them.
            sentences = split_sentences(initial, self.parser_config.raw_chunk_config.trim_sentences)

            # Go sentence by sentence, building up chunks
            for sentence in sentences:
                if len(sentence) > self.parser_config.chunk_size:
                    if len(chunk) > 0:
                        chunks.append(chunk)
                    chunk = b""
                    split = split_sentence_into_fragments(sentence, self.parser_config.chunk_size)
                    chunks.extend(split)
                else:
                    text = sentence + b" "
                    if len(chunk) + len(text) > self.parser_config.chunk_size:
                        chunks.append(chunk)
                        chunk = b""
                    chunk += text
            # Add the last chunk
            if len(chunk) > 0:
                chunks.append(chunk)
        else:
            # We don't appear to have sentences. This is probably object detection, or something similar
            # Lets just drop a detection per line in chunks.
            for et in self.extracted_text:
                use_text = et.modified if et.modified else et.text
                text = use_text + b"\n"
                if len(text) > self.parser_config.chunk_size:
                    # dump what we already have and reset
                    if len(chunk) > 0:
                        chunks.append(chunk)
                    chunk = b""
                    split = split_by_byte_size(text, self.parser_config.chunk_size)
                    chunks.extend(split)
                else:
                    if len(chunk) + len(text) > self.parser_config.chunk_size:
                        chunks.append(chunk)
                        chunk = b""
                    chunk += text
            # Add the last chunk
            if len(chunk) > 0:
                chunks.append(chunk)

        return chunks

    def get_plain_text(self) -> bytes:
        """
        This will create a plain text document from the extracted text, but not chunk it.
        """
        logging.debug("Getting Plain Text")
        if self.plain_text is None:
            self.build_plain_text()
        return cast(bytes, self.plain_text)

    def build_plain_text(self):
        initial = self.convert("plaintext")
        if initial is None:
            logging.error("Error converting to plaintext")
            return

        # Perform some Cleanup
        if self.parser_config.raw_chunk_config.clean_plain_text:
            logging.debug("Cleaning up Plain Text")
            initial = cleanup_sentence(initial)

        logging.debug(f"Built Plain Text: {initial.decode('utf-8')}")
        # Update internal PlainText field
        self.plain_text = initial

    def get_sentences(self) -> list[bytes]:
        """
        Sentences from Plaintext
        """
        logging.debug("Getting Sentences from Plain Text")
        self.extract_if_empty()
        plain_text = self.get_plain_text()
        sentences = split_sentences(plain_text, self.parser_config.raw_chunk_config.trim_sentences)
        return sentences

def make_line(content: bytes, index: int, tio: "TextIO") -> bytes:
    """Prefix text with chunk markers."""
    marker = tio.parser_config.chunk_markers.start + "{}" + tio.parser_config.chunk_markers.end
    s = marker.format(index) + content.decode("utf-8")
    return s.encode("utf-8")

def inspect_bytes(content: bytes, extension: str) -> DetectedFiletype:
    """
    Return Detect results from filetypes.
    """
    dft, _ = detect(content, extension)
    return dft


def inspect(filepath: str) -> DetectedFiletype:
    """
    Run Inspect on a file.
    """
    extension = Path(filepath).suffix.lstrip(".").lower()
    failed = DetectedFiletype(
        mime="unknown",
        encoding="unknown",
        extension=extension,
    )

    try:
        with open(filepath, "rb") as f:
            content = f.read()
    except OSError:
        return failed

    return inspect_bytes(content, extension)


class ParserConfig(BaseModel):
    raw_chunk_config: "RawChunkConfig" = Field(
        alias="rawChunkConfig",
        default_factory=lambda: RawChunkConfig(
            cleanPlainText=True,
            trimSentences=True,
        ),
    )
    """Config for raw chunks"""

    chunk_size: int = Field(
        alias="chunkSize",
        default=MB,
    )
    """Size of the chunk to send to the translation engine"""

    chunk_markers: "ChunkMarkerConfig" = Field(
        alias="chunkMarkers",
        default_factory=lambda: ChunkMarkerConfig(
            start='<p translate="no">||',
            end="||</p>",
        ),
    )
    """Markers used to split chunks in a larger text block"""

    line_break_placeholder: str = Field(
        alias="lineBreakPlaceholder", default='<br lb="true"/>'
    )
    """Placeholder for line breaks"""

    escape_emojis: bool = Field(
        alias="escapeEmojis",
        default=False,
    )
    """Escape emojis in the text"""

    emoji_markers: "ChunkMarkerConfig" = Field(
        alias="emojiMarkers",
        default_factory=lambda: ChunkMarkerConfig(
            start='<p translate="no">emoji:',
            end=":emoji</p>",
        ),
    )
    """Markers to use for emojis"""

    emoji_regex: str = Field(
        alias="emojiRegex", default=r'<p translate="no">emoji:(\d+|\s+):emoji<\/p>'
    )
    """Regex to use for extracting emojis"""

    # EmojiPostFunc is not serializable; you could support it as a runtime-only field:
    emoji_post_func: Callable[[str], str] = Field(
        default=lambda input: input, exclude=True  # excluded from JSON
    )
    """Function to run on the emoji after it is extracted (not included in JSON)"""

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
        "protected_namespaces": (),
    }


class RawChunkConfig(BaseModel):
    clean_plain_text: bool = Field(alias="cleanPlainText")
    """Clean up the plain text output"""

    trim_sentences: bool = Field(alias="trimSentences")
    """Trim sentences to remove extra whitespace"""

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
        "protected_namespaces": (),
    }


default_parser_config = ParserConfig()

TEXTIO_VERSION = "1.5.1"
