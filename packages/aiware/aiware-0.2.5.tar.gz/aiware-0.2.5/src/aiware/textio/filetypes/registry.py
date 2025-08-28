from pydantic import BaseModel

from aiware.textio.filetypes.parser import FiletypeParser


class SupportedTypes:
    """
    The supported types definition is a map of mimetypes to a list of filetype parsers.
    The order in the list will be determined the order as which filetype parse checks will be made.
    Example:

        supported_types = SupportedTypes(
            "text/xml": ["ttml", "xmlnodes"],
        )

    In the above definition, the mimetype "text/xml" will be checked against the parser "ttml" first,
    and then "xmlnodes" if "ttml" fails. If it reaches the end of a list without a successful parser
    match, then the mimetype is not supported.

    This is expected to be modified inside each filetype we add using supported_types.Add("ttml","text/xml") as an example
    """

    types: dict[str, list[str]] = {}

    @classmethod
    def add(cls, parser: str, media_type: str):
        if media_type in cls.types:
            cls.types[media_type].append(parser)
        else:
            cls.types[media_type] = [parser]


class ExtensionsMap:
    """
    If we have an extension, we can directly map it to parsers if we lack a mimetype
    In many cases, the mimetype is probably going to just be text/plain, text/xml, or application/json
    so having extension mapping can help avoid having to check through a ton of parsers.
    """

    extensions: dict[str, list[str]] = {}

    @classmethod
    def add(cls, parser: str, extension: str):
        if extension in cls.extensions:
            cls.extensions[extension].append(parser)
        else:
            cls.extensions[extension] = [parser]

class OutputDefinition(BaseModel):
    extension: str
    media_type: str


class OutputDefinitions:
    """
    Output Definitions is used when we want to write a file, and we need to know what extension and mimetype to use.
    """

    definitions: dict[str, OutputDefinition] = {}

    @classmethod
    def add(cls, parser: str, extension: str, media_type: str):
        cls.definitions[parser] = OutputDefinition(extension=extension, media_type=media_type)

class Registry:
    """
    The Registry is a map of filetype parsers (by string) to their respective types.
    You should leave this alone, and instead append to the Registry inside the init
    function for your filetype parser
    """

    parsers: dict[str, type[FiletypeParser]] = {}

    @classmethod
    def add(cls, parser: str, parser_type: type[FiletypeParser]):
        cls.parsers[parser] = parser_type

def register(parser: str, parser_type: type[FiletypeParser], extensions: list[str], media_types: list[str]):
    Registry.add(parser, parser_type)
    for extension in extensions:
        ExtensionsMap.add(parser, extension)
    for media_type in media_types:
        SupportedTypes.add(parser, media_type)

    OutputDefinitions.add(parser, extensions[0], media_types[0])
