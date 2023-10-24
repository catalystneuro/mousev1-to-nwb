# Notes concerning the abdeladim_2023 conversion
## Experimental protocol:
Holographic emulation of visually evoked neural activity at the mesoscale by specific co-activation of functionally defined ensembles. We further showed how one can use this system to probe functional interactions between distant brain regions. Finally, we showed that we can decode the identity of the specific photo-stimulus purely from the modulation of activity of postsynaptic neurons in downstream areas.
## Data streams:
**From Scope of the Work:**
- imaging data (Scan Image),
- segmentation (Suite2P), 
- Holographic stimulation (ndx-holographic stimulation), missing
- behavior (Videos), missing
- event annotations including stimulation events.(?) missing

**From [Paper](https://www.biorxiv.org/content/10.1101/2023.03.02.530875v2.full):**
- imaging data (Scan Image),
- segmentation (Suite2P), 
- Holographic stimulation (ndx-holographic stimulation)
- Visual stimulation
- retinotopy
(no mention of behavioural videos)
## Data organisation: 
- Raw tiff: 7 epochs (link to behaviour I assume) - not clear what the abbreviations stands for:
    - ret ?
    - ori (oriented?)
    - stim (holographic stimulus?)
    - expt (?)
	For each epochs we have:
    - `\*IntegrationRois\*.csv` which headers are: [`timestamp`, `frameNumber`, `ROI 1`, `ROI 2`, `ROI 3`, etc]. Are those response traces or stimulation traces?
    - `\*PSTH\*.mat`. This goes in the analysis container correct?
    - every .tif file is 100MB and could be concatenated in time
- makeMasks3D_img.mat : image masks for identified ROIs (red and green channel superimpose - blue channel is 0) and target ROIs for photstim (3 distinct axial `slices` that are acquired round-robin at ~19Hz total (~6Hz / slice)
- `img920`: tiff_path.rglob(`\*920_\*.tif\*`),
- `img1020`: tiff_path.rglob(`\*1020_\*.tif\*`),
- `img800`: tiff_path.rglob(`\*800_\*.tif\*`),
I assume they are summary images for the 3 slices and 800/920/1020 has something to do with the spatial information.

However, from the analysis code, I can see there are other files that potentially contain critical metadata:
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


Always in the analysis code, in particular in the [SetupDaqFile](https://github.com/willyh101/analysis/blob/5bd562ca531a6cc9ce9a57ed76229d89a8fcb82d/holofun/daq.py#L11C1-L58C59) class there is a reference to a dataset containing even subject metadata. 
## Metadata:
From SetupDaqFile class in holofun, I see there is a lot of metadata that must go into the NWBFile. They seem to come from a .mat file called setupdaq 
## Lab code:
[willyh101/analysis](https://github.com/willyh101/analysis/tree/5bd562ca531a6cc9ce9a57ed76229d89a8fcb82d)
[adesnik-lab/holography](https://github.com/adesnik-lab/holography/tree/main)
