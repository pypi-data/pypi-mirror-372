from __future__ import annotations

from importlib import metadata as importlib_metadata

from .str_sim_scorer import StrSimScorer
from .utils import (
    collect_alleles,
    compute_scores,
    count_matching_alleles,
    scores_array_to_df,
)


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:
        return "unknown"


version: str = get_version()

__all__ = [
    "StrSimScorer",
    "collect_alleles",
    "compute_scores",
    "count_matching_alleles",
    "scores_array_to_df",
    "version",
]
