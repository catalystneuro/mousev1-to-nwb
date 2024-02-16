from neuroconv.utils import FolderPathType
from neuroconv.datainterfaces.ophys.suite2p.suite2pdatainterface import Suite2pSegmentationInterface

from roiextractors.extractors.suite2p.suite2psegmentationextractor import Suite2pSegmentationExtractor

class Hendricks2024SegmentationInterface(Suite2pSegmentationInterface):
    """
    Data Interface for writing imaging data for the MouseV1 to NWB file using Hendricks2024SinglePlaneImagingExtractor.
    """

    Extractor = Suite2pSegmentationExtractor

    def __init__(
        self,
        folder_path: FolderPathType,
        channel_name: str,
        plane_name: str,
        plane_segmentation_name: str,
        start_frame: int,
        end_frame: int,
        verbose: bool = True,
    ):
        super().__init__(
            folder_path=folder_path,
            channel_name=channel_name,
            plane_name=plane_name,
            plane_segmentation_name=plane_segmentation_name,
            verbose=verbose,
        )
        self.segmentation_extractor = self.segmentation_extractor.frame_slice(
            start_frame=start_frame, end_frame=end_frame
        )

