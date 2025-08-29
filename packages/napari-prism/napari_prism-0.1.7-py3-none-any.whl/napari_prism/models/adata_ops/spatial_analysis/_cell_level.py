"""Spatial analyses which generate metrics at the cell level."""

from itertools import combinations_with_replacement
from typing import Literal

import numpy as np
import pandas as pd
import scipy
from anndata import AnnData
from joblib import Parallel, delayed
from loguru import logger
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors

from napari_prism.models.adata_ops.spatial_analysis._utils import (
    symmetrise_graph,
)


# Pairwise Cell Computations
def compute_targeted_degree_ratio(
    adata,
    adjacency_matrix,
    phenotype_column,
    phenotype_A,  # source phenotype
    phenotype_B,  # target phenotype
    directed=False,
):
    """For each node in the adjacency matrix, compute the ratio of its
    targets that are of phenotype_pair.

    If directed, then this becomes the outdegree ratio. i.e.) If
    KNN, then the score is the ratio of its closest K neighbors being of
    the other specified type.

    If not directed, then this becomes a simple degree ratio, with the graph
    being symmetrised (enforce A->B, then B->A).

    """
    mat = adjacency_matrix if directed else symmetrise_graph(adjacency_matrix)

    a_mask = adata.obs[phenotype_column] == phenotype_A
    b_mask = adata.obs[phenotype_column] == phenotype_B
    a_ix = list(np.where(a_mask)[0])
    b_ix = list(np.where(b_mask)[0])
    a = mat[a_ix]  # A rows -> all cols
    ab = mat[np.ix_(a_ix, b_ix)]  # A rows -> B cols

    a_edge_degrees = a.sum(axis=1)  # Total connections for each A cell
    a_target_degrees = ab.sum(
        axis=1
    )  # Total connections to B cells for each A cell

    a_ab = np.divide(
        a_target_degrees, a_edge_degrees
    )  # For each A cell, ratio of B connections to total connections

    return a_ab


def compute_pair_interactions(
    adata: AnnData,
    phenotype_column: str,
    phenotype_A: str,
    phenotype_B: str,
    method: Literal["nodes", "edges"],
    adjacency_matrix: np.ndarray | scipy.sparse.csr.csr_matrix = None,
    connectivity_key: str = "spatial_connectivities",
) -> tuple[int, int, bool]:
    """
    Uses adjacency_matrix first if supplied, otherwise tries to find
    adjacency matrix in adata.obsp using `connectivity_key`.

    Compute the number of interactions between two phenotypes in a graph.
    Enforced symmetric relations. i.e.) IF A -> B, then B -> A.

    If neighbors graph constructed with radius, then already symmetric.

    Returns:
    total_interactions: Number of interactions between phenotype_pair
    total_cells: Total number of cells in the graph
    missing: True if not enough cells for comparison
    """
    adata = adata.copy()
    adata.obs = adata.obs.reset_index()
    if adjacency_matrix is None:
        if connectivity_key not in adata.obsp:
            raise ValueError(
                "No adjacency matrix provided and no "
                "connectivity key found in adata.obsp"
            )
        else:
            adjacency_matrix = adata.obsp[connectivity_key]

    sym = symmetrise_graph(adjacency_matrix)
    a_ix = list(
        adata.obs[adata.obs[phenotype_column] == phenotype_A].index.astype(int)
    )
    b_ix = list(
        adata.obs[adata.obs[phenotype_column] == phenotype_B].index.astype(int)
    )
    ab = sym[np.ix_(a_ix, b_ix)]  # A rows -> B cols
    ba = sym[np.ix_(b_ix, a_ix)]  # B rows -> A cols

    total_cells = sum(ab.shape)

    # Count the number of nodes of pair A and B that neighbor each other / totals
    if method == "nodes":
        if isinstance(adjacency_matrix, np.ndarray):
            f_sum = ab.any(
                axis=1
            ).sum()  # How many A cells have atleast 1 B neighbor
            s_sum = ba.any(
                axis=1
            ).sum()  # How many B cells have atleast 1 A neighbor

        elif isinstance(adjacency_matrix, csr_matrix):
            f_sum = (ab.getnnz(axis=1) > 0).sum()
            s_sum = (ba.getnnz(axis=1) > 0).sum()

        else:
            raise ValueError("invalid adjacency matrix type")

        total_interactions = (
            f_sum + s_sum
        )  # Represents total number of interacting cells in A and B

    # Count the number of times pair A and B neighbor each other / totals
    elif method == "edges":
        f_sum = (
            ab.sum()
        )  # How many B neighbors every A cells have in the graph
        s_sum = (
            ba.sum()
        )  # How many A neighbors every B cells have in the graph

        total_interactions = (
            f_sum + s_sum
        )  # Represents total number of interactions between A and B

    else:
        raise ValueError("invalid method")

    # Account for self comparisons. Normalised by density, but need to report counts
    if phenotype_A == phenotype_B:
        total_interactions = total_interactions / 2
        total_cells = total_cells / 2

    # # Minimum number of cells for a comparison
    not_enough_cells = total_cells < 2
    # For different phenotypes. If self, then not_enough_cells will be 0 anyway
    not_enough_of_category = len(a_ix) == 0 or len(b_ix) == 0

    missing = False
    if not_enough_cells or not_enough_of_category:
        missing = True

    return total_interactions, total_cells, missing


def proximity_density(
    adata: AnnData,
    grouping: str,
    phenotype: str,
    pairs: list[tuple[str, str]] = None,
    connectivity_key: str = "spatial_connectivities",
    multi_index: bool = False,
    inplace: bool = True,
    n_jobs: int = 4,
) -> None | tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Computes proximity density from scimap's p-score function compatible with
    squidpy-generated .obsp spatial graphs. By default, stores the results
    inplace.

    Proximity density is defined as the number of cells of a given pair of
    phenotypes being in proximity of one another, divided by the total number of
    cells.

    The definition of proximity depends on the adjacency matrix computed via
    squidpy.gr.spatial_neighbors. To stay true to the original definition of
    proximity density, the adjacency matrix should be a radial graph of a given
    radius in um.

    Args:
        adata: AnnData object.
        grouping: Column name in adata.obs to group by.
        phenotype: Column name in adata.obs to compute proximity for.
        pairs: List of tuples of phenotype pairs to compute proximity for.
            If None, computes proximity for all unique phenotype pairs.
        connectivity_key: Key for the adjacency matrix in adata.obsp.
        multi_index: If True, returns a multi-indexed DataFrame.
        inplace: If True, stores the results in adata.uns.

    Returns:
        If inplace is False, returns a tuple of three dataframes, the
        first containing the proximity density results, the second containing
        the masks for missing values, and the third containing the cell counts
        for each pair of phenotypes.
    """
    # Drop na phenotype rows
    adata = adata[~adata.obs[phenotype].isna()]

    if connectivity_key not in adata.obsp:
        raise ValueError("No adjacency matrix found in adata.obsp.")

    if grouping not in adata.obs.columns:
        raise ValueError("Grouping column not found in adata.obs.")

    if phenotype not in adata.obs.columns:
        raise ValueError("Phenotype column not found in adata.obs.")

    if pairs is None:
        phenotypes = list(adata.obs[phenotype].unique())
        pairs = list(combinations_with_replacement(phenotypes, 2))

    labels = (phenotype, f"neighbour_{phenotype}")

    adata_list = [
        adata[adata.obs[grouping] == g] for g in adata.obs[grouping].unique()
    ]

    def _process_adata_subset(
        adata_subset, pairs, phenotype, connectivity_key, grouping
    ):
        group = adata_subset.obs[grouping].unique()[0]

        densities = {}
        masks = {}
        counts = {}

        for pair in pairs:
            total_interactions, total_cells, missing = (
                compute_pair_interactions(
                    adata=adata_subset,
                    phenotype_column=phenotype,
                    phenotype_A=pair[0],
                    phenotype_B=pair[1],
                    method="nodes",
                    connectivity_key=connectivity_key,
                )
            )

            if total_cells == 0:
                densities[pair] = 0
            else:
                densities[pair] = total_interactions / total_cells
            masks[pair] = missing
            counts[pair] = total_cells

        return group, densities, masks, counts

    results = Parallel(n_jobs=n_jobs)(
        delayed(_process_adata_subset)(
            adata_subset, pairs, phenotype, connectivity_key, grouping
        )
        for adata_subset in adata_list
    )

    grouping_comparisons = {}
    mask_comparisons = {}
    count_comparisons = {}

    for group, densities, masks, counts in results:
        grouping_comparisons[group] = densities
        mask_comparisons[group] = masks
        count_comparisons[group] = counts

    grouping_df = pd.DataFrame(grouping_comparisons)
    grouping_df.index = grouping_df.index.set_names(labels)
    grouping_df.columns.name = grouping
    mask_df = pd.DataFrame(mask_comparisons)
    mask_df.index = mask_df.index.set_names(labels)
    mask_df.columns.name = grouping
    count_df = pd.DataFrame(count_comparisons)
    count_df.index = count_df.index.set_names(labels)
    count_df.columns.name = grouping

    if not multi_index:
        grouping_df = grouping_df.reset_index()
        mask_df = mask_df.reset_index()
        count_df = count_df.reset_index()

    if inplace:
        adata.uns["proximity_density_results"] = grouping_df
        adata.uns["proximity_density_masks"] = mask_df
        adata.uns["proximity_density_cell_counts"] = count_df
        return adata
    else:
        return grouping_df, mask_df, count_df


# Neighborhoods
def _get_neighborhoods_from_job(
    job,
    region_groupby,
    knn,
    x_coordinate: str,
    y_coordinate: str,
    z_coordinate: str,
):
    """For a given job (i.e. a given region/image in the dataset), return the indices of the nearest neighbors, for each cell in that job.
    Called by process_jobs.

        Params:
            job (str): Metadata containing start time, index of reigon, region name, indices of reigon in original dataframe.
            n_neighbors (str): Number of neighbors to find for each cell.

        Returns:
            neighbors (numpy.ndarray): Array of indices where each row corresponds to a cell, and values correspond to indices of the nearest neighbours found for that cell. Sorted.
    """
    # Unpack job metadata file
    _, region, indices = job
    region = region_groupby.get_group(region)

    if z_coordinate is None:
        coords = [x_coordinate, y_coordinate]
    else:
        coords = [x_coordinate, y_coordinate, z_coordinate]

    X_data = region.loc[indices][coords].values
    # Perform sklearn unsupervised nearest neighbors learning, on the x y coordinate values
    # Essentially does euclidean metric; but technically Minkowski, with p=2
    neighbors = NearestNeighbors(n_neighbors=knn).fit(X_data)
    # Unpack results
    distances, indices = neighbors.kneighbors(X_data)
    sorted_neighbors = _sort_neighbors(region, distances, indices)
    return sorted_neighbors.astype(np.int32)


def _sort_neighbors(region, distances, indices):
    """Processes the two outputs of sklearn NearestNeighbors to sort indices of nearest neighbors."""
    # Sort neighbors
    args = distances.argsort(axis=1)
    add = np.arange(indices.shape[0]) * indices.shape[1]
    sorted_indices = indices.flatten()[args + add[:, None]]
    neighbors = region.index.values[sorted_indices]
    return neighbors


def cellular_neighborhoods_sq(
    adata,
    phenotype: str,
    connectivity_key: str,
    #    library_key: str | None = None,
    k_kmeans: list[int] = None,
    mini_batch_kmeans: bool = True,
    parallelise: bool = False,
) -> None:
    """
    Compute Nolan's cellular neighborhoods compatible with squidpy-generated
    .obsp spatial graphs. By default, stores the results inplace.

    Args:
        adata: AnnData object.
        phenotype: Cell label to compute neighborhoods on.
        connectivity_key: Key for the adjacency matrix in adata.obsp. Ideally,
            should be a KNN graph to stay true to the original definition of
            cellular neighborhoods.
        k_kmeans: List of K values to use for KMeans clustering. If None,
            defaults to [10].
        mini_batch_kmeans: If True, uses MiniBatchKMeans instead of KMeans.
    """
    if k_kmeans is None:
        k_kmeans = [10]

    # phenotypes = adata.obs[phenotype].unique().dropna()

    conn = adata.obsp[connectivity_key]
    # row_ix, col_ix = conn.nonzero()
    # List incase of ragged arr -> i.e. if graph is not symmetric.
    neighbors = [[] for _ in range(conn.shape[0])]

    # For each row or cell, get its neighbors according to the graph;
    cell_indices = adata.obs.index
    # for r in range(conn.shape[0]):
    #     cix = np.where(row_ix == r)
    #     neighbors[r] = col_ix[cix]

    # speed up with csr row ptrs
    neighbors = [
        conn.indices[conn.indptr[i] : conn.indptr[i + 1]]
        for i in range(conn.shape[0])
    ]

    X_dat = adata.obs
    dummies = pd.get_dummies(X_dat[phenotype])
    dummy_cols = dummies.columns
    dummies_np = dummies.values

    counted_neighbors = np.zeros(
        (conn.shape[0], dummies_np.shape[1]), dtype=int
    )
    for i, neighbor_indices in enumerate(neighbors):
        if neighbor_indices.size > 0:
            counted_neighbors[i] = dummies_np[neighbor_indices].sum(axis=0)

    total_neighbor_counts = pd.DataFrame(
        counted_neighbors, columns=dummy_cols, index=cell_indices
    )

    # Reannotate the frequency graph; technically these can be in obsm
    total_neighbor_counts.columns.name = phenotype
    adata.obsm["neighbor_counts"] = total_neighbor_counts
    logger.info("Neighbor phenotype counts done")

    # Below represnet distinct following step in workflow; KMeans
    kmeans_cls = MiniBatchKMeans if mini_batch_kmeans else KMeans

    kmeans_instance = None
    labels = []
    inertias = []
    enrichment_scores = {}
    logger.info("Starting KMeans loop")
    for k in k_kmeans:
        logger.info(k)
        # Instantiate kmeans instance
        if kmeans_instance is not None:
            kmeans_instance.n_clusters = k
        else:
            kmeans_instance = kmeans_cls(
                n_clusters=k,
                n_init=3,
                random_state=0,
                init="k-means++",  # 'best' initializer for kms
            )

        # first
        y = kmeans_instance.fit_predict(total_neighbor_counts.values)

        # enrichment scores;
        distances_to_centroids = kmeans_instance.cluster_centers_
        # frequencies = total_neighbor_counts.astype(bool).mean(axis=0).values
        frequencies = (
            dummies[total_neighbor_counts.columns].mean(axis=0).values
        )
        num = distances_to_centroids + frequencies
        norm = (distances_to_centroids + frequencies).sum(
            axis=1, keepdims=True
        )
        score = np.log2(num / norm / frequencies)
        score_df = pd.DataFrame(
            score,
            columns=pd.Index(total_neighbor_counts.columns, name=phenotype),
        )
        score_df.index.name = "CN_index"

        enrichment_scores[str(k)] = score_df
        inertias.append(kmeans_instance.inertia_)
        labels.append(y)

    # Store in DataArray-like format
    # matrices are ragged so data is a dictionary.
    adata.uns["cn_enrichment_matrices"] = enrichment_scores
    adata.uns["cn_enrichment_matrices_dims"] = {"k_kmeans": k_kmeans}

    cn_labels = pd.DataFrame(np.array(labels).T)
    cn_labels.columns = k_kmeans
    cn_labels.columns = cn_labels.columns.astype(str)
    cn_labels.index = adata.obs.index
    # structured
    # cn_labels = np.array(cn_labels)#, dtype=[("k_kmeans", cn_labels.dtype)])

    adata.obsm["cn_labels"] = cn_labels
    adata.uns["cn_labels_dims"] = {"k_kmeans": k_kmeans}

    cn_inertias = pd.DataFrame(
        inertias,
        columns=["Inertia"],
        index=pd.Index(k_kmeans, name="k_kmeans"),
    )
    adata.uns["cn_inertias"] = cn_inertias
