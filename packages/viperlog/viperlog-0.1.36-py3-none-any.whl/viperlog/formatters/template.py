import re
from logging import LogRecord
from typing import Dict, Callable, Tuple, List, Optional, Protocol

#ModifierFn = Callable[[str], str] | Callable[[str,str], str]
ModifierFn = Callable[[str,str|None], str]
PlaceholderModifierDef = Tuple[ModifierFn|None,str,str|None]
from ..logger import getLogger

from datetime import datetime, UTC
from dataclasses import dataclass

#pattern = re.compile(r"\$\{([^}]+)\}")
pattern = re.compile(r"\$\{([^}]+)}")


@dataclass(slots=True)
class TemplateColumn:
    type: str  # "literal" or "placeholder"
    #text: Optional[str] = None
    #variable: Optional[str] = None
    contents: Optional[str] = None
    modifiers: Optional[List[tuple]] = None


class IMessageTemplate(Protocol):
    def render(self, record: LogRecord) -> str:...

class MessageTemplate:
    """
    Parses a message template for use in a formatter
    The style is:
    ${variable}
    ${variable|modifier1}
    ${variable|modifier1|modifier2}
    ${variable|modifier1|modifier2=mod2value}
    Modifiers are executed in order from left to right, so if you do a padding and a max_length then the order matters
    These will get replaced, what is left is passed to the standard python logging library

    You could use:
    ${asctime|leftpad=5} to print the time padded to 5 chars on the left.
    Options:
    - asctime
    - name
    -
    """
    _started_at:datetime = datetime.now(UTC)
    _modifier_lookup:Dict[str,ModifierFn] = {
        # modifier names should all be lowercase here
        "upper": (lambda x,_ : x.upper()),
        "lower": (lambda x,_ : x.lower()),
        "trim": (lambda x,_ : x.strip()),
        "max_length": (lambda x,l : x[0:int(l)]),
        "pad_left": (lambda x,l : str(x).ljust(int(l), ' ')),
        "pad_right": (lambda x,l : str(x).rjust(int(l), ' ')),
        "pad_center": (lambda x,l : str(x).center(int(l), ' ')),
    }

    def __init__(self, template:str):
        self.template = template
        self._columns:List[TemplateColumn] = []
        self._parse_template()

    def _render_text(self, text:str, record:LogRecord) -> str:
       return text

    def _render_variable(self, variable: str, value: str, record:LogRecord) -> str:
        """Called after applying modifiers to the value"""
        return value

    def _prepare_variable(self, variable:str, value:str, record:LogRecord)->str:
        """ Called before applying modifiers to the value """
        return value

    def _get_variable_value(self, variable, record:LogRecord)->str:
        # process build-in variable names
        # TODO: complete this list
        if variable == 'message':
            return record.getMessage()
        elif variable == 'asctime':
            return "{:.3f}".format(record.relativeCreated)
            #diff = datetime.now(UTC) - MessageTemplate._started_at
            #return "{:.3f}".format(diff.total_seconds())
        elif variable == 'datetime':
            return datetime.now(UTC).isoformat().replace("+00:00", "Z")
        elif variable == 'date':
            return datetime.now(UTC).date().isoformat()
        elif variable == 'time':
            return datetime.now(UTC).time().replace(microsecond=0).isoformat()

        # attempt to fetch from record
        value = getattr(record, variable)
        if value is not None:
            return str(value)

        # Fall back on variable name
        return str(variable)  # raw variable as fallback

    def _get_modifier_fn(self, modifier:str)->Optional[ModifierFn]:
        name = modifier.lower()
        if name in MessageTemplate._modifier_lookup:
            fn = MessageTemplate._modifier_lookup[name]
            return fn
        return None


    def render(self, record:LogRecord)->str:
        result = []
        for c in self._columns:
            if c.type == 'literal':
                #result.append(c['text'])
                result.append(self._render_text(c.contents, record))
            elif c.type == 'placeholder':
                variable = c.contents
                modifiers = c.modifiers
                #value:str = str(variable) # raw variable as fallback

                value = self._get_variable_value(variable, record)

                value = self._prepare_variable(variable, value, record)
                if modifiers:
                    modifier:PlaceholderModifierDef|None = None
                    for modifier in modifiers:
                        if not modifier[0]:
                            # missing function
                            continue
                        value = modifier[0](value,modifier[2])
                result.append(self._render_variable(variable, value, record))
                #result.append(value)
            else:
                # this should never happen
                getLogger(self.__class__.__name__).error('Unknown column type ' + c['type'])

        return ''.join(result)

    def _parse_template(self):
        logger = getLogger(self.__class__.__name__)
        s = self.template
        results:List[TemplateColumn] = []
        last_end = 0

        for m in pattern.finditer(s):
            # literal before the match
            if m.start() > last_end:
                #results.append({"type": "literal", "text": s[last_end:m.start()]})
                results.append(TemplateColumn(type="literal", contents=s[last_end:m.start()]))

            # placeholder match
            parts = m.group(1).split("|")
            var = parts[0]
            mods = []
            for p in parts[1:]:
                name:str = p
                val:str|None = None
                fn:ModifierFn|None = None
                if "=" in p:
                    name, val = p.split("=", 1)
                #else:
                #    mods.append((p, None))
                fn = self._get_modifier_fn(name)
                if not fn:
                    logger.warning(f"Unknown modifier {name}")
                mods.append((fn, name, val))
            results.append(TemplateColumn(
                type="placeholder",
                contents=var,
                modifiers=mods
            ))
            #results.append({
            #    "type": "placeholder",
            #    "variable": var,
            #    "modifiers": mods
            #})

            last_end = m.end()

        # trailing literal
        if last_end < len(s):
            results.append(TemplateColumn(type="literal", contents= s[last_end:]))
            #results.append({"type": "literal", "text": s[last_end:]})

        self._columns = results

