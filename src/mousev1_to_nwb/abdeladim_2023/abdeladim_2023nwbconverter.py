"""Primary NWBConverter class for this dataset."""
from typing import Dict
from neuroconv import NWBConverter

"""Primary NWBConverter class for this dataset."""
from neuroconv.utils import FolderPathType
from typing import Optional
from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface
from abdeladim_2023segmentationinterface import Abdeladim2023SegmentationInterface


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
        verbose: bool = True,
    ):
        self.verbose = verbose
        self.data_interface_objects = dict()

        self.plane_map = segmentation_to_imaging_map

        available_channels = Abdeladim2023SinglePlaneImagingInterface.get_available_channels(
            folder_path=imaging_folder_path
        )
        available_planes = Abdeladim2023SinglePlaneImagingInterface.get_available_planes(
            folder_path=imaging_folder_path
        )
        for channel_name in available_channels:
            for plane_name in available_planes:
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
                        segmentation_source_data.update(plane_segmentation_name=plane_segmentation_name)
                    Abdeladim2023SegmentationInterface(**segmentation_source_data)
                    self.data_interface_objects.update(
                        {segmentation_interface_name: Abdeladim2023SegmentationInterface(**segmentation_source_data)}
                    )
