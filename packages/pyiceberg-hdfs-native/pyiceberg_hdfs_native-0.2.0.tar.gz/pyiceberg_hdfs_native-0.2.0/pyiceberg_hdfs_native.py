from functools import lru_cache
from typing import Callable
from fsspec import AbstractFileSystem
import hdfs_native.fsspec
from pyiceberg.io.fsspec import FsspecFileIO
from pyiceberg.typedef import Properties


class HdfsFileIO(FsspecFileIO):
    def __init__(self, properties: Properties) -> None:
        super().__init__(properties)
        self.get_fs: Callable[[str], AbstractFileSystem] = lru_cache(self._get_fs)

    def _get_fs(self, scheme: str) -> AbstractFileSystem:
        if scheme != "hdfs":
            raise ValueError(f"Unsupported scheme: {scheme}")
        return hdfs_native.fsspec.HdfsFileSystem()
