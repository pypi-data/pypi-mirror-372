from logging import LogRecord, DEBUG, INFO, WARNING, ERROR, FATAL

from viperlog.formatters import BasicFormatter
from viperlog.formatters.base import BaseFormatter
from typing import Optional
from .console_template import ConsoleTemplate, DEFAULT_CONSOLE_TEMPLATE


class ConsoleFormatter(BasicFormatter): #(BaseFormatter[str]):
    def __init__(self, template:Optional[str|ConsoleTemplate] = DEFAULT_CONSOLE_TEMPLATE):
        if template is None:
            template = DEFAULT_CONSOLE_TEMPLATE
        if isinstance(template,str):
            template = ConsoleTemplate(template)
        super().__init__(template)

    # def format(self, record: LogRecord) -> str:
    #     result = []
    #     level_style = "italic"
    #     if record.levelno == INFO:
    #         level_style += " white"
    #     elif record.levelno == WARNING:
    #         level_style += " orange"
    #     elif record.levelno == ERROR:
    #         level_style += " red"
    #     elif record.levelno == FATAL:
    #         level_style += " bold red"
    #     result.append('[' + level_style + ']')
    #     result.append(record.levelname.upper())
    #     result.append('[/' + level_style + '] ')
    #
    #     # TODO: format & replace message contents
    #     result.append(record.getMessage())
    #     return "".join(result)

