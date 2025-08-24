from __future__ import annotations

from pathlib import Path

import pandas as pd


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
        return OuraData(pd.read_csv(path, sep=";", header=0))
