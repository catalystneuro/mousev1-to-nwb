"""Primary NWBConverter class for this dataset."""

from typing import Optional

from neuroconv import NWBConverter
from neuroconv.utils import FolderPathType, FilePathType, DeepDict

from hendricks_2024_imaginginterface import Hendricks2024SinglePlaneImagingInterface
from hendricks_2024_segmentationinterface import Hendricks2024SegmentationInterface
from hendricks_2024_holostiminterface import Hendricks2024HolographicStimulationInterface
from hendricks_2024_visualstimulusinterface import Hendricks2024VisualStimuliInterface


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
    si_available_channels = Hendricks2024SinglePlaneImagingInterface.get_available_channels(
        folder_path=imaging_folder_path
    )
    si_available_channels = [channel_name.replace(" ", "") for channel_name in si_available_channels]
    si_available_planes = Hendricks2024SinglePlaneImagingInterface.get_available_planes(folder_path=imaging_folder_path)

    s2p_available_channels = Hendricks2024SegmentationInterface.get_available_channels(
        folder_path=segmentation_folder_path
    )
    s2p_available_planes = Hendricks2024SegmentationInterface.get_available_planes(folder_path=segmentation_folder_path)

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


class Hendricks2024NWBConverter(NWBConverter):
    """Primary conversion class for Hendricks2024 dataset."""

    def __init__(
        self,
        imaging_folder_path: FolderPathType,
        segmentation_folder_path: Optional[FolderPathType] = None,
        segmentation_to_imaging_map: Optional[dict] = None,
        segmentation_start_frame: Optional[int] = 0,
        segmentation_end_frame: Optional[int] = 100,
        holographic_stimulation_file_path: Optional[FilePathType] = None,
        epoch_name: Optional[str] = None,
        visual_stimulus_file_path: Optional[FilePathType] = None,
        visual_stimulus_type: Optional[str] = None,
        verbose: bool = True,
    ):
        self.verbose = verbose
        self.data_interface_objects = dict()

        self.plane_map = segmentation_to_imaging_map

        self.available_channels = Hendricks2024SinglePlaneImagingInterface.get_available_channels(
            folder_path=imaging_folder_path
        )
        self.available_planes = Hendricks2024SinglePlaneImagingInterface.get_available_planes(
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
                    {imaging_interface_name: Hendricks2024SinglePlaneImagingInterface(**imaging_source_data)}
                )

        if segmentation_folder_path:
            available_planes = Hendricks2024SegmentationInterface.get_available_planes(
                folder_path=segmentation_folder_path
            )
            available_channels = Hendricks2024SegmentationInterface.get_available_channels(
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
                        segmentation_source_data.update(plane_segmentation_name=plane_segmentation_name)
                    Hendricks2024SegmentationInterface(**segmentation_source_data)
                    self.data_interface_objects.update(
                        {segmentation_interface_name: Hendricks2024SegmentationInterface(**segmentation_source_data)}
                    )
                    
        if visual_stimulus_file_path and visual_stimulus_type:
            visual_stimulus_interface_name = "VisualStimulus"
            visual_stimulus_source_data = dict(
                folder_path=imaging_folder_path,
                visual_stimulus_file_path=visual_stimulus_file_path,
                visual_stimulus_type=visual_stimulus_type,
                verbose=verbose,
            )
            Hendricks2024VisualStimuliInterface(**visual_stimulus_source_data)
            self.data_interface_objects.update(
                {visual_stimulus_interface_name: Hendricks2024VisualStimuliInterface(**visual_stimulus_source_data)}
            )
        if holographic_stimulation_file_path:
            holographic_stimulation_interface_name = "HolographicStimulation"
            holographic_stimulation_source_data = dict(
                folder_path=imaging_folder_path,
                holographic_stimulation_file_path=holographic_stimulation_file_path,
                epoch_name=epoch_name,
                verbose=verbose,
            )
            Hendricks2024HolographicStimulationInterface(**holographic_stimulation_source_data)
            self.data_interface_objects.update(
                {
                    holographic_stimulation_interface_name: Hendricks2024HolographicStimulationInterface(
                        **holographic_stimulation_source_data
                    )
                }
            )

    def get_metadata(self) -> DeepDict:
        metadata = super().get_metadata()
        for interface_name in self.data_interface_objects.keys():
            if "Imaging" in interface_name:
                imaging_metadata = self.data_interface_objects[interface_name].get_metadata()
                device_metadata = imaging_metadata["Ophys"]["Device"]
                metadata["Ophys"]["Device"] = device_metadata
                break
        for interface_name in self.data_interface_objects.keys():
            if "Imaging" in interface_name:
                imaging_metadata = self.data_interface_objects[interface_name].get_metadata()
                imaging_plane_metadata_name = imaging_metadata["Ophys"]["ImagingPlane"][0]["name"]
                for metadata_ind in range(len(metadata["Ophys"]["ImagingPlane"])):
                    if imaging_plane_metadata_name == metadata["Ophys"]["ImagingPlane"][metadata_ind]["name"]:
                        metadata["Ophys"]["ImagingPlane"][metadata_ind] = imaging_metadata["Ophys"]["ImagingPlane"][0]

        return metadata
