from __future__ import annotations  # used to type hint the return of init_from_file
from pathlib import Path
from typing import Optional, List
from abc import ABC, abstractmethod
from geopic_tag_reader import reader


class MetadataHandler(ABC):
    @staticmethod
    @abstractmethod
    def new_from_file(file_name: Path) -> Optional[MetadataHandler]:
        """
        Method to create the handler from a file.
        If the handler cannot be created from this file, returns None
        """
        pass

    @abstractmethod
    def get(self, file_name: Path) -> Optional[reader.PartialGeoPicTags]:
        """
        Method overloaded by the MetadataHandler

        It takes the path of a picture file and return a PartialGeoPicTags if possible
        """
        return None


def find_handler(path) -> Optional[MetadataHandler]:
    """
    Find a MetadataHandler in the directory.

    Each registered MetadataHandler is responsible to know if they can be inited by a given file
    """
    from . import csv

    handler_list: List[type[MetadataHandler]] = [
        # add all handlers here
        csv.CsvMetadataHandler,
    ]
    for f in path.iterdir():
        if not f.is_file():
            continue

        for handler_class in handler_list:
            h = handler_class.new_from_file(f)
            if h:
                return h

    return None
