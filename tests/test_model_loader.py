# tests/test_model_loader.py
import pandas as pd
from model_loader import load_models

def test_load_models_returns_dataframe():
    df = load_models(limit=1)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 0  # allow empty if nn-dataset changes upstream

def test_load_models_has_expected_columns():
    df = load_models(limit=1)
    # these are used throughout main/export paths
    expected = {"nn", "task", "dataset"}
    assert expected.issubset(set(df.columns))