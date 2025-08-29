import pandas as pd
import numpy as np


def _assign_qcells_by_clustering(
    df: pd.DataFrame,
    priority_number=10.0,
    num_qcells_to_assign_total=20,
    max_num_clusters=7,
):
    num_observations = len(df)

    cluster_labels, num_clusters = compute_clustering(
        df, max_num_clusters=max_num_clusters
    )
    cluster_num_samples_arr = [sum(cluster_labels == i) for i in range(num_clusters)]
    qcell_cluster_proportions = [
        cluster_num_samples / num_observations
        for cluster_num_samples in cluster_num_samples_arr
    ]

    qid_to_sample_priorities = {}
    offset = 0
    for cluster in range(num_clusters):
        if cluster != num_clusters - 1:
            num_cells_to_assign = round(
                qcell_cluster_proportions[cluster] * num_qcells_to_assign_total
            )
        else:
            num_cells_to_assign = num_qcells_to_assign_total - offset

        for qid in range(offset, num_cells_to_assign + offset):
            relevant_idxs = cluster_labels == cluster
            qid_to_sample_priorities[qid] = [
                priority_number if relevant_idxs[i] else 1.0
                for i in range(num_observations)
            ]
        offset += num_cells_to_assign

    return qid_to_sample_priorities


def compute_clustering(df, max_num_clusters, num_clusters=None):
    X = get_data_matrix(df)

    range_n_clusters = list(range(2, max_num_clusters + 1))
    silhouette_averages = []
    for n in range_n_clusters:
        silhouette_avg, _ = fit_and_predict_clustering(X, n)
        silhouette_averages.append(silhouette_avg)
    num_clusters_with_best_silhouette_score = range_n_clusters[
        np.argmax(silhouette_averages)
    ]

    num_clusters = (
        num_clusters
        if num_clusters is not None
        else num_clusters_with_best_silhouette_score
    )
    _, cluster_labels = fit_and_predict_clustering(X, num_clusters)

    return cluster_labels, num_clusters


def get_data_matrix(df):
    import sklearn.preprocessing

    ordinal_encoder = sklearn.preprocessing.OrdinalEncoder()
    standard_scaler = sklearn.preprocessing.StandardScaler()
    X = ordinal_encoder.fit_transform(df)
    X = standard_scaler.fit_transform(X)
    return X


def fit_and_predict_clustering(X, n_clusters):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    # Initialize the clusterer with n_clusters value and a random generator
    clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = clusterer.fit_predict(X)

    # The silhouette_score gives the average value for all the samples.
    # This gives a perspective into the density and separation of the formed clusters
    silhouette_avg = silhouette_score(X, cluster_labels)

    return silhouette_avg, cluster_labels
