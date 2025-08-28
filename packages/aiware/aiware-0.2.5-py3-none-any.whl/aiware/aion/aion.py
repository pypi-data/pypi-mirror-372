from pydantic import BaseModel, Field, ConfigDict, RootModel
from typing import Dict, List, Optional, Any, Union
from enum import Enum

AION_PACKAGE_VERSION = "1.3.1"

# Type aliases
AionVendor = Any  # Can be any arbitrary data
AionSchemaGUID = str
AionSchemaData = Dict[str, Any]


class AionObjectType(str, Enum):
    """Object type enumeration"""

    OBJECT = "object"  # Object detection
    FACE = "face"  # Face detection
    FACIAL_FEATURES = "facial-features"  # Facial Features
    LICENSE_PLATE = "licensePlate"  # License plate detection
    LOGO = "logo"  # Logo detection
    FINGERPRINT = "fingerprint"  # Audio fingerprinting
    SPEAKER = "speaker"  # Speaker recognition
    SOUND = "sound"  # Sound recognition
    CONCEPT = "concept"  # Concept recognition
    KEYWORD = "keyword"  # Keyword detection
    TEXT = "text"  # Recognized or extracted text (OCR / text extraction)
    NAMED_ENTITY = "namedEntity"  # Entity extraction
    FACE_VERIFICATION = "face-verification"  # Face verification
    SPEAKER_VERIFICATION = "speaker-verification"  # Speaker (voice) verification
    BARCODE = "barcode"  # Barcode


class AionTag(BaseModel):
    """AionTag are tags associated with this file (optional)

    Format: { "key": "<name>", "value": "<value>" }
      - For speech detected: "speech"="true"
      - For silence detected: "silence"="true"
      - For partial output: "partial"="true"
      - For ground truth:  Set tag to be "groundTruth": "<provider>"
      - For content moderation, Key must be: "moderation:adult", "moderation:violence", "moderation:nsfw",
        "moderation:nudity", "moderation:fakeNews", "moderation:pii"
      - For gender: "gender" : "male|female"
    """

    key: Optional[str] = Field(default=None, description="Key for the tag")
    value: Optional[str] = Field(
        default=None, description='(optional, if not specified defaults to "true")'
    )
    score: Optional[float] = Field(default=None, description="(optional)")

    model_config = ConfigDict(populate_by_name=True)


class AionSentiment(BaseModel):
    """AionSentiment provides a measurement of sentiment. Provides a scale of how negative to
    positive it is. If a single number is returned, then positive must be used

    Scale: 0.0 to 1.0 for all fields
    """

    positive_value: float = Field(alias="positiveValue", description="(required)")
    positive_confidence: Optional[float] = Field(
        default=None, alias="positiveConfidence", description="(optional)"
    )
    negative_value: float = Field(alias="negativeValue", description="(required)")
    negative_confidence: Optional[float] = Field(
        default=None, alias="negativeConfidence", description="(optional)"
    )

    model_config = ConfigDict(populate_by_name=True)


class AionGPS(BaseModel):
    """AionGPS GPS coordinates for this file (optional)

    Format: UTM (preferred) | WGS 1984
    """

    latitude: float = Field(description="GPS latitude coordinate")
    longitude: float = Field(description="GPS longitude coordinate")
    precision: Optional[float] = Field(default=None, description="in meters")
    direction: Optional[float] = Field(default=None, description="0-360")
    velocity: Optional[float] = Field(default=None, description="in meters/second")
    altitude: Optional[float] = Field(default=None, description="in meters")

    model_config = ConfigDict(populate_by_name=True)


class AionEmotion(BaseModel):
    """AionEmotion Emotions can be specified for whole file for overall tone, in an object (e.g. face
    recognition), in series (e.g. for transcript/sentiment), or in series.object (e.g. for
    time-specific face recognition)
    """

    emotion: Optional[str] = Field(
        default=None,
        description='"angry", "happy", "sad", etc. Can be any string field.',
    )
    emotion_value: Optional[float] = Field(
        default=None,
        alias="emotionValue",
        description="How strong.  0.0 = none, 1.0 = 100% (optional)",
    )
    emotion_confidence: Optional[float] = Field(
        default=None,
        alias="emotionConfidence",
        description="0.0 = 0%, 1.0 = 100% (optional)",
    )

    model_config = ConfigDict(populate_by_name=True)


class AionMedia(BaseModel):
    """AionMedia Media for linking to files when the engine's cognition results in file outputs"""

    asset_id: Optional[str] = Field(
        default=None, alias="assetId", description="ID of the associated asset"
    )
    content_type: Optional[str] = Field(
        default=None,
        alias="contentType",
        description="Content Type (optional). Format: Must be a valid MIME type (see https://www.iana.org/assignments/media-types/media-types.xhtml)",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language Identification (optional) Format: BCP-47 https://tools.ietf.org/rfc/bcp/bcp47.txt",
    )

    model_config = ConfigDict(populate_by_name=True)


class AionTranscription(BaseModel):
    """AionTranscription Transcription isauxiliary output used for speaker verification engines. Provides a confidence score between the transcribed audio and a specified phrase."""

    confidence: float = Field(description="(required)")
    text: Optional[str] = Field(default=None, description="(optional)")

    model_config = ConfigDict(populate_by_name=True)


class AionAge(BaseModel):
    """AionAge Age of object"""

    min: float = Field(description="in years")
    max: float = Field(description="in years")
    confidence: Optional[float] = Field(default=None, description="0.0 - 1.0")

    model_config = ConfigDict(populate_by_name=True)


class AionPoint(BaseModel):
    """Point in bounding polygon"""

    x: float = Field(
        description="horizontal fraction of media width, 0.0 = left, 1.0 = right"
    )
    y: float = Field(
        description="vertical fraction of media height, 0.0 = top, 1.0 = bottom"
    )

    model_config = ConfigDict(populate_by_name=True)


class AionPoly(RootModel[List[AionPoint]]):
    """AionPoly Bounding polygon. Ordered array of points defined clockwise for polygons and
    counter-clockwise for holes. Implicit line from last to first
    """

    model_config = ConfigDict(populate_by_name=True)


class AionFaceLandmark(BaseModel):
    """AionFaceLandmark Face landmark"""

    type: str = Field(description='Feature name like "mouth" or "chin" (required)')
    location_poly: Optional[AionPoly] = Field(
        default=None,
        alias="locationPoly",
        description="Polygon defining the feature (optional)",
    )

    model_config = ConfigDict(populate_by_name=True)


class AionObjectCategory(BaseModel):
    """AionObjectCategory Object detection / keyword detection (optional)"""

    class_name: Optional[str] = Field(
        default=None, alias="class", description='Example: "animal"'
    )
    id: Optional[str] = Field(
        default=None, alias="@id", description='Example: "kg:/m/0dl567"'
    )
    confidence: Optional[float] = Field(default=None, description="0.0 - 1.0")

    model_config = ConfigDict(populate_by_name=True)


class AionStructureData(RootModel[Dict[AionSchemaGUID, AionSchemaData]]):
    """AionStructureData  Structured data values. This is an object whose keys are the schema IDs and values are
    data that conforms to the schema.

    For Example:

    "structuredData": {
       "aaaa-aaaa-aaaa-...": {
          "key1" : "value",
          ...
          "keyN" : "valueN"
       },
       "bbbb-bbbb-bbbb-...": {
          "key1" : "value",
          ...
          "keyN" : "valueN"
       }
    }
    """

    model_config = ConfigDict(populate_by_name=True)


class AionObject(BaseModel):
    """AionObject Object Data in this section applies to things (e.g. faces, objects, logos, OCR) detected in
    the file but not in a specific time range.
    """

    type: Optional[AionObjectType] = Field(
        default=None, description="Type of object detected"
    )
    label: Optional[str] = Field(
        default=None,
        description="Main label for this object (required if no other identifying information (e.g. text, entityId) is specified, otherwise optional)",
    )
    uri: Optional[str] = Field(
        default=None,
        description="URI to thumbnail to show in the UI (optional). If not provided but boundingPoly is provided, one can be constructed dynamically from the boundingPoly.",
    )
    entity_id: Optional[str] = Field(
        default=None, alias="entityId", description="Entity reference (optional)"
    )
    library_id: Optional[str] = Field(
        default=None,
        alias="libraryId",
        description="Library containing the entity reference (optional)",
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score (optional). Format 0.0 (0% confident) to 1.0 (100% confident)",
    )
    text: Optional[str] = Field(
        default=None,
        description="Text found (required for OCR and text extraction, otherwise optional)",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language Identification (optional) Format: BCP-47 https://tools.ietf.org/rfc/bcp/bcp47.txt // NOT TECHNICALLY IN THE SPEC, BUT IN THE SPIRIT OF THE SPEC",
    )
    page: Optional[int] = Field(
        default=None,
        description="Document location (optional).      For referencing where in a document recognized text or entities or occur. It is highly recommended to define at least one to ensure proper ordering for indexing. For non-paginated document types like plain text files you can simply enumerate paragraphs based on line breaks.",
    )
    paragraph: Optional[int] = Field(
        default=None, description="Document location (optional)."
    )
    sentence: Optional[int] = Field(
        default=None, description="Document location (optional)."
    )
    mode: Optional[str] = Field(
        default=None,
        description='Used for verification engines (optional). Values: "enroll" or "verify"',
    )
    transcription: Optional[AionTranscription] = Field(
        default=None,
        description="Transcription (optional). An auxiliary output used for speaker verification engines.",
    )
    sentiment: Optional[AionSentiment] = Field(
        default=None, description="Sentiment (optional)"
    )
    emotions: Optional[List[AionEmotion]] = Field(
        default=None, description="Emotions (optional)"
    )
    age: Optional[AionAge] = Field(default=None, description="Age in years (optional)")
    face_landmarks: Optional[List[AionFaceLandmark]] = Field(
        default=None, alias="faceLandmarks", description="Face landmarks (optional)"
    )
    object_category: Optional[List[AionObjectCategory]] = Field(
        default=None,
        alias="objectCategory",
        description="Object detection / keyword detection (optional)",
    )
    region: Optional[str] = Field(
        default=None,
        description='Specifies the region match was found (optional). Valid values: "left", "right", "top", "bottom"',
    )
    bounding_poly: Optional[AionPoly] = Field(
        default=None, alias="boundingPoly", description="Bounding polygon (optional)"
    )
    gps: Optional[List[AionGPS]] = Field(
        default=None, description="GPS coordinates for this object (optional)"
    )
    structured_data: Optional[AionStructureData] = Field(
        default=None,
        alias="structuredData",
        description="Structured data values for this object (optional)",
    )
    reference_id: Optional[str] = Field(
        default=None,
        alias="referenceId",
        description="Reference ID that links to an embedding defined in the top level embedding section (optional)",
    )
    vendor: Optional[AionVendor] = Field(
        default=None, description="Custom data for this object (optional)"
    )
    fingerprint_vector: Optional[List[float]] = Field(
        default=None,
        alias="fingerprintVector",
        description="Fingerprint vector (optional)",
    )
    tags: Optional[List[AionTag]] = Field(
        default=None, description="Tags associated with this time slice (optional)"
    )

    model_config = ConfigDict(populate_by_name=True)


class AionWord(BaseModel):
    """AionWord A single word or phrase. This is in an ordered sequence of words, so utteranceLength means
    how many subsequent time-slices this word would override. For example, if the phrase sounds
    like "of thier own" but is actually "of throne" then the timeslices could look like this:

    "series" : [
        {
          "words": [
            { "word":"of", "confidence":0.9, "utteranceLength":1, "bestPath":true }
          ]
        },
        {
          "words": [
            { "word":"their", "confidence":0.5, "utteranceLength":1, "bestPath":false }
            { "word":"throne", "confidence":0.8, "utteranceLength":2, "bestPath":true }
          ]
        },
        {
          "words": [
            { "word":"own", "confidence":0.5, "utteranceLength":1, "bestPath": false }
          ]
        },
    ]

    Note that the booleans are pointers to booleans and are omitted when empty, so to set a
    boolean value, use the setters
    """

    word: str = Field(description="The word spoken (required)")
    confidence: Optional[float] = Field(
        default=None,
        description="The confidence level of the detected word spoken (optional). Format 0.0 - 1.0",
    )
    utterance_length: Optional[int] = Field(
        default=None,
        alias="utteranceLength",
        description="Number of consecutive time-slices the utterance spans (optional)",
    )
    best_path: Optional[bool] = Field(
        default=None,
        alias="bestPath",
        description="Is this word included in the best path through a transcript lattice? (optional)",
    )
    partial: Optional[bool] = Field(
        default=None,
        description="The word is part of a partial, in-progress, tentative transcription (optional)",
    )

    def set_best_path(self, value: bool) -> None:
        """Set best path value"""
        self.best_path = value

    def set_partial(self, value: bool) -> None:
        """Set partial value"""
        self.partial = value

    model_config = ConfigDict(populate_by_name=True)


class AionSeries(BaseModel):
    """AionSeries Time Series Data describes data that applies to a specific time range within the file. This
    is the most common section used for insights from audio and video files.
    """

    start_time_ms: int = Field(
        alias="startTimeMs",
        description="Time in milliseconds (relative to the source asset start) of the start of this time slice (required)",
    )
    stop_time_ms: int = Field(
        alias="stopTimeMs",
        description="Time in milliseconds (relative to the source asset start) of the end of this time slice (required)",
    )
    tags: Optional[List[AionTag]] = Field(
        default=None, description="Tags associated with this time slice (optional)"
    )
    summary: Optional[str] = Field(
        default=None, description="Summary of time slice (optional)"
    )
    speaker_id: Optional[str] = Field(
        default=None,
        alias="speakerId",
        description='Speaker identification (optional). Example "channel0", "speaker1"',
    )
    words: Optional[List[AionWord]] = Field(
        default=None,
        description="Transcript (optional) all word edges between 2 time nodes",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language Identification (optional) Format: BCP-47 https://tools.ietf.org/rfc/bcp/bcp47.txt",
    )
    sentiment: Optional[AionSentiment] = Field(
        default=None, description="Sentiment (optional)"
    )
    emotions: Optional[List[AionEmotion]] = Field(
        default=None, description="Emotions detected (optional)"
    )
    entity_id: Optional[str] = Field(
        default=None, alias="entityId", description="Entity reference (optional)"
    )
    library_id: Optional[str] = Field(
        default=None,
        alias="libraryId",
        description="Library containing the entity reference (optional)",
    )
    object: Optional[AionObject] = Field(
        default=None, description="Object (Face, Object, Logo, OCR, ..) (optional)"
    )
    gps: Optional[List[AionGPS]] = Field(
        default=None, description="GPS coordinates for this object (optional)"
    )
    structured_data: Optional[AionStructureData] = Field(
        default=None,
        alias="structuredData",
        description="Structured data values for this object (optional)",
    )
    media: Optional[List[AionMedia]] = Field(
        default=None,
        description="Media for linking to files when the engine's cognition results in file outputs (optional)",
    )
    reference_id: Optional[str] = Field(
        default=None,
        alias="referenceId",
        description="Reference ID that links to an embedding defined in the top level embedding section (optional)",
    )
    vendor: Optional[AionVendor] = Field(
        default=None, description="Custom data for this object (optional)"
    )

    model_config = ConfigDict(populate_by_name=True)


class AionEmbedding(BaseModel):
    """AionEmbedding Embedding data"""

    vector: List[float] = Field(description="Embedding vector")
    tags: Optional[List[AionTag]] = Field(
        default=None, description="Tags associated with this embedding"
    )
    reference_id: Optional[str] = Field(
        default=None, alias="referenceId", description="Reference ID - MUST BE A UUID"
    )

    model_config = ConfigDict(populate_by_name=True)


class AionProcessedStats(BaseModel):
    """AionProcessedStats are used to provide information for billing"""

    processed_bytes: Optional[str] = Field(
        default=None,
        alias="processedBytes",
        description="Number of bytes processed (optional)",
    )
    processed_media_seconds: Optional[str] = Field(
        default=None,
        alias="processedMediaSeconds",
        description="Number of seconds of media processed (optional)",
    )
    external_api_calls: Optional[str] = Field(
        default=None,
        alias="externalAPICalls",
        description="Number of External API Calls made by process (optional)",
    )
    llm_completion_tokens: Optional[str] = Field(
        default=None,
        alias="llmCompletionTokens",
        description="Number of completion tokens used by an LLM engine (optional)",
    )
    llm_prompt_tokens: Optional[str] = Field(
        default=None,
        alias="llmPromptTokens",
        description="Number of prompt tokens used by an LLM engine (optional)",
    )
    llm_total_tokens: Optional[str] = Field(
        default=None,
        alias="llmTotalTokens",
        description="Total number of tokens used by an LLM engine (optional)",
    )
    vendor: Optional[AionVendor] = Field(
        default=None, description="Vendor specific data (optional)"
    )

    model_config = ConfigDict(populate_by_name=True)


class Aion(BaseModel):
    """Aion struct represents the complete vtn-standard document"""

    # Preamble : The preamble contains various high-level information for this vtn-standard document
    schema_id: Optional[str] = Field(
        default=None,
        alias="schemaId",
        description="Schema version to validate engine outputs against (optional)",
    )
    source_engine_id: Optional[str] = Field(
        default=None,
        alias="sourceEngineId",
        description="Denotes the engine that created it (optional, provided by Veritone)",
    )
    source_engine_name: Optional[str] = Field(
        default=None,
        alias="sourceEngineName",
        description="Engine name used to generate output (optional, provided by Veritone)",
    )
    task_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="taskPayload",
        description="Task payload describing the associated tasks that summon the engine (optional, provided by Veritone)",
    )
    task_id: Optional[str] = Field(
        default=None,
        alias="taskId",
        description="The associated task (optional, provided by Veritone)",
    )
    generated_date: Optional[str] = Field(
        default=None,
        alias="generatedDateUtc",
        description='Date this document was generated (optional, set by Veritone if not included) Format: ISO8601 "2017-12-08T17:19:02Z"',
    )
    external_source_id: Optional[str] = Field(
        default=None,
        alias="externalSourceId",
        description="Vendor specific reference.  Used to map engine output against vendor referenced data ID (optional)",
    )
    validation_contracts: Optional[List[str]] = Field(
        default=None,
        alias="validationContracts",
        description="Specification for the contracts used for output validation (optional) See http://docs.veritone.com/#/engines/engine_standards/capability/ for more information",
    )

    # File Data : Data in this section applies to the file being analyzed as a whole. This is a
    # commonly used section for files with no time spans like images or text documents, or for
    # expressing summary data that spans the entire length of a media file.
    tags: Optional[List[AionTag]] = Field(
        default=None, description="Tags associated with this file (optional)"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language Identification (optional) Format: BCP-47 https://tools.ietf.org/rfc/bcp/bcp47.txt",
    )
    summary: Optional[str] = Field(
        default=None, description="Summary of document (optional)"
    )
    sentiment: Optional[AionSentiment] = Field(
        default=None, description="Sentiment (optional)"
    )
    gps: Optional[List[AionGPS]] = Field(
        default=None, description="GPS coordinates for this file (optional)"
    )
    emotions: Optional[List[AionEmotion]] = Field(
        default=None, description="Emotions for whole file (optional)"
    )
    media: Optional[List[AionMedia]] = Field(
        default=None,
        description="Media for linking to files when the engine's cognition results in file outputs (optional)",
    )
    vendor: Optional[AionVendor] = Field(
        default=None, description="Custom data for this document (optional)"
    )

    # Object Data
    object: Optional[List[AionObject]] = Field(
        default=None,
        description="Overall File Objects : Data in this section applies to things (e.g. faces, objects, logos, OCR) detected in the file but not in a specific time range.",
    )

    # Time Series Data
    series: Optional[List[AionSeries]] = Field(
        default=None,
        description="Data in this section applies to a specific time ranges within the file. This is the most common section used for insights from audio and video files.",
    )

    # Embedding Data
    embedding: Optional[List[AionEmbedding]] = Field(
        default=None, description="Embedding data for this file (optional)"
    )

    # Processing Stats
    processed_stats: AionProcessedStats = Field(
        default_factory=lambda: AionProcessedStats(),
        alias="processedStats",
        description="Processing statistics for this document (optional)",
    )

    model_config = ConfigDict(populate_by_name=True)
