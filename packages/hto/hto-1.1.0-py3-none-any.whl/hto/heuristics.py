#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pprint import pformat
import scipy.sparse
import anndata as ad

from ._classify import classify, assert_demux
from ._defaults import DEFAULTS, DESCRIPTIONS
from ._logging import get_logger
from ._meta import add_meta
from ._utils import get_layer

def heuristics(
    adata_hto: ad.AnnData,
    inplace: bool = DEFAULTS["inplace"],
    verbose: int = DEFAULTS["verbose"],
    key_normalise: str = DEFAULTS["add_key_normalise"],
    key_denoise: str = DEFAULTS["add_key_denoise"],
    add_key_hashid: str = DEFAULTS["add_key_hashid"],
    add_key_doublet: str = DEFAULTS["add_key_doublet"],
):
    raise NotImplementedError("Heuristics function is not implemented yet.")