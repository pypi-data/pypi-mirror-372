
from logging import LogRecord
from typing import List, Optional, Dict, Any
from viperlog.formatters import BaseFormatter, DictFormatter
from viperlog.formatters.base import BaseFormatter
from viperlog.formatters.dict_formatter import DictFormatter

#from viperlog.processors import BaseProcessor, GenericProcessor
from viperlog.processors.base_generic import GenericProcessor

import httpx

class HttpProcessor(GenericProcessor[Dict[str, Any]]):

    def __init__(self, url:str, formatter:Optional[BaseFormatter[Dict[str, Any]]]=DictFormatter()):
        super().__init__(formatter)
        self._url = url

    def process_messages(self, records: List[Dict[str, Any]]) -> None:
        body = records
        httpx.post(self._url, json = body)


#class HttpProcessor(BaseProcessor):
#    def __init__(self, url:str):
#        super().__init__()
#        self._url = url
#        self._formatter = DictFormatter()#
#
#    def process_records(self, records: List[LogRecord]) -> None:
#        body = [self._formatter.format(r) for r in records]
#        httpx.post(self._url, json = body)


