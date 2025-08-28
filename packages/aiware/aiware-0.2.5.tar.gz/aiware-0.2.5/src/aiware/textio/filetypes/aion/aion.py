from datetime import timedelta
from aiware.aion import Aion
from aiware.aion.aion import AionObject, AionObjectType, AionSeries, AionWord
from aiware.textio.filetypes.parser import ExtractedText, FiletypeParser, FiletypeParserExpectations


import json
from typing import List, Optional

from aiware.textio.helpers import duration_to_milliseconds, milliseconds_to_duration


def get_aion_type(content: bytes) -> Optional[List[str]]:
    """Get the Aion type from content bytes

    Args:
        content: Raw bytes content to analyze

    Returns:
        List of Aion types if detected, None otherwise
    """
    try:
        aion = content_to_aion(content)
    except Exception:
        return None

    # If we have ValidationContracts, just return those
    if aion.validation_contracts and len(aion.validation_contracts) > 0:
        return aion.validation_contracts

    # if object[0].type exists, return that
    if aion.object and len(aion.object) > 0 and aion.object[0].type is not None:
        return [aion.object[0].type.value]

    # if series[0].words exists, return "transcript"
    if (
        aion.series
        and len(aion.series) > 0
        and aion.series[0].words
        and len(aion.series[0].words) > 0
    ):
        return ["transcript"]

    # if series[0].object.type exists, return that
    if (
        aion.series
        and len(aion.series) > 0
        and aion.series[0].object is not None
        and aion.series[0].object.type is not None
    ):
        return [aion.series[0].object.type.value]

    return None


def is_aion_type(content: bytes, aion_type: str) -> bool:
    """Check if content matches a specific Aion type

    Args:
        content: Raw bytes content to analyze
        aion_type: The Aion type to check for

    Returns:
        True if content matches the specified Aion type, False otherwise
    """
    aion_types = get_aion_type(content)
    if aion_types is None:
        return False

    return aion_type in aion_types


def content_to_aion(content: bytes) -> Aion:
    """Convert content bytes to Aion object

    Args:
        content: Raw bytes content to parse

    Returns:
        Parsed Aion object

    Raises:
        Exception: If content cannot be parsed as Aion object
    """
    try:
        # Decode bytes to string
        json_str = content.decode("utf-8")
        # Create Aion object from JSON data
        return Aion.model_validate_json(json_str)
    except:
        raise Exception("Failed to parse content as Aion object")


def extract_in_object(content: bytes, field: str) -> List[ExtractedText]:
    """Some AION replacements are as easy as extract a single field from an object
    There is no reason to rewrite this logic in every single Extract function

    Args:
        content: Raw bytes content to analyze
        field: Field name to extract ("label" or "text")

    Returns:
        extracted_text_list
    """
    # unmarshal content into aion struct
    aion = content_to_aion(content)

    resp: List[ExtractedText] = []

    # keep indexing outside our loops, because we may index
    # both an object and a series, and the rebuild order
    # needs to stay consistent
    index = 0

    # handle object first
    if aion.object and len(aion.object) > 0:
        for obj in aion.object:
            if field == "label" and obj.label:
                resp.append(
                    ExtractedText(text=obj.label.encode("utf-8"), index=[index])
                )
            elif field == "text" and obj.text:
                resp.append(ExtractedText(text=obj.text.encode("utf-8"), index=[index]))
            index += 1

    # then handle series
    if aion.series and len(aion.series) > 0:
        for series in aion.series:
            start_time = series.start_time_ms
            stop_time = series.stop_time_ms

            if series.object:
                if field == "label" and series.object.label:
                    resp.append(
                        ExtractedText(
                            text=series.object.label.encode("utf-8"),
                            index=[index],
                            startTime=milliseconds_to_duration(start_time),
                            endTime=milliseconds_to_duration(stop_time),
                        )
                    )
                elif field == "text" and series.object.text:
                    resp.append(
                        ExtractedText(
                            text=series.object.text.encode("utf-8"),
                            index=[index],
                            startTime=milliseconds_to_duration(start_time),
                            endTime=milliseconds_to_duration(stop_time),
                        )
                    )
            index += 1

    return resp


def aion_output(a: Aion) -> bytes:
    """
    Pretty print the JSON for an Aion object into a byte array.

    Mirrors Go:

        func aionOutput(a aion.Aion) ([]byte, error)
    """
    try:
        output = a.model_dump_json(by_alias=True, exclude_none=True, indent=2).encode("utf-8")
    except Exception as err:
        raise err

    return output


def convert_in_object(
    content: Optional[bytes], language: Optional[str], field: str, extracted: List[ExtractedText]
) -> bytes:
    """
    Make a new AION file and fill it with the extracted Text.

    Mirrors Go:

        func convertInObject(content []byte, language string, field string, extracted []ExtractedText) ([]byte, error)
    """

    aion_doc = Aion(object=[])

    if language:
        aion_doc.language = language

    object_type: AionObjectType = AionObjectType.TEXT
    if field == "label":
        object_type = AionObjectType.OBJECT

    for e in extracted:
        new_object = AionObject(type=object_type)
        text_value = str(e.modified if e.modified is not None else e.text)

        if field == "label":
            new_object.label = text_value
        elif field == "text":
            new_object.text = text_value

        aion_doc.object = aion_doc.object or []
        aion_doc.object.append(new_object)

    # pretty print the JSON in a byte array
    return json.dumps(aion_doc.model_dump(by_alias=True), indent=2).encode("utf-8")


def rebuild_in_object(
    content: Optional[bytes], language: Optional[str], field: str, extracted: List[ExtractedText]
) -> bytes:
    """The opposite of the above function, rebuilds the JSON output of an AION file.

    Args:
        content: Original content bytes
        language: Language code to set
        field: Field name to rebuild ("label" or "text")
        extracted: List of extracted text with modifications

    Returns:
        rebuilt_content_bytes
    """
    if content is None or len(content) == 0:
        return convert_in_object(content, language, field, extracted)

    aion = content_to_aion(content)

    # Build a map of modified objects
    modification_map: dict[int, bytes] = {}
    for e in extracted:
        if e.modified is not None:
            modification_map[e.index[0]] = e.modified

    # keep indexing outside our loops, because we may index
    # both an object and a series, and the rebuild order
    # needs to stay consistent
    index = 0

    # handle object first
    if aion.object and len(aion.object) > 0:
        for i in range(len(aion.object)):
            if index in modification_map:
                if field == "label":
                    aion.object[i].label = modification_map[index].decode("utf-8")
                elif field == "text":
                    aion.object[i].text = modification_map[index].decode("utf-8")
            index += 1

    # then handle series
    if aion.series and len(aion.series) > 0:
        for i, series in enumerate(aion.series):
            if index in modification_map:
                if series.object:
                    if field == "label":
                        series.object.label = modification_map[index].decode("utf-8")
                    elif field == "text":
                        series.object.text = modification_map[index].decode("utf-8")
                if language:
                    aion.series[i].language = language
            index += 1

    if language:
        aion.language = language

    # pretty print the JSON in a byte array
    return aion_output(aion)


class AbstractAionParser(FiletypeParser):
    pass


class AionTextParser(AbstractAionParser):
    language: Optional[str] = None

    @classmethod
    def is_a(cls, content: bytes) -> bool:
        return is_aion_type(content, "text")

    def extract(self, content: bytes) -> list[ExtractedText]:
        return extract_in_object(content, "text")

    def rebuild(self, content: Optional[bytes], extracted: list[ExtractedText]) -> bytes:
        return rebuild_in_object(content, self.language, "text", extracted)

    def set_language(self, lang: str):
        self.language = lang


class AionObjectParser(AbstractAionParser):
    language: Optional[str] = None

    @classmethod
    def is_a(cls, content: bytes) -> bool:
        return is_aion_type(content, "object")

    def extract(self, content: bytes) -> list[ExtractedText]:
        return extract_in_object(content, "label")

    def rebuild(self, content: Optional[bytes], extracted: list[ExtractedText]) -> bytes:
        return rebuild_in_object(content, self.language, "label", extracted)

    def set_language(self, lang: str):
        self.language = lang


class AionTranscriptParser(AbstractAionParser):
    language: Optional[str] = None

    @classmethod
    def is_a(cls, content: bytes) -> bool:
        return is_aion_type(content, "transcript")

    def expectations(self):
        return FiletypeParserExpectations(
            build_sentences=True
        )

    def extract(self, content: bytes) -> List[ExtractedText]:
        aion_obj = content_to_aion(content)

        resp: List[ExtractedText] = []
        index = 0

        for series in aion_obj.series or []:
            words = series.words or []

            if len(words) > 1:
                # Look for best path
                found_best_path = False
                for word in words:
                    if word.best_path:
                        found_best_path = True
                        resp.append(
                            ExtractedText(
                                index=[index],
                                text=word.word.encode(),
                                startTime=milliseconds_to_duration(
                                    series.start_time_ms
                                ),
                                endTime=milliseconds_to_duration(series.stop_time_ms),
                                extractedFrom={"series": series, "word": word},
                            )
                        )
                        break
                if not found_best_path:
                    # fallback to first
                    w = words[0]
                    resp.append(
                        ExtractedText(
                            index=[index],
                            text=w.word.encode(),
                            startTime=milliseconds_to_duration(series.start_time_ms),
                            endTime=milliseconds_to_duration(series.stop_time_ms),
                            extractedFrom={"series": series, "word": w},
                        )
                    )
            elif len(words) == 1:
                w = words[0]
                resp.append(
                    ExtractedText(
                        index=[index],
                        text=w.word.encode(),
                        startTime=milliseconds_to_duration(series.start_time_ms),
                        endTime=milliseconds_to_duration(series.stop_time_ms),
                        extractedFrom={"series": series, "word": w},
                    )
                )

            index += 1

        return resp

    def rebuild(self, content: Optional[bytes], extracted: List[ExtractedText]) -> bytes:
        if not content:
            # convert mode: new transcript
            a = Aion(
                schemaId="https://docs.veritone.com/schemas/vtn-standard/transcript.json",
                validationContracts=["transcript"],
                series=[],
            )
        else:
            a = content_to_aion(content)
            a.series = []

        for e in extracted:
            text = e.modified.decode() if e.modified else e.text.decode()

            word = (e.extracted_from or {}).get("word", AionWord(word=text))
            if isinstance(word, AionWord):
                word.word = text
            else:
                word = AionWord(word=text)

            series = (e.extracted_from or {}).get(
                "series", AionSeries(startTimeMs=0, stopTimeMs=0, words=[])
            )
            if isinstance(series, AionSeries):
                series.words = [word]
                series.start_time_ms = duration_to_milliseconds(
                    e.start_time or timedelta()
                )
                series.stop_time_ms = duration_to_milliseconds(
                    e.end_time or timedelta()
                )
            else:
                series = AionSeries(
                    startTimeMs=duration_to_milliseconds(e.start_time or timedelta()),
                    stopTimeMs=duration_to_milliseconds(e.end_time or timedelta()),
                    words=[word],
                )

            if self.language:
                series.language = self.language

            a.series = a.series or []
            a.series.append(series)

        if self.language:
            a.language = self.language

        return aion_output(a)

    def set_language(self, lang: str):
        self.language = lang
