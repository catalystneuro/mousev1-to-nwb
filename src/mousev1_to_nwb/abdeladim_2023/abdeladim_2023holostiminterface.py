from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Optional

import numpy as np
import h5py
from neuroconv import BaseDataInterface
from neuroconv.tools.roiextractors.roiextractors import get_default_segmentation_metadata
from neuroconv.utils import FolderPathType, FilePathType, get_base_schema, get_schema_from_hdmf_class
from pynwb import NWBFile
from pynwb.device import Device
from pynwb.ogen import OptogeneticStimulusSite
from pynwb.ophys import PlaneSegmentation, OpticalChannel
from natsort import natsorted
from roiextractors.extractors.tiffimagingextractors.scanimagetiff_utils import (
    parse_metadata,
    extract_extra_metadata,
    extract_timestamps_from_file,
)
from ndx_patterned_ogen import (
    PatternedOptogeneticStimulusTable,
    OptogeneticStimulusTarget,
    TemporalFocusing,
    PatternedOptogeneticStimulusSite,
    SpatialLightModulator2D,
    LightSource,
)


def check_optogenetic_stim_data(
    file_path: FilePathType,
    epoch_name: str = None,
    fields_to_check: list = [
        "targeted_cells",
        "stim_id",
        "roi_powers_mW",
        "hz_per_cell",
        "spikes_per_cell",
        "stim_times",
        "scanimage_targets",
        "suite2p_targets",
        "scanimage_hologram_list",
    ],
):
    with h5py.File(file_path, "r") as file:
        if epoch_name not in file:
            raise ValueError(
                f"'{epoch_name}' is not a valid name for an epoch with holographic stimulation. "
                f"This file only contains holographic stimulation data for epochs: {list(file.keys())}"
            )

        else:
            for i in fields_to_check:
                if i not in file[epoch_name]:
                    raise ValueError(f"'{i}' missing from {epoch_name} holographic stimulation data")


class Abdeladim2023HolographicStimulationInterface(BaseDataInterface):
    """
    Data Interface for writing holographic photostimulation data for the MouseV1 to NWB file
    using Abdeladim2023HolographicStimulationInterface.
    """

    def __init__(
        self,
        folder_path: FolderPathType,
        holographic_stimulation_file_path: FilePathType,
        epoch_name: str = None,
        targeted_plane_segmentation_name: Optional[str] = None,
        verbose: bool = True,
    ):
        """
        Data interface for adding the holographic stimulation to the NWB file.

        Parameters
        ----------
        folder_path : FolderPathType
            The folder path that contains the imaging data.
        targeted_plane_segmentation_name: str, optional
            The name of the plane segmentation to use for the holographic stimulation.
        holographic_stimulation_file_path: FilePathType
            The file path for the .hdf5 file that contains the holographic stimulation data
        epoch_name: str,
            The name of the epoch where the holographic stimulation is carried out
        verbose : bool, default: True
        """
        folder_path = Path(folder_path)
        tif_file_paths = natsorted(folder_path.glob("*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{folder_path}'."
        self._total_number_of_trials = len(tif_file_paths)

        self.trial_start_times = []
        for tif_file_path in tif_file_paths:
            timestamps = extract_timestamps_from_file(file_path=tif_file_path)
            self.trial_start_times.append(timestamps[0])

        self.image_metadata = extract_extra_metadata(file_path=tif_file_paths[0])
        self.metadata_parsed = parse_metadata(self.image_metadata)
        self.rois_metadata = self.metadata_parsed["roi_metadata"]

        self.targeted_plane_segmentation_name = targeted_plane_segmentation_name or "PlaneSegmentationTargetedHologram"
        try:
            check_optogenetic_stim_data(file_path=holographic_stimulation_file_path, epoch_name=epoch_name)
        except ValueError as ve:
            print(f"Error: {str(ve)}")

        data = h5py.File(holographic_stimulation_file_path, "r")
        data = data[epoch_name]
        self._targeted_to_segmented_roi_ids_map = data["targeted_cells"][:]
        self._suite2p_segmented_coordinates = data["suite2p_targets"][:]
        self._scanimage_hologram_list = data["scanimage_hologram_list"][:]
        self._scanimage_target_coordinates = data["scanimage_targets"][:]
        self._trial_to_stimulation_ids_map = data["stim_id"][:]
        # self._power_per_trial = data["power_per_cell"][:]
        self._frequency_per_trial = data["hz_per_cell"][:]
        self._n_spike_per_trial = data["spikes_per_cell"][:]
        self._stimulus_time_per_targeted_rois = data["stim_times"][:]
        self._stimulus_power_per_targeted_rois = data["roi_powers_mW"][:]

        self.epoch_name = epoch_name
        super().__init__(folder_path=folder_path)
        self.verbose = verbose

    def get_metadata_schema(self) -> dict:
        metadata_schema = super().get_metadata_schema()
        metadata_schema["required"] = ["Ophys"]
        metadata_schema["properties"]["Ophys"] = get_base_schema()
        metadata_schema["properties"]["Ophys"]["properties"] = dict(
            Device=dict(type="array", minItems=1, items=get_schema_from_hdmf_class(Device)),
        )
        metadata_schema["properties"]["Ophys"]["properties"].update(
            OptogeneticStimulusSite=get_schema_from_hdmf_class(OptogeneticStimulusSite),
            OptogeneticDevice=dict(
                type="object",
                required=["SpatialLightModulator2D", "LightSource"],
                properties=dict(
                    SpatialLightModulator=get_schema_from_hdmf_class(SpatialLightModulator2D),
                    LightSource=get_schema_from_hdmf_class(LightSource),
                ),
            ),
        )
        metadata_schema["properties"]["Ophys"]["properties"]["OptogeneticStimulusSite"].update(type="array")

        return metadata_schema

    def get_metadata(self) -> dict:
        metadata = get_default_segmentation_metadata()
        return metadata

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = None,
        stub_test: bool = False,
    ) -> None:
        metadata_copy = deepcopy(metadata)

        device_name = metadata_copy["Ophys"]["Device"][0]["name"]
        device = nwbfile.devices[device_name]

        # Add stimulus pattern to NWBFile
        temporal_focusing_metadata = metadata_copy["LabMetaData"]["TemporalFocusing"]
        temporal_focusing = TemporalFocusing(**temporal_focusing_metadata)
        nwbfile.add_lab_meta_data(temporal_focusing)

        # Add SLM device to NWBFile
        spatial_light_modulator_metadata = metadata_copy["Ophys"]["OptogeneticDevice"]["SpatialLightModulator2D"]
        spatial_light_modulator_metadata.update(spatial_resolution=[1024, 1024])
        spatial_light_modulator_name = spatial_light_modulator_metadata["name"]
        if spatial_light_modulator_name not in nwbfile.devices:
            nwbfile.add_device(SpatialLightModulator2D(**spatial_light_modulator_metadata))
        spatial_light_modulator = nwbfile.devices[spatial_light_modulator_name]

        # Add light source device to NWBFile
        light_source_metadata = metadata_copy["Ophys"]["OptogeneticDevice"]["LightSource"]
        light_source_name = light_source_metadata["name"]
        if light_source_name not in nwbfile.devices:
            nwbfile.add_device(LightSource(**light_source_metadata))
        light_source = nwbfile.devices[light_source_name]

        # Add optogenetic stimulus site to NWBFile
        stimulus_site_metadata = metadata_copy["Ophys"]["OptogeneticStimulusSite"][0]
        stimulus_site_metadata.update(
            device=device, spatial_light_modulator=spatial_light_modulator, light_source=light_source
        )
        stim_site = PatternedOptogeneticStimulusSite(**stimulus_site_metadata)
        nwbfile.add_ogen_site(stim_site)

        # Create a plane segmentation object for targeted ROIs
        optical_channel = OpticalChannel(
            name="Green",
            description="Green channel for functional imaging.",
            emission_lambda=513.0,
        )

        fov_size_in_um = np.array(self.rois_metadata["imagingRoiGroup"]["rois"]["scanfields"]["sizeXY"])
        frame_dimesion = np.array(self.rois_metadata["imagingRoiGroup"]["rois"]["scanfields"]["pixelResolutionXY"])

        imaging_plane_name = "ImagingPlaneHolographicStimulation"
        imaging_plane = nwbfile.create_imaging_plane(
            name=imaging_plane_name,
            optical_channel=optical_channel,
            imaging_rate=float(
                self.image_metadata["SI.hRoiManager.scanFrameRate"]
            ),  # Frame rate on the entire volumetric stack
            description="Imaging plane for the holographic stimulation.",
            device=device,
            excitation_lambda=920.0,
            indicator="GCaMP6s",
            location="Primary visual cortex (V1), 140-200 um below pia",
            grid_spacing=fov_size_in_um / frame_dimesion,
            grid_spacing_unit="micrometers",
            origin_coords=self.rois_metadata["imagingRoiGroup"]["rois"]["scanfields"]["centerXY"],
            origin_coords_unit="micrometers",
        )

        # Add plane segmentation to store the Accepted Suite2p ROIs concatenated over the planes
        plane_segmentation = PlaneSegmentation(
            name="PlaneSegmentationChannel1ConcatenatedPlanes",
            description="Accepted Suite2p ROIs concatenated over the planes",
            imaging_plane=imaging_plane,
        )

        for segmented_roi in self._suite2p_segmented_coordinates:
            plane_segmentation.add_roi(voxel_mask=[np.append(segmented_roi, 1)])

        # add global_ids
        segmented_to_glob_ids = np.array(plane_segmentation[:].index)
        plane_segmentation.add_column(
            name="global_ids",
            description="Global roi ids to match targeted and segmented ROIs",
            data=segmented_to_glob_ids,
        )

        nwbfile.processing["ophys"]["ImageSegmentation"].add_plane_segmentation(plane_segmentation)

        # Add plane segmentation to store the targeted ROIs
        targeted_plane_segmentation = PlaneSegmentation(
            name=self.targeted_plane_segmentation_name,
            description="Targeted ROIs from the ScanImage metadata",
            imaging_plane=imaging_plane,
        )

        for target_roi in self._scanimage_target_coordinates:
            targeted_plane_segmentation.add_roi(voxel_mask=[np.append(target_roi, 1)])

        # add global_ids
        targeted_not_stimulated_rois = self._targeted_to_segmented_roi_ids_map[
            np.isnan(self._targeted_to_segmented_roi_ids_map)
        ]
        targeted_to_glob_ids = np.zeros((len(self._targeted_to_segmented_roi_ids_map)))
        targeted_to_glob_ids[np.isnan(self._targeted_to_segmented_roi_ids_map)] = np.arange(
            len(segmented_to_glob_ids), len(segmented_to_glob_ids) + len(targeted_not_stimulated_rois)
        )
        targeted_to_glob_ids[
            ~np.isnan(self._targeted_to_segmented_roi_ids_map)
        ] = self._targeted_to_segmented_roi_ids_map[~np.isnan(self._targeted_to_segmented_roi_ids_map)]

        targeted_plane_segmentation.add_column(
            name="global_ids",
            description="Global roi ids to match targeted and segmented ROIs",
            data=targeted_to_glob_ids.astype(int),
        )

        nwbfile.processing["ophys"]["ImageSegmentation"].add_plane_segmentation(targeted_plane_segmentation)

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable", description="Patterned stimulus"
        )
        for trial, hologram_index in enumerate(self._trial_to_stimulation_ids_map):
            # 7expt has incomplete data
            if trial >= self._total_number_of_trials:
                break
            # create hologram from hologram list
            if hologram_index != 0:  #
                hologram_index = hologram_index - 1
                targeted_roi_indexes = self._scanimage_hologram_list[hologram_index]
                targeted_roi_indexes = list(targeted_roi_indexes[~np.isnan(targeted_roi_indexes)].astype(int))
                segmented_roi_indexes = self._targeted_to_segmented_roi_ids_map[targeted_roi_indexes]
                segmented_roi_indexes = list(segmented_roi_indexes[~np.isnan(segmented_roi_indexes)].astype(int))

                if len(targeted_roi_indexes) > 0:
                    targeted_rois = targeted_plane_segmentation.create_roi_table_region(
                        name="targeted_rois",
                        description="targeted rois",
                        region=targeted_roi_indexes,
                    )
                    segmented_rois = plane_segmentation.create_roi_table_region(
                        name="segmented_rois",
                        description="segmented rois",
                        region=segmented_roi_indexes,
                    )
                    hologram_name = f"Hologram{hologram_index}"
                    hologram = OptogeneticStimulusTarget(
                        name=hologram_name, targeted_rois=targeted_rois, segmented_rois=segmented_rois
                    )
                    if hologram_name not in nwbfile.lab_meta_data:
                        nwbfile.add_lab_meta_data(hologram)

                    trial_start_time = self.trial_start_times[trial]
                    frequency = self._frequency_per_trial[trial]
                    n_spike = self._n_spike_per_trial[trial]
                    stimulus_power = self._stimulus_power_per_targeted_rois[targeted_roi_indexes]
                    stimulus_time = self._stimulus_time_per_targeted_rois[targeted_roi_indexes]
                    start_time = trial_start_time + stimulus_time
                    stop_time = start_time + np.round(n_spike / frequency, decimals=2)
                    # Since each roi in the Hologram receive the stimuli at different times and different power, 
                    # here we add one interval for each stimulus time and indicate which roi has been stimulated 
                    # by setting power as an 1D array where the only non-zero element would be 
                    # the one reffered to the roi stimulated in the current stimulus onset.
                    # NB: if "power" is defined as array it must have the same lenght as "targeted_rois"
                    for i in range(len(targeted_roi_indexes)):
                        if ~np.isnan(start_time[i]) and ~np.isnan(stimulus_power[i]):
                            power = np.zeros((len(targeted_roi_indexes)))
                            power[i] = stimulus_power[i]
                            stimulus_table.add_interval(
                                start_time=start_time[i],
                                stop_time=stop_time[i],
                                power=power,
                                frequency=frequency,
                                stimulus_pattern=temporal_focusing,
                                targets=nwbfile.lab_meta_data[hologram_name],
                                stimulus_site=stim_site,
                            )
        if len(stimulus_table["start_time"]) == 0:
            print(f"No stimulus onset has been found in {self.epoch_name}")
            print("No PatternedOptogeneticStimulusTable will be created")
        else:
            nwbfile.add_time_intervals(stimulus_table)
