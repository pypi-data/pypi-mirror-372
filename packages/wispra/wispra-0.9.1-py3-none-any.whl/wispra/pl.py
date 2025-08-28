"""
Author: Wang Zilu
Email: 1923524070@qq.com
Date: 2025.8.20
Description: CCI_plot
"""

def plot_genes_grid_expression(
    adata,
    genes=None,
    celltypes=None,
    grid_size=100,
    mode="normal",
    score_mode="product",
    celltype_key="subclass",
    L_gene=None,
    R_gene=None,
    outline_json_dir=None,
    library_id_key=None,
    groupby_keys=None,
    cmap="magma_r",
    x_margin_factor_left=5,
    x_margin_factor_right=5,
    y_margin_factor_top=5,
    y_margin_factor_bottom=5,
    margin=5,
    show_legend=True,
):
    """
    Plot gene expression or ligand–receptor interaction scores on a spatial grid.

    This function aggregates expression values or interaction scores into grid bins 
    and visualizes them as heatmaps per chip (library). It supports both normal 
    single/multi-gene expression visualization and ligand–receptor cell–cell 
    interaction (CCI) visualization.

    Parameters
    ----------
    adata : AnnData
        AnnData object containing spatial transcriptomics data.
        Must have `.obsm["spatial"]` for spatial coordinates and `.X` (LogNormalization)for gene expression.

    genes : list of str, optional (default: None)
        List of gene names to visualize in "normal" mode.
        Required if `mode="normal"`.

    celltypes : list of str, optional (default: None)
        Subset of cell types to include. 
        Used for filtering in "normal" mode and defining ligand/receptor cell types in "CCI" mode.

    grid_size : int, optional (default: 100)
        Size of grid bins (in spatial coordinate units).

    mode : {"normal", "CCI"}, optional (default: "normal")
        - "normal": plot expression values of one or multiple genes.
        - "CCI": compute and plot ligand–receptor interaction scores between two cell types.

    score_mode : {"product", "sum", "mean"}, optional (default: "product")
        Method for aggregating multiple genes' expression values in "normal" mode:
        - "product": multiply expressions.
        - "sum": sum expressions.
        - "mean": average expressions.

    celltype_key : str, optional (default: "subclass")
        Column in `adata.obs` specifying cell type annotation.

    L_gene : list of str, optional (default: None)
        List of ligand genes. Required in "CCI" mode.

    R_gene : list of str, optional (default: None)
        List of receptor genes. Required in "CCI" mode.

    outline_json_dir : str, optional (default: None)
        Directory containing JSON files with tissue outlines.
        If provided, outlines are drawn for each chip.

    library_id_key : str, optional (default: None)
        Column in `adata.obs` specifying chip/library IDs. 
        If None, all data is treated as a single chip.

    groupby_keys : list of str, optional (default: None)
        Additional metadata keys from `adata.obs` to include in grouped results.
        Useful for stratifying scores by experimental condition (e.g., "time").

    cmap : str, optional (default: "magma_r")
        Colormap for visualizing scores.

    x_margin_factor_left, x_margin_factor_right : float, optional (default: 5)
        Extra margins (in grid units) added to X-axis plot limits.

    y_margin_factor_top, y_margin_factor_bottom : float, optional (default: 5)
        Extra margins (in grid units) added to Y-axis plot limits.

    margin : int, optional (default: 5)
        Additional padding applied to both X and Y axes.

    show_legend : bool, optional (default: True)
        If True, display a colorbar legend for interaction scores.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The matplotlib figure object containing the heatmap(s).

    score_grid : numpy.ndarray
        2D array of scores aligned to the grid (NaN for empty bins).

    grouped : pandas.DataFrame
        Aggregated scores per grid bin (and per group if `groupby_keys` specified).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy as np
    import pandas as pd
    import os
    import json
    import glob
    from scipy.sparse import issparse

    def apply_transformation_to_coords(coords, transformation_matrix):
        coords_homogeneous = np.hstack([coords, np.ones((coords.shape[0], 1))])
        matrix = np.array(transformation_matrix).reshape(3, 3)
        transformed = coords_homogeneous @ matrix.T
        return transformed[:, :2]

    def find_outline_json(outline_json_dir, chip_id):
        pattern = os.path.join(outline_json_dir, f"*{chip_id}*.json")
        matched_files = glob.glob(pattern)
        if not matched_files:
            raise FileNotFoundError(f"No JSON file containing '{chip_id}' found in {outline_json_dir}")
        return matched_files[0]

    if library_id_key is not None and library_id_key in adata.obs:
        all_chip_ids = adata.obs[library_id_key].unique()
    else:
        if mode == "normal":
            if genes is not None and len(genes) > 0:
                temp_name = "_".join(genes)
            else:
                temp_name = "single_chip"
        elif mode == "CCI":
            if (L_gene is not None and len(L_gene) > 0) or (R_gene is not None and len(R_gene) > 0):
                temp_name = "_".join((L_gene if L_gene else []) + (R_gene if R_gene else []))
            else:
                temp_name = "single_chip"
        else:
            temp_name = "single_chip"

        all_chip_ids = [temp_name]
        adata.obs[f"__{temp_name}"] = temp_name
        library_id_key = f"__{temp_name}"

    n_chips = len(all_chip_ids)

    global_xmin, global_xmax = np.inf, -np.inf
    global_ymin, global_ymax = np.inf, -np.inf
    for chip_id in all_chip_ids:
        adata_chip = adata[adata.obs[library_id_key] == chip_id]
        coords = adata_chip.obsm["spatial"]
        x_bin = (coords[:, 0] // grid_size).astype(int)
        y_bin = (coords[:, 1] // grid_size).astype(int)
        global_xmin = min(global_xmin, x_bin.min())
        global_xmax = max(global_xmax, x_bin.max())
        global_ymin = min(global_ymin, y_bin.min())
        global_ymax = max(global_ymax, y_bin.max())

    grid_width = global_xmax - global_xmin + 1
    grid_height = global_ymax - global_ymin + 1
    extent = [global_xmin - 0.5, global_xmax + 0.5, global_ymax + 0.5, global_ymin - 0.5]

    fig = plt.figure(figsize=(5 * n_chips, 6), dpi=300)

    for idx, chip_id in enumerate(all_chip_ids):
        adata_chip = adata[adata.obs[library_id_key] == chip_id].copy()
        coords = adata_chip.obsm["spatial"]
        x = coords[:, 0]
        y = coords[:, 1]
        x_bin = (x // grid_size).astype(int)
        y_bin = (y // grid_size).astype(int)
        df = pd.DataFrame({"x": x, "y": y, "x_bin": x_bin, "y_bin": y_bin})

        if groupby_keys is not None:
            for key in groupby_keys:
                if key in adata_chip.obs:
                    df[key] = adata_chip.obs[key].values

        if mode == "normal":
            assert genes is not None and len(genes) > 0
            for gene in genes:
                assert gene in adata.var_names

            X = adata_chip[:, genes].X

            if issparse(X):
                X = X.toarray()
            for i, gene in enumerate(genes):
                df[gene] = X[:, i]

            if celltypes is not None:
                df[celltype_key] = adata_chip.obs[celltype_key].values
                df = df[df[celltype_key].isin(celltypes)]

            group_cols = ["x_bin", "y_bin"] + (groupby_keys if groupby_keys else [])
            gene_means = df.groupby(group_cols)[genes].mean().reset_index()

            if score_mode == "product":
                gene_means["score"] = gene_means[genes].prod(axis=1)
            elif score_mode == "sum":
                gene_means["score"] = gene_means[genes].sum(axis=1)
            elif score_mode == "mean":
                gene_means["score"] = gene_means[genes].mean(axis=1)
            else:
                raise ValueError("score_mode must be 'product', 'sum' or 'mean'")

            grouped = gene_means[["x_bin", "y_bin", "score"] + (groupby_keys if groupby_keys else [])]

        elif mode == "CCI":
            assert L_gene is not None and R_gene is not None and len(celltypes) == 2
            source_type, target_type = celltypes
            for gene in L_gene + R_gene:
                assert gene in adata.var_names
        
            df[celltype_key] = adata_chip.obs[celltype_key].values
            X = adata_chip[:, L_gene + R_gene].X
            if issparse(X):
                X = X.toarray()

            all_bins = df.groupby(["x_bin", "y_bin"]).size().reset_index()[["x_bin", "y_bin"]]
            all_bins["dummy"] = 1 

            df_L = df[df[celltype_key] == source_type].copy()
            for i, gene in enumerate(L_gene):
                df_L[gene] = X[df[celltype_key] == source_type, i]
            grouped_L = df_L.groupby(["x_bin", "y_bin"])[L_gene].mean()
            grouped_L["L_expr"] = grouped_L.prod(axis=1)

            df_R = df[df[celltype_key] == target_type].copy()
            for j, gene in enumerate(R_gene):
                df_R[gene] = X[df[celltype_key] == target_type, len(L_gene) + j]
            grouped_R = df_R.groupby(["x_bin", "y_bin"])[R_gene].mean()
            grouped_R["R_expr"] = grouped_R.prod(axis=1)

            merged = pd.merge(all_bins, grouped_L["L_expr"], on=["x_bin", "y_bin"], how="left")
            merged = pd.merge(merged, grouped_R["R_expr"], on=["x_bin", "y_bin"], how="left")
        
            merged["score"] = np.nan
            merged.loc[merged["L_expr"].notna() & merged["R_expr"].notna(), "score"] = merged["L_expr"] * merged["R_expr"]
            merged.loc[(merged["L_expr"].notna() & merged["R_expr"].isna()) |
                       (merged["L_expr"].isna() & merged["R_expr"].notna()), "score"] = -1
 
            merged["score"] = merged["score"].fillna(-1)
        
            grouped = merged[["x_bin", "y_bin", "score"]]

        else:
            raise ValueError("mode must be 'normal' or 'CCI'")

        score_grid = np.full((grid_height, grid_width), np.nan)

        for _, row in grouped.iterrows():
            xi = int(row["x_bin"] - global_xmin)
            yi = int(row["y_bin"] - global_ymin)
            score_grid[yi, xi] = row["score"]

        base_cmap = plt.get_cmap(cmap)
        colors = base_cmap(np.linspace(0, 1, 256))
        colors_with_gray = np.vstack(([0.7, 0.7, 0.7, 0.6], colors))
        custom_cmap = ListedColormap(colors_with_gray)
        positive_scores = score_grid[score_grid > 0]
        vmin = -1
        vmax = np.nanpercentile(positive_scores, 99) if positive_scores.size > 0 else 1
        norm = plt.Normalize(vmin=vmin, vmax=vmax)

        ax = fig.add_axes([0.05 + idx * (0.9 / n_chips), 0.1, 0.9 / n_chips, 0.8])
        im = ax.imshow(score_grid, cmap=custom_cmap, origin="upper", interpolation="none", extent=extent, norm=norm)
        ax.set_xlim(global_xmin - 0.5 - margin * x_margin_factor_left, global_xmax + 0.5 + margin * x_margin_factor_right)
        ax.set_ylim(global_ymax + 0.5 + margin * y_margin_factor_top, global_ymin - 0.5 - margin * y_margin_factor_bottom)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{chip_id}", fontsize=12)

        if outline_json_dir is not None and chip_id != "single_chip":
            json_file = find_outline_json(outline_json_dir, chip_id)
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    data = json.load(f)
                matrix = data["corr_para"]["transformation_matrix"]
                for line in data["lines"]:
                    pts = np.array(line["countours"])
                    pts_trans = apply_transformation_to_coords(pts, matrix)
                    ax.plot(pts_trans[:, 0] / grid_size - 0.5, pts_trans[:, 1] / grid_size - 0.5, color="black", lw=0.5, alpha=0.5)

        if show_legend:
            box = ax.get_position()
            cbar_width = 0.015 
            cbar_pad = 0.01 + idx * (0.9 / n_chips) 
            ax_cbar = fig.add_axes([
                box.x1 + 0.01, 
                box.y0,
                cbar_width,
                box.height
            ])
            cbar = fig.colorbar(im, cax=ax_cbar)
            cbar.ax.tick_params(labelsize=6)
            cbar.set_label("Interaction score", fontsize=6)

    plt.show()
    return fig, score_grid, grouped


def plot_colocalization_celltypes(
    adata,
    celltypes,
    celltype_key="subclass",
    library_id_key=None,
    point_size=5,
    figsize=(5, 5),
    celltype_colors=["red", "blue"],
    background_color="lightgray",
    distance_threshold=100,
    outline_json_dir=None,
    x_margin_factor_left=5,
    x_margin_factor_right=5,
    y_margin_factor_top=5,
    y_margin_factor_bottom=5,
    show_legend=True,
    invert_y=False,
    margin=5,
):
    """
    Plot co-localization of two specified cell types in spatial transcriptomics data.

    This function identifies cells of two specified types that are spatially close 
    (within a given distance threshold) and highlights them in different colors. 
    Non-target or non-co-localized cells are shown in a background color. 
    Optionally, tissue outlines can be added from JSON files.

    Parameters
    ----------
    adata : AnnData
        AnnData object containing spatial transcriptomics data. 
        Must have `.obsm["spatial"]` for coordinates and `.obs[celltype_key]` for cell type annotation.

    celltypes : list of str
        List containing two cell type names to visualize and analyze for co-localization.

    celltype_key : str, optional (default: "subclass")
        Column name in `adata.obs` specifying the cell type annotation.

    library_id_key : str, optional (default: None)
        Column in `adata.obs` specifying multiple library/chip IDs. 
        If None, all data is treated as one chip.

    point_size : int, optional (default: 5)
        Base point size for plotting. Used as a multiplier for different categories 
        (e.g., co-localized cells plotted larger).

    figsize : tuple, optional (default: (5, 5))
        Figure size per chip (width, height).

    celltype_colors : list of str, optional (default: ["red", "blue"])
        Colors for the two specified cell types.

    background_color : str, optional (default: "lightgray")
        Color used for non-target and non-co-localized cells.

    distance_threshold : float, optional (default: 100)
        Maximum Euclidean distance between two cells of different types 
        to consider them as co-localized.

    outline_json_dir : str, optional (default: None)
        Directory containing JSON files with tissue outline information. 
        JSON files must include `transformation_matrix` and `lines` with coordinates.

    x_margin_factor_left, x_margin_factor_right : float, optional (default: 5)
        Multipliers for margins on the left and right X-axis boundaries.

    y_margin_factor_top, y_margin_factor_bottom : float, optional (default: 5)
        Multipliers for margins on the top and bottom Y-axis boundaries.

    show_legend : bool, optional (default: True)
        If True, display a legend explaining color categories.

    invert_y : bool, optional (default: False)
        If True, invert Y-axis coordinates before plotting.

    margin : int, optional (default: 5)
        Additional padding added to plot limits.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The matplotlib Figure object containing the plots.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.spatial.distance import cdist
    import os, json, glob

    def apply_transformation_to_coords(coords, transformation_matrix):
        coords_homogeneous = np.hstack([coords, np.ones((coords.shape[0], 1))])
        matrix = np.array(transformation_matrix).reshape(3, 3)
        transformed = coords_homogeneous @ matrix.T
        return transformed[:, :2]    

    def find_outline_json(outline_json_dir, chip_id):
        pattern = os.path.join(outline_json_dir, f"*{chip_id}*.json")
        matched_files = glob.glob(pattern)
        if not matched_files:
            raise FileNotFoundError(f"No JSON file containing '{chip_id}' found in {outline_json_dir}")
        return matched_files[0]

    if library_id_key is not None and library_id_key in adata.obs.columns:
        chips = adata.obs[library_id_key].unique()
    else:
        temp_name = "_".join(celltypes)
        chips = [temp_name]
        adata.obs[f"__{temp_name}"] = temp_name
        library_id_key = f"__{temp_name}"
    n_chips = len(chips)

    global_xmin, global_xmax = np.inf, -np.inf
    global_ymin, global_ymax = np.inf, -np.inf
    for chip_id in chips:
        if chip_id == "single_chip":
            coords = adata.obsm["spatial"]
        else:
            coords = adata[adata.obs[library_id_key] == chip_id].obsm["spatial"]
        global_xmin = min(global_xmin, coords[:, 0].min())
        global_xmax = max(global_xmax, coords[:, 0].max())
        global_ymin = min(global_ymin, coords[:, 1].min())
        global_ymax = max(global_ymax, coords[:, 1].max())

    margin = margin
    fig = plt.figure(figsize=(figsize[0] * n_chips, figsize[1]), dpi=300)

    for i, chip_id in enumerate(chips):
        ax = fig.add_axes([0.05 + i * (0.9 / n_chips), 0.1, 0.9 / n_chips, 0.8])

        if library_id_key is not None and library_id_key in adata.obs.columns:
            adata_chip = adata[adata.obs[library_id_key] == chip_id]
        else:
            adata_chip = adata

        coords = adata_chip.obsm["spatial"]
        ct = adata_chip.obs[celltype_key]

        idx1 = ct == celltypes[0]
        idx2 = ct == celltypes[1]
        coords1 = coords[idx1]
        coords2 = coords[idx2]

        dist_matrix = cdist(coords1, coords2)
        close_pairs = np.where(dist_matrix < distance_threshold)
        idx1_keep = np.unique(np.where(idx1)[0][close_pairs[0]])
        idx2_keep = np.unique(np.where(idx2)[0][close_pairs[1]])

        keep_mask = np.zeros(len(adata_chip), dtype=bool)
        keep_mask[idx1_keep] = True
        keep_mask[idx2_keep] = True

        coords_plot = coords.copy()
        if invert_y:
            coords_plot[:, 1] = -coords_plot[:, 1]

        other_mask = ~(idx1 | idx2)
        ax.scatter(
            coords_plot[other_mask, 0], coords_plot[other_mask, 1],
            c=background_color, s=point_size * 3, alpha=0.6, edgecolors='none', label="Other celltypes"
        )

        only_one_mask = (idx1 | idx2) & ~keep_mask
        ax.scatter(
            coords_plot[only_one_mask, 0], coords_plot[only_one_mask, 1],
            c=background_color, s=point_size * 6, alpha=0.8, edgecolors='none', label="Not co-localized"
        )

        ax.scatter(
            coords_plot[idx1_keep, 0], coords_plot[idx1_keep, 1],
            c=celltype_colors[0], s=point_size * 10, label=celltypes[0], alpha=1, edgecolors='none'
        )
        ax.scatter(
            coords_plot[idx2_keep, 0], coords_plot[idx2_keep, 1],
            c=celltype_colors[1], s=point_size * 10, label=celltypes[1], alpha=1, edgecolors='none'
        )

        if outline_json_dir is not None and chip_id != "all":
            json_file = find_outline_json(outline_json_dir, chip_id)
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                matrix = data['corr_para']['transformation_matrix']
                for line in data['lines']:
                    pts = np.array(line['countours'])
                    pts_trans = apply_transformation_to_coords(pts, matrix)
                    if invert_y:
                        pts_trans[:, 1] = -pts_trans[:, 1]
                    ax.plot(
                        pts_trans[:, 0],
                        pts_trans[:, 1],
                        color='black',
                        lw=0.5,
                        alpha=0.5
                    )

        ax.set_xlim(global_xmin - 5 - margin*x_margin_factor_left,
                    global_xmax + 5 + margin*x_margin_factor_right)
        ax.set_ylim(global_ymax + 5 + margin*y_margin_factor_top,
                    global_ymin - 5 - margin*y_margin_factor_bottom)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.axis("off")
        ax.set_title(f"{chip_id}", fontsize=10)

    if show_legend:
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=celltype_colors[0], edgecolor='none', label=celltypes[0]),
            Patch(facecolor=celltype_colors[1], edgecolor='none', label=celltypes[1]),
            Patch(facecolor=background_color, edgecolor='none', alpha=0.8, label="Not co-localized"),
            Patch(facecolor=background_color, edgecolor='none', alpha=0.6, label="Other celltypes"),
        ]
        fig.subplots_adjust(bottom=0.15)  
        fig.legend(
            handles=legend_elements,
            loc='lower center',
            bbox_to_anchor=(0.5, 0.2),  
            ncol=4,
            frameon=False,
            handlelength=1.2,
            fontsize=10
        )

    plt.show()
    return fig