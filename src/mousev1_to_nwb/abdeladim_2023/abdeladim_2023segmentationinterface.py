from neuroconv.datainterfaces.ophys.basesegmentationextractorinterface import BaseSegmentationExtractorInterface
from roiextractors.extractors.suite2p.suite2psegmentationextractor import Suite2pSegmentationExtractor
from neuroconv.utils import DeepDict, FolderPathType
from neuroconv.datainterfaces.ophys.suite2p.suite2pdatainterface import Suite2pSegmentationInterface
from typing import Optional


class Abdeladim2023SegmentationInterface(Suite2pSegmentationInterface):
    """
    Data Interface for writing imaging data for the MouseV1 to NWB file using Abdeladim2023SinglePlaneImagingExtractor.
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

    # def get_metadata(self) -> DeepDict:
    #     metadata = super().get_metadata()

    #     device_name = "CustomMicroscope"  # TODO how can I use the yaml file spec here?
    #     metadata["Ophys"]["Device"][0].update(
    #         name=device_name,
    #         description="The mesoscale read/write platform was custom-built around a 2P random-access fluorescence mesoscope previously described in detail (Sofroniew 2016)",
    #         manufacturer="Thorlabs Inc.",
    #     )

    #     imaging_plane_name = metadata["Ophys"]["ImagingPlane"][0]["name"]

    #     optical_channel_metadata = {
    #         "chan1": {
    #             "name": "GreenChannel",  # to match the one extracted from suite2p
    #             "emission_lambda": 513.0,
    #             "description": "Green channel for functional imaging.",
    #         },
    #         "chan2": {
    #             "name": "RedChannel",  # to match the one extracted from suite2p
    #             "emission_lambda": 592.0,
    #             "description": "Red channel for anatomical imaging.",
    #         },
    #     }[self.source_data["channel_name"]]

    #     device_name = metadata["Ophys"]["Device"][0]["name"]

    #     indicator = {"chan1": "GCaMP6f", "chan2": "mRuby"}[self.source_data["channel_name"]]

    #     location = {
    #         "plane0": "Primary visual cortex (V1), 200 um below pia",
    #         "plane1": "Primary visual cortex (V1), 170 um below pia",
    #         "plane2": "Primary visual cortex (V1), 140 um below pia",
    #     }[self.source_data["plane_name"]]

    #     imaging_plane_metadata = metadata["Ophys"]["ImagingPlane"][0]
    #     imaging_plane_metadata.update(
    #         name=imaging_plane_name,
    #         optical_channel=[optical_channel_metadata],
    #         device=device_name,
    #         excitation_lambda=920.0,
    #         indicator=indicator,
    #         location=location,
    #     )
    #     return metadata
