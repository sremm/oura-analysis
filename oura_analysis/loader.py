from __future__ import annotations
import pandas as pd
from pathlib import Path


class OuraData:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @property
    def data_table(self) -> pd.DataFrame:
        """Fetches data in a pandas DataFrame"""
        return self._data.copy()

    @staticmethod
    def from_path(path: Path) -> OuraData:
        """Loads data from a path"""
        data = pd.read_csv(path, header=0)
        return OuraData(pd.read_csv(path))
