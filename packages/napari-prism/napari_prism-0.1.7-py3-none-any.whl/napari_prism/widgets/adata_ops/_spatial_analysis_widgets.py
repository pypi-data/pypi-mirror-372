from itertools import product

import napari
import numpy as np
import pandas as pd
import squidpy as sq
from anndata import AnnData
from kneed import KneeLocator
from magicgui.widgets import ComboBox, Container, Select, create_widget
from napari.qt.threading import thread_worker
from napari.utils.events import EmitterGroup
from qtpy.QtWidgets import QTabWidget

from napari_prism.constants import DEFAULT_DIVERGENT_CMAP
from napari_prism.models.adata_ops.feature_modelling._obs import ObsAggregator
from napari_prism.models.adata_ops.spatial_analysis._cell_level import (
    cellular_neighborhoods_sq,
    proximity_density,
)
from napari_prism.widgets._widget_utils import RangeEditInt
from napari_prism.widgets.adata_ops._base_widgets import AnnDataOperatorWidget
from napari_prism.widgets.adata_ops._plot_widgets import (
    ComplexHeatmapPlotCanvas,
    HeatmapPlotCanvas,
    LinePlotCanvas,
)


class GraphBuilderWidget(AnnDataOperatorWidget):
    """Wrapper for sq.gr.spatial_neighbors functions + extra utils."""

    DEFAULT_STATIC_KWARGS = {
        "elements_to_coordinate_systems": None,  # Widgets work with Adatas, Sdata inputs not supported for the moment
        "table_key": None,  # Widgets work with Adatas, Sdata inputs not supported for the moment
        "coord_type": "generic",  # Imaging package, not visium/etc
    }

    def __init__(self, viewer: "napari.viewer.Viewer", adata: AnnData) -> None:
        super().__init__(viewer, adata)
        #: Events for when an anndata object is changed
        self.events = EmitterGroup(
            source=self,
            adata_changed=None,
        )

    def create_parameter_widgets(self) -> None:
        """Create widgets for the `squidpy.gr.spatial_neighbors` function."""
        self.spatial_key = ComboBox(
            name="SpatialKeys", choices=self.get_obsm_keys, label="spatial_key"
        )
        self.spatial_key.scrollable = True

        self.library_key = ComboBox(
            name="LibraryKeys",
            choices=self.get_categorical_obs_keys,
            label="library_key",
        )
        self.library_key.scrollable = True

        self.n_neighs = create_widget(
            value=10,
            name="n_neighs",
            annotation=int,
            widget_type="SpinBox",
            options={"min": 1, "max": 200, "step": 1},
        )

        self.radius = create_widget(
            value=-1,
            name="radius",
            annotation=float,
            widget_type="SpinBox",
            options={"min": -1, "step": 1.0, "nullable": True},
        )

        self.delaunay = create_widget(
            value=False,
            name="delaunay",
            widget_type="CheckBox",
            annotation=bool,
        )

        self.percentile = create_widget(
            value=0.0,
            name="percentile",
            annotation=float,
            widget_type="SpinBox",
            options={"min": 0.0, "max": 100.0, "step": 1.0, "nullable": True},
        )

        self.transform = ComboBox(
            value=None,
            name="transform",
            choices=["spectral", "cosine"],
            label="transform",
            nullable=True,
        )

        self.set_diag = create_widget(
            value=False,
            name="set_diag",
            widget_type="CheckBox",
            annotation=bool,
        )

        self.key_added = create_widget(
            value="spatial",
            name="key_added",
            annotation=str,
            widget_type="LineEdit",
        )

        self.build_graph_button = create_widget(
            name="Build Graph", widget_type="PushButton", annotation=bool
        )
        self.build_graph_button.changed.connect(self.build_graph)

        self.extend(
            [
                self.spatial_key,
                self.library_key,
                self.n_neighs,
                self.radius,
                self.delaunay,
                self.percentile,
                self.transform,
                self.set_diag,
                self.key_added,
                self.build_graph_button,
            ]
        )

    @thread_worker
    def _build_graph(self):
        self.build_graph_button.enabled = False
        kwargs = self.DEFAULT_STATIC_KWARGS
        kwargs["spatial_key"] = self.spatial_key.value
        kwargs["library_key"] = self.library_key.value
        kwargs["n_neighs"] = self.n_neighs.value
        kwargs["radius"] = (
            self.radius.value if self.radius.value > -1 else None
        )
        kwargs["delaunay"] = self.delaunay.value
        kwargs["percentile"] = (
            self.percentile.value if self.percentile.value > 0 else None
        )
        kwargs["transform"] = self.transform.value
        kwargs["set_diag"] = self.set_diag.value
        kwargs["key_added"] = self.key_added.value

        # Inplace operations.
        sq.gr.spatial_neighbors(self.adata, copy=False, **kwargs)
        self.build_graph_button.enabled = True

    def build_graph(self) -> None:
        """Build the spatial graph using the provided parameters. Once built,
        refresh all widgets to show the AnnData with the spatial graph."""
        worker = self._build_graph()
        worker.start()
        worker.finished.connect(
            lambda: self.events.adata_changed(adata=self.adata)
        )


class NolanComputeWidget(AnnDataOperatorWidget):
    """Implementation of the cellular neighborhoods identification notebook:
    https://github.com/nolanlab/NeighborhoodCoordination/blob/master/
    Neighborhoods/Neighborhood%20Identification.ipynb
    """

    def __init__(self, viewer: "napari.viewer.Viewer", adata: AnnData):
        #: Emits a signal when the CNs are computed. Used by the accompanying
        # plot widget.
        self.events = EmitterGroup(
            source=self,
            adata_changed=None,
            cns_computed=None,  # for preloaded CNs
        )

        super().__init__(viewer, adata)

    def create_parameter_widgets(self) -> None:
        """Expose the main parameters for identifying cellular neighborhoods."""
        self.connectivity_key = ComboBox(
            name="SpatialKeys", choices=self.get_obsp_keys, label="spatial_key"
        )
        self.connectivity_key.scrollable = True

        self.phenotype_key = ComboBox(
            name="PhenotypeKeys",
            choices=self.get_categorical_obs_keys,
            label="phenotype",
        )

        self.k_kmeans_selection = RangeEditInt(
            start=5, stop=15, step=1, name="Number of CNs to search"
        )

        self.mini_batch_kmeans_toggle = create_widget(
            value=False,
            name="mini batch kmeans",
            widget_type="CheckBox",
            annotation=bool,
        )

        # self.parallelise_toggle = create_widget(
        #     value=False,
        #     name="parallelise",
        #     widget_type="CheckBox",
        #     annotation=bool
        # )

        self.compute_cns_button = create_widget(
            name="Compute CNs", widget_type="PushButton", annotation=bool
        )
        self.compute_cns_button.changed.connect(self.compute_nolan_cns)

        self.extend(
            [
                self.connectivity_key,
                self.phenotype_key,
                self.k_kmeans_selection,
                self.mini_batch_kmeans_toggle,
                self.compute_cns_button,
            ]
        )

    @thread_worker
    def _compute_nolan_cns(self) -> None:
        self.compute_cns_button.enabled = False
        kes = list(self.k_kmeans_selection.value)
        kes[1] = kes[1] + kes[2]
        ks = [int(x) for x in np.arange(*kes)]

        cellular_neighborhoods_sq(
            self.adata,
            phenotype=self.phenotype_key.value,
            connectivity_key=self.connectivity_key.value,
            # library_key=self.library_key.value,
            k_kmeans=ks,
            mini_batch_kmeans=self.mini_batch_kmeans_toggle.value,
        )
        self.compute_cns_button.enabled = True
        return self.adata

    def compute_nolan_cns(self) -> None:
        """Compute cellular neighborhoods over a range of many different k or
        number of CNs."""
        worker = self._compute_nolan_cns()
        worker.start()
        worker.returned.connect(lambda x: self.events.adata_changed(adata=x))

    def update_model(self, adata):
        super().update_model(adata)
        if (
            "cn_inertias" in adata.uns
            and "cn_enrichment_matrices" in adata.uns
        ):
            self.events.cns_computed(adata=adata)


class NolanPlotWidget(QTabWidget):
    """Accompoanying plot widget for the NolanComputeWidget. Contains the
    kneedle plot to assess the quality of clustering for identifying CNs, and
    the enrichment matrix plot to show phenotype enrichment in each CN."""

    #: Default keys used to store the results of the CN computation.
    CN_INERTIAS_KEY = "cn_inertias"
    CN_INERTIAS_ATTR = "uns"
    CN_ENRICHMENT_KEY = "cn_enrichment_matrices"
    CN_ENRICHMENT_ATTR = "uns"
    CN_LABELS_KEY = "cn_labels"
    CN_LABELS_ATTR = "obsm"

    def __init__(
        self, viewer: "napari.viewer.Viewer", compute_tab: NolanComputeWidget
    ) -> None:
        """
        Args:
            viewer: The napari viewer instance.
            compute_tab: The compute tab widget that contains the parameters
                for computing the CNs.
        """
        self.events = EmitterGroup(
            source=self,
            adata_changed=None,
        )

        super().__init__()
        self.viewer = viewer
        self.adata = None
        self.compute_tab = compute_tab
        self.compute_tab.events.cns_computed.connect(
            lambda x: self.update_adata(x.adata)
        )
        self.knee_point = None
        self.kneedle_plot = LinePlotCanvas(self.viewer, self)
        self.addTab(self.kneedle_plot, "Kneedle Plot")

        self.enrichment_matrix_plot = Container()
        self.enrichment_matrix_canvas = HeatmapPlotCanvas(self.viewer, self)
        self.choose_K = ComboBox(
            name="Ks",
            choices=self.get_k_kmeans,
            label="Choose K Kmeans run",
            value=None,
            nullable=True,
        )
        self.choose_K.changed.connect(self.update_enrichment_plot)
        self.export_K = create_widget(
            name="Export K", widget_type="PushButton", annotation=bool
        )
        self.export_K.changed.connect(self.export_kmeans)
        self.enrichment_matrix_plot.extend([self.choose_K, self.export_K])
        self.enrichment_matrix_plot.native.layout().addWidget(
            self.enrichment_matrix_canvas
        )
        self.addTab(self.enrichment_matrix_plot.native, "Enrichment Matrix")

        self.reset_choices()

    def export_kmeans(self):
        if self.choose_K.value is not None:
            k = self.choose_K.value
            data = self.adata.obsm["cn_labels"][str(k)]
            self.adata.obs[f"cns_k{k}"] = data.astype("category")
            self.events.adata_changed(adata=self.adata)

    def update_adata(self, adata: AnnData) -> None:
        """Update the adata model and the contained plots. Also update the
        kneedle plot to check if the new AnnData has the results from computing
        CNs."""
        self.adata = adata
        self.reset_choices()

    def reset_choices(self) -> None:
        """Since this is a QTabWidget, we need to reset the choices of the
        contained widgets when the adata model is updated."""
        self.enrichment_matrix_plot.reset_choices()

    def update_kneedle_plot(self) -> None:
        """Update and/or create the Kneedle plot to assess the 'stability' or
        quality of KMeans clustering for identifying CNs."""
        uns_d = getattr(self.adata, self.CN_INERTIAS_ATTR)

        inertia_results = uns_d.get(self.CN_INERTIAS_KEY, None)

        if inertia_results is not None:
            ks = inertia_results.index
            inertias = inertia_results.values
            kneedle = KneeLocator(
                x=list(ks),
                y=list(inertias.flatten()),
                S=1.0,
                curve="convex",
                direction="decreasing",
            )
            self.knee_point = kneedle.knee
            self.knee_point_y = inertia_results.loc[self.knee_point]["Inertia"]
            self.kneedle_plot.plot(
                inertia_results.reset_index(),
                x="k_kmeans",
                y="Inertia",
                grid=True,
            )
            self.kneedle_plot.axes.axvline(
                self.knee_point,
                linestyle="--",
                label="knee/elbow",
                color="r",
            )

            self.knee_point_text = self.kneedle_plot.axes.text(
                self.knee_point,
                self.knee_point_y,
                f"knee/elbow: {self.knee_point}",
                ha="right",
                va="top",
                color="r",
                transform=self.kneedle_plot.axes.get_xaxis_transform(),
            )

            self.kneedle_plot.axes.legend()
        else:
            self.kneedle_plot.clear()

    def get_k_kmeans(self, widget=None) -> None:
        """Get the KMeans runs that were used to compute the CNs."""
        if self.adata is None:
            return []
        else:
            uns_d = getattr(self.adata, self.CN_INERTIAS_ATTR)

            inertia_results = uns_d.get(self.CN_INERTIAS_KEY, None)

            if inertia_results is None:
                return []
            else:
                return list(inertia_results.index)

    def update_enrichment_plot(self) -> None:
        """Update the enrichment matrix plot to show the phenotype enrichment in
        each CN."""
        uns_d = getattr(self.adata, self.CN_ENRICHMENT_ATTR)

        enrichment_results = uns_d.get(self.CN_ENRICHMENT_KEY, None)

        # Choose a k
        chosen_k = self.choose_K.value

        if self.choose_K.value is not None:
            data = enrichment_results[str(chosen_k)].T.sort_index()
            cmap = DEFAULT_DIVERGENT_CMAP
            mag_max = data.abs().max().max()
            self.enrichment_matrix_canvas.plot(
                data=data,
                cmap=cmap,
                vmin=-mag_max,
                vmax=mag_max,
                vcenter=0,
                figsize=(6, 5),  # default?
            )
        else:
            self.enrichment_matrix_canvas.clear()


class NolanWidget(QTabWidget):
    """Parent widget to contain the compute and plot tabs for the Nolan
    cellular neighborhoods identification widgets."""

    def __init__(self, viewer: "napari.viewer.Viewer", adata: AnnData) -> None:
        self.events = EmitterGroup(
            source=self,
            adata_changed=None,  # Passes outputs
        )
        super().__init__()
        self.viewer = viewer

        self.compute_tab = NolanComputeWidget(self.viewer, adata)
        self.compute_tab.events.adata_changed.connect(
            self.events.adata_changed
        )
        self.addTab(self.compute_tab.native, "Compute")

        self.plot_tab = NolanPlotWidget(self.viewer, self.compute_tab)
        self.plot_tab.events.adata_changed.connect(self.events.adata_changed)
        self.addTab(self.plot_tab, "Visualise")

        self.currentChanged.connect(lambda x: self._on_tab_changed(x))

    def _on_tab_changed(self, index):
        if self.widget(index) == self.plot_tab:
            self.plot_tab.update_kneedle_plot()


class ProximityDensityComputeWidget(AnnDataOperatorWidget):
    """Implementation of the proximity density component from the spatial_pscore
    function in scimap."""

    def __init__(self, viewer: "napari.viewer.Viewer", adata: AnnData) -> None:
        #: Emits a signal when the proximity density is computed. Used by the
        # accompanying plot widget.
        self.events = EmitterGroup(
            source=self, adata_changed=None, prox_computed=None
        )
        super().__init__(viewer, adata)

    def reset_choices(self) -> None:
        super().reset_choices()
        self.pair_selection.reset_choices()

    def create_parameter_widgets(self) -> None:
        """Expose the main parameters for computing proximity density."""
        self.connectivity_key = ComboBox(
            name="SpatialKeys", choices=self.get_obsp_keys, label="spatial_key"
        )
        self.connectivity_key.scrollable = True

        self.library_key = ComboBox(
            name="LibraryKeys",
            choices=self.get_categorical_obs_keys,
            label="library_key",
        )
        self.library_key.scrollable = True

        self.phenotype_key = ComboBox(
            name="PhenotypeKeys",
            choices=self.get_multi_categorical_obs_keys,
            label="phenotype",
        )
        self.phenotype_key.changed.connect(self.reset_choices)

        self.pair_selection = Container(layout="horizontal")

        self.first_selection = Select(
            name="PairSelection",
            choices=self.get_obs_categories,
            label="Select pairs (if none selected, uses all)",
        )
        self.second_selection = Select(
            name="PairSelection", choices=self.get_obs_categories, label=" "
        )
        self.pair_selection.extend(
            [self.first_selection, self.second_selection]
        )

        self.compute_button = create_widget(
            name="Compute", widget_type="PushButton", annotation=bool
        )
        self.compute_button.changed.connect(self.compute_proximity_density)

        self.extend(
            [
                self.connectivity_key,
                self.library_key,
                self.phenotype_key,
                self.pair_selection,
                self.compute_button,
            ]
        )

    def get_obs_categories(self, widget=None) -> None:
        """Get the categories of the selected phenotype key."""
        obs_key = self.phenotype_key.value

        if self.adata is None or obs_key is None:
            return []
        else:
            return self.adata.obs[obs_key].cat.categories.tolist()

    @thread_worker
    def _compute_proximity_density(self) -> None:
        self.compute_button.enabled = False
        f = self.first_selection.value
        s = self.second_selection.value
        phenotypes = self.adata.obs[
            self.phenotype_key.value
        ].cat.categories.tolist()

        # TODO: should be options in proximity_density
        if s == [] and f == []:
            pairs = None  # Handled by func
        else:
            if s == []:
                pairs = list(product(phenotypes, f))
            elif f == []:
                pairs = list(product(phenotypes, s))
            else:
                pairs = list(product(f, s))

        adata = proximity_density(
            self.adata,
            pairs=pairs,
            grouping=self.library_key.value,
            phenotype=self.phenotype_key.value,
            connectivity_key=self.connectivity_key.value,
            multi_index=False,
        )
        self.compute_button.enabled = True
        return adata

    def compute_proximity_density(self) -> None:
        """Compute the proximity density for the selected pairs of phenotypes.

        See: https://scimap.xyz/Functions/tl/spatial_pscore/
        """
        worker = self._compute_proximity_density()
        worker.start()
        worker.returned.connect(lambda x: self.events.adata_changed(adata=x))

    def update_model(self, adata):
        super().update_model(adata)
        if "proximity_density_results" in adata.uns:
            self.events.prox_computed(adata=adata)


class ProximityDensityPlotWidget(QTabWidget):
    """Accompanying plot widget for the ProximityDensityComputeWidget.
    TODO: IMPLEMENT PLOT"""

    #: Default keys used to store the results of the proximity density
    # computation in the AnnData object.
    PROX_RESULTS_KEY = "proximity_density_results"
    PROX_RESULTS_ATTR = "uns"
    PROX_MASKS_KEY = "proximity_density_masks"
    PROX_MASKS_ATTR = "uns"
    PROX_CELL_COUNTS_KEY = "proximity_density_cell_counts"
    PROX_CELL_COUNTS_ATTR = "uns"

    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        compute_tab: ProximityDensityComputeWidget,
    ) -> None:
        super().__init__()
        self.viewer = viewer
        self.adata = None
        self.obs_helper = None
        self.compute_tab = compute_tab
        self.compute_tab.events.prox_computed.connect(
            lambda x: self.update_adata(x.adata)
        )
        self.pch_plot = Container()
        # Higher level plot parameters
        self.region_key = ComboBox(
            name="RegionKeys",
            choices=self.get_categorical_obs_keys,
            label="region_key",
        )
        self.region_key.scrollable = True
        self.region_key.changed.connect(self.update_obs_helper)

        # TODO; Single metadata for now, multiple later -> to a Select widget
        self.metadata_key = ComboBox(
            name="MetadataKeys",
            choices=self.get_parallel_keys,
            label="metadata_key",
        )
        self.metadata_key.scrollable = True

        self.plot_button = create_widget(
            name="Plot", widget_type="PushButton", annotation=bool
        )
        self.plot_button.changed.connect(self.update_pch_plot)
        self.pch_plot.extend(
            [self.region_key, self.metadata_key, self.plot_button]
        )
        # PLOTS
        self.pch_canvas = ComplexHeatmapPlotCanvas(self.viewer, self)
        self.pch_plot.native.layout().addWidget(self.pch_canvas)
        self.addTab(self.pch_plot.native, "Complex Heatmap")

    def update_pch_plot(self):
        # Unpack variables
        data = self.adata.uns[self.PROX_RESULTS_KEY]
        # indices;

        # re-instantiate mli
        data = data.set_index(data.columns[:2].tolist())

        # TODO; Single metadata for now, multiple later -> to a Select widget
        metadata_keys = self.metadata_key.value

        left_pad = 0.01
        right_pad = 0.85
        bottom_pad = 0.1
        top_pad = 0.95

        self.pch_canvas.plot(
            data,
            self.obs_helper,
            metadata_keys,
            subplots_adjust=(left_pad, bottom_pad, right_pad, top_pad),
        )

    def update_obs_helper(self) -> None:
        region = self.region_key.value
        if region is not None and self.adata is not None:
            self.obs_helper = ObsAggregator(self.adata, region)

    def update_adata(self, adata: AnnData) -> None:
        self.adata = adata
        self.update_obs_helper()
        # update plot call here
        self.reset_choices()

    def get_parallel_keys(self, widget=None) -> list[str]:
        """Get the keys of the obs attribute that are parallel keys.
        These keys are used to group the data in the proximity density results
        for plotting."""
        if self.adata is not None or self.obs_helper is not None:
            return self.obs_helper.parallel_keys
        else:
            return []

    def get_categorical_obs_keys(self, widget=None) -> list[str]:
        """Returns categorical keys of the obs attribute of the AnnData object.
        If `adata` is None, returns an empty list."""
        # Can be obs keys too
        if self.adata is None:
            return []
        else:
            return [
                x
                for x in self.adata.obs.columns
                if isinstance(self.adata.obs[x].dtype, pd.CategoricalDtype)
            ]

    def reset_choices(self) -> None:
        # reset the contained plot if it contains choices
        self.pch_plot.reset_choices()


class ProximityDensityWidget(QTabWidget):
    """Parent widget to contain the compute and plot tabs for the Proximity
    Density widgets."""

    def __init__(self, viewer: "napari.viewer.Viewer", adata: AnnData) -> None:
        self.events = EmitterGroup(
            source=self,
            adata_changed=None,  # Passes ProximityDensityComputeWidget output
        )
        super().__init__()
        self.viewer = viewer

        self.compute_tab = ProximityDensityComputeWidget(self.viewer, adata)
        self.compute_tab.events.adata_changed.connect(
            self.events.adata_changed
        )
        self.addTab(self.compute_tab.native, "Compute")

        self.plot_tab = ProximityDensityPlotWidget(
            self.viewer, self.compute_tab
        )
        self.addTab(self.plot_tab, "Visualise")
