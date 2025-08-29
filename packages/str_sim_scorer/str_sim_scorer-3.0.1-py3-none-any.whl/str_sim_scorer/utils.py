from __future__ import annotations

import logging
import warnings
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import sparse


def collect_alleles(
    df: pd.DataFrame, sample_id_col_name: str, locus_col_names: List[str]
) -> pd.DataFrame:
    """
    Given a data frame and the column names containing sample IDs and allele counts at
    STR loci, create a long data frame of unique alleles at observed loci for every
    sample.

    :param df: DataFrame containing STR profile data
    :param sample_id_col_name: Name of the column containing sample IDs
    :param locus_col_names: Names of columns containing allele counts at STR loci
    :return: a data frame of unique (sample ID, locus, allele count) records
    """

    # save the sample IDs as a category now incase `alleles` end up having zero rows
    sample_id_dtype = pd.CategoricalDtype(
        categories=df.sort_values(sample_id_col_name)[
            sample_id_col_name
        ].drop_duplicates()
    )

    # get all allele counts as a long data frame (one allele per profile-locus)
    alleles = df.melt(
        id_vars=[sample_id_col_name],
        value_vars=locus_col_names,
        var_name="locus",
        value_name="allele",
    ).dropna()

    alleles = alleles.set_index([sample_id_col_name, "locus"])

    # make data frame of unique (sample ID, locus, allele count) records
    alleles = (
        alleles["allele"]
        .str.extractall(r"(?P<allele>\d+(?:\.\d)?)")
        .reset_index()
        .drop(columns="match")
        .drop_duplicates()
        .sort_values([sample_id_col_name, "locus", "allele"])
        .reset_index(drop=True)
    )

    # use categories since this data frame and its derivations might be large
    alleles[sample_id_col_name] = alleles[sample_id_col_name].astype(sample_id_dtype)
    alleles[["locus", "allele"]] = alleles[["locus", "allele"]].astype("category")

    return alleles


def count_matching_alleles(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    allele_col_name: str,
    sample_ids: List[str],
) -> np.ndarray:
    """
    Given a long data frame with columns for sample ID, STR locus name (e.g. "tpox"),
    and count of a single allele (e.g. "11.1"), construct a symmetric numpy array such
    that cells `(i, j)` and `(j, i)` are the number of shared allele counts across all
    STR loci in samples `i` and `j`.

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param allele_col_name: name of column containing an allele count
    :param sample_ids: list of sample IDs (the output array rows/cols will be ordered
    by this list)
    :return: a symmetric matrix counting the matching alleles for pairs of samples
    """

    allele_presence = df.copy()

    # create indicator before pivoting into a sparse array
    allele_presence["present"] = True

    # pivot into wide data frame indicating presence of each allele counts at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        allele_presence = allele_presence.pivot(
            values="present",
            index=[locus_col_name, allele_col_name],
            columns=sample_id_col_name,
        ).notna()

    if len(allele_presence) == 0:
        # this might happen if intial _df has no rows
        return np.zeros((len(sample_ids), len(sample_ids)), dtype=np.uint16)

    # ensure pivot has a column for every sample ID
    allele_presence = allele_presence.reindex(columns=sample_ids, fill_value=False)

    # convert to sparse matrix (sample_id_col_name by locus_allele_cols)
    x = sparse.csc_array(allele_presence, dtype=np.uint16)

    # get symmetric matrix (ID by ID) of pairwise intersection set sizes
    return chunked_gram_matrix(x, max_chunk_size=500)


def chunked_gram_matrix(x: sparse.csc_array, max_chunk_size: int) -> np.ndarray:
    """
    Calculate the gram matrix ((x^T)x) for a given matrix `x` in chunks.

    :param x: a numpy array
    :param max_chunk_size: the maximum number of columns per chunk
    :return: the gram matrix
    """

    n_col = x.shape[1]  # pyright: ignore
    n_chunks = ceil(n_col / max_chunk_size)
    chunk_size = n_col / n_chunks

    y = np.zeros((n_col, n_col), dtype=np.uint16)

    def compute_chunk(i: int) -> Tuple[int, int, np.ndarray]:
        """
        Compute the gram matrix of a subset of `x`.

        :param i: the chunk index
        :return: a tuple of the row indexes and dense numpy array for this chunk
        """

        logging.info(f"Calculating gram matrix (chunk {i + 1} of {n_chunks})")

        i1 = ceil(i * chunk_size)
        i2 = min(ceil((i + 1) * chunk_size), n_col)

        chunk = x[:, i1:i2]  # pyright: ignore
        result = chunk.T.dot(x).toarray().astype(np.uint16)

        return i1, i2, result

    with ThreadPoolExecutor() as executor:
        for i1, i2, result in executor.map(compute_chunk, range(n_chunks)):
            y[i1:i2, :] = result

    return y


def compute_scores(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    allele_col_name: str,
    sample_ids: List[str],
    reference_sample_ids: Optional[List[str]] = None,
) -> Tuple[np.ma.MaskedArray, np.ma.MaskedArray]:
    """
    Given a long data frame with columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct numpy arrays counting
    the loci available used to compare each pair of samples and the similarity score
    (Tanabe or masters vs. reference depending on the pair).

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param allele_col_name: name of column containing an allele count
    :param sample_ids: list of sample IDs (the output array rows/cols will be ordered
    by this list)
    :param reference_sample_ids: a list of sample IDs that are for reference profiles
    :return: a tuple of (1) masked array counting loci used for pairs of samples and (2)
    masked array of scores
    """

    if reference_sample_ids is None:
        reference_sample_ids = []

    if not isinstance(df[sample_id_col_name].dtype, pd.CategoricalDtype):
        # force sample IDs to be categories in the provided order (for consistent
        # pivoting)
        df[sample_id_col_name] = pd.Categorical(
            df[sample_id_col_name], categories=sample_ids
        )

    # track which sample IDs (in their provided order) are references
    idx_is_ref = df.dtypes[sample_id_col_name].categories.isin(reference_sample_ids)

    # make masks for cells (pairs of samples) that are irrelevant under the two scoring
    # modes
    mvr_mask, tanabe_mask = make_masks(idx_is_ref)

    # combined mask for the final matrices (n_loci_used and scores)
    output_mask = tanabe_mask & mvr_mask

    # count number of shared alleles across all loci for all pairs of samples
    n_shared_alleles = count_matching_alleles(
        df, sample_id_col_name, locus_col_name, allele_col_name, sample_ids
    )

    # compute Tanabe scores for pairs of non-reference samples
    n_loci_used_tanabe, scores_tanabe = compute_tanabe_scores(
        df.loc[~df[sample_id_col_name].isin(reference_sample_ids)],
        sample_id_col_name,
        locus_col_name,
        sample_ids,
        n_shared_alleles,
        mask=tanabe_mask,
    )

    if len(reference_sample_ids) == 0:
        return n_loci_used_tanabe, scores_tanabe

    # compute masters vs. reference scores
    n_loci_used_mvr, scores_mvr = compute_master_vs_reference_scores(
        df,
        sample_id_col_name,
        locus_col_name,
        idx_is_ref,
        n_shared_alleles,
        mask=mvr_mask,
    )

    # take the union of the matrices under the two modes
    n_loci_used = np.ma.masked_array(
        n_loci_used_mvr.filled(0) + n_loci_used_tanabe.filled(0),
        mask=output_mask,
        fill_value=0,
    )

    scores = np.ma.masked_array(
        scores_mvr.filled(0) + scores_tanabe.filled(0),
        mask=output_mask,
        fill_value=0,
    )

    return n_loci_used, scores


def make_masks(idx_is_ref: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Construct masks for the two different STR profile similarity algorithms/scoring
    modes based on which sample IDs (i.e. the rows/cols of the similarity matrix being
    created) are references.

    :param idx_is_ref: a numpy array of booleans, where the nth item is True if
    `sample_ids[n]` is a reference
    :return: a tuple of boolean ndarrays to be used as masks in numpy masked arrays for
    (1) cells calculable using the Tanabe algorithm, and (2) cells calculable using the
    masters vs. reference algorithm
    """

    # cell is True when it's NOT a pair of samples that can be calculated using Tanabe
    # scoring
    tanabe_mask = np.logical_or(
        np.eye(len(idx_is_ref), dtype=bool),  # i==j (self-comparison)
        idx_is_ref[:, None] | idx_is_ref[None, :],  # either i,j is a ref
    )

    # cell is True when it's NOT a pair of samples that can be calculated using masters
    # vs. references scoring
    mvr_mask = np.logical_or(
        np.eye(len(idx_is_ref), dtype=bool),  # i==j (self-comparison)
        (idx_is_ref[:, None] | ~idx_is_ref[None, :]),  # i is ref, j is not
    )

    # there should be no pair of sample that's calculable both ways
    assert not (~tanabe_mask & ~mvr_mask).any()

    return mvr_mask, tanabe_mask


def compute_tanabe_scores(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    sample_ids: List[str],
    n_shared_alleles: np.ndarray,
    mask: np.ndarray,
) -> Tuple[np.ma.MaskedArray, np.ma.MaskedArray]:
    """
    Given a long data frame with columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct numpy arrays counting
    the loci available used to compare each pair of samples and the Tanabe score for
    pairs of samples where neither is a reference.

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param sample_ids: list of sample IDs (the output array rows/cols will be ordered
    by this list)
    :param n_shared_alleles: an array counting the number of common/shared alleles for
    pairs of samples across all loci
    :param mask: mask for pairs of samples that aren't relevant for Tanabe score
    calcuation (i.e. one of them is a reference)
    :return: a tuple of (1) masked array counting loci used for pairs of samples and (2)
    masked array of Tanabe scores
    """

    locus_presence = df.copy()

    # create indicator of there being at least one allele at a locus+sample
    locus_presence["present"] = True

    # pivot into wide data frame counting alleles observed at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        locus_presence = locus_presence.pivot_table(
            values="present",
            index=sample_id_col_name,
            columns=locus_col_name,
            aggfunc=np.sum,  # pyright: ignore
        )

    if len(locus_presence) == 0:
        # return empty arrays
        return np.ma.masked_array(
            np.zeros_like(mask), mask=mask, fill_value=0, dtype=np.int8
        ), np.ma.masked_array(
            np.full_like(mask, fill_value=np.NaN, dtype=np.float64),
            mask=mask,
            fill_value=0,
            dtype=np.float64,
        )

    # ensure pivot has a row for every sample ID
    locus_presence = locus_presence.reindex(index=sample_ids, fill_value=0)

    # we now have an array of sample IDs (rows) and locus counts (cols)
    n_alleles_at_locus = np.array(locus_presence)

    # Minkowski addition gives us the pairwise sums of the rows
    x = (n_alleles_at_locus[:, None] + n_alleles_at_locus).reshape(
        -1, n_alleles_at_locus.shape[1]
    )

    # construct another matrix of the same shape, but this time use 0/1 to indicate
    # which loci are present in both profiles for each pair
    has_alleles_at_locus = n_alleles_at_locus.copy()
    has_alleles_at_locus[has_alleles_at_locus > 0] = 1

    # tile `has_alleles_at_locus` into same shape as `x`
    xz = (has_alleles_at_locus[:, None] * has_alleles_at_locus).reshape(
        -1, has_alleles_at_locus.shape[1]
    )

    # sum the number of alleles in each pair, but only at loci where both profiles
    # had allele data
    nz_pair_combs = x * xz  # element-wise
    n_total_alleles = np.sum(nz_pair_combs, axis=1).reshape(
        (has_alleles_at_locus.shape[0], has_alleles_at_locus.shape[0])
    )

    # calculate the Tanabe score
    scores = np.divide(
        2.0 * n_shared_alleles,
        n_total_alleles,
        out=np.full_like(n_shared_alleles, fill_value=np.nan, dtype=np.float64),
        where=n_total_alleles != 0,
    )

    # calculate a symmetric array of the number of loci used in score calculation
    n_loci_used = np.sum(xz, axis=1).reshape(
        (has_alleles_at_locus.shape[0], has_alleles_at_locus.shape[0])
    )

    return (
        np.ma.masked_array(n_loci_used, mask=mask, fill_value=0, dtype=np.int8),
        np.ma.masked_array(scores, mask=mask, fill_value=0, dtype=np.float64),
    )


def compute_master_vs_reference_scores(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    idx_is_ref: np.ndarray,
    n_shared_alleles: np.ndarray,
    mask: np.ndarray,
) -> Tuple[np.ma.MaskedArray, np.ma.MaskedArray]:
    """
    Given a long data frame with columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct numpy arrays counting
    the loci available used to compare each pair of samples and the masters vs.
    reference similarity score for pairs of samples where the second of which is a
    reference.

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param idx_is_ref: a numpy array of booleans, where the nth item is True if
    `sample_ids[n]` is a reference
    :param n_shared_alleles: an array counting the number of common/shared alleles for
    pairs of samples across all loci
    :param mask: mask for pairs of samples that aren't relevant for masters vs.
    reference score calcuation
    :return: a tuple of (1) masked array counting loci used for pairs of samples and (2)
    masked array of masters vs. reference scores
    """

    # the subset of the diagonal for the ref elements gives the number of alleles
    # for reference samples
    n_ref_alleles_vec = n_shared_alleles[idx_is_ref, idx_is_ref]
    n_ref_alleles = np.zeros_like(n_shared_alleles)
    n_ref_alleles[:, idx_is_ref] = n_ref_alleles_vec

    # calculate the query vs. master scores
    scores = n_shared_alleles / n_ref_alleles

    # can do a direct count of unique loci for reference samples
    n_loci_used_vec = np.array(
        df.groupby(sample_id_col_name)[locus_col_name].nunique()
    )[idx_is_ref]
    n_loci_used = np.zeros_like(n_shared_alleles, dtype=np.int8)
    n_loci_used[:, idx_is_ref] = n_loci_used_vec[None, :]

    return (
        np.ma.masked_array(n_loci_used, mask=mask, fill_value=0, dtype=np.int8),
        np.ma.masked_array(scores, mask=mask, fill_value=0, dtype=np.float64),
    )


def scores_array_to_df(
    n_loci_used: np.ma.MaskedArray,
    scores: np.ma.MaskedArray,
    sample_id_col_name: str,
    sample_ids: List[str],
    reference_sample_ids: Optional[List[str]] = None,
    full: bool = False,
) -> pd.DataFrame:
    """
    Convert n_loci_used and score matrices into a long-form Pandas DataFrame.

    :param sample_id_col_name: name of column for sample IDs
    :param sample_ids: list of sample IDs corresponding to matrix rows/columns
    :param n_loci_used: n_loci_used array from `compute_scores` (common loci count)
    :param scores: scores array from `compute_scores`
    :param reference_sample_ids: a list of sample IDs that are for reference profiles
    :param full: if True, include both (id1, id2) and (id2, id1) rows for pairs where
    both represent a valid comparison (e.g. neither is a ref)
    :return: DataFrame with columns ```[
        '{sample_id_col_name}1',
        '{sample_id_col_name}2',
        'n_loci_used',
        'score'
    ]```
    """

    if reference_sample_ids is None:
        reference_sample_ids = []

    # ensure sample IDs are categorical
    sample_ids_cat = pd.CategoricalDtype(categories=sample_ids)

    # track which sample IDs (in their natural order) are references
    idx_is_ref = sample_ids_cat.categories.isin(reference_sample_ids)

    # reconstruct the masks the same way they were done during scoring
    mvr_mask, tanabe_mask = make_masks(idx_is_ref)

    if not full:
        # only use one of the triangular matrices for the Tanabe-scored pairs
        tanabe_mask[np.tril_indices_from(tanabe_mask, k=-1)] = True

    # get the final list of indexes for cells to be included in the returned data frame
    output_mask = tanabe_mask & mvr_mask
    idx = np.where(~output_mask)

    sample_ids_r = pd.Categorical.from_codes(idx[0], categories=sample_ids)
    sample_ids_c = pd.Categorical.from_codes(idx[1], categories=sample_ids)

    df = (
        pd.DataFrame(
            {
                f"{sample_id_col_name}1": sample_ids_r,
                f"{sample_id_col_name}2": sample_ids_c,
                "n_loci_used": n_loci_used[idx].data,
                "score": scores[idx].data,
            }
        )
        .astype({"n_loci_used": "uint8", "score": "Float64"})
        .sort_values([f"{sample_id_col_name}1", f"{sample_id_col_name}2"])
    )

    return df.reset_index(drop=True)  # pyright: ignore
