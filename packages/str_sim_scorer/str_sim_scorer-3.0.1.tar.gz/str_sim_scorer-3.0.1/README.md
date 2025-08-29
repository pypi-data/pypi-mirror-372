from str_sim_scorer import StrSimScorer

# STR Similarity Scorer

This repository contains a Python package to compute the [similarity score](https://www.cellosaurus.org/str-search/help.html) for pairs of records in an input data frame, some of which may be optionally specified as reference profiles.

This package computes the number of matching and total alleles and common loci largely through matrix algebra, so it's fast enough to be run on thousands of samples (millions of pairs).

## Installation

Install `str_sim_scorer` [from PyPI](https://pypi.org/project/str_sim_scorer/) using the package manager of your choice.

## Usage

The `StrSimScorer` class provides an object-oriented interface with caching for efficient computation:

```py
import pandas as pd
from str_sim_scorer import StrSimScorer

df = pd.DataFrame(
    [
        {
            "id": "sample1",
            "csf1po": "11, 13",
            "d13s317": "11, 12",
            "d16s539": "9, 12",
            "d18s51": "11, 19",
            "d21s11": "29, 31.2",
            "d3s1358": "17",
            "d5s818": "13",
            "d7s820": "10",
            "d8s1179": "12, 13",
            "fga": "24",
            "penta_d": "9, 12",
            "penta_e": "7, 13",
            "th01": "6, 8",
            "tpox": "11",
        },
        {
            "id": "sample2",
            "csf1po": "12",
            "d13s317": "11, 12",
            "d16s539": "8, 12",
            "d18s51": "17, 18",
            "d21s11": "28, 33.2",
            "d3s1358": "16",
            "d5s818": "11",
            "d7s820": "8, 13",
            "d8s1179": "9, 10",
            "fga": "21, 25",
            "penta_d": "9, 12",
            "penta_e": "7",
            "th01": "7, 9.3",
            "tpox": "8",
        },
        {
            "id": "sample3",
            "csf1po": "11, 12",
            "d13s317": "8",
            "d16s539": "11",
            "d18s51": "18",
            "d21s11": pd.NA,
            "d3s1358": "16",
            "d5s818": "10, 11",
            "d7s820": "12",
            "d8s1179": "11",
            "fga": "26",
            "penta_d": pd.NA,
            "penta_e": "13.1, 12.1",
            "th01": "6, 9.3",
            "tpox": "12",
        },
    ]
)

# Create the comparison object
scorer = StrSimScorer(
    df,
    sample_id_col_name="id",
    locus_col_names=[
        "csf1po",
        "d13s317",
        "d16s539",
        "d18s51",
        "d21s11",
        "d3s1358",
        "d5s818",
        "d7s820",
        "d8s1179",
        "fga",
        "penta_d",
        "penta_e",
        "th01",
        "tpox",
    ],
)

scores = scorer.scores(output="df")
```

### Output formats

Using `output="df"` returns a DataFrame for distinct pairs of IDs:
```
>>> print(scores)
       id1      id2  n_loci_used     score
0  sample1  sample2           14   0.26087
1  sample1  sample3           12  0.114286
2  sample2  sample3           12  0.285714
```

Using `output="full_df"` returns the same data with both (id1, id2) and (id2, id1) rows:
```
>>> scores_sym = comp.scores(output="symmetric_df")
>>> print(scores_sym)
       id1      id2  n_loci_used     score
0  sample1  sample2           14   0.26087
1  sample1  sample3           12  0.114286
2  sample2  sample1           14   0.26087
3  sample2  sample3           12  0.285714
4  sample3  sample1           12  0.114286
5  sample3  sample2           12  0.285714
```

Using `output="array"` returns the raw similarity matrix as a numpy [masked array](https://numpy.org/doc/stable/reference/routines.ma.html):
```
>>> array = comp.scores(output="array")
>>> print(array)
masked_array(
  data=[[--, 0.2608695652173913, 0.11428571428571428],
        [0.2608695652173913, --, 0.2857142857142857],
        [0.11428571428571428, 0.2857142857142857, --]],
  mask=[[ True, False, False],
        [False,  True, False],
        [False, False,  True]],
  fill_value=0.0)
>>> print(scorer.sample_ids) # the row/col names of the matrix 
['sample1', 'sample2', 'sample3']
```

Only cells representing a valid and relevant pair of samples are unmasked, which is why the diagonal is masked in this example. 

### Algorithms

#### Tanabe / non-empty markers

This package implements two [algorithms](https://www.cellosaurus.org/str-search/help.html). For a pair of samples where neither is indicated as a "reference", the score is calculated using the Tanabe algorithm under the "non-empty markers" mode. Thus, `n_loci_used` is the number of loci where both samples had data.

#### Master vs. reference / reference markers

If your input data frame has a boolean column indicating that some samples are references (e.g. STR profiles from a canonical source like Cellosaurus), set the `is_reference_col_name` argument to the name of that column. A cell `i,j` in the scores matrix will be computed using the "masters vs. reference" algorithm if `scorer.sample_ids[i]` is a master (i.e. real sample) and `scorer.sample_ids[j]` is a reference. In ths case, `n_loci_used` is the number of loci present in the reference.

```py
import pandas as pd
from str_sim_scorer import StrSimScorer

df = pd.DataFrame(
    [
        {
            "id": "sample1",
            "is_ref": False,
            "csf1po": "11, 13",
            "d13s317": "11, 12",
            "d16s539": "9, 12",
            "d18s51": "11, 19",
            "d21s11": "29, 31.2",
            "d3s1358": "17",
            "d5s818": "13",
            "d7s820": "10",
            "d8s1179": "12, 13",
            "fga": "24",
            "penta_d": "9, 12",
            "penta_e": "7, 13",
            "th01": "6, 8",
            "tpox": "11",
        },
        {
            "id": "sample2",
            "is_ref": True,
            "csf1po": "12",
            "d13s317": "11, 12",
            "d16s539": "8, 12",
            "d18s51": "17, 18",
            "d21s11": "28, 33.2",
            "d3s1358": "16",
            "d5s818": "11",
            "d7s820": "8, 13",
            "d8s1179": "9, 10",
            "fga": "21, 25",
            "penta_d": "9, 12",
            "penta_e": "7",
            "th01": "7, 9.3",
            "tpox": "8",
        },
        {
            "id": "sample3",
            "is_ref": False,
            "csf1po": "11, 12",
            "d13s317": "8",
            "d16s539": "11",
            "d18s51": "18",
            "d21s11": pd.NA,
            "d3s1358": "16",
            "d5s818": "10, 11",
            "d7s820": "12",
            "d8s1179": "11",
            "fga": "26",
            "penta_d": pd.NA,
            "penta_e": "13.1, 12.1",
            "th01": "6, 9.3",
            "tpox": "12",
        },
    ]
)

scorer = StrSimScorer(
    df,
    sample_id_col_name="id",
    locus_col_names=[
        "csf1po",
        "d13s317",
        "d16s539",
        "d18s51",
        "d21s11",
        "d3s1358",
        "d5s818",
        "d7s820",
        "d8s1179",
        "fga",
        "penta_d",
        "penta_e",
        "th01",
        "tpox",
    ],
    is_reference_col_name="is_ref",
)

scores = scorer.scores(output="array")
```

```
>>> print(scores)
masked_array(
  data=[[--, 0.2608695652173913, 0.11428571428571428],
        [--, --, --],
        [0.11428571428571428, 0.21739130434782608, --]],
  mask=[[ True, False, False],
        [ True,  True,  True],
        [False, False,  True]],
  fill_value=0.0)
```

- Cells for pairs of non-reference samples like `0,2` and `2,0` (a vs. c) are computed using the Tanabe algorithm.
- Cells like `0,1` (a vs. b) and `2,1` (c vs. b) are computed against the reference sample b, so they use the other algorithm and loci counting mode.
- Cells `1,0` (b vs. a) and `1,2` (b vs. c) are masked since these involve comparisons that are irrelevant under both algorithms.  

## Development

### Installation

1. Install the required system dependencies:
   - [pyenv](https://github.com/pyenv/pyenv)
   - [Poetry](https://python-poetry.org/)
   - [pre-commit](https://pre-commit.com/)
 
3. Install the required Python version (>=3.9):
	```bash
	pyenv install "$(cat .python-version)"
	```

4. Confirm that `python` maps to the correct version:
	```
	python --version
	```

5. Set the Poetry interpreter and install the Python dependencies:
	```bash
	poetry env use "$(pyenv which python)"
	poetry install
	```

Run `poetry run pyright` to check static types with [Pyright](https://microsoft.github.io/pyright).

### Testing

```bash
poetry run pytest
```
