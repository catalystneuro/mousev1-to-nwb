from dateutil.parser import parse as dateparse
import datetime
import json
from pathlib import Path
from natsort import natsorted
from abdeladim_2023imagingextractor import Abdeladim2023SinglePlaneImagingExtractor
from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import BaseImagingExtractorInterface
from neuroconv.utils import FolderPathType
from neuroconv.utils.dict import DeepDict
from roiextractors.extractors.tiffimagingextractors.scanimagetiff_utils import extract_extra_metadata
from roiextractors.extractors.tiffimagingextractors.scanimagetiffimagingextractor import (
    ScanImageTiffSinglePlaneImagingExtractor,
)


class Abdeladim2023SinglePlaneImagingInterface(BaseImagingExtractorInterface):
    """
    Data Interface for writing imaging data for the MouseV1 to NWB file using Abdeladim2023SinglePlaneImagingExtractor.
    """

    Extractor = Abdeladim2023SinglePlaneImagingExtractor

    @classmethod
    def get_available_channels(cls, folder_path):
        tif_file_paths = natsorted(folder_path.glob("*.tif"))
        return ScanImageTiffSinglePlaneImagingExtractor.get_available_channels(file_path=tif_file_paths[0])

    @classmethod
    def get_available_planes(cls, folder_path):
        tif_file_paths = natsorted(folder_path.glob("*.tif"))
        return ScanImageTiffSinglePlaneImagingExtractor.get_available_planes(file_path=tif_file_paths[0])

    def __init__(
        self,
        folder_path: FolderPathType,
        channel_name: str,
        plane_name: str,
        verbose: bool = True,
    ):
        self.channel_name = channel_name
        self.plane_name = plane_name

        self.folder_path = Path(folder_path)
        tif_file_paths = natsorted(self.folder_path.glob("*.tif"))
        assert tif_file_paths, f"The TIF image files are missing from '{self.folder_path}'."
        self.image_metadata = extract_extra_metadata(file_path=tif_file_paths[0])
        super().__init__(folder_path=folder_path, channel_name=channel_name, plane_name=plane_name, verbose=verbose)

    def get_metadata(self) -> DeepDict:
        metadata = super().get_metadata()

        if "state.internal.triggerTimeString" in self.image_metadata:
            extracted_session_start_time = dateparse(self.image_metadata["state.internal.triggerTimeString"])
            metadata["NWBFile"].update(session_start_time=extracted_session_start_time)
        elif "epoch" in self.image_metadata:
            # Versions of ScanImage at least as recent as 2020, and possibly earlier, store the start time under keyword
            # `epoch`, as a string encoding of a Matlab array, example `'[2022  8  8 16 56 7.329]'`
            # dateparse can't cope with this representation, so using strptime directly
            extracted_session_start_time = datetime.datetime.strptime(
                self.image_metadata["epoch"], "[%Y %m %d %H %M %S.%f]"
            )
            metadata["NWBFile"].update(session_start_time=extracted_session_start_time)

        ophys_metadata = metadata["Ophys"]
        two_photon_series_metadata = ophys_metadata["TwoPhotonSeries"][0]

        # Extract many scan image properties and attach them as dict in the description
        if self.image_metadata is not None:
            extracted_description = json.dumps(self.image_metadata)
            two_photon_series_metadata.update(description=extracted_description)

        channel_name_without_space = self.channel_name.replace(" ", "")

        # TODO indicators = {"Channel1": "GCaMP6f", "Channel2": "tdTomato"} # Not specified

        channel_metadata = {
            "Channel1": {
                "name": "Green",
                "emission_lambda": 500.0,# TODO Not specified
                "description": "Green channel of the microscope",
            },
            "Channel2": {
                "name": "Red",
                "emission_lambda": 500.0,# TODO Not specified
                "description": "Red channel of the microscope",
            },
        }[channel_name_without_space]

        optical_channel_metadata = channel_metadata

        device_name = "CustomMicroscope"
        metadata["Ophys"]["Device"][0].update(
            name=device_name,
            description="The mesoscale read/write platform was custom-built around a 2P random-access fluorescence mesoscope previously described in detail (Sofroniew 2016)",
            manufacturer="Thorlabs Inc.",
        )

        # TODO indicator = indicators[channel_name_without_space]
        imaging_plane_name = f"ImagingPlane{channel_name_without_space}Plane{self.plane_name}"
        imaging_plane_metadata = metadata["Ophys"]["ImagingPlane"][0]
        imaging_plane_metadata.update(
            name=imaging_plane_name,
            optical_channel=[optical_channel_metadata],
            device=device_name,
            excitation_lambda=920.0, # TODO Not specified
            # TODO indicator=indicator,
            imaging_rate=float(self.image_metadata["SI.hRoiManager.scanVolumeRate"]),
        )

        two_photon_series_metadata = metadata["Ophys"]["TwoPhotonSeries"][0]
        two_photon_series_metadata.update(
            name=f"TwoPhotonSeries{channel_name_without_space}Plane{self.plane_name}",
            imaging_plane=imaging_plane_name,
            scan_line_rate=1 / float(self.image_metadata["SI.hRoiManager.linePeriod"]),
            description=f"Two photon series acquired with {self.channel_name} at plane {self.plane_name}",
        )

        return metadata

    def set_aligned_timestamps(self):
        self.imaging_extractor._times
