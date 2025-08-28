
from aiware.textio.filetypes.plaintext.plaintext import PlaintextParser
from aiware.textio.filetypes.registry import register


register("plaintext", PlaintextParser, ["txt"], ["text/plain"])
