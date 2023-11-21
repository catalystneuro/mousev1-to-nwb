"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from neuroconv.utils import FolderPathType
from neuroconv.datainterfaces.ophys.suite2p.suite2pdatainterface import Suite2pSegmentationInterface
from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface

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

    s2p_available_channels = Suite2pSegmentationInterface.get_available_channels(folder_path=segmentation_folder_path)
    s2p_available_planes = Suite2pSegmentationInterface.get_available_planes(folder_path=segmentation_folder_path)

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
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        ImagingChannel1Plane0=Abdeladim2023SinglePlaneImagingInterface,
        ImagingChannel1Plane1=Abdeladim2023SinglePlaneImagingInterface,
        ImagingChannel1Plane2=Abdeladim2023SinglePlaneImagingInterface,        
        ImagingChannel2Plane0=Abdeladim2023SinglePlaneImagingInterface,
        ImagingChannel2Plane1=Abdeladim2023SinglePlaneImagingInterface,
        ImagingChannel2Plane2=Abdeladim2023SinglePlaneImagingInterface,
    )
