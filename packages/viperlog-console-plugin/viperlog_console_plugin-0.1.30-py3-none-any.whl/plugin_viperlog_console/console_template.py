from logging import LogRecord, INFO, WARNING, ERROR, FATAL
from typing import Optional, Dict
from viperlog.formatters.template import MessageTemplate, ModifierFn

DEFAULT_CONSOLE_TEMPLATE:str = "${markup|literal=:smiley:} ${levelname|upper|pad_left=5|max_length=5}: ${date|style=italic} ${time|style=bold italic}   ${asctime}  ${message}"

from rich.markup import escape as rich_escape

class ConsoleTemplate(MessageTemplate):
    f"""
    In addition to everything supported by the  {MessageTemplate} class
    this class adds some console features:
    - style modifier: applies the style to the value
    - markup variable + literal modifier - inserts the literal value unescaped (e.g. $&#123;markup|literal=:emoji:&#125;
    
    """
    _modifier_lookup:Dict[str,ModifierFn] = {
        # modifier names should all be lowercase here
        # style modifier applies styling ...
        "style": (lambda x,l : ''.join(['[', l, ']', x, '[/]'])),
        "literal": (lambda x,l : str(l)),
    }

    def __init__(self, template: str):
        super().__init__(template)

    def _get_variable_value(self, variable, record: LogRecord) -> str:
        if variable == "markup":
            return "xx"
        return super()._get_variable_value(variable, record)

    def _get_modifier_fn(self, modifier:str)->Optional[ModifierFn]:
        name = modifier.lower()
        if name in ConsoleTemplate._modifier_lookup:
            return ConsoleTemplate._modifier_lookup[name]
        if name in MessageTemplate._modifier_lookup:
            return MessageTemplate._modifier_lookup[name]
        return None

    def _render_text(self, text:str, record:LogRecord) -> str:
        # escaping is done here
        return rich_escape(text)
    def _prepare_variable(self, variable:str, value:str, record:LogRecord) ->str:
        # escaping is done here
        return rich_escape(value)

    def _render_variable(self, variable: str, value: str, record:LogRecord) -> str:
        # when we get here the value should already have been escaped
        #  so it is safe to add markup

        # add some color
        if variable == "markup":
            # contents should have been be replaced with a modifier
            return value
        if variable == "level" or variable == "levelno" or variable == "levelname":
            level_style = "italic"
            if record.levelno == INFO:
                level_style += " white"
            elif record.levelno == WARNING:
                level_style += " orange"
            elif record.levelno == ERROR:
                level_style += " red"
            elif record.levelno == FATAL:
                level_style += " bold red"
            return '['+level_style+']' + value + '[/]'

        return value
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