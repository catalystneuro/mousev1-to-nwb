"""Primary script to run to convert an entire session for of data using the NWBConverter."""
from pathlib import Path
from typing import Union
import glob
import datetime
from zoneinfo import ZoneInfo

from neuroconv.utils import load_dict_from_file, dict_deep_update

from abdeladim_2023imaginginterface import Abdeladim2023SinglePlaneImagingInterface
from abdeladim_2023nwbconverter import Abdeladim2023NWBConverter
from abdeladim_2023nwbconverter import get_default_segmentation_to_imaging_name_mapping

def session_to_nwb(
    data_dir_path: Union[str, Path], output_dir_path: Union[str, Path], session_id: str, subject_id:str, stub_test: bool = False
):
    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    nwbfile_path = output_dir_path / f"{session_id}.nwb"

    # Add Imaging
    imaging_folder_path = data_dir_path / "raw-tiffs" / session_id
    # Add Segmentation
    segmentation_folder_path = data_dir_path / "processed-suite2p-data/suite2p"

    segmentation_to_imaging_plane_map = get_default_segmentation_to_imaging_name_mapping(imaging_folder_path, segmentation_folder_path)

    converter = Abdeladim2023NWBConverter(
        imaging_folder_path=imaging_folder_path,
        segmentation_folder_path=segmentation_folder_path,
        segmentation_to_imaging_map=segmentation_to_imaging_plane_map,
        verbose=False,
    )

    conversion_options = {
        interface_name: dict(stub_test=stub_test) for interface_name in converter.data_interface_objects.keys()
    }
    photon_series_index = 0
    for interface_name in converter.data_interface_objects.keys():
        if "Imaging" in interface_name:
            conversion_options[interface_name]={"photon_series_index":photon_series_index}     
            photon_series_index += 1

    # Add datetime to conversion
    metadata = converter.get_metadata()

    # Update default metadata with the editable in the corresponding yaml file
    editable_metadata_path = Path(__file__).parent / "abdeladim_2023_metadata.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)
    metadata["Subject"].update(subject_id=subject_id)
    metadata["NWBFile"].update(session_id=session_id)
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
    subject_id = "unknown"  # TODO ask for subject_id

    session_to_nwb(
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        session_id=session_id,
        subject_id=subject_id,
        stub_test=stub_test,
    )
