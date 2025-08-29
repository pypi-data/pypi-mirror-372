from __future__ import annotations

from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd

from str_sim_scorer.utils import collect_alleles, compute_scores, scores_array_to_df


class StrSimScorer:
    """
    A class for performing STR (Short Tandem Repeat) profile comparisons.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        sample_id_col_name: str,
        locus_col_names: List[str],
        is_reference_col_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the StrSimScorer with STR profile data.

        :param df: DataFrame containing STR profile data
        :param sample_id_col_name: Name of the column containing sample IDs
        :param locus_col_names: Names of columns containing allele counts at STR loci
        """

        self.df = df.copy()
        self.sample_id_col_name = sample_id_col_name
        self.locus_col_names = locus_col_names
        self.is_reference_col_name = is_reference_col_name
        self.reference_sample_ids = []

        self.alleles = collect_alleles(
            self.df, self.sample_id_col_name, self.locus_col_names
        )

        self.sample_ids = self.alleles.dtypes[sample_id_col_name].categories.tolist()

        if is_reference_col_name is not None:
            self.reference_sample_ids = df.loc[
                df[is_reference_col_name], sample_id_col_name
            ].tolist()

        self._n_loci_used, self._scores = compute_scores(
            df=self.alleles,
            sample_id_col_name=self.sample_id_col_name,
            locus_col_name="locus",
            allele_col_name="allele",
            sample_ids=self.sample_ids,
            reference_sample_ids=self.reference_sample_ids,
        )

    def n_loci_used(self) -> np.ma.MaskedArray:
        """
        Count the number of loci used in score calculation for all pairs of profiles.

        :return: Symmetric matrix of common loci counts
        """

        return self._n_loci_used

    def scores(
        self, output: Literal["array", "df", "full_df"]
    ) -> Union[np.ma.MaskedArray, pd.DataFrame]:
        """
        Compute similarity scores for all profile pairs using the either they Tanabe or
        masters vs. reference algorithm, depending on the pair of samples.

        :param output: Output format
            - 'array' for a masked numpy array
            - 'df' for a long DataFrame
            - 'full_df' for a long DataFrame, including mirrors of rows where the scores
              of i,j and j,i are equivalent (i.e. the Tanabe scores)
        :return: scores (and number of loci used) in the requested format
        """

        if output == "array":
            return self._scores
        elif output == "df":
            return scores_array_to_df(
                n_loci_used=self._n_loci_used,
                scores=self._scores,
                sample_id_col_name=self.sample_id_col_name,
                sample_ids=self.sample_ids,
                reference_sample_ids=self.reference_sample_ids,
            )
        elif output == "full_df":
            return scores_array_to_df(
                n_loci_used=self._n_loci_used,
                scores=self._scores,
                sample_id_col_name=self.sample_id_col_name,
                sample_ids=self.sample_ids,
                reference_sample_ids=self.reference_sample_ids,
                full=True,
            )

    @property
    def n_profiles(self) -> int:
        """
        Get the number of samples/STR profiles in the dataset.

        :return: Number of unique profiles
        """

        return len(self.sample_ids)

    @property
    def n_loci(self) -> int:
        """
        Get the number of STR loci being analyzed.

        :return: Number of locus columns specified during initialization
        """

        return len(self.locus_col_names)
