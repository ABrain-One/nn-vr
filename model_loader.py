"""Load model metadata rows from nn-dataset (see ab.nn.api.data)."""

from __future__ import annotations

import pandas as pd
from ab.nn.api import data


def load_models(
    limit: int | None = None,
    nn: str | None = None,
) -> pd.DataFrame:
    """
    Return rows with nn_code, task, dataset, metric, prm, etc.
    `nn` filters by model name; `limit` maps to max_rows.
    """
    return data(nn=nn, max_rows=limit)
