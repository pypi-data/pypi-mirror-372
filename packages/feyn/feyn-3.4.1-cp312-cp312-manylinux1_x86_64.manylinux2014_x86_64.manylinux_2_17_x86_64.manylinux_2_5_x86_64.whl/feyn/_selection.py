"""Functions to prune models and select better ones."""
from typing import List, Optional
from math import exp

import feyn
from feyn._typings import check_types

from collections import Counter

from feyn.metrics import get_posterior_probabilities


@check_types()
def prune_models(
    models: List[feyn.Model],
    keep_n: Optional[int] = None,
) -> List[feyn.Model]:
    """Prune a list of models to remove redundant and poorly performing ones.

    Arguments:
        models {List[feyn.Model]} -- The list of models to prune.

    Keyword Arguments:
        keep_n {Optional[int]} -- At most this many models will be returned. If None, models are left to be pruned by other redundancies. (default: {None})

    Raises:
        TypeError: if inputs don't match the correct type.

    Returns:
        List[feyn.Model] -- The list of pruned models.
    """
    if len(models) == 0:
        return models

    if keep_n is not None and keep_n < 0:
        raise ValueError("keep_n needs to be positive")

    if keep_n is None:
        keep_n = len(models)

    # Always keep the best
    res = models[0:1]

    hashes = set()
    hashes.add(hash(res[0]))
    qid_counter = Counter()

    for m in models[1:]:
        if len(res) == keep_n:
            break

        # Check for duplicate structure
        model_hash = hash(m)
        if model_hash in hashes:
            continue

        qid = m._program.qid
        qid_counter[qid] += 1

        # Calculate the half-life of the model and decide if it should die.
        models_density = 100
        max_age = 50
        n = 10
        tau = 0.693
        if m.age > max_age * exp(-qid_counter[qid] / (models_density / (n * tau))) + 1:
            continue

        hashes.add(model_hash)
        res.append(m)

    return res


@check_types()
def get_diverse_models(
    models: List[feyn.Model],
    n: int = 10,
) -> List[feyn.Model]:
    """Select at most n best performing models from a collection, such that they are sufficiently diverse in their lineage.

    Arguments:
        models {List[feyn.Model]} -- The list of models to find the best ones in.

    Keyword Arguments:
        n {int} -- The maximum number of best models to identify. (default: {10})

    Raises:
        TypeError: if inputs don't match the correct type.

    Returns:
        List[feyn.Model] -- The best sufficiently diverse models under distance_func.
    """
    if len(models) == 0:
        return models

    seen = set()
    res = []

    for m in models:
        if len(res) == n:
            break

        qid = m._program.qid
        if qid in seen:
            continue

        found = any([_canonical_compare(other, m) for other in res])
        if not found:
            res.append(m)
            seen.add(qid)

    return res


def _get_bayesian_best(
    models: List[feyn.Model],
    n: int = 3,
    prob_cutoff: float = 0.05,
) -> List[feyn.Model]:
    """Select the n best performing models from a collection, such that the posterior probability inferred from their
       BIC is sufficiently high.

    Arguments:
        models {List[feyn.Model]} -- The list of models to find the best ones in.

    Keyword Arguments:
        n {int} -- The maximum number of best models to identify. (default: {10})
        prob_cutoff {float} -- Minimum relative probability to keep model (default: {0.05})

    Raises:
        TypeError: if inputs don't match the correct type.

    Returns:
        List[feyn.Model] -- The best sufficiently diverse models under distance_func.
    """
    if len(models) <= n:
        return models

    list_bic = [model.bic for model in models]
    posteriors = get_posterior_probabilities(list_bic)

    res = [model for i, model in enumerate(models) if posteriors[i] > prob_cutoff]

    return res



def _canonical_compare(m, other):
    p, other = m._program.copy(), other._program.copy()
    plen, olen = p.find_end(0), other.find_end(0)
    if plen != olen:
        return False
    else:
        # Canonize both programs
        for i in range(plen):
            p.canonize(i)
        for i in range(olen):
            other.canonize(i)

        # check for equality
        equal = True
        for code, code_other in zip(p, other):
            equal &= code == code_other
        return equal
