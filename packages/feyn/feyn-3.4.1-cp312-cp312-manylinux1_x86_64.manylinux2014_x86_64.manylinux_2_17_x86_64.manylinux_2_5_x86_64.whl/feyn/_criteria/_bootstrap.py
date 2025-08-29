from collections import Counter

import numpy as np
import pandas as pd


def get_sample_weights_bootstrap(df):
    index = df.index
    new_index = np.random.choice(index, len(df))
    dict_boot = Counter(new_index)

    return [dict_boot.get(ind, 0) for ind in index]


def _assign_qcells_by_bootstrap(df: pd.DataFrame, num_qcells_to_assign_total=20):
    return {
        qid: get_sample_weights_bootstrap(df)
        for qid in range(num_qcells_to_assign_total)
    }
