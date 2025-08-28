from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


def sha256(path: Path) -> str:
    with open(path, "rb") as f:
        b = f.read()
    return hashlib.sha256(b).hexdigest()


class FileType(Enum):
    FILE_TYPE_UNKNOWN = 0
    FILE_TYPE_FOLDER = 1
    FILE_TYPE_VIDEO = 2
    FILE_TYPE_AUDIO = 3
    FILE_TYPE_IMAGE = 4
    FILE_TYPE_RECORDING = 5
    FILE_TYPE_RECORDING_SESSION = 6
    FILE_TYPE_RECORDING_MAPPING = 7
    FILE_TYPE_PLATFORM = 8
    FILE_TYPE_INSTANCE = 9
    FILE_TYPE_SIGNAL_DATABASE = 10


@dataclass
class File:
    path: str
    type: FileType
    created_time: datetime
    modified_time: datetime
    size: int
