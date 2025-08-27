
#from abc import ABC, abstractmethod
from logging import LogRecord, NOTSET
from typing import List, Dict, Optional

from .base import BaseFilter


class PackageFilter(BaseFilter):
    def __init__(self, package_level_map:Optional[Dict[str,int]] = None):
        self._map = {}
        self._map_keys = []
        self.set_package_level("", NOTSET)
        if package_level_map:
            for k,v in package_level_map.items():
                self.__add_package_key(k,v)
            self.__create_key_mapping()


    def __add_package_key(self, package_name:str, level:int)->None:
        # we append a "." to prevent partial package name matches.
        key = (package_name + '.').lower()
        self._map[key] = level

    def __create_key_mapping(self):
        # create a mapping, longest match first and then alphabetically because we can ;-)
        #self._map_keys = sorted([x for x in self._map.keys()], key=lambda s:(-len(s), s))
        self._map_keys = sorted(self._map.keys(), key=lambda s:(-len(s), s))

    def set_package_level(self, package_name:str, level:int)->None:
        """
        Sets min log levels for packages
        Configure this with an empty package name to set the root log level
        :param package_name:
        :param level:
        :return: True if the record should be filtered out, false if it is not matched
        """
        self.__add_package_key(package_name, level)
        self.__create_key_mapping()

    def is_match(self, record: LogRecord) -> bool:
        # find a match, check the longest variants first
        name = record.name + '.'
        for prefix in self._map_keys:
            #print(prefix, name)
            if name == prefix or name.startswith(prefix):
                level = self._map[prefix]
                return level > record.levelno
        # not in list, so not filtered at all
        return False



