from logging import LogRecord
from typing import List, Optional, Literal
from viperlog.processors.base_string import BaseStringProcessor
#from plugin_viperlog_console.console_formatter import ConsoleFormatter
from .console_formatter import ConsoleFormatter, ConsoleTemplate
from rich import print as rich_print
from rich.console import Console

class ConsoleProcessor(BaseStringProcessor):
    def __init__(self, color_system:Optional[
            Literal["auto", "standard", "256", "truecolor", "windows"]
        ] = "auto", template:Optional[str|ConsoleTemplate]=None):
        super().__init__(ConsoleFormatter(template=template))
        #color_system = "standard"
        self.supports_batching = False
        self._console = Console(color_system=color_system)

    def process_messages(self, records: List[str]) -> None:
        for r in records:
            #rich_print(r)
            self._console.print(r)



