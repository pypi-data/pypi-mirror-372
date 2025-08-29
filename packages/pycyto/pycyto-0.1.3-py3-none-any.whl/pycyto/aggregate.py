import os
import re
import sys

import anndata as ad
import polars as pl


def _write_h5ad(
    adata: ad.AnnData,
    sample_outdir: str,
    sample: str,
    compress: bool = False,
    mode: str = "gex",
):
    adata.obs_names_make_unique()  # always make unique
    adata.write_h5ad(
        os.path.join(sample_outdir, f"{sample}_{mode}.h5ad"),
        compression="gzip" if compress else None,
    )


def _write_assignments_tsv(
    assignments: pl.DataFrame,
    sample_outdir: str,
    sample: str,
):
    assignments.write_csv(
        os.path.join(sample_outdir, f"{sample}_assignments.tsv"),
        separator="\t",
    )


def _filter_crispr_adata_to_gex_barcodes(
    gex_adata: ad.AnnData,
    crispr_adata: ad.AnnData,
) -> ad.AnnData:
    """Filters the CRISPR data to only include barcodes present in the GEX data.

    Creates a dummy column on each that captures all unique information.

    # already annotated
    index: (cell_barcode + flex_barcode + lane_id)

    # to create
    dummy = index + sample + experiment
    """
    gex_adata.obs["dummy"] = (
        gex_adata.obs.index
        + "-"
        + gex_adata.obs["sample"]
        + "-"
        + gex_adata.obs["experiment"]
    )
    crispr_adata.obs["dummy"] = (
        crispr_adata.obs.index
        + "-"
        + crispr_adata.obs["sample"]
        + "-"
        + crispr_adata.obs["experiment"]
    )
    mask = crispr_adata.obs["dummy"].isin(gex_adata.obs["dummy"])
    gex_adata.obs.drop(columns=["dummy"], inplace=True)  # type: ignore
    crispr_adata.obs.drop(columns=["dummy"], inplace=True)  # type: ignore
    return crispr_adata[mask]


def _process_gex_crispr_set(
    gex_adata_list: list[ad.AnnData],
    crispr_adata_list: list[ad.AnnData],
    assignments_list: list[pl.DataFrame],
    sample_outdir: str,
    sample: str,
    compress: bool = False,
):
    gex_adata = ad.concat(gex_adata_list)
    crispr_adata = ad.concat(crispr_adata_list)
    assignments = pl.concat(assignments_list, how="vertical_relaxed").unique()

    if assignments["cell_id"].str.contains("CR").any():
        assignments = assignments.with_columns(
            match_barcode=pl.col("cell_id") + "-" + pl.col("lane_id").cast(pl.String)
        ).with_columns(pl.col("match_barcode").str.replace("CR", "BC"))
        crispr_adata.obs.index = crispr_adata.obs.index.str.replace("CR", "BC")
    else:
        assignments = assignments.with_columns(
            match_barcode=pl.col("cell_id") + "-" + pl.col("lane_id").cast(pl.String)
        )

    gex_adata.obs = gex_adata.obs.merge(  # type: ignore
        assignments.select(["match_barcode", "assignment", "counts", "moi"])
        .to_pandas()
        .set_index("match_barcode"),
        left_index=True,
        right_index=True,
        how="left",
    )

    # Filter crispr adata to filtered barcodes
    filt_crispr_adata = _filter_crispr_adata_to_gex_barcodes(
        gex_adata=gex_adata,
        crispr_adata=crispr_adata,
    )

    # Write both modes
    _write_h5ad(
        adata=gex_adata,
        sample_outdir=sample_outdir,
        sample=sample,
        compress=compress,
        mode="gex",
    )
    _write_h5ad(
        adata=filt_crispr_adata,
        sample_outdir=sample_outdir,
        sample=sample,
        compress=compress,
        mode="crispr",
    )
    _write_assignments_tsv(
        assignments=assignments,
        sample_outdir=sample_outdir,
        sample=sample,
    )


def _load_assignments_for_experiment_sample(
    root: str,
    crispr_bcs: list[str],
    lane_id: str,
    experiment: str,
    sample: str,
) -> list[pl.DataFrame]:
    assignments_list = []
    expected_crispr_assignments_dir = os.path.join(root, "assignments")
    for crispr_bc in crispr_bcs:
        expected_crispr_assignments_path = os.path.join(
            expected_crispr_assignments_dir,
            f"{crispr_bc}.assignments.tsv",
        )
        if os.path.exists(expected_crispr_assignments_path):
            bc_assignments = pl.read_csv(
                expected_crispr_assignments_path,
                separator="\t",
            ).with_columns(
                pl.lit(sample).alias("sample"),
                pl.lit(experiment).alias("experiment"),
                pl.lit(lane_id).alias("lane_id"),
                pl.lit(crispr_bc).alias("bc_idx"),
            )
            assignments_list.append(bc_assignments)
        else:
            print(
                f"Missing expected CRISPR assignments data for `{crispr_bc}` in {root} in path: {expected_crispr_assignments_path}",
                file=sys.stderr,
            )
    return assignments_list


def _load_gex_anndata_for_experiment_sample(
    root: str,
    gex_bcs: list[str],
    lane_id: str,
    experiment: str,
    sample: str,
) -> list[ad.AnnData]:
    gex_adata_list = []
    expected_gex_adata_dir = os.path.join(root, "counts")
    for gex_bc in gex_bcs:
        expected_gex_adata_path = os.path.join(
            expected_gex_adata_dir, f"{gex_bc}.filt.h5ad"
        )
        if os.path.exists(expected_gex_adata_path):
            bc_adata = ad.read_h5ad(expected_gex_adata_path)
            bc_adata.obs["sample"] = sample
            bc_adata.obs["experiment"] = experiment
            bc_adata.obs["lane_id"] = lane_id
            bc_adata.obs["bc_idx"] = gex_bc
            bc_adata.obs.index += "-" + bc_adata.obs["lane_id"].astype(str)
            gex_adata_list.append(bc_adata)
        else:
            print(
                f"Missing expected GEX data for `{gex_bc}` in {root} in path: {expected_gex_adata_path}",
                file=sys.stderr,
            )
    return gex_adata_list


def _load_crispr_anndata_for_experiment_sample(
    root: str,
    crispr_bcs: list[str],
    lane_id: str,
    experiment: str,
    sample: str,
) -> list[ad.AnnData]:
    crispr_adata_list = []
    expected_crispr_adata_dir = os.path.join(root, "counts")
    for crispr_bc in crispr_bcs:
        expected_crispr_adata_path = os.path.join(
            expected_crispr_adata_dir, f"{crispr_bc}.h5ad"
        )
        if os.path.exists(expected_crispr_adata_path):
            bc_adata = ad.read_h5ad(expected_crispr_adata_path)
            bc_adata.obs["sample"] = sample
            bc_adata.obs["experiment"] = experiment
            bc_adata.obs["lane_id"] = lane_id
            bc_adata.obs["bc_idx"] = crispr_bc
            bc_adata.obs.index += "-" + bc_adata.obs["lane_id"].astype(str)
            crispr_adata_list.append(bc_adata)
        else:
            print(
                f"Missing expected CRISPR data for `{crispr_bc}` in {root} in path: {expected_crispr_adata_path}",
                file=sys.stderr,
            )
    return crispr_adata_list


def aggregate_data(
    config: pl.DataFrame, cyto_outdir: str, outdir: str, compress: bool = False
):
    unique_samples = config["sample"].unique().to_list()
    for s in unique_samples:
        unique_experiments = (
            config.filter(pl.col("sample") == s)["experiment"].unique().to_list()
        )

        gex_adata_list = []
        crispr_adata_list = []
        assignments_list = []

        for e in unique_experiments:
            print(f"Processing sample {s} experiment {e}...", file=sys.stderr)

            subset = config.filter(pl.col("sample") == s, pl.col("experiment") == e)

            # identify necessary prefixes for output
            unique_prefixes = subset["expected_prefix"].unique().to_list()
            prefix_regex = re.compile(rf"^({'|'.join(unique_prefixes)}).*")

            # determine data regex
            crispr_regex = re.compile(r".+_CRISPR_Lane.+")
            gex_regex = re.compile(r".+_GEX_Lane.+")
            lane_regex = re.compile(r"_Lane(\d+)")

            gex_bcs = (
                subset.filter(pl.col("mode") == "gex")
                .select("bc_component")
                .to_series()
                .unique()
                .to_list()
            )
            crispr_bcs = (
                subset.filter(pl.col("mode") == "crispr")
                .select("bc_component")
                .to_series()
                .unique()
                .to_list()
            )

            n_matches = 0
            for root, _dirs, _files in os.walk(cyto_outdir):
                basename = os.path.basename(root)
                if prefix_regex.search(basename):
                    print(f"Processing {basename}...", file=sys.stderr)

                    lane_regex_match = lane_regex.search(basename)
                    if lane_regex_match:
                        lane_id = lane_regex_match.group(1)
                    else:
                        raise ValueError(f"Invalid basename: {basename}")

                    # process crispr data
                    if crispr_regex.match(basename):
                        # Load in assignments
                        local_assignments_list = (
                            _load_assignments_for_experiment_sample(
                                root=root,
                                crispr_bcs=crispr_bcs,
                                lane_id=lane_id,
                                experiment=e,
                                sample=s,
                            )
                        )
                        assignments_list.extend(local_assignments_list)

                        # Load in crispr anndata
                        local_crispr_adata_list = (
                            _load_crispr_anndata_for_experiment_sample(
                                root=root,
                                crispr_bcs=crispr_bcs,
                                lane_id=lane_id,
                                experiment=e,
                                sample=s,
                            )
                        )
                        crispr_adata_list.extend(local_crispr_adata_list)

                    # process gex data
                    elif gex_regex.search(basename):
                        local_gex_list = _load_gex_anndata_for_experiment_sample(
                            root=root,
                            gex_bcs=gex_bcs,
                            lane_id=lane_id,
                            experiment=e,
                            sample=s,
                        )
                        gex_adata_list.extend(local_gex_list)

                    n_matches += 1

                    # finish on expected number of prefixes (don't recurse too deeply)
                    if n_matches == len(unique_prefixes):
                        break

        sample_outdir = os.path.join(outdir, s)
        os.makedirs(sample_outdir, exist_ok=True)

        # CRISPR + GEX case
        if len(gex_adata_list) > 0 and len(assignments_list) > 0:
            _process_gex_crispr_set(
                gex_adata_list=gex_adata_list,
                crispr_adata_list=crispr_adata_list,
                assignments_list=assignments_list,
                sample_outdir=sample_outdir,
                sample=s,
                compress=compress,
            )

        elif len(gex_adata_list) > 0:
            print("Writing GEX data...", file=sys.stderr)
            gex_adata = ad.concat(gex_adata_list)
            _write_h5ad(
                adata=gex_adata,
                sample_outdir=sample_outdir,
                sample=s,
                compress=compress,
                mode="gex",
            )

        elif len(assignments_list) > 0:
            print("Writing assignments...", file=sys.stderr)
            assignments = pl.concat(assignments_list, how="vertical_relaxed").unique()
            _write_assignments_tsv(
                assignments=assignments,
                sample_outdir=sample_outdir,
                sample=s,
            )

            print("Writing crispr h5ad...", file=sys.stderr)
            crispr_adata = ad.concat(crispr_adata_list)
            _write_h5ad(
                adata=crispr_adata,
                sample_outdir=sample_outdir,
                sample=s,
                compress=compress,
                mode="crispr",
            )
