"""
SCD Case-Control Matching Plugin

This plugin provides epidemiologically sound case-control matching with proper
risk-set sampling methodology to avoid immortal time bias.
"""

from __future__ import annotations

import json
# from typing import TYPE_CHECKING

import polars as pl

from matching_plugin._internal import __version__ as __version__  # type: ignore
from matching_plugin._internal import format_match_output as _format_match_output_rust  # type: ignore
from matching_plugin._internal import match_scd_cases as _match_scd_cases_rust  # type: ignore

# if TYPE_CHECKING:
#     from matching_plugin.typing import IntoExprColumn

__all__ = [
    "__version__",
    "complete_scd_matching_workflow",
    "create_match_output_format",
]


def complete_scd_matching_workflow(
    mfr_data: pl.DataFrame,
    lpr_data: pl.DataFrame,
    vital_data: pl.DataFrame | None = None,
    matching_ratio: int = 5,
    birth_date_window_days: int = 30,
    parent_birth_date_window_days: int = 365,
    match_parent_birth_dates: bool = True,
    match_mother_birth_date_only: bool = False,
    require_both_parents: bool = False,
    match_parity: bool = True,
    algorithm: str = "risk_set",
) -> pl.DataFrame:
    """
    Complete SCD case-control matching workflow with risk-set sampling.

    Combines MFR/LPR data, performs matching, and returns the standard output format.
    Cases are processed chronologically by diagnosis date to avoid immortal time bias.
    Optionally incorporates vital status data for temporal validity.

    Parameters
    ----------
    mfr_data : pl.DataFrame
        Output from process_mfr_data() - eligible population with parent info
    lpr_data : pl.DataFrame
        Output from process_lpr_data() - SCD status for all eligible children
    vital_data : pl.DataFrame, optional
        Output from process_vital_status() - death/emigration events for children and parents
        If provided, ensures individuals and parents are alive/present at matching time
    matching_ratio : int, default 5
        Number of controls to match per case
    birth_date_window_days : int, default 30
        Maximum difference in days between case and control birth dates
    parent_birth_date_window_days : int, default 365
        Maximum difference in days between parent birth dates
    match_parent_birth_dates : bool, default True
        Whether to match on parent birth dates
    match_mother_birth_date_only : bool, default False
        Whether to match only on maternal birth dates
    require_both_parents : bool, default False
        Whether both parents are required for matching
    match_parity : bool, default True
        Whether to match on parity (birth order)
    algorithm : str, default "risk_set"
        Algorithm to use for matching. Options:
        - "risk_set": Basic risk-set sampling methodology
        - "spatial_index": Optimized with parallel processing and spatial indexing (3-10x faster)
        - "partitioned_parallel": Ultra-optimized with advanced data structures (20-60% faster than spatial_index)

    Returns
    -------
    pl.DataFrame
        Output format: MATCH_INDEX, PNR, ROLE, INDEX_DATE
        - MATCH_INDEX: Unique identifier for each case-control group (1:X matching)
        - PNR: Person identifier
        - ROLE: "case" or "control"
        - INDEX_DATE: SCD diagnosis date from the case

        When vital_data is provided:
        - Ensures children and parents are alive/present at matching time
        - Individuals who died or emigrated before case diagnosis cannot serve as controls
        - Chronological processing with proper temporal validity
    """
    # Validate algorithm parameter
    valid_algorithms = ["risk_set", "spatial_index", "partitioned_parallel"]
    if algorithm not in valid_algorithms:
        raise ValueError(
            f"Invalid algorithm '{algorithm}'. Must be one of: {valid_algorithms}"
        )

    algorithm_names = {
        "risk_set": "basic risk-set sampling",
        "spatial_index": "optimized with spatial indexing",
        "partitioned_parallel": "ultra-optimized with advanced data structures",
    }

    if vital_data is not None:
        print(
            f"Starting SCD case-control matching with vital status using {algorithm_names[algorithm]}..."
        )
    else:
        print(
            f"Starting SCD case-control matching using {algorithm_names[algorithm]}..."
        )

    # Combine MFR and LPR data
    combined_data = mfr_data.join(lpr_data, on="PNR", how="inner")
    print(f"Combined dataset: {len(combined_data):,} individuals")

    if vital_data is not None:
        print(f"Vital events data: {len(vital_data):,} events")

    # Perform risk-set sampling matching (with or without vital data)
    config = {
        "matching": {
            "birth_date_window_days": birth_date_window_days,
            "parent_birth_date_window_days": parent_birth_date_window_days,
            "match_parent_birth_dates": match_parent_birth_dates,
            "match_mother_birth_date_only": match_mother_birth_date_only,
            "require_both_parents": require_both_parents,
            "match_parity": match_parity,
            "matching_ratio": matching_ratio,
        },
        "algorithm": algorithm,
    }

    matched_cases = _match_scd_cases_rust(combined_data, vital_data, json.dumps(config))

    # Transform to requested output format
    output_df = _format_match_output_rust(matched_cases)

    print(f"Matching complete: {len(output_df):,} records")
    print(f"Match groups: {output_df['MATCH_INDEX'].n_unique():,}")
    print(f"Cases: {(output_df['ROLE'] == 'case').sum():,}")
    print(f"Controls: {(output_df['ROLE'] == 'control').sum():,}")

    return output_df


def create_match_output_format(matched_cases_df: pl.DataFrame) -> pl.DataFrame:
    """
    Transform matched cases into the standard output format.

    Parameters
    ----------
    matched_cases_df : pl.DataFrame
        Matched cases DataFrame from the Rust matching functions

    Returns
    -------
    pl.DataFrame
        Standard output format: MATCH_INDEX, PNR, ROLE, INDEX_DATE
        - MATCH_INDEX: Unique identifier for each case-control group
        - PNR: Person identifier
        - ROLE: "case" or "control"
        - INDEX_DATE: SCD diagnosis date from the case (same for all members of match group)
    """
    return _format_match_output_rust(matched_cases_df)
