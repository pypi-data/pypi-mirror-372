from .aion import AionTextParser, AionObjectParser, AionTranscriptParser
from aiware.textio.filetypes.registry import register

# https://docs.veritone.com/schemas/vtn-standard/text/text.json
register("aion-text", AionTextParser, ["aion", "json"], ["application/vnd.veritone.aion+json", "application/json"])
# https://docs.veritone.com/schemas/vtn-standard/object/object.json
register("aion-object", AionObjectParser, ["aion", "json"], ["application/vnd.veritone.aion+json", "application/json"])
# https://docs.veritone.com/schemas/vtn-standard/transcript/transcript.json
register("aion-transcript", AionTranscriptParser, ["aion", "json"], ["application/vnd.veritone.aion+json", "application/json"])
