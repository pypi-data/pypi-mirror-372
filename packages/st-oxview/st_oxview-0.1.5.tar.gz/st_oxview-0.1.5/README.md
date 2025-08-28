# Streamlit Oxview Component

A Streamlit component for the display of coarse-grained DNA/RNA 3D models.
It is a wrapper around the [oxdna-viewer](https://github.com/sulcgroup/oxdna-viewer.git). The colormap is always disabled.

## Installation

**This component requires access to write files to the temporary directory.**

```
pip install st_oxview
```

## Example

![Alt Text](https://github.com/Lucandia/st_oxview/blob/main/example.png?raw=true)

Look at the [example](https://stoxview.streamlit.app/) for a streamlit Web App:

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stoxview.streamlit.app/)

## Usage

### Display with drag and drop

You can make a empty oxview fram and drag and drop the files to the frame.

```
import streamlit as st
from st_oxview import oxview_from_text

success = oxview_from_file()

```
*Just drag and drop the files to the frame.*


### Display from file paths

```
import streamlit as st
from st_oxview import oxview_from_file

success = oxview_from_file(configuration=path_to_conf, # path to the configuration file
                           topology=path_to_topo,      # path to the topology file
                           forces=None,                # path to the forces file
                           pdb=None,                   # path to the pdb file
                           js_script=None,             # path to the javascript script file
                           colormap=None,              # name of the Matplotlib colormap
                           index_colors=None,          # A color for each index according to the colormap (list of values between 0 and 1)
                           frame_id=None,                 # ID of the oxView frame: if a frame ID is set, it will be reused instead of creating a new frame
                           width='99%',                # width of the viewer frame
                           height='500',               # height of the viewer frame
                           key=None)                   # streamlit component key
```

### Display from text

```
import streamlit as st
from st_oxview import oxview_from_text

with open("configuration.dat", "r") as f:
    conf_text = f.read()

with open("topology.top", "r") as f:
    topo_text = f.read()

success = oxview_from_file(configuration=conf_text, # text of the configuration file
                           topology=topo_text,      # text of the topology file
                           forces=None,             # text of the forces file
                           pdb=None,                # text of the pdb file
                           js_script=None,          # text of the javascript script file
                           colormap=None,           # name of the Matplotlib colormap
                           index_colors=None,       # A color for each index according to the colormap (list of values between 0 and 1)
                           width='99%',             # width of the viewer frame
                           height='500',            # height of the viewer frame
                           key=None)                # streamlit component key


```

The functions return a boolean value indicating if the program was able to write and read the files.

## How to cite:

Please include this citation if the OxView Component is used in an academic study:

```
Lucandia. Lucandia/st_oxview; Zenodo, 2024. https://zenodo.org/doi/10.5281/zenodo.12515559.
```

[![DOI](https://zenodo.org/badge/819322738.svg)](https://zenodo.org/doi/10.5281/zenodo.12515559)


## License

Code is licensed under the GNU General Public License v3.0 ([GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html))

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
