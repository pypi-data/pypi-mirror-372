
from .base import BaseFormatter
from .template import IMessageTemplate
from logging import LogRecord
from typing import Optional

class BasicFormatter(BaseFormatter[str]):
    def __init__(self, template:Optional[str|IMessageTemplate] = None):
        super().__init__(template)
        #if isinstance(template, str):
        #    template = MessageTemplate(template)
        #self.template:Optional[MessageTemplate] = template

    def format(self, record: LogRecord) -> str:
        if self.template:
            return self.template.render(record)
        return record.getMessage()
