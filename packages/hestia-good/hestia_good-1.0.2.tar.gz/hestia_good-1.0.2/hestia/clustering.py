import time
from typing import Optional

import numpy as np
import pandas as pd
import polars as pl
from scipy.sparse.csgraph import connected_components
from tqdm import tqdm

from hestia.similarity import sim_df2mtx


def generate_clusters(
    df: pd.DataFrame,
    field_name: str,
    sim_df: pl.DataFrame,
    threshold: float = 0.4,
    verbose: int = 0,
    cluster_algorithm: str = 'greedy_incremental',
    filter_smaller: Optional[bool] = True
) -> np.ndarray:
    """Generates clusters from a DataFrame.

    :param df: DataFrame with entities to cluster.
    :type df: pd.DataFrame
    :param field_name: Name of the field with the entity information
    (e.g., `protein_sequence` or `structure_path`), defaults to 'sequence'.
    :type field_name: str
    :param threshold: Similarity value above which entities will be
    considered similar, defaults to 0.4
    :param sim_df: DataFrame with similarities (`metric`) between
    `query` and `target`, it is the product of `calculate_similarity` function
    :type sim_df: pl.DataFrame
    :type threshold: float
    :param verbose: How much information will be displayed.
    Options:
        - 0: Errors,
        - 1: Warnings,
        - 2: All
    Defaults to 0
    :type verbose: int
    :param cluster_algorithm: Clustering algorithm to use.
    Options:
        - `CDHIT` or `greedy_incremental`
        - `greedy_cover_set`
        - `connected_components`
    Defaults to "CDHIT".
    :type cluster_algorithm: str, optional
    :raises NotImplementedError: Clustering algorithm is not supported
    :return: DataFrame with entities and the cluster they belong to.
    :rtype: np.ndarray
    """
    start = time.time()
    if isinstance(sim_df, pl.DataFrame):
        sim_df = sim_df.to_pandas()

    if cluster_algorithm in ['greedy_incremental', 'CDHIT']:
        clusters = _greedy_incremental_clustering(df, field_name, sim_df,
                                                  threshold, verbose)
    elif cluster_algorithm in ['greedy_cover_set']:
        clusters = _greedy_cover_set(df, sim_df, threshold, verbose)
    elif cluster_algorithm in ['connected_components']:
        clusters = _connected_components_clustering(df, sim_df, threshold,
                                                    verbose, filter_smaller)
    else:
        raise NotImplementedError(
            f'Clustering algorithm: {cluster_algorithm} is not supported'
        )
    if verbose > 2:
        print(f'Clustering has taken {time.time() - start:.3f} s to compute.')

    return clusters


def _greedy_incremental_clustering(
    df: pd.DataFrame,
    field_name: str,
    sim_df: pd.DataFrame,
    threshold: float,
    verbose: int
) -> np.ndarray:
    df['lengths'] = df[field_name].map(len)
    df.sort_values(by='lengths', ascending=False, inplace=True)

    clusters = []
    clustered = set()
    sim_df = sim_df[sim_df['metric'] > threshold]

    if verbose > 2:
        pbar = tqdm(df.index)
    else:
        pbar = df.index

    for i in pbar:
        if i in clustered:
            continue
        in_cluster = set(sim_df.loc[sim_df['query'] == i, 'target'])
        in_cluster.update(set(sim_df.loc[sim_df['target'] == i, 'query']))
        in_cluster.update(set([i]))
        in_cluster = in_cluster.difference(clustered)

        for j in in_cluster:
            clusters.append(i)
        clustered.update(in_cluster)

    if verbose > 1:
        print('Clustering has generated:',
              f'{len(np.unique(clusters)):,d} clusters for',
              f'{len(df):,} entities')
    return np.array(clusters)


def _greedy_cover_set(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    threshold: float,
    verbose: int
) -> np.ndarray:
    def _find_connectivity(df, sim_df):
        neighbours = []
        for i in tqdm(df.index):
            in_cluster = set(sim_df.loc[sim_df['query'] == i, 'target'])
            in_cluster.update(set(sim_df.loc[sim_df['target'] == i, 'query']))
            neighbours.append(in_cluster)
        return neighbours

    sim_df = sim_df[sim_df['metric'] > threshold]
    neighbours = _find_connectivity(df, sim_df)
    order = np.argsort(neighbours)[::-1]

    clusters = np.zeros((len(df)))
    clustered = set()
    if verbose > 2:
        pbar = tqdm(order)
    else:
        pbar = order

    for i in pbar:
        if i in clustered:
            continue
        in_cluster = neighbours[i]
        in_cluster.update([i])
        in_cluster = in_cluster.difference(clustered)
        clustered.update(in_cluster)

        for j in in_cluster:
            clusters[j] = i
    unique_clusters, cluster_pop = np.unique(clusters, return_counts=True)
    if verbose > 1:
        print('Clustering has generated:',
              f'{len(unique_clusters):,d} clusters for',
              f'{len(df):,} entities')
    return clusters


def _connected_components_clustering(
    df: pd.DataFrame,
    sim_df: pd.DataFrame,
    threshold: float,
    verbose: int,
    filter_smaller: Optional[bool] = True
) -> np.ndarray:
    matrix = sim_df2mtx(sim_df, len(df), len(df),
                        threshold=threshold,
                        filter_smaller=filter_smaller)
    n, labels = connected_components(matrix, directed=False,
                                     return_labels=True)
    if verbose > 2:
        print('Clustering has generated:',
              f'{n:,d} connected components for',
              f'{len(df):,} entities')
    return labels
