"""Primary script to run to convert an entire session for of data using the NWBConverter."""
from pathlib import Path
from typing import Union
import glob
import datetime
from zoneinfo import ZoneInfo

from neuroconv.utils import load_dict_from_file, dict_deep_update

from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface
from abdeladim_2023nwbconverter import Abdeladim2023NWBConverter


def session_to_nwb(
    data_dir_path: Union[str, Path], output_dir_path: Union[str, Path], session_id: str, stub_test: bool = False
):
    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    subject_id = "unknown"  # TODO ask for subject_id
    nwbfile_path = output_dir_path / f"{session_id}.nwb"

    source_data = dict()
    conversion_options = dict()

    # Add Imaging
    imaging_path = data_dir_path / "raw-tiffs" / session_id
    available_channels = Abdeladim2023SinglePlaneImagingInterface.get_available_channels(folder_path=imaging_path)
    available_planes = Abdeladim2023SinglePlaneImagingInterface.get_available_planes(folder_path=imaging_path)
    photon_series_index = 0
    for channel in available_channels:
        for plane in available_planes:
            channel_name_without_space = channel.replace(" ", "")
            interface_name = f"Imaging{channel_name_without_space}Plane{plane}"
            source_data[interface_name] = {
                "folder_path": str(imaging_path),
                "channel_name": channel,
                "plane_name": plane,
            }
            conversion_options[interface_name] = {"stub_test": stub_test, "photon_series_index": photon_series_index}
            photon_series_index += 1

    converter = Abdeladim2023NWBConverter(source_data=source_data)

    # Add datetime to conversion
    metadata = converter.get_metadata()

    # Update default metadata with the editable in the corresponding yaml file
    editable_metadata_path = Path(__file__).parent / "abdeladim_2023_metadata.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)
    metadata = dict_deep_update(metadata, {"Subject": {"subject_id": subject_id}})
    # Run conversion
    converter.run_conversion(
        metadata=metadata, 
        nwbfile_path=nwbfile_path, 
        conversion_options=conversion_options, 
        overwrite=True
    )


if __name__ == "__main__":
    # Parameters for conversion
    root_path = Path(f"/media/amtra/Samsung_T5/CN_data")
    data_dir_path = root_path / "MouseV1-to-nwb"
    output_dir_path = root_path / "MouseV1-conversion_nwb/"
    stub_test = True
    session_id = "7expt"  # "2ret","3ori","4ori","5stim","6stim","7expt"

    session_to_nwb(
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        session_id=session_id,
        stub_test=stub_test,
    )
