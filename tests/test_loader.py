from oura_analysis.loader import OuraData


def test_load_oura_data():
    """Tests that OuraData can be loaded from a path"""
    data = OuraData.from_path("tests/oura_trends_for_test.csv")
    data_table = data.data_table
    assert data_table.shape == (2, 54)
    assert "Average HRV" in data_table.columns
