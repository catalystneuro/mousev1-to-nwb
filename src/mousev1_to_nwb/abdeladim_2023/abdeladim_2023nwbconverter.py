"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)

from mousev1_to_nwb.abdeladim_2023 import Abdeladim2023BehaviorInterface


class Abdeladim2023NWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Recording=SpikeGLXRecordingInterface,
        LFP=SpikeGLXLFPInterface,
        Sorting=PhySortingInterface,
        Behavior=Abdeladim2023BehaviorInterface,
    )
