"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)

from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface


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
