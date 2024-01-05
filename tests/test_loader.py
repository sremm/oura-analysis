from oura_analysis.loader import OuraDataNumeric, OuraDataTimeseries


def test_load_oura_data():
    """Tests that OuraData can be loaded from a path"""
    data = OuraDataNumeric.from_path("tests/oura_trends_for_test.csv")
    data_table = data.data_table
    assert data_table.shape == (2, 54)
    assert "Average HRV" in data_table.columns


def test_load_oura_data_from_json():
    data = OuraDataTimeseries.from_path("tests/oura_timeseries_for_test.json")
    hr = data.heart_rate()
    hrv = data.hrv()
    assert len(hr) == len(hrv)
    assert len(hr) == 1
    assert len(hr["2023-11-02"]) == 6
