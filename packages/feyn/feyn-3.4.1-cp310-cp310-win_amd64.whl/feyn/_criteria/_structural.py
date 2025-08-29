import numpy as np

from feyn.metrics._diversity import levenshtein_distance


def _compute_average_structural_diversity_difference_scores(models):
    structural_diversity_difference_scores = np.zeros((len(models), len(models)))
    for i in range(len(models)):
        for j in range(i, len(models)):
            structural_diversity_difference_scores[i, j] = levenshtein_distance(models[i], models[j])
            structural_diversity_difference_scores[j, i] = structural_diversity_difference_scores[i, j]

    mean_distances_without_diagonal = structural_diversity_difference_scores.sum(axis=0)/(structural_diversity_difference_scores.shape[0]-1)
    return mean_distances_without_diagonal


def _sort_by_structural_diversity(models):
    average_structural_diversity_difference_scores = _compute_average_structural_diversity_difference_scores(models)
    for i, m in enumerate(models):
        m.structural_diversity_difference_score_total = average_structural_diversity_difference_scores[i]

    # Objective function: Mix of loss, complexity and structural diversity
    # Lower bic is better, higher structural diversity score is better
    models = sorted(models, key=lambda m: m.bic + (-1) * m.structural_diversity_difference_score_total, reverse=False)

    return models
