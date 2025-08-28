"""
Author: Wang Zilu
Email: 1923524070@qq.com
Date: 2025.8.20
Description: CCI_tools
"""

def build_interaction_dicts(
    interaction_df,
    species="human"
):
    """
    Build interaction-to-genes and interaction-to-pathway mappings.

    Parameters
    ----------
    interaction_df : pd.DataFrame
        Must contain the following columns:
        ["ligand", "receptor", "source", "target", "pathway_name", "prob", "pval"]
    species : {"human", "mouse"}, default "human"
        If "human": ligand/receptor names are forced to UPPERCASE.
        If "mouse": ligand/receptor names are formatted as Capitalized (Title case).

    Returns
    -------
    interaction_dict : dict
        Mapping {interaction: [ligand_genes + receptor_genes]}.
    interaction_to_pathway : dict
        Mapping {interaction: pathway}.
    """
    import pandas as pd
    
    required_cols = ["ligand", "receptor", "source", "target", "pathway_name", "prob", "pval"]
    missing = [c for c in required_cols if c not in interaction_df.columns]
    if missing:
        raise ValueError(f"interaction_df missing required columns: {missing}")

    if species.lower() == "human":
        interaction_df["ligand"] = interaction_df["ligand"].str.upper()
        interaction_df["receptor"] = interaction_df["receptor"].str.upper()
    elif species.lower() == "mouse":
        interaction_df["ligand"] = interaction_df["ligand"].str.capitalize()
        interaction_df["receptor"] = interaction_df["receptor"].str.capitalize()
    else:
        raise ValueError("species must be either 'human' or 'mouse'")

    interaction_df["interaction"] = interaction_df["ligand"] + "_" + interaction_df["receptor"]

    def extract_genes(name: str):
        name = str(name).split("-")[-1]
        return list(name.split("_"))

    interaction_dict = {}
    for _, row in interaction_df.iterrows():
        ligand_genes = extract_genes(row["ligand"])
        receptor_genes = extract_genes(row["receptor"])
        interaction = row["interaction"]
        interaction_dict[interaction] = ligand_genes + receptor_genes

    interaction_to_pathway = {
        row["interaction"]: row["pathway_name"]
        for _, row in interaction_df.iterrows()
    }

    return interaction_dict, interaction_to_pathway

def compute_interaction_score(
    adata,
    interaction_dict,
    groupby_keys=None,
    grid_size=100,
    library_id_key=None,
    output_dir=None,
    verbose=True,
    plot_name_prefix="result",
):
    """
    Compute and visualize interaction scores for a set of gene pairs/groups.

    Parameters
    ----------
    adata : AnnData
        AnnData object containing spatial transcriptomics data. 
        Must have `.var_names` for genes and `.obsm["spatial"]` for coordinates.

    interaction_dict : dict
        Dictionary where keys are interaction names (str) and values are lists of genes (list of str).
        Example: {"InteractionA": ["Gene1", "Gene2"], "InteractionB": ["Gene3", "Gene4", "Gene5"]}

    groupby_keys : list of str, optional (default: None)
        Keys from `adata.obs` to group cells/spots before computing scores. 
        If None, scores will be aggregated only by spatial grid bins.

    grid_size : int, optional (default: 100)
        Size of the grid bin for spatial aggregation (in pixels).

    library_id_key : str, optional (default: None)
        Column in `adata.obs` specifying multiple library/chip IDs.
        If None, all data will be treated as a single library.

    output_dir : str
        Directory where output files (PDF of plots and CSV of scores) will be saved.

    verbose : bool, optional (default: True)
        If True, print progress and warnings (e.g., skipped interactions).

    plot_name_prefix : str, optional (default: "result")
        Prefix for output file names. Will generate:
        - "<prefix>.pdf" for batch plots
        - "<prefix>_scores.csv" for interaction scores matrix

    Returns
    -------
    heatmap_wide : pandas.DataFrame
        Wide-format matrix of interaction scores. Rows = interactions,
        columns = groups (from `groupby_keys` or spatial bins).

    skipped_pairs : list
        List of interactions that were skipped due to missing genes or errors.
    """
    import os
    import pandas as pd
    import numpy as np
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
    from .pl import plot_genes_grid_expression

    if output_dir is None:
        raise ValueError("output_dir must be specified")
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, f"{plot_name_prefix}_LRpairs.pdf")
    csv_path = os.path.join(output_dir, f"{plot_name_prefix}_scores.csv")

    heatmap_matrix_long = []
    skipped_pairs = []

    with PdfPages(pdf_path) as pdf:
        for interaction, genes in interaction_dict.items():
            try:
                missing_genes = [g for g in genes if g not in adata.var_names]
                if missing_genes:
                    skipped_pairs.append(interaction)
                    if verbose:
                        print(f"{interaction} skipped, missing genes: {missing_genes}")
                    continue

                fig, score_grid, grouped = plot_genes_grid_expression(
                    adata=adata,
                    genes=genes,
                    grid_size=grid_size,
                    groupby_keys =groupby_keys,
                    mode="normal",
                    celltype_key="subclass",
                    library_id_key=library_id_key
                )
                pdf.savefig(fig)
                plt.close(fig)

                if "score" not in grouped.columns:
                    skipped_pairs.append(interaction)
                    if verbose:
                        print(f"{interaction} skipped, no 'score' in grouped")
                    continue

                non_zero = grouped["score"][grouped["score"] > 0]
                score_max = non_zero.quantile(0.995) if len(non_zero) > 0 else 1.0
                grouped["score_capped"] = grouped["score"].clip(upper=score_max)

                if groupby_keys is not None:
                    missing = [col for col in groupby_keys if col not in grouped.columns]
                    if missing:
                        skipped_pairs.append(interaction)
                        if verbose:
                            print(f"{interaction} missing columns {missing}, skipped")
                        continue
                    df_grouped = grouped.groupby(groupby_keys)["score_capped"].mean().reset_index()
                    df_grouped["interaction"] = interaction
                    heatmap_matrix_long.append(df_grouped)
                else:
                    grouped["interaction"] = interaction
                    grouped["group_key"] = grouped["x_bin"].astype(str) + "_" + grouped["y_bin"].astype(str)
                    heatmap_matrix_long.append(grouped)

            except Exception as e:
                skipped_pairs.append(interaction)
                if verbose:
                    print(f"Skipping {interaction} due to error: {e}")

    if heatmap_matrix_long:
        heatmap_df = pd.concat(heatmap_matrix_long, axis=0)
        if groupby_keys is not None:
            group_cols = groupby_keys + ["interaction"]
            heatmap_wide = heatmap_df.pivot_table(index="interaction", columns=groupby_keys[0] if len(groupby_keys)==1 else groupby_keys, values="score_capped")
        else:
            heatmap_wide = heatmap_df.pivot(index="interaction", columns="group_key", values="score_capped")
        heatmap_wide.to_csv(csv_path)
        if verbose:
            print(f"Score matrix saved to: {csv_path}")
    else:
        heatmap_wide = pd.DataFrame()
        if verbose:
            print("No valid interaction scores generated.")

    if verbose:
        print("Batch plotting complete.")
        print(f"Skipped interactions: {skipped_pairs if skipped_pairs else 'None'}")

    return heatmap_wide, skipped_pairs



def compute_cci_score_sum(
    adata,
    source_type,
    target_type,
    L_gene,
    R_gene,
    celltype_key="subclass",
    spatial_key="spatial",
    library_key="chip",
    grid_size=400
):
    """
    Compute total colocalization score between source and target cell types
    using ligand-receptor product expression on spatial grid.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with spatial and expression data.
    source_type : str
        Cell type label for ligand-expressing source cells.
    target_type : str
        Cell type label for receptor-expressing target cells.
    L_gene : list of str
        List of ligand gene names.
    R_gene : list of str
        List of receptor gene names.
    celltype_key : str, default "subclass"
        Column in `adata.obs` containing cell type labels.
    spatial_key : str, default "spatial"
        Key in `adata.obsm` for spatial coordinates.
    library_key : str, default "chip"
        Column in `adata.obs` identifying different tissue slices or chips.
    grid_size : int, default 400
        Grid bin size (in microns) used to group cells spatially.

    Returns
    -------
    total_score : float
        Total colocalization interaction score across all chips.
    """

    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    from scipy.sparse import issparse
    from tqdm import tqdm

    total_score = 0
    for chip_id in adata.obs[library_key].unique():
        adata_chip = adata[adata.obs[library_key] == chip_id].copy()
        coords = adata_chip.obsm[spatial_key]
        x = coords[:, 0]
        y = coords[:, 1]
        x_bin = (x // grid_size).astype(int)
        y_bin = (y // grid_size).astype(int)

        df = pd.DataFrame({"x_bin": x_bin, "y_bin": y_bin})
        df[celltype_key] = adata_chip.obs[celltype_key].values

        genes = L_gene + R_gene
        for gene in genes:
            assert gene in adata.var_names

        X = adata_chip[:, genes].X
        if issparse(X):
            X = X.toarray()

        df_L = df[df[celltype_key] == source_type].copy()
        for i, gene in enumerate(L_gene):
            df_L[gene] = X[df[celltype_key] == source_type, i]

        df_R = df[df[celltype_key] == target_type].copy()
        for j, gene in enumerate(R_gene):
            df_R[gene] = X[df[celltype_key] == target_type, len(L_gene) + j]

        if df_L.empty or df_R.empty:
            continue

        grouped_L = df_L.groupby(["x_bin", "y_bin"])[L_gene].mean()
        grouped_L["L_expr"] = grouped_L.prod(axis=1)

        grouped_R = df_R.groupby(["x_bin", "y_bin"])[R_gene].mean()
        grouped_R["R_expr"] = grouped_R.prod(axis=1)

        merged = pd.merge(grouped_L["L_expr"], grouped_R["R_expr"], left_index=True, right_index=True)
        merged["score"] = merged["L_expr"] * merged["R_expr"]

        total_score += merged["score"].sum()

    return total_score


def generate_cci_heatmap(
    adata,
    source_subclasses=None,
    target_subclasses=None,
    subclass_key="subclass",
    celltype_key=None,  
    L_gene=["SLC1A3", "GLS"],
    R_gene=["GRM7"],
    grid_size=400,
    spatial_key="spatial",
    library_key="chip",
    cmap="Reds"
):
    """
    Generate a heatmap of total colocalization interaction scores
    between source and target cell types or subclasses.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix with spatial and expression data.
    source_subclasses : list of str
        List of source subclasses (or cell types) to evaluate as ligand producers.
    target_subclasses : list of str
        List of target subclasses (or cell types) to evaluate as receptor producers.
    subclass_key : str, default "subclass"
        Column in `adata.obs` with subclass annotations.
    celltype_key : str or None, default None
        Column in `adata.obs` with finer cell type annotations.
        If None, subclass_key will be used as default.
    L_gene : list of str
        List of ligand gene names.
    R_gene : list of str
        List of receptor gene names.
    grid_size : int, default 400
        Grid bin size (in microns) used to group cells spatially.
    spatial_key : str, default "spatial"
        Key in `adata.obsm` for spatial coordinates.
    library_key : str, default "chip"
        Column in `adata.obs` identifying different tissue slices or chips.
    cmap : str, default "Reds"
        Colormap used for heatmap display.

    Returns
    -------
    heatmap_df : pd.DataFrame
        Heatmap matrix of colocalization interaction scores between each source-target pair.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from tqdm import tqdm
    import anndata as ad

    if celltype_key is not None:
        df = adata.obs[[subclass_key, celltype_key]]

        source_annots = df[df[subclass_key].isin(source_subclasses)][celltype_key].unique()
        target_annots = df[df[subclass_key].isin(target_subclasses)][celltype_key].unique()

        heatmap_df = pd.DataFrame(index=target_annots, columns=source_annots, dtype=float)

        for t_ann in tqdm(target_annots, desc="Target"):
            for s_ann in source_annots:
                score = compute_cci_score_sum(
                    adata=adata,
                    source_type=s_ann,
                    target_type=t_ann,
                    L_gene=L_gene,
                    R_gene=R_gene,
                    celltype_key=celltype_key,
                    spatial_key=spatial_key,
                    library_key=library_key,
                    grid_size=grid_size
                )
                heatmap_df.at[t_ann, s_ann] = score
    else:
        subclasses = adata.obs[subclass_key]
        source_set = sorted(set(source_subclasses))
        target_set = sorted(set(target_subclasses))

        heatmap_df = pd.DataFrame(index=target_set, columns=source_set, dtype=float)

        for t in tqdm(target_set, desc="Target"):
            for s in source_set:
                score = compute_cci_score_sum(
                    adata=adata,
                    source_type=s,
                    target_type=t,
                    L_gene=L_gene,
                    R_gene=R_gene,
                    celltype_key=subclass_key,  
                    spatial_key=spatial_key,
                    library_key=library_key,
                    grid_size=grid_size
                )
                heatmap_df.at[t, s] = score

    heatmap_df = heatmap_df.fillna(0)

    plt.figure(figsize=(6, 4))
    sns.heatmap(heatmap_df, cmap=cmap, annot=False, fmt=".1f")
    plt.title("CCI Score Sum by Source/Target")
    plt.xlabel("Source Cell Types")
    plt.ylabel("Target Cell Types")
    plt.tight_layout()
    plt.show()

    return heatmap_df
