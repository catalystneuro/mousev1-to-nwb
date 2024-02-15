# mousev1-to-nwb
NWB conversion scripts for MouseV1 lab data to the [Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.


## Basic installation

You can install the latest release of the package with pip:

```
pip install mousev1-to-nwb
```

We recommend that you install the package inside a [virtual environment](https://docs.python.org/3/tutorial/venv.html). A simple way of doing this is to use a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) from the `conda` package manager ([installation instructions](https://docs.conda.io/en/latest/miniconda.html)). Detailed instructions on how to use conda environments can be found in their [documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

### Running a specific conversion
Once you have installed the package with pip, you can run any of the conversion scripts in a notebook or a python file:

https://github.com/catalystneuro/mousev1-to-nwb//tree/main/src/abdeladim_2023/abdeladim_2023_conversion_script.py




## Installation from Github
Another option is to install the package directly from Github. This option has the advantage that the source code can be modifed if you need to amend some of the code we originally provided to adapt to future experimental differences. To install the conversion from GitHub you will need to use `git` ([installation instructions](https://github.com/git-guides/install-git)). We also recommend the installation of `conda` ([installation instructions](https://docs.conda.io/en/latest/miniconda.html)) as it contains all the required machinery in a single and simple instal

From a terminal (note that conda should install one in your system) you can do the following:

```
git clone https://github.com/catalystneuro/mousev1-to-nwb
cd mousev1-to-nwb
conda env create --file make_env.yml
conda activate mousev1-to-nwb-env
```

This creates a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) which isolates the conversion code from your system libraries.  We recommend that you run all your conversion related tasks and analysis from the created environment in order to minimize issues related to package dependencies.

Alternatively, if you want to avoid conda altogether (for example if you use another virtual environment tool) you can install the repository with the following commands using only pip:

```
git clone https://github.com/catalystneuro/mousev1-to-nwb
cd mousev1-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs).

### Running a specific conversion
To run a specific conversion, you might need to install first some conversion specific dependencies that are located in each conversion directory:
```
pip install -r src/mousev1_to_nwb/abdeladim_2023/abdeladim_2023_requirements.txt
```

You can run a specific conversion with the following command:
```
python src/mousev1_to_nwb/abdeladim_2023/abdeladim_2023_conversion_script.py
```

## Repository structure
Each conversion is organized in a directory of its own in the `src` directory:

    mousev1-to-nwb/
    ├── LICENSE
    ├── make_env.yml
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── src
        ├── mousev1_to_nwb
        │   ├── conversion_directory_1
        │   └── abdeladim_2023
        │       ├── abdeladim_2023imagingextractor.py
        │       ├── abdeladim_2023imaginginterface.py
        │       ├── abdeladim_2023segmentationinterface.py
        │       ├── abdeladim_2023holostiminterface.py
        │       ├── abdeladim_2023visualstimulusinterface.py
        │       ├── abdeladim_2023nwbconverter.py
        │       ├── abdeladim_2023_convert_session.py
        │       ├── abdeladim_2023_metadata.yml
        │       ├── abdeladim_2023_holostim_metadata.yml
        │       ├── abdeladim_2023_requirements.txt
        │       ├── abdeladim_2023_notes.md
        │       ├── abdeladim_2023_conversion_script.py
        │       └── __init__.py
        │   ├── conversion_directory_b

        └── __init__.py

 For example, for the conversion `abdeladim_2023` you can find a directory located in `src/mousev1-to-nwb/abdeladim_2023`. Inside each conversion directory you can find the following files:

* `abdeladim_2023_conversion_script.py`: this script run the conversion of one full session (all epochs). Data directories, output directory, subject id and other information to run the conversion should be defined here.
* `abdeladim_2023_convert_sesion.py`: this script defines the function to convert one full session of the conversion.
* `abdeladim_2023_requirements.txt`: dependencies specific to this conversion.
* `abdeladim_2023_metadata.yml`: metadata in yaml format for this specific conversion.
* `abdeladim_2023imagingextractor.py`: the extractor for the imaging data.
* `abdeladim_2023imaginginterface.py`: the interface for the imaging data.
* `abdeladim_2023segmentationinterface.py`: the interface for the segmentation data.
* `abdeladim_2023_holostim_metadata.yml`: metadata in yaml format for holographic stimulus specs.
* `abdeladim_2023holostiminterface.py`: the interface for the holographic stimulus data.
* `abdeladim_2023visualstimulusinterface.py`: the interface for the visual stimulus data.
* `abdeladim_2023nwbconverter.py`: the place where the `NWBConverter` class is defined.
* `abdeladim_2023_notes.md`: notes and comments concerning this specific conversion.

