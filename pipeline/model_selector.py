from typing import List, Dict, Optional
import os

# Force UTF-8 to avoid nn-dataset Windows encoding bug
os.environ["PYTHONUTF8"] = "1"

class ModelSelectionError(Exception):
    pass

def _import_nn_api():
    try:
        from ab.nn.api import data
        return data
    except ImportError as e:
        raise ModelSelectionError(
            "nn-dataset API not installed. Install with:\n"
            "pip install --no-cache-dir git+https://github.com/ABrain-One/nn-dataset "
            "--upgrade --force"
        ) from e


def select_models(
    mode: str,
    names: Optional[List[str]] = None,
    task: Optional[str] = None,
    dataset: Optional[str] = None,
    only_best: bool = True,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    Select model metadata from nn-dataset via API.
    Returns metadata only (no files).
    """

    data_fn = _import_nn_api()

    try:
        df = data_fn(
            task=task,
            dataset=dataset,
            only_best_accuracy=only_best
        )
    except Exception as e:
        raise ModelSelectionError(f"Failed to query nn-dataset API: {e}") from e

    if df.empty:
        raise ModelSelectionError("No models returned by nn-dataset API")

    all_names = df["nn"].unique().tolist()

    if mode == "all":
        selected_names = all_names

    elif mode == "one":
        if not names or len(names) != 1:
            raise ModelSelectionError("Mode 'one' requires exactly one name")
        selected_names = names

    elif mode == "many":
        if not names:
            raise ModelSelectionError("Mode 'many' requires names")
        selected_names = names

    else:
        raise ModelSelectionError(f"Invalid mode '{mode}'")

    df_selected = df[df["nn"].isin(selected_names)]

    if df_selected.empty:
        raise ModelSelectionError(
            f"No models matched selection. Requested={selected_names}"
        )

    records = df_selected.to_dict("records")

    if limit is not None:
        records = records[:limit]

    return records
