import math
from pathlib import Path

import geopandas as gpd
import napari
import numpy as np
import pandas as pd
import shapely
import skimage
import xarray as xr
from magicgui.widgets import ComboBox, Select, Table, create_widget
from napari.qt.threading import thread_worker
from numpy import dtype, ndarray
from qtpy.QtWidgets import QAbstractItemView, QHBoxLayout
from spatialdata.transformations import Scale, Translation, get_transformation
from xarray import DataArray

from napari_prism.models.tma_ops._tma_image import (
    MultiScaleImageOperations,
    SingleScaleImageOperations,
    TMADearrayer,
    TMAMasker,
    TMAMeasurer,
    TMASegmenter,
)
from napari_prism.widgets._widget_utils import (
    create_static_selection_widget,
    get_selected_layer,
)
from napari_prism.widgets.tma_ops._base_widgets import (
    MultiScaleImageNapariWidget,
    SingleScaleImageNapariWidget,
)


class UtilsNapariWidget(MultiScaleImageNapariWidget):
    # TODO:
    # 1) Shapes -> User modifies layer -> Update sdata shapes manually
    # Shift L and Shift E of the layer does not inherit the scaling factor
    # So the added shape is the downscaled one
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        model: TMAMasker | None = None,  # placeholder?
        *args,
        **kwargs,
    ) -> None:
        super().__init__(viewer, model, *args, **kwargs)
        self.create_parameter_widgets()
        # The model changes when 1) sdata is changed, 2) image_name is changed;
        # These events are trigged by napari_spatialdata.view on layer update
        # When layer is updated -> Get the contained sdata if any;
        self.update_model()
        self.viewer.layers.selection.events.changed.connect(self.update_model)

    def create_parameter_widgets(self):
        self.add_selected_image_channel_button = create_widget(
            value=False,
            name="Add current view as standalone",
            annotation=bool,
            widget_type="PushButton",
            options={"enabled": False},
        )

        self.add_selected_image_channel_button.changed.connect(
            self.add_selected_image_channel
        )

        self.overwrite_save_selected_layer_button = create_widget(
            value=False,
            name="Overwrite save selected layer",
            annotation=bool,
            widget_type="PushButton",
            options={"enabled": False},
        )
        self.overwrite_save_selected_layer_button.changed.connect(
            self.overwrite_save_selected_layer
        )

        self.mask_expansion_entry = create_widget(
            value=0,
            name="Expand segmentation masks by um units",
            annotation=float,
            widget_type="LineEdit",
            options={"nullable": True},
        )
        self.mask_expansion_button = create_widget(
            value=False,
            name="Expand segmentation masks",
            annotation=bool,
            widget_type="PushButton",
            options={"enabled": False},
        )
        self.mask_expansion_button.changed.connect(self.expand_masks)
        self.mask_widgets = QHBoxLayout()
        self.mask_widgets.addWidget(self.mask_expansion_entry.native)
        self.mask_widgets.addWidget(self.mask_expansion_button.native)
        self.extend(
            [
                self.add_selected_image_channel_button,
                self.overwrite_save_selected_layer_button,
            ]
        )
        self.native.layout().addLayout(self.mask_widgets)

        self.save_sdata_to_disk_button = create_widget(
            value=False,
            name="Save in-memory spatialdata elements to disk",
            annotation=bool,
            widget_type="PushButton",
            options={
                "tooltip": "Saves on-memory elements to on-disk objects."
            },
        )
        self.save_sdata_to_disk_button.changed.connect(self.save_sdata_to_disk)
        self.native.layout().addWidget(self.save_sdata_to_disk_button.native)

    def save_sdata_to_disk(self):
        """Save the sdata elements to disk."""

        selected = self.viewer.layers.selection.active
        if selected is not None and "sdata" in selected.metadata:
            sdata = selected.metadata["sdata"]
            mem_elements, _ = sdata._symmetric_difference_with_zarr_store()
            if len(mem_elements) > 0:
                for element in mem_elements:
                    sdata.write_element(element.split("/")[-1])
        else:
            print("No sdata found in the selected layer.")

    def get_saveable_layers(self, widget=None):
        """Sdata attrs"""
        return [
            x.name
            for x in self.viewer.layers
            if "sdata" in x.metadata and x.metadata["sdata"] is not None
        ]

    def add_selected_image_channel(self):
        channel = self.get_channel()
        image = self.model.get_image()
        image_list = [image.sel(c=channel)[x].image for x in image]
        self.viewer.add_image(
            image_list,
            name=f"{self.model.image_name} View: ({channel})",
            multiscale=True,
            blending="additive",
        )

    def merge_image_labels(
        self,
        labels: list[DataArray | ndarray[dtype[bool]]],
    ) -> DataArray | ndarray[dtype[bool]]:
        """Merge multiple labels into a single DataArray."""

    def update_model(self):
        selected = self.viewer.layers.selection.active

        if selected is not None and "sdata" in selected.metadata:
            if isinstance(selected, napari.layers.shapes.shapes.Shapes):
                # Support only shapes for now
                self.model = SingleScaleImageOperations(
                    selected.metadata["sdata"], selected.metadata["name"]
                )
                self.overwrite_save_selected_layer_button.enabled = True
                self.add_selected_image_channel_button.enabled = False
                self.mask_expansion_button.enabled = False
            elif isinstance(
                selected.data, napari.layers._multiscale_data.MultiScaleData
            ):
                self.model = MultiScaleImageOperations(
                    selected.metadata["sdata"], selected.metadata["name"]
                )
                self.add_selected_image_channel_button.enabled = True
                self.overwrite_save_selected_layer_button.enabled = False
                self.mask_expansion_button.enabled = False
            elif isinstance(selected, napari.layers.Labels):
                # Support only labels for now
                self.model = SingleScaleImageOperations(
                    selected.metadata["sdata"], selected.metadata["name"]
                )
                self.overwrite_save_selected_layer_button.enabled = False
                self.add_selected_image_channel_button.enabled = False
                self.mask_expansion_button.enabled = True
            else:
                self.model = None
                self.add_selected_image_channel_button.enabled = False
                self.overwrite_save_selected_layer_button.enabled = False
                self.mask_expansion_button.enabled = False

            self.reset_choices()

        else:
            self.model = None
            self.reset_choices()
            self.add_selected_image_channel_button.enabled = False
            self.overwrite_save_selected_layer_button.enabled = False

    def expand_masks(self):
        layer = self.viewer.layers.selection.active

        expansion_um = float(self.mask_expansion_entry.value)
        expansion_px = self.model.convert_um_to_px(expansion_um)
        expanded = skimage.segmentation.expand_labels(layer.data, expansion_px)
        # inherited_metadata = layer.metadata
        # inherited_metadata["global_seg_mask"] = expanded
        self.viewer.add_labels(
            expanded,
            name=layer.name + f"_expanded_{expansion_um}um",
            affine=layer.affine,
            metadata={
                "sdata": layer.metadata["sdata"],
                "global_seg_mask": expanded,
                "transformation_sequence": layer.metadata[
                    "transformation_sequence"
                ],
                "name": layer.name + f"_expanded_{expansion_um}um",
                "parent_layer": layer.metadata["parent_layer"],
                "_current_cs": layer.metadata["_current_cs"],
            },
        )

    def overwrite_save_selected_layer(self):
        layer = self.viewer.layers.selection.active

        # Shapes Directive;
        def _update_metadata(layer):
            """From https://github.com/scverse/napari-spatialdata/blob/
            a38e2866c9195866fecf1eca0f911d52587b163a/src/napari_spatialdata/
            _viewer.py

            Modified so that layer.metadata["_columns_df"] is assigned the
            TMA labels, instead of None.
            """
            element = self.model.sdata[self.model.image_name]
            stored_geoms = element["geometry"]
            current_geoms = layer.data

            def bbox_to_array(row):
                return np.array(
                    [
                        [row["miny"], row["maxx"]],  # Top-right
                        [row["maxy"], row["maxx"]],  # Bottom-right
                        [row["maxy"], row["minx"]],  # Bottom-left
                        [row["miny"], row["minx"]],  # Top-left
                        [
                            row["miny"],
                            row["maxx"],
                        ],  # Closing point (Top-right)
                    ]
                )

            stored_geoms = [
                bbox_to_array(row) for _, row in stored_geoms.bounds.iterrows()
            ]

            def find_missing_array_indices(original_list, modified_list):
                missing_indices = []
                for i, orig_array in enumerate(original_list):
                    if not any(
                        np.array_equal(orig_array, mod_array)
                        for mod_array in modified_list
                    ):
                        missing_indices.append(i)
                return missing_indices

            missing_indices = find_missing_array_indices(
                stored_geoms, current_geoms
            )

            if missing_indices != []:
                updated_gdf = element.drop(index=missing_indices)
                updated_gdf = updated_gdf.reset_index(drop=True)
                updated_n_indices = updated_gdf.shape[0]
                updated_indices = list(range(updated_n_indices))
                columns_df_label = layer.metadata["_columns_df"].columns[0]
                updated_columns_df = pd.DataFrame(
                    updated_gdf[columns_df_label]
                )

                # update layer metadata
                layer.metadata["_n_indices"] = updated_n_indices
                layer.metadata["_indices"] = updated_indices
                layer.metadata["_columns_df"] = updated_columns_df

        def _save_annotated_shapes_layer(layer):
            updated_data = layer.data
            annotations_inherited = layer.metadata["_columns_df"][
                "tma_label"
            ].values
            # TODO: Technically below should be handled by the model..?
            geoms_t = [x[:, ::-1] for x in updated_data]
            geoms = [shapely.geometry.Polygon(x) for x in geoms_t]
            gdf_recon = gpd.GeoDataFrame(
                {"geometry": geoms, "tma_label": annotations_inherited}
            )
            # Inherit transformations from layer
            element = layer.metadata["sdata"][layer.metadata["name"]]
            transforms = get_transformation(element, "global")
            # print("adding shapes", gdf_recon)

            self.model.add_shapes(
                gdf_recon,
                layer.name,  # Overwrite;
                write_element=True,
                transformations={"global": transforms},
            )

        if (
            isinstance(layer, napari.layers.shapes.shapes.Shapes)
            and "_columns_df" in layer.metadata
            and "sdata" in layer.metadata
            and "name" in layer.metadata
            and isinstance(layer.data, list)
        ):
            updated_n_indices = len(layer.data)
            # If a shape deletion occurred,
            if layer.metadata["_n_indices"] > updated_n_indices:
                _update_metadata(layer)
            _save_annotated_shapes_layer(layer)


class TMAMaskerNapariWidget(MultiScaleImageNapariWidget):
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        model: TMAMasker | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(viewer, model, *args, **kwargs)
        self.create_parameter_widgets()
        # The model changes when 1) sdata is changed, 2) image_name is changed;
        # These events are trigged by napari_spatialdata.view on layer update
        # When layer is updated -> Get the contained sdata if any;
        self.viewer.layers.selection.events.changed.connect(self.update_model)

    #        self.update_model()

    # def set_init_bbox(self):
    #     pass

    def get_bbox_shape_layers(self, widget=None):
        rects = [None]
        if self.model is not None:
            for x in self.viewer.layers:
                if (
                    isinstance(x, napari.layers.shapes.shapes.Shapes)
                    and len(x.shape_type) == 1
                    and x.shape_type[0] == "rectangle"
                ):
                    rects = [None, x.name]
        return rects

    def get_bbox_shape_bounds(
        self, bbox_layer: napari.layers.shapes.shapes.Shapes
    ) -> tuple[int, int, int, int]:
        data_arr = np.array(bbox_layer.data[0])[:, 1:]
        xs = data_arr[:, 1]
        ys = data_arr[:, 0]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        # Cast all values to nearest integer; min as floor, max as ceil
        xmin, ymin = map(math.floor, (xmin, ymin))
        xmax, ymax = map(math.ceil, (xmax, ymax))

        return (xmin, ymin, xmax, ymax)

    def update_model(self):
        # Create widgets on initialisation; can tak from launch method
        # layer = get_selected_layer(
        #     self._viewer, self._select_layer_widget)
        selected = self.viewer.layers.selection.active

        if (
            selected is not None
            and "sdata" in selected.metadata
            and isinstance(selected, napari.layers.Image)
            and isinstance(
                selected.data, napari.layers._multiscale_data.MultiScaleData
            )
        ):
            self.model = TMAMasker(
                selected.metadata["sdata"], selected.metadata["name"]
            )

            self.reset_choices()
            self._generate_masks_button.enabled = True
        else:
            if (
                selected is not None
                and "masks" in selected.metadata
                and "transforms" in selected.metadata
                and "channel_label" in selected.metadata
                and "masks_gdf" in selected.metadata
                and "parent_layer" in selected.metadata
                and isinstance(selected, napari.layers.Labels)
            ):
                parent = selected.metadata["parent_layer"]
                self.model = TMAMasker(
                    parent.metadata["sdata"], parent.metadata["name"]
                )
                self.reset_choices()
                self._save_results_button.enabled = True
                self._generate_masks_button.enabled = False
            else:
                self.model = None
                self.reset_choices()
                self._save_results_button.enabled = False
                self._generate_masks_button.enabled = False
        # self.set_parent_layer(layer)
        # self.model = TMAMasker(
        #     layer.data,
        #     layer.name,
        #     self.working_channel,
        #     self.scale_index,
        #     layer.metadata["mpp"])

        # TODO: needs a callback to delete the outputs if update_tma_model is called

    def create_parameter_widgets(self):
        super().create_parameter_widgets()

        # self._inherit_correction_settings = create_widget(
        #     value=False,
        #     name="Apply image correction from layer controls",
        #     annotation=bool,
        #     widget_type="CheckBox"
        # )

        # Create widgets on initialisation; can tak from launch method
        self._bbox_shape_layer_selection = ComboBox(
            name="ValidBboxLayers",
            choices=self.get_bbox_shape_layers,
            label="Select shape to mask within",
        )

        self._mask_channel_selection = Select(
            name="MaskingChannels",
            choices=self.get_channels,
            label="Select channel(s) for masking",
        )

        self._sigma_slider = create_widget(
            value=10,
            name="Gaussian Blur Sigma/Spread in um",
            annotation=float,
            options={"min": 0, "step": 0.25, "max": 50},
            widget_type="SpinBox",
        )

        self._expansion_slider = create_widget(
            value=10,
            name="Blur expansion in um",
            annotation=int,
            options={"min": 0, "step": 1, "max": 100},
            widget_type="SpinBox",
        )

        self._li_threshold_button = create_widget(
            value=False,
            name="Apply Li Thresholding",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._sobel_button = create_widget(
            value=False,
            name="Apply 2D Sobel filter (edgify)",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._adaptive_histogram_button = create_widget(
            value=False,
            name="Apply local histogram equalisation",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._gamma_correction_button = create_widget(
            value=False,
            name="Apply gamma (0.2) correction",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._estimated_core_diameter_um_entry = create_widget(
            value=700,
            name="Estimated core diameter in um",
            annotation=float,
            widget_type="LineEdit",
        )

        self._thresholding_core_fraction_entry = create_widget(
            value=0.25,
            name="Masks with this fraction of estimated core area to include",
            annotation=float,
            widget_type="LineEdit",
        )

        # TODO: left off
        # self._mask_label_entry = create_widget(
        #     value="mask",
        #     name="Mask label",
        #     annotation=str,
        #     widget_type="LineEdit")

        self._generate_masks_button = create_widget(
            value=False,
            name="Generate masks",
            annotation=bool,
            widget_type="PushButton",
        )

        self._fill_holes_checkbox = create_widget(
            value=False,
            name="Fill holes",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._remove_small_spots_size_entry = create_widget(
            value=0,
            name="Remove small spots",
            annotation=int,
            options={"min": 0, "step": 10, "max": 1000},
            widget_type="SpinBox",
        )

        self._save_results_button = create_widget(
            value=False,
            name="Save results",
            annotation=bool,
            widget_type="PushButton",
        )

        # Populate container with widgets;
        ls = [
            # self._inherit_correction_settings,
            self._bbox_shape_layer_selection,
            self._mask_channel_selection,
            self._sigma_slider,
            self._expansion_slider,
            self._li_threshold_button,
            self._sobel_button,
            self._adaptive_histogram_button,
            self._gamma_correction_button,
            self._estimated_core_diameter_um_entry,
            self._thresholding_core_fraction_entry,
            self._fill_holes_checkbox,
            self._remove_small_spots_size_entry,
            self._generate_masks_button,
            self._save_results_button,
        ]
        # If initialised with an sdata, enable
        if self.model is not None:
            self._generate_masks_button.enabled = True
            self._save_results_button.enabled = True
        else:
            self._generate_masks_button.enabled = False
            self._save_results_button.enabled = False

        self._generate_masks_button.changed.connect(self._generate)
        self._save_results_button.changed.connect(
            self._save_selected_layer_to_sdata
        )
        self.extend(ls)

    # TODO: Thread worker and progress bar
    def _generate(self):  # Similar to nested _generate
        # Check if user has provided and selected a bounding box
        if self._bbox_shape_layer_selection.value is not None:
            bbox_layer = get_selected_layer(
                self.viewer, self._bbox_shape_layer_selection
            )
            bbox_bounds = self.get_bbox_shape_bounds(bbox_layer)
        else:
            bbox_bounds = None

        # Check if user wants to use the viewer settings for the image
        contrast_limits = None
        gamma = None
        # TODO:
        # if self._inherit_correction_settings.value:
        #     selected = self.viewer.layers.selection.active
        #     contrast_limits = selected.contrast_limits
        #     gamma = selected.gamma

        scale = self.get_multiscale_image_scales()[self.scale_index]
        results = self.model.mask_tma_cores(
            channel=self._mask_channel_selection.value,  # self.get_channel()
            scale=scale,
            mask_selection=bbox_bounds,
            sigma_um=self._sigma_slider.value,
            expansion_um=self._expansion_slider.value,
            li_threshold=self._li_threshold_button.value,
            edge_filter=self._sobel_button.value,
            adapt_hist=self._adaptive_histogram_button.value,
            gamma_correct=self._gamma_correction_button.value,
            estimated_core_diameter_um=float(
                self._estimated_core_diameter_um_entry.value
            ),
            core_fraction=float(self._thresholding_core_fraction_entry.value),
            contrast_limits=contrast_limits,
            gamma=gamma,
            fill_holes=self._fill_holes_checkbox.value,
            remove_small_spots_size=self._remove_small_spots_size_entry.value,
        )

        masks, transformation_sequence, channel_label, masks_gdf = results
        masks = masks.astype(np.int32)
        self.latest_masks = masks
        self.latest_transforms = transformation_sequence
        self.latest_channel_label = channel_label
        self.latest_masks_gdf = masks_gdf
        # current_cs = self.get_sdata_widget().coordinate_system_widget._system
        # Retrieve affine transform as per spatialdata specifications;
        # cs = transformation_sequence.keys().__iter__().__next__() if current_cs is None else current_cs
        # ct = transformation_sequence.get(cs)
        affine = transformation_sequence.to_affine_matrix(
            ("y", "x"), ("y", "x")
        )
        # Show mask in memory to viewer, not as sdata yet
        parent_layer = self.viewer.layers.selection.active
        self.viewer.add_labels(
            masks,
            name=channel_label + "_mask",
            affine=affine,
            # For saving later
            metadata={
                "sdata": self.model.sdata,
                "masks": masks,
                "transforms": transformation_sequence,
                "channel_label": channel_label,
                "masks_gdf": masks_gdf,
                "name": channel_label + "_mask",
                "parent_layer": parent_layer,
                "_current_cs": parent_layer.metadata["_current_cs"],
            },
        )

        # refresh the Sdata elements after this is called.
        # NOTE: will be depracated in 0.5.0 napari

    def _save_selected_layer_to_sdata(self):
        selected = self.viewer.layers.selection.active
        if (
            selected is not None
            and "masks" in selected.metadata
            and "transforms" in selected.metadata
            and "channel_label" in selected.metadata
            and "masks_gdf" in selected.metadata
            and "parent_layer" in selected.metadata
            and isinstance(selected, napari.layers.Labels)
        ):
            self.update_model()
            self.model.save_masks(
                selected.metadata["masks"],
                selected.name,  # The name in the viewer
                selected.metadata["transforms"],
            )

            self.model.save_shapes(
                selected.metadata["masks_gdf"],
                selected.name,  # The name in the viewer
                selected.metadata["transforms"],
            )
            self.refresh_sdata_widget()


class TMADearrayerNapariWidget(SingleScaleImageNapariWidget):
    # TODO: Deleted shape event -> Update layer of tma_labels
    # TODO: Log TMA Grid as an AnnData Tablemodel; obsm attr.
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        model: TMADearrayer | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(viewer, model, *args, **kwargs)
        self.create_parameter_widgets()
        self.viewer.layers.selection.events.changed.connect(self.update_model)

    def get_line_shape_layers(self, widget=None):
        """Support multiple lines."""
        lines = [None]
        if self.model is not None:
            for x in self.viewer.layers:
                if (
                    isinstance(x, napari.layers.shapes.shapes.Shapes)
                    and x.shape_type[0] == "line"
                ):
                    lines = [None, x.name]
        return lines

    def get_line_mean_lengths(
        self, line_layer: napari.layers.shapes.shapes.Shapes
    ) -> float:
        lines = line_layer.data
        lengths = []
        for line in lines:
            arr = np.array(line)[:, 1:]
            xs = arr[:, 0]
            ys = arr[:, 1]
            length = np.sqrt((xs[1] - xs[0]) ** 2 + (ys[1] - ys[0]) ** 2)
            lengths.append(length)
        return np.mean(lengths)

    def _dearray(self):
        #   layer = get_selected_layer(self.viewer, self._select_layer_widget)
        masks_gdf = self.model.sdata.get(self.model.image_name + "_poly", None)

        results = self.model.dearray_and_envelope_tma_cores(
            float(self._estimated_core_diameter_um_entry.value),
            expected_rows=int(self._nrows_entry.value),
            expected_cols=int(self._ncols_entry.value),
            expectation_margin=0.2,
            masks_gdf=masks_gdf,
        )  # Sets self.gff

        tma_cores, tma_envelope, envelopes, transforms = results
        self.latest_tma_cores = tma_cores
        self.latest_tma_envelope = tma_envelope
        self.latest_envelopes = envelopes
        self.latest_transforms = transforms

        # affine = transforms["global"].to_affine_matrix(("y", "x"), ("y", "x"))
        # parent_layer = self.viewer.layers.selection.active

        # # from napari-spatialdata _viewer.py
        # simplify = len(envelopes) > config.POLYGON_THRESHOLD
        # polygons, indices = _get_polygons_properties(envelopes, simplify)
        # polygons = _transform_coordinates(polygons, f=lambda x: x[::-1])

        # self.viewer.add_shapes(
        #     polygons,
        #     name="TMA envelope",
        #     affine=affine,
        #     shape_type="polygon",
        #     edge_color="#12f4f9",
        #     edge_width=2,
        #     face_color="#FF0000",
        #     metadata={
        #         "sdata": self.model.sdata,
        #         "tma_envelope": tma_envelope,
        #         "tma_cores": tma_cores,
        #         "envelopes": envelopes,
        #         "name": "TMA envelope",
        #         "transforms": transforms,
        #         "parent_layer": parent_layer,
        #         "_current_cs": parent_layer.metadata["_current_cs"],
        #     },
        # )
        self.model.save_dearray_results(
            tma_cores=tma_cores,
            tma_envelope=tma_envelope,
            envelopes=envelopes,
            transforms=transforms,
        )
        self.refresh_sdata_widget()
        # Add tma_envelope
        self.get_sdata_widget()._onClick("tma_envelope")

        # TODO: Create coordainte system from bboxes ?

    def _save_selected_layer_to_sdata(self):
        selected = self.viewer.layers.selection.active
        if (
            selected is not None
            and "tma_envelope" in selected.metadata
            and "tma_cores" in selected.metadata
            and "envelopes" in selected.metadata
            and "transforms" in selected.metadata
            and "parent_layer" in selected.metadata
            and isinstance(selected, napari.layers.Labels)
        ):
            self.update_model()
            self.model.save_dearray_results(
                tma_cores=selected.metadata["tma_cores"],
                tma_envelope=selected.metadata["tma_envelope"],
                envelopes=selected.metadata["envelopes"],
                transforms=selected.metadata["transforms"],
            )

            self.refresh_sdata_widget()

    def _create_tma_grid_widget(self):
        """Create a TMA grid representation of tickboxes; left labels are the A-I of the grid
        bottom labels are 1-10 of the grid.

        If a tick exists, clicking it will remove the core from the representation
        (but its original position kept, so if re-ticked will default to that)

        If a tick doesnt exist, clicking it will add a core in the approximate
        area where it should be (i.e. if E-3 and E-5 exists, if E-4 doesnt exist
        aand then added, then its added between E3 and E4 -> Uses the estimated grid position)

        """
        final_grid_labels = self.model.final_grid_labels
        #        grid_positions = self.model.grid_positions
        rows = len(final_grid_labels)
        cols = len(final_grid_labels[0])
        row_labels = tuple([f"{chr(65 + i)}" for i in range(rows)])
        col_labels = tuple([f"{i+1}" for i in range(cols)])

        grid = Table(final_grid_labels, name="Grid")
        grid.row_headers = row_labels
        grid.column_headers = col_labels

        # Widget resizing
        self.max_width = self.width = 800
        self.max_height = self.height = 1000
        grid.max_width = grid.width = self.max_width
        grid.max_height = grid.height = self.max_height

        # Adjust default spacing
        column_spacing = 20
        for i in range(grid.native.columnCount()):
            grid.native.horizontalHeader().setSectionResizeMode(
                i, grid.native.horizontalHeader().Stretch
            )
            grid.native.setColumnWidth(i, column_spacing)

        # Make read only - noneditable
        grid.native.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.grid = grid

        def _highlight_selected_tma_cell(r, c):
            print(r, c)

        grid.native.cellClicked.connect(_highlight_selected_tma_cell)

        if "Grid" in self.asdict():
            self.__delattr__("Grid")
        # self.extend([self.grid])

    def _update_tma_grid_widget(self):
        """Update the TMA grid widget - for user-interaction of creating and
        deleting rows. Needs add and remove row in base model class
        TMADearrayer."""

    def update_model(self):
        """TODO: allow for multiple masks -> Mask merge"""
        selected = self.viewer.layers.selection.active
        if (
            selected is not None
            and "sdata" in selected.metadata
            and isinstance(selected, napari.layers.Labels)
            and not isinstance(
                selected.data, napari.layers._multiscale_data.MultiScaleData
            )
        ):
            self.model = TMADearrayer(
                selected.metadata["sdata"], selected.metadata["name"]
            )

            self.reset_choices()
            self._dearray_button.enabled = True
        else:
            self.model = None
            self.reset_choices()
            self._dearray_button.enabled = False

    def create_parameter_widgets(self):
        super().create_parameter_widgets()

        self._estimated_core_diameter_um_entry = create_widget(
            value=700,
            name="Estimated core diameter in um",
            annotation=float,
            widget_type="LineEdit",
        )

        self._nrows_entry = create_widget(
            value=0,
            name="Enforce number of rows",
            annotation=int,
            widget_type="LineEdit",
        )

        self._ncols_entry = create_widget(
            value=0,
            name="Enforce number of columns",
            annotation=int,
            widget_type="LineEdit",
        )

        # Make invisible until mask has been made
        self._dearray_button = create_widget(
            value=False,
            name="Dearray",
            annotation=bool,
            widget_type="PushButton",
            options={"enabled": True},
        )
        self._dearray_button.changed.connect(self._dearray)
        # self._dearray_button.changed.connect(self._create_tma_grid_widget)

        if self.model is not None:
            self._dearray_button.enabled = True
        else:
            self._dearray_button.enabled = False

        self.extend(
            [
                self._estimated_core_diameter_um_entry,
                self._nrows_entry,
                self._ncols_entry,
                self._dearray_button,
            ]
        )


class TMASegmenterNapariWidget(MultiScaleImageNapariWidget):
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        model: TMASegmenter | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(viewer, model, *args, **kwargs)
        self.create_parameter_widgets()
        self.viewer.layers.selection.events.changed.connect(self.update_model)

    def update_model(self):
        selected = self.viewer.layers.selection.active

        if (
            selected is not None
            and "sdata" in selected.metadata
            and isinstance(selected, napari.layers.Image)
            and isinstance(
                selected.data, napari.layers._multiscale_data.MultiScaleData
            )
        ):
            self.model = TMASegmenter(
                selected.metadata["sdata"], selected.metadata["name"]
            )
            self.reset_choices()
            self._run_segmentation_button.enabled = True
            self._preview_segmentation_button.enabled = True
        else:
            if (
                selected is not None
                and "global_seg_mask" in selected.metadata
                and "transformation_sequence" in selected.metadata
                and "parent_layer" in selected.metadata
                and isinstance(selected, napari.layers.Labels)
            ):
                parent = selected.metadata["parent_layer"]
                self.model = TMASegmenter(
                    parent.metadata["sdata"], parent.metadata["name"]
                )
                self.reset_choices()
                self._run_segmentation_button.enabled = False
                self._preview_segmentation_button.enabled = False
                self._save_segmentation_button.enabled = True
            else:
                self.model = None
                self.reset_choices()
                self._run_segmentation_button.enabled = False
                self._preview_segmentation_button.enabled = False
                self._save_segmentation_button.enabled = False

        # self.viewer.add_labels(
        #     global_seg_mask,
        #     name=self.model.image_name + "_segmentation",
        #     affine=affine,
        #     metadata={
        #         "sdata": self.model.sdata,
        #         "global_seg_mask": global_seg_mask,
        #         "transformation_sequence": transformation_sequence,
        #         "name": self.model.image_name + "_segmentation",
        #         "parent_layer": parent_layer,
        #         "_current_cs": parent_layer.metadata["_current_cs"],
        #     },

    def get_multiscale_image_shapes(self, widget=None):
        """TODO: temp solution. Until lower scale segmentation is implemented
        and revisited."""
        shapes = super().get_multiscale_image_shapes(widget)
        if shapes != [None]:
            return [shapes[-1]]
        return shapes

    def create_parameter_widgets(self):
        super().create_parameter_widgets()

        self._base_model_selection = create_static_selection_widget(
            "BaseModels",
            TMASegmenter.CP_DEFAULT_MODELS,
            "Cellpose 3.0 Base Models",
        )

        self._denoise_model_selection = create_static_selection_widget(
            "DenoiseModels",
            TMASegmenter.CP_DENOISE_MODELS,
            "(Optional) Cellpose 3.0 Denoiser Models",
        )

        self._custom_model_file_edit = create_widget(
            value=None,
            name="Custom Model File",
            annotation=Path,
            widget_type="FileEdit",
            options={"mode": "r", "enabled": True},
        )
        # NOTE: can rename tiles to 'regions' to be more explicit
        # since tiles can refer to segmentation tiling
        self._tiling_shape_layer_selection = ComboBox(
            name="TilingShapeLayers",
            choices=self.get_tiling_shape_layers,
            label="Select shapes layer for tiling",
            nullable=True,
        )
        self._tiling_shape_layer_selection.changed.connect(self.reset_choices)

        self._tile_name_column_selection = ComboBox(
            name="TileNameColumn",
            choices=self.get_tiling_shape_layer_cols,
            label="Select column for tile names",
        )

        # TODO: incremental like the transforms widget for multichannel + MIP/MaxIP merge then seg on that
        self._segmentation_channel_selection = Select(
            name="SegmentationChannel",
            choices=self.get_channels,
            label="Select channel(s) for segmentation",
        )
        self._segmentation_channel_selection.native.setMinimumHeight(100)

        self._channel_merge_method_selection = ComboBox(
            name="ChannelMergeMethods",
            choices=["max", "mean", "sum", "median"],
            label="Method for merging multiple channels",
        )

        self._optional_nuclear_channel_selection = ComboBox(
            name="SegmentationChannel",
            choices=self.get_channels,
            label="Select optional nuclear channel",
            nullable=True,
        )

        # TODO: replace nucleus with just diameter; some models are cyto etc
        self._nuclei_diameter_um_entry = create_widget(
            value=-1,
            name="Nucleus diameter (um)",
            annotation=float,
            widget_type="LineEdit",
            options={
                "tooltip": (
                    "If value is 0 or negative, will default to automated"
                    " diameter estimation."
                )
            },
        )

        self._cellprob_threshold_slider = create_widget(
            value=0.0,
            name="Cell Probability Threshold",
            annotation=float,
            options={
                "min": -6,
                "step": 0.01,
                "max": 6.0,
                "tooltip": ("Decrease if undersegmenting in dim areas."),
            },
            widget_type="FloatSlider",
        )

        self._flow_threshold_slider = create_widget(
            value=0.4,
            name="Flow Threshold",
            annotation=float,
            options={
                "min": 0.0,
                "step": 0.01,
                "max": 1.0,
                "tooltip": (
                    "Decrease if segmentation shapes are unexpected, increase"
                    " if undersegmenting."
                ),
            },
            widget_type="FloatSlider",
        )

        self._debug_mode_button = create_widget(
            value=False,
            name="First and Last Tile only",
            annotation=bool,
            widget_type="CheckBox",
        )

        self._n_random_tiles_entry = create_widget(
            value=0,
            name="Number of random tiles to segment",
            annotation=int,
            widget_type="SpinBox",
            options={"nullable": True},
        )

        self._preview_segmentation_button = create_widget(
            value=False,
            name="Preview Segmentation",
            annotation=bool,
            widget_type="PushButton",
        )
        self._preview_segmentation_button.changed.connect(
            self.preview_segmentation
        )

        self._run_segmentation_button = create_widget(
            value=False,
            name="Run Segmentation",
            annotation=bool,
            widget_type="PushButton",
        )
        self._save_segmentation_button = create_widget(
            value=False,
            name="Save Segmentation",
            annotation=bool,
            widget_type="PushButton",
        )
        self._save_segmentation_button.changed.connect(
            self._save_selected_layer_to_sdata
        )

        self._run_segmentation_button.changed.connect(self.run_segmentation)
        self._buttons = QHBoxLayout()
        self._buttons.addWidget(self._preview_segmentation_button.native)
        self._buttons.addWidget(self._run_segmentation_button.native)
        self._buttons.addWidget(self._save_segmentation_button.native)

        self.extend(
            [
                self._base_model_selection,
                self._denoise_model_selection,
                self._custom_model_file_edit,
                self._tiling_shape_layer_selection,
                self._tile_name_column_selection,
                self._segmentation_channel_selection,
                self._channel_merge_method_selection,
                self._optional_nuclear_channel_selection,
                self._nuclei_diameter_um_entry,
                self._cellprob_threshold_slider,
                self._flow_threshold_slider,
                self._debug_mode_button,
                # self._run_segmentation_button,
            ]
        )

        self.native.layout().addLayout(self._buttons)

    def get_tiling_shape_layers(self, widget=None):
        return [
            x.name
            for x in self.viewer.layers
            if isinstance(x, napari.layers.shapes.shapes.Shapes)
            and "sdata" in x.metadata
            and x.name in x.metadata["sdata"].shapes
            and isinstance(
                x.metadata["sdata"].shapes[x.name], gpd.GeoDataFrame
            )
        ]

    def get_tiling_shape_layer_cols(self, widget=None):
        if self._tiling_shape_layer_selection.value is not None:
            layer = get_selected_layer(
                self.viewer, self._tiling_shape_layer_selection.value
            )
            layer_gdf = layer.metadata["sdata"].shapes[layer.name]
            cat_cols = [
                x
                for x in layer_gdf.columns
                if isinstance(
                    layer_gdf[x].dtype, pd.CategoricalDtype | pd.StringDtype
                )
                or pd.api.types.is_string_dtype(layer_gdf[x])
            ]
            return cat_cols
        else:
            return []

    def disable_function_button(self, button):
        button.enabled = False

    def enable_function_button(self, button):
        button.enabled = True

    @thread_worker
    def _preview_segmentation(self):
        # self.run_segmentation(preview=True) -. NOTE: too slow, mimick with add
        channels = self._segmentation_channel_selection.value
        method = self._channel_merge_method_selection.value
        image = self.model.get_image()

        if self._optional_nuclear_channel_selection.value is not None:
            nc = self._optional_nuclear_channel_selection.value
            image_list = [image.sel(c=channels + [nc])[x].image for x in image]
            image_list = [
                xr.concat(
                    [
                        (
                            self.model.get_multichannel_image_projection(
                                im, channels, method=method
                            )
                            .transpose("x", "y", "c")
                            .compute()
                        ),
                        im.sel(c="DAPI"),
                    ],
                    dim="c",
                )
                for im in image_list
            ]

        else:
            image_list = [image.sel(c=channels)[x].image for x in image]
            image_list = [
                self.model.get_multichannel_image_projection(
                    im, channels, method=method
                ).compute()
                for im in image_list
            ]

        def dataarray_to_rgb(dataarray):
            if "c" not in dataarray.dims:
                raise ValueError("Input DataArray must have a 'c' dimension.")

            c_size = dataarray.sizes["c"]

            if c_size == 1:
                # Create an RGB image where the first channel is green
                green_channel = dataarray.isel(c=0)
                rgb_image = xr.concat(
                    [
                        xr.zeros_like(green_channel),
                        green_channel,
                        xr.zeros_like(green_channel),
                    ],
                    dim="c",
                )
                rgb_image = rgb_image.assign_coords(c=["R", "G", "B"])
            elif c_size == 2:
                # rgb, first channel green, second blue
                green_channel = dataarray.isel(c=0)
                blue_channel = dataarray.isel(c=1)
                rgb_image = xr.concat(
                    [
                        xr.zeros_like(green_channel),
                        green_channel,
                        blue_channel,
                    ],
                    dim="c",
                )
                rgb_image = rgb_image.assign_coords(c=["R", "G", "B"])
            else:
                raise ValueError(
                    "DataArray must have 1 or 2 channels in the 'c' dimension."
                )

            rgb_image = rgb_image.transpose("y", "x", "c")
            return rgb_image

        image_list = [dataarray_to_rgb(im) for im in image_list]

        return image_list

    def preview_segmentation(self):
        def _handle_preview_segmentation(image_list):
            self.viewer.add_image(
                image_list,
                name="Segmentation Input Preview",
                multiscale=True,
                blending="additive",
                rgb=True,
            )

        worker = self._preview_segmentation()
        self.disable_function_button(self._preview_segmentation_button)
        worker.start()
        worker.returned.connect(_handle_preview_segmentation)
        worker.finished.connect(
            lambda: self.enable_function_button(
                button=self._preview_segmentation_button
            )
        )

    def run_segmentation(self):
        worker = self._run_segmentation()
        self.disable_function_button(self._run_segmentation_button)
        worker.start()
        worker.returned.connect(self.add_segmentation_layer)
        # worker.finished.connect(self.post_run_segmentation)
        worker.finished.connect(
            lambda: self.enable_function_button(
                button=self._run_segmentation_button
            )
        )
        worker.finished.connect(self.refresh_sdata_widget)

    def add_segmentation_layer(self, out):
        global_seg_mask, transformation_sequence = out
        affine = transformation_sequence.to_affine_matrix(
            ("y", "x"), ("x", "y")
        )
        parent_layer = self.viewer.layers.selection.active

        global_seg_mask = xr.DataArray(
            global_seg_mask.T,
            dims=("y", "x"),
            coords={
                "y": np.arange(global_seg_mask.shape[1]),
                "x": np.arange(global_seg_mask.shape[0]),
            },
        )

        self.viewer.add_labels(
            global_seg_mask,
            name=self.model.image_name + "_segmentation",
            affine=affine,
            metadata={
                "sdata": self.model.sdata,
                "global_seg_mask": global_seg_mask,
                "transformation_sequence": transformation_sequence,
                "name": self.model.image_name + "_segmentation",
                "parent_layer": parent_layer,
                "_current_cs": parent_layer.metadata["_current_cs"],
            },
        )

    # def post_run_segmentation(self):
    #     seg_name = self.model.image_name + "_labels"
    #     if seg_name in self.viewer.layers:
    #         labels = get_selected_layer(
    #             self.viewer, self.model.image_name + "_labels"
    #         )
    #         self.viewer.layers.remove(labels)
    #         sdata_widget = self.get_sdata_widget()
    #         sdata_widget._onClick(
    #             text=labels.name
    #         )  # mimick re-adding the layer

    @thread_worker
    def _run_segmentation(self):
        # Validate parameters from widget
        data_sd = None
        if self._tiling_shape_layer_selection.value is not None:
            # Get the scaling factor of the chosen image scale;
            tiling_layer = get_selected_layer(
                self.viewer, self._tiling_shape_layer_selection
            )

            data_sd = tiling_layer.metadata["sdata"].shapes[tiling_layer.name]
            data_sd = data_sd.copy()
            transforms = get_transformation(data_sd).transformations
            # Scale must be supplied.?
            scale = [x for x in transforms if isinstance(x, Scale)][0].scale
            # Rescale data;
            data_sd["geometry"] = data_sd["geometry"].scale(
                *scale, origin=(0, 0)
            )

            translate = [x for x in transforms if isinstance(x, Translation)]
            if translate != []:
                axes = translate[0].axes
                translate = translate[0].translation
                if axes[0] == "y":
                    translate = translate[::-1]

                data_sd["geometry"] = data_sd["geometry"].translate(*translate)

        scale = self.get_multiscale_image_scales()[self.scale_index]
        out = self.model.segment_all(  # noqa: F841
            scale=scale,
            segmentation_channel=self._segmentation_channel_selection.value,
            tiling_shapes=data_sd,
            model_type=self._base_model_selection.value.name,
            nuclei_diam_um=float(self._nuclei_diameter_um_entry.value),
            channel_merge_method=self._channel_merge_method_selection.value,
            optional_nuclear_channel=self._optional_nuclear_channel_selection.value,
            tiling_shapes_annotation_column=self._tile_name_column_selection.value,
            cellprob_threshold=float(self._cellprob_threshold_slider.value),
            flow_threshold=float(self._flow_threshold_slider.value),
            custom_model=self._custom_model_file_edit.value,
            denoise_model=self._denoise_model_selection.value.name,
            debug=self._debug_mode_button.value,
            preview=False,
        )
        if out is not None:
            return out

    def _save_selected_layer_to_sdata(self):
        selected = self.viewer.layers.selection.active
        if (
            selected is not None
            and "global_seg_mask" in selected.metadata
            and "transformation_sequence" in selected.metadata
            and "parent_layer" in selected.metadata
            and isinstance(selected, napari.layers.Labels)
        ):
            self.update_model()
            self.model.save_segmentation(
                global_seg_mask=selected.metadata["global_seg_mask"],
                label_name=selected.name,
                transformation_sequence=selected.metadata[
                    "transformation_sequence"
                ],
            )

            self.refresh_sdata_widget()


class TMAMeasurerNapariWidget(MultiScaleImageNapariWidget):
    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        model: TMAMeasurer | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(viewer, model, *args, **kwargs)
        self.create_parameter_widgets()
        # The model changes when 1) sdata is changed, 2) image_name is changed;
        # These events are trigged by napari_spatialdata.view on layer update
        # When layer is updated -> Get the contained sdata if any;
        self.viewer.layers.selection.events.changed.connect(self.update_model)

    def create_parameter_widgets(self):
        self._segmentation_layer_selection = ComboBox(
            name="SegmentationLayers",
            choices=self.get_segmentation_layers,
            label="Select segmentation layer",
            nullable=False,
        )
        self._segmentation_layer_selection.changed.connect(self.update_model)

        self._tiling_shape_layer_selection = ComboBox(
            name="TilingShapeLayers",
            choices=self.get_tiling_shape_layers,
            label="Select shapes layer for tiling",
            nullable=True,
        )
        self._tiling_shape_layer_selection.changed.connect(self.reset_choices)

        self._extended_properties_toggle = create_widget(
            value=False,
            name="Measure extended properties",
            annotation=bool,
            widget_type="CheckBox",
            options={
                "tooltip": (
                    f"Additional properties: "
                    f"{TMAMeasurer.EXTENDED_EXPORT_PROPERTIES}"
                )
            },
        )

        self._intensity_mode_selection = ComboBox(
            name="IntensityMode",
            choices=["mean", "median"],
            label="Intensity mode for expression",
            nullable=False,
        )

        self._measure_labels_button = create_widget(
            value=False,
            name="Save Measurements",
            annotation=bool,
            widget_type="PushButton",
            options={
                "tooltip": (
                    f"Measure defaults properties: "
                    f"{TMAMeasurer.EXPORT_PROPERTIES}"
                )
            },
        )

        if self.model is None:
            self._measure_labels_button.enabled = False
        self._measure_labels_button.changed.connect(self.measure_labels)

        self._adata_name_entry = create_widget(
            value="adata",
            label="AnnData label",
            name="AnnData name",
            annotation=str,
            widget_type="LineEdit",
        )

        self._buttons = QHBoxLayout()
        self._buttons.addWidget(self._adata_name_entry.native)
        self._buttons.addWidget(self._measure_labels_button.native)

        self.extend(
            [
                self._segmentation_layer_selection,
                self._tiling_shape_layer_selection,
                self._extended_properties_toggle,
                self._intensity_mode_selection,
                # self._measure_labels_button,
            ]
        )

        self.native.layout().addLayout(self._buttons)

    def enable_function_button(self):
        self._measure_labels_button.enabled = True

    def disable_function_button(self):
        self._measure_labels_button.enabled = False

    def get_segmentation_layers(self, widget=None):
        return [
            x.name
            for x in self.viewer.layers
            if isinstance(x, napari.layers.labels.labels.Labels)
            and "sdata" in x.metadata
            # and "adata" in x.metadata
        ]

    def get_tiling_shape_layers(self, widget=None):
        return [
            x.name
            for x in self.viewer.layers
            if isinstance(x, napari.layers.shapes.shapes.Shapes)
            and "sdata" in x.metadata
            and x.name in x.metadata["sdata"].shapes
            and isinstance(
                x.metadata["sdata"].shapes[x.name], gpd.GeoDataFrame
            )
        ]

    def update_model(self):
        # Create widgets on initialisation; can tak from launch method
        # layer = get_selected_layer(
        #     self._viewer, self._select_layer_widget)
        selected = self.viewer.layers.selection.active

        if (
            selected is not None
            and "sdata" in selected.metadata
            and isinstance(
                selected.data, napari.layers._multiscale_data.MultiScaleData
            )
            and self._segmentation_layer_selection.value is not None
        ):
            self.model = TMAMeasurer(
                selected.metadata["sdata"], selected.metadata["name"]
            )

            self.reset_choices()
            self.enable_function_button()
        else:
            self.model = None
            self.reset_choices()
            self.disable_function_button()

    def measure_labels(self):
        worker = self._measure_labels()
        worker.start()
        worker.returned.connect(self.annotate_labels_with_adata)
        worker.finished.connect(self.post_measure_labels)

    def post_measure_labels(self):
        # TODO: after this, the labels layer needs to be updated with the new table sdata
        # consider; viewermodel.add_sdata_labels | sdataviewer._get_table_data
        # labels.metadata["sdata"] = self.model.sdata
        # NOTE: temp sol; delete and re-add the layer
        labels = get_selected_layer(
            self.viewer, self._segmentation_layer_selection
        )
        self.viewer.layers.remove(labels)
        sdata_widget = self.get_sdata_widget()
        sdata_widget._onClick(text=labels.name)  # mimick re-adding the layer
        self.enable_function_button()

    def annotate_labels_with_adata(self, out):
        adata, cell_index_label = out
        labels_layer = get_selected_layer(
            self.viewer, self._segmentation_layer_selection
        )
        # Add as metadata layer to sdata;
        self.model.save_measurements(
            adata=adata,
            output_table_name=self._adata_name_entry.value,
            label_name=labels_layer.name,
            instance_key=cell_index_label,
        )

    @thread_worker
    def _measure_labels(self):
        self.disable_function_button()
        # Validate parameters from widget
        data_sd = None
        if self._tiling_shape_layer_selection.value is not None:
            # Get the scaling factor of the chosen image scale;
            tiling_layer = get_selected_layer(
                self.viewer, self._tiling_shape_layer_selection
            )

            data_sd = tiling_layer.metadata["sdata"].shapes[tiling_layer.name]
            data_sd = data_sd.copy()
            transforms = get_transformation(data_sd).transformations
            scale = [x for x in transforms if isinstance(x, Scale)][0].scale
            # Rescale data;
            data_sd["geometry"] = data_sd["geometry"].scale(
                *scale, origin=(0, 0)
            )

            translate = [x for x in transforms if isinstance(x, Translation)]
            if translate != []:
                axes = translate[0].axes
                translate = translate[0].translation
                if axes[0] == "y":
                    translate = translate[::-1]

                data_sd["geometry"] = data_sd["geometry"].translate(*translate)

        labels = get_selected_layer(
            self.viewer, self._segmentation_layer_selection
        )
        assert isinstance(
            labels.data, xr.core.dataarray.DataArray
        ), "Selected layer must be a DataArray."
        return self.model.measure_labels(
            labels=labels.data,
            tiling_shapes=data_sd,
            extended_properties=self._extended_properties_toggle.value,
            intensity_mode=self._intensity_mode_selection.value,
            labels_name=labels.name,
        )
