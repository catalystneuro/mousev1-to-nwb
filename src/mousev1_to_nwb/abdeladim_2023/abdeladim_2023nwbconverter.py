"""Primary NWBConverter class for this dataset."""
from typing import Dict
from neuroconv import NWBConverter
from neuroconv.utils import FolderPathType, FilePathType
from typing import Optional
from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface
from abdeladim_2023segmentationinterface import Abdeladim2023SegmentationInterface
from abdeladim_2023holostiminterface import Abdeladim2023HolographicStimulationInterface
from pynwb import NWBFile
from pynwb.ophys import PlaneSegmentation
import numpy as np


def get_default_segmentation_to_imaging_name_mapping(
    imaging_folder_path: FolderPathType, segmentation_folder_path: FolderPathType
) -> dict or None:
    """
    Get the default mapping between imaging and segmentation planes.

    Parameters
    ----------
    imaging_folder_path: FolderPathType
        The folder path that contains the ScanImage TIF imaging output (.tif files).
    segmentation_folder_path: FolderPathType
        The folder that contains the Suite2P segmentation output. (usually named "suite2p")
    """
    si_available_channels = Abdeladim2023SinglePlaneImagingInterface.get_available_channels(
        folder_path=imaging_folder_path
    )
    si_available_channels = [channel_name.replace(" ", "") for channel_name in si_available_channels]
    si_available_planes = Abdeladim2023SinglePlaneImagingInterface.get_available_planes(folder_path=imaging_folder_path)

    s2p_available_channels = Abdeladim2023SegmentationInterface.get_available_channels(
        folder_path=segmentation_folder_path
    )
    s2p_available_planes = Abdeladim2023SegmentationInterface.get_available_planes(folder_path=segmentation_folder_path)

    if len(s2p_available_channels) == 1 and len(s2p_available_planes) == 1:
        return None

    segmentation_channel_plane_names = [
        f"{channel_name.capitalize()}{plane_name.capitalize()}"
        for channel_name in s2p_available_channels
        for plane_name in s2p_available_planes
    ]

    if len(si_available_planes) > 1:
        imaging_channel_plane_names = [
            f"{channel_name.capitalize()}Plane{plane_name.capitalize()}"
            for channel_name in si_available_channels
            for plane_name in si_available_planes
        ]
    else:
        imaging_channel_plane_names = si_available_channels

    segmentation_to_imaging_name_mapping = dict(zip(segmentation_channel_plane_names, imaging_channel_plane_names))

    return segmentation_to_imaging_name_mapping


class Abdeladim2023NWBConverter(NWBConverter):
    """Primary conversion class for Abdeladim2023 dataset."""

    def __init__(
        self,
        imaging_folder_path: FolderPathType,
        segmentation_folder_path: Optional[FolderPathType] = None,
        segmentation_to_imaging_map: dict = None,
        segmentation_start_frame: int = 0,
        segmentation_end_frame: int = 100,
        holographic_stimulation_file_path: Optional[FilePathType] = None,
        epoch_name: Optional[str] = None,
        verbose: bool = True,
    ):
        self.verbose = verbose
        self.data_interface_objects = dict()

        self.plane_map = segmentation_to_imaging_map

        self.available_channels = Abdeladim2023SinglePlaneImagingInterface.get_available_channels(
            folder_path=imaging_folder_path
        )
        self.available_planes = Abdeladim2023SinglePlaneImagingInterface.get_available_planes(
            folder_path=imaging_folder_path
        )
        for channel_name in self.available_channels:
            for plane_name in self.available_planes:
                channel_name_without_space = channel_name.replace(" ", "")
                imaging_interface_name = f"Imaging{channel_name_without_space}Plane{plane_name}"
                imaging_source_data = dict(
                    folder_path=imaging_folder_path,
                    channel_name=channel_name,
                    plane_name=plane_name,
                    verbose=verbose,
                )
                self.data_interface_objects.update(
                    {imaging_interface_name: Abdeladim2023SinglePlaneImagingInterface(**imaging_source_data)}
                )

        if segmentation_folder_path:
            available_planes = Abdeladim2023SegmentationInterface.get_available_planes(
                folder_path=segmentation_folder_path
            )
            available_channels = Abdeladim2023SegmentationInterface.get_available_channels(
                folder_path=segmentation_folder_path
            )
            for channel_name in available_channels:
                for plane_name in available_planes:
                    plane_name_suffix = f"{channel_name.capitalize()}{plane_name.capitalize()}"
                    segmentation_interface_name = f"Segmentation{plane_name_suffix}"
                    segmentation_source_data = dict(
                        folder_path=segmentation_folder_path,
                        channel_name=channel_name,
                        plane_name=plane_name,
                        start_frame=segmentation_start_frame,
                        end_frame=segmentation_end_frame,
                        verbose=verbose,
                    )
                    if self.plane_map:
                        plane_segmentation_name = "PlaneSegmentation" + self.plane_map.get(
                            plane_name_suffix, None
                        ).replace("_", "")
                        segmentation_source_data.update(
                            plane_segmentation_name=plane_segmentation_name,
                        )
                    Abdeladim2023SegmentationInterface(**segmentation_source_data)
                    self.data_interface_objects.update(
                        {segmentation_interface_name: Abdeladim2023SegmentationInterface(**segmentation_source_data)}
                    )

        if holographic_stimulation_file_path:
            holographic_stimulation_interface_name = "HolographicStimulation"
            holographic_stimulation_source_data = dict(
                folder_path=imaging_folder_path,
                holographic_stimulation_file_path=holographic_stimulation_file_path,
                epoch_name=epoch_name,
                verbose=verbose,
            )
            Abdeladim2023HolographicStimulationInterface(**holographic_stimulation_source_data)
            self.data_interface_objects.update(
                {
                    holographic_stimulation_interface_name: Abdeladim2023HolographicStimulationInterface(
                        **holographic_stimulation_source_data
                    )
                }
            )

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata, conversion_options: Optional[dict] = None) -> None:
        super().add_to_nwbfile(nwbfile=nwbfile, metadata=metadata, conversion_options=conversion_options)

        if "HolographicStimulation" in self.data_interface_objects.keys():
            holographic_stimulation_interface = self.data_interface_objects["HolographicStimulation"]
            segmentation_interface_names = [
                interface_name
                for interface_name in self.data_interface_objects.keys()
                if interface_name.startswith("SegmentationChan1")
            ]
            imaging_plane = nwbfile.imaging_planes["ImagingPlaneHolographicStimulation"]

            # create a plane segmentation for segmented ROIs
            plane_segmentation = PlaneSegmentation(
                name="PlaneSegmentationChannel1ConcatenatedPlanes",
                description="Accepted Suite2p ROIs concatenated over the planes",
                imaging_plane=imaging_plane,
            )
            for interface_name in segmentation_interface_names:
                segmentation_interface = self.data_interface_objects[interface_name]
                accepted_rois = segmentation_interface.segmentation_extractor.get_accepted_list()
                accepted_roi_masks = segmentation_interface.segmentation_extractor.get_roi_pixel_masks(accepted_rois)

                for roi_mask in accepted_roi_masks:
                    plane_segmentation.add_roi(pixel_mask=roi_mask)

            # create global ids to match targeted and succefully stimulated rois
            targeted_to_segmented_roi_ids_map = holographic_stimulation_interface._targeted_to_segmented_roi_ids_map

            segmented_to_glob_ids = np.array(plane_segmentation[:].index)

            plane_segmentation.add_column(
                name="global_ids",
                description="Global roi ids to match targeted and segmented ROIs",
                data=segmented_to_glob_ids,
            )

            targeted_not_stimulated_rois = targeted_to_segmented_roi_ids_map[
                np.isnan(targeted_to_segmented_roi_ids_map)
            ]
            targeted_to_glob_ids = np.zeros((len(targeted_to_segmented_roi_ids_map)))
            targeted_to_glob_ids[np.isnan(targeted_to_segmented_roi_ids_map)] = np.arange(
                len(segmented_to_glob_ids), len(segmented_to_glob_ids) + len(targeted_not_stimulated_rois)
            )
            targeted_to_glob_ids[~np.isnan(targeted_to_segmented_roi_ids_map)] = targeted_to_segmented_roi_ids_map[
                ~np.isnan(targeted_to_segmented_roi_ids_map)
            ]

            targeted_plane_segmentation = nwbfile.processing["ophys"]["ImageSegmentation"].get_plane_segmentation(
                holographic_stimulation_interface.targeted_plane_segmentation_name
            )


            targeted_plane_segmentation.add_column(
                name="global_ids",
                description="Global roi ids to match targeted and segmented ROIs",
                data=targeted_to_glob_ids.astype(int),
            )

            nwbfile.processing["ophys"]["ImageSegmentation"].add_plane_segmentation(plane_segmentation)
