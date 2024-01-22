# Notes concerning the abdeladim_2023 conversion


# Reference papers
From [Probing inter-areal computations with a cellular resolution two-photon holographic mesoscope](https://www.biorxiv.org/content/10.1101/2023.03.02.530875v2.full): 
Holographic emulation of visually evoked neural activity at the mesoscale by specific co-activation of functionally defined ensembles (holograms). They further showed how one can use this system to probe functional interactions between distant brain regions. Finally, they showed that they can decode the identity of the specific photo-stimulus purely from the modulation of activity of postsynaptic neurons in downstream areas.

See also [The logic of recurrent circuits in the primary visual cortex](https://www.biorxiv.org/content/10.1101/2022.09.20.508739v1.full)
 and  [All-optical recreation of naturalistic neural activity with a multifunctional transgenic reporter mouse](https://www.sciencedirect.com/science/article/pii/S2211124723009208)

## Experimental protocol:

The microscope is calibrated to aim holograms/optogenetic stimulation to pixel coordinates in ScanImage. 
After motion correcting and processing the data with suite2p, they extract cell masks and traces. 
Then (x,y) pixel targeted locations are matched to (x,y) suite2p locations using a simple distance matching algorithm (with a maximum distance threshold). 
For various reasons, suite2p will not always detect a cell in the location where hologram shoul be. 
To preserve indexing, those are marked as NaN.

## Data streams:

TODO: update with other papers: 
https://www.biorxiv.org/content/10.1101/2022.09.20.508739v1.full ,
https://www.sciencedirect.com/science/article/pii/S2211124723009208

**From Scope of the Work:**
- imaging data (ScanImage),
- segmentation (Suite2P), 
- Holographic stimulation (Custom Matlab code, HDF5 file)
- event annotations. missing

### Data exploraton:
The example data shared is structured as follow:
- imaging data --> "raw_tiffs" folder containing a folder for each session: "2ret","3ori","4ori","5stim","6stim","7expt"
- suite2p data --> "processed-suite2p-data"
- holographic stimulation -->  processed "example_data.hdf5" file

#### Imaging data (ScanImage):
- each session has multiple .tif files to be concatenated in time --> use MultiImageExtractor
- image dimension: 
    - n_xpixels: `'SI.hRoiManager.pixelsPerLine': '512'`
    - n_ypixels: `'SI.hRoiManager.linesPerFrame': '512'`
- number of planes:   `'SI.hStackManager.numSlices': '3'`
- ? is it the distances at which the 3 planes are acquired: `'SI.hStackManager.arbitraryZs': '[0 30 55]',`. If it's so this represent the voxel number at which the planes are acquired. Infact if we look at names of the three .tiff files common to all sessions (`img800`,`img920`,`img1020` which probably indicates summary images at the 3 different planes) we can extract the info that:
    - Plane0 is acquired at 800um 
    - Plane1 is acquired at 920um (with a relative ditance from Plane0 of 30*4um)
    - Plane2 is acquired at 1020um (with a relative ditance from Plane0 of 55*4um)
From this I suppose that the grid_spacing in the z direction is 4um but I need to confirm
- two channel: "Channel 1"--> Green, "Channel 2" --> Red 
    - `SI.hChannels.channelMergeColor : {'green';'red';'red';'red'}`
    - `SI.hChannels.channelName : {'Channel 1' 'Channel 2' 'Channel 3' 'Channel 4'}`
    - `SI.hChannels.channelSave : [1;2]`
- round-robin acquisition at --> `SI.hRoiManager.scanFrameRate: 19.0686`
- plane acquisition rate at --> `SI.hRoiManager.scanVolumeRate : 6.35621`
- line acquisition rate at -->  1/`SI.hRoiManager.linePeriod : 6.31833e-05`

- ? is this the subject_id? `'SI.hUserFunctions.userFunctionsCfg__8.Arguments': "{'w51_1'}"` (the tif file report 'w57_1')

**Other metadata needed for the imaging data stream:**
- grid_spacing in um for x, y and z direction 
- indicators for the 2 optical channels
- emission_lambda for the 2 optical channels
- excitation_lambda taken from paper: 920 nm 
---------------------------
#### Segmentation data (Suite2P),
The output of suit2p are not divided into sessions and there is no reference about the session to which it refers to. Thus, I checked the nuber of frames for the s2p data to see if I found any corrispondence with the one of the session, but turns out that:
- Suit2p data has 41305 frames for each Plane ('frames_per_folder': [ 9604,  6203,  6394,  1708,  3527, 13869])
- While raw imaing data has in total 31422 frames (for each channel and plane combo):
    - 9604 in 2ret
    - 6203 in 3ori
    - 6394 in 4ori
    - 1708 in 5stim
    - 3527 in 6stim
    - 3986 in 7expt

Then I notice that the subject_id is different:
    - 'w57_1' from paths saved in suite2p 
    - 'w51_1' from ScanImage userFunction

Therefore, the Suit2p processing is done by concatenating the different sessions/epochs. 
--> we should save timestamps for the suit2p data as well as for the imaging series
--> we could save each epoch as a separate series, so that the series' description can be specific of the protocol and the holographic series that refers to just "5stim" and  "7expt" has a direct correspective in the acquisition imaging series.

---------------------------
#### Holographic stimulation data (custom):
The holographic data are just for the the "5stim" and "7expt" sessions
from the README provided in the data folder:
**Variables and nomenclature**
`roi` = suite2p cell or roi. integer index into suite2p rois. NaN is a placeholder for a location that was targeted but not detected by suite2p. _<span style="color: red;">missing</span> -> from email: info to be ignored, only need to have `hologram_list`_
`hologram` = array/list of targeted rois that comprise a single stimulation event. i.e. a hologram could be a single cell stimulated, or n cells stimulated simultaneously. _<span style="color: red;">missing</span> -> from email: info to be ignored, only need to have `hologram_list`_
`hologram_list` = list of unique stimulations/holograms that is indexed by `stim_id`
`targeted_cells` = overally list of all suite2p cells targeted and matched to holographic stimuli
`stim_times` = stimulation time (in seconds) within a trial for each roi, NaN means the cell was not stimulated
`stim_id` = trialwise index into `hologram_list`, note this is idx-1, as the first "stim" condition is a control trial
`power_per_cell` = power per cell/stimulation site in mW
`spikes_per_cell` = stim frequency per cell/stimulation site _<span style="color: red;">what is the difference from hz_per_cell?</span>.-> from email: it's a typo, it actually means the number of stimulation per cell/stimulation site_
`hz_per_cell` = stimulationd frequency per cell/stimulation site
`frame_rate` = aquisition frame rate in Hz _<span style="color: red;">missing</span> -> from email: it's the same as in Suite2P_

##### Session "5stim"
In "5stim" there are 24 trials (`len(stim_id): 24`). Each trial correspond to a multipage .tif file in the "5stim" imaging folder, indeed there are 24 .tif files in the folder. There are 36 combinations of max 10 ROIs (over a total of 368-->`len(targeted_cells)`) stimulated at the same time (`hologram_list.shape: (36,10)`). Only the first 8 combinations are referred in `stim_id`, the actual values of `stim_id` range from 0 (that is a control trial where there is no actual stimulation: `power_per_cell` and `spikes_per_cell` are 0) to 8 (`hologram_list[7]`).

##### Session "7expt"
In "7expt" there are 723 trials (`len(stim_id): 723`). Each trial correspond to a multipage .tif file in the "7expt" imaging folder, only 209 .tif files in the folder--> <span style="color: red;">some files are missing</span>. 10 ROIs stimulated in separate trials alone (`hologram_list.shape: (10,1)`). All ROIs in hologram list are stimulated at least once: `stim_id` range from 0 -control trial- to 10 (`hologram_list[9]`).
NB: for `stim_id`=4 --> `hologram_list[3]` is nan <span style="color: red;">why?</span> 

#### ROIs indices
In the example.hdf5 file the targeted cells are 368 (`len(targeted_cells)`) in total, both for 5stim and 7expt. `targeted_cells` value span from 0 to 700 (`np.nanmax(targeted_cells)`).
If we sum the number of cells ideatified as true cells in Suite2p over the 3 plane we obtain 702 cells (`len(iscell_0[iscell_0[:,0]!=0.])+len(iscell_1[iscell_1[:,0]!=0.])+len(iscell_2[iscell_2[:,0]!=0.])`). 

In the ScanImage .tif metadata there is a dictonary saved as text that the function `extract_extra_metadata` cannot parse, where information on the ROIs are stored. 
```
"RoiGroups":{
    "imagingRoiGroup":{# general imaging space metadata (only 2D)
        ...
        "centerXY": [-1.776356839e-16,0.1],
        "sizeXY": [13.5,13.5], # size of the FOV 
        "rotationDegrees": 0,
        "enable": 1,
        "pixelResolutionXY": [512,512],
        "pixelToRefTransform": [[0.0263671875,0,-6.763183594],
                                [0,0.263671875,-6.663183594],
                                [0,0,1]],
        "affine":  [[13.5,0,-6.75],
                    [0,13.5,-6.65],
                    [0,0,1]]
        ...
    }, 
    "photostimRoiGroups":null, # no spatial info on photostimRoiGroups
    "integrationRoiGroup":{
        ...
        "rois": [
        {
          "ver": 1,
          "classname": "scanimage.mroi.Roi",
          "name": "ROI 1",
            ...
          "zs": 0,
          "scanfields": {
            ...
            "centerXY": [2.518066406,1.062402344],
            "sizeXY": [0.2373046875,0.2373046875],
            "rotationDegrees": 0,
            "enable": 1,
            "threshold": 100,
            "channel": 1,
            "processor": "cpu",
            "mask": [roi_pixel_mask 9x9 binary matrix],
            "affine": [[0.2373046875,0,2.518066406],
                       [0,0.2373046875,1.062402344],
                       [0,0,1]]
          },
          "discretePlaneMode": 1,
          "powers": null,
          "pzAdjust": null,
          "Lzs": null,
          "interlaceDecimation": null,
          "interlaceOffset": null,
          "enable": 1
        },
        ... # all the 368 ROIs
        ]
    } # imaging space metadata for each ROI
}
```
In `imagingRoiGroup` we can probably extract info on the dimension of the field of view (XY) from `"sizeXY"` and divide by the dimension to get the grid_spacing (z dimension missed)

In `integrationRoiGroup` we can associate the 368 ROIs with the plane they belong to from `"zs": 0/30/55` 

--> in `targeted_list` the ROI are ordered as the one reported in `integrationRoiGroup`?
--> is Plane0 at zs = 0, Plane1 at zs = 30 and Plane2 at zs = 55 for Suite2p data?

If so we can recover the extact roi_id pointing to the correct PlaneSegmentation where the roi are stored.

--------------------
**Ignore these files**
- makeMasks3D_img.mat : image masks for identified ROIs (red and green channel superimpose - blue channel is 0) and target ROIs for photstim (3 distinct axial `slices` that are acquired round-robin at ~19Hz total (~6Hz / slice))
- `img920`: tiff_path.rglob(`\*920_\*.tif\*`),
- `img1020`: tiff_path.rglob(`\*1020_\*.tif\*`),
- `img800`: tiff_path.rglob(`\*800_\*.tif\*`),

## Metadata:
From the analysis code, I can see there are other files that potentially contain critical metadata:
- <span style="color: red;">`setupdaq`: tiff_path.glob(date[2:]+`\*.mat`)</span>,
- `s2p`: edrive.rglob(`suite2p`),
- `clicked_cells`: tiff_path.rglob(`\*clicked\*.npy`),
- `mm3d`: tiff_path.rglob(`makeMasks3D_img.mat`),
- `img920`: tiff_path.rglob(`\*920_\*.tif\*`),
- `img1020`: tiff_path.rglob(`\*1020_\*.tif\*`),
- `img800`: tiff_path.rglob(`\*800_\*.tif\*`),
- <span style="color: red;">`ori`: tiff_path.rglob(`\*ori\*.mat`)</span>,
- <span style="color: red;">`ret`: tiff_path.rglob(`\*ret\*.mat`)</span>,
`si_online`: tiff_path.rglob(`\*IntegrationRois\*.csv`),
- <span style="color: red;">`mat`: tiff_path.rglob(`\*.mat`)</span>

In the analysis code, in particular in the [SetupDaqFile](https://github.com/willyh101/analysis/blob/5bd562ca531a6cc9ce9a57ed76229d89a8fcb82d/holofun/daq.py#L11C1-L58C59) class there is a reference to a dataset containing subject metadata. 

From SetupDaqFile class in holofun, I see there is a lot of metadata that must go into the NWBFile. They seem to come from a .mat file called setupdaq
> HDF5 file and Suite2P files has all info needed.  
## Lab code:
[willyh101/analysis](https://github.com/willyh101/analysis/tree/5bd562ca531a6cc9ce9a57ed76229d89a8fcb82d)
[adesnik-lab/holography](https://github.com/adesnik-lab/holography/tree/main)


# <span style="color: red;">Questions:</span>

**<span style="color: red;">1. Other metadata needed for the imaging data stream:</span>**
- grid_spacing in um for x, y and z direction 
- indicators for the 2 optical channels
- emission_lambda for the 2 optical channels
- excitation_lambda taken from paper: 920 nm 

**<span style="color: red;">2. Other metadata needed for the imaging data stream:</span>**
- excitation_lambda for photostimulation
- opsin used
- laser-related metadata
- spatial light modulator metadata

**<span style="color: red;">3. Other metadata needed for subject and session</span>**


