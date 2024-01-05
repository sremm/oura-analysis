from __future__ import annotations
import pandas as pd
from pathlib import Path
import numpy as np
from typing import List, Dict
import json


class OuraDataNumeric:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    @property
    def data_table(self) -> pd.DataFrame:
        """Fetches data in a pandas DataFrame"""
        return self._data.copy()

    @staticmethod
    def from_path(path: Path) -> OuraDataNumeric:
        """Loads data from a path"""
        data = pd.read_csv(path, header=0)
        return OuraDataNumeric(pd.read_csv(path))


class OuraDataTimeseries:
    def __init__(self, data: Dict) -> None:
        self._data = data

    @staticmethod
    def from_path(path: Path) -> OuraDataTimeseries:
        """loads data from path"""
        with Path(path).open("r") as f:
            data = json.load(f)
        return OuraDataTimeseries(data)

    def heart_rate(self) -> Dict[str, np.array]:
        return {
            item["date"]: np.array(item["heart_rate"]["items"]).astype(float)
            for item in self._data["data"]
            if item["heart_rate"] is not None
        }

    def hrv(self) -> Dict[str, np.array]:
        return {
            item["date"]: np.array(item["hrv"]["items"]).astype(float)
            for item in self._data["data"]
            if item["hrv"] is not None
        }
