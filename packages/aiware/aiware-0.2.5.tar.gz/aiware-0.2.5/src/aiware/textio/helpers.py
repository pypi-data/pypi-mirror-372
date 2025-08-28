from datetime import timedelta
from pathlib import Path
import re
from typing import List


MB = 1024 * 1024

# This function might need to be fleshed out more in the future.
# Its currently just assuming that string conversion in python will work all the time
def convert_to_utf8(content: bytes, encoding: str = "utf8") -> bytes:
	return bytes(str(content, encoding), encoding)

# Sentence delimiters (end of sentence)
SENTENCE_DELIMITERS: List[str] = [
    ".", "․", "﹒", "．", "·", "?", "!", ";", "…", "。"
]

# Only consider a sentence delimiter if followed by a space
SENTENCE_DELIMITERS_REGEX = re.compile(r'([.․﹒．·?!;…。]\s)')

# Sentence fragment delimiters (not full sentence-ending punctuation)
SENTENCE_FRAGMENT_DELIMITERS: List[str] = [
    ",", ":", "՝", "،", "߸", "᠂", "᠈", "–", "—", "、",
    "︐", "︑", "︓", "︱", "︲", "﹐", "﹑", "﹕", "﹘", "﹣",
    "，", "－", "：", "､"
]

SENTENCE_FRAGMENT_DELIMITERS_REGEX = re.compile(
    r'([,:՝،߸᠂᠈–—、︐︑︓︱︲﹐﹑﹕﹘﹣，－：､])'
)


def has_runes(content: bytes, runes: list[str]) -> bool:
    """Return True if any rune from the list is in the content"""
    for char in content.decode('utf-8'):
        if char in runes:
            return True
    return False


def has_sentence_delimiter(content: bytes) -> bool:
    """Check if content contains a sentence delimiter rune."""
    return has_runes(content, SENTENCE_DELIMITERS)

def get_extension_from_path(filepath: str) -> str:
	return Path(filepath).suffix.lstrip(".").lower()

def milliseconds_to_duration(ms: int) -> timedelta:
    return timedelta(milliseconds=ms)

def duration_to_milliseconds(d: timedelta) -> int:
    return int(d.total_seconds() * 1000)

def split_sentences(content: bytes, trim_space: bool) -> list[bytes]:
    """
    Split content into sentences using SENTENCE_DELIMITERS_REGEX.
    Trim space if trim_space=True.
    """
    d = "~|split|~"  # delimiter unlikely to be in text
    spliti = SENTENCE_DELIMITERS_REGEX.sub(lambda m: m.group(1) + d, str(content))
    split = spliti.split(d)
    out = []
    for s in split:
        if trim_space:
            s = s.strip()
        if len(s) > 0:
            out.append(s)
    return out


def split_sentence_into_fragments(content: bytes, fragment_max: int) -> list[bytes]:
    """
    Split a sentence into fragments using SENTENCE_FRAGMENT_DELIMITERS_REGEX.
    Fragments longer than fragment_max are split further by byte size.
    """
    d = "~|split|~"
    spliti = SENTENCE_FRAGMENT_DELIMITERS_REGEX.sub(lambda m: m.group(1) + d, str(content))
    split = [s.strip() for s in spliti.split(d)]
    fragments = []
    for s in split:
        if len(s) > fragment_max:
            smaller = split_by_byte_size(bytes(s, "utf8"), fragment_max)
            fragments.extend(smaller)
        else:
            fragments.append(s)
    return fragments

def split_by_byte_size(text: bytes, chunk_size: int) -> List[bytes]:
    """
    Split a byte array into chunks of a given size, breaking at spaces.
    """
    chunks: List[bytes] = []
    chunk: bytes = b""
    words = text.split(b" ")

    for word in words:
        use_word = word + b" "  # add space back
        if len(chunk) + len(use_word) > chunk_size:
            if chunk:
                chunks.append(chunk)
            chunk = b""
        chunk += use_word

    if chunk:
        chunks.append(chunk)

    return chunks

def cleanup_sentence(sentence: bytes) -> bytes:
    """Clean up a sentence by trimming, normalizing spaces, and fixing punctuation spacing."""
    # Decode to string for regex ops
    text = sentence.decode("utf-8", errors="ignore")
    
    # Trim whitespace
    text = text.strip()
    
    # Remove double/multiple spaces
    text = re.sub(r"\s+", " ", text)
    
    # Remove space before punctuation (any ASCII/non-ASCII punctuation)
    text = re.sub(r"\s([^\w\s])", r"\1", text)
    
    return text.encode("utf-8")
