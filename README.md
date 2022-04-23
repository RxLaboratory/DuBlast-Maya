# DuBlast for Maya

Better Playblasts for Maya

- Auto-Select the right camera!
- Rendering options.
- Burn in metadata and frame number.
- Modern and animator-friendly video format (Lightweight intra-frame mp4).
- Auto-save next to the Maya scene file.
- Simple and performant default player (ffplay).
- No need to install Quicktime anymore...

[![Maya](https://img.shields.io/badge/Maya-Win-informational?color=lightgrey&logo=autodesk)](#) [![GitHub](https://img.shields.io/github/license/RxLaboratory/Duik?color=lightgrey)](LICENSE.md)

<!-- status -->
<!-- end:status -->

**Documentation:**
[![Website](https://img.shields.io/badge/website-RxLab-informational)](https://rxlaboratory.org/tools/dublast-for-maya/)

<!-- statistics -->
<!-- end:statistics -->  

<!-- progress -->
<!-- end:progress --><!-- {1} -->

<!-- funding -->
<!-- end:funding -->

<!-- community -->
<!-- end:community -->

## Installation

*DuBlast* should work with either *Python 2.x* or *Python 3.x*.  
For now, it works only on *Windows*, but making it work on *Linux* should be easy.

- Download the [latest release](https://github.com/RxLaboratory/DuMAF_DuBlast/releases).
- Unzip all the files to one of the Maya plug-ins folder.  
    `C:\Users\YourName\Documents\maya\plug-ins\`
- In the Maya Plug-in Manager, click the *Refresh* button, then enable *DuBlast* by checking the *Loaded* box. You'll probably want to check the *Auto load* box too...

## Usage

You can create a playblast using the new Maya command `dublast`.

```py
# Python
import maya.cmds as cmds
cmds.dublast()
```

```mel
// Mel
dublast
```

You can add this command to a shelf, or use it to create a keyboard shortcut. The provided `dublast.png` file can be used as an icon with your shelf button.

When running the command, a preview window and these options are shown:

![](https://github.com/RxLaboratory/DuMAF_DuBlast/blob/main/dublast_screenshot.png?raw=true)

- Camera: Select the camera to use for the playblast. By default, *DuBlast* selects the first camera found in the render settings.
- Size: Set the size ratio according to the render settings.
- Renderer: Set the render options
- Comment: Set a short comment to be added to the file name and the burned in metadata.

DuBlast automatically burns some metadata in the video:

- The current frame number
- The optional comment
- The name of the camera
- The focal length of the camera

Note that some of these metadata may not be visible if the output size is too small.

### Using the default video player (ffplay)

DuBlast automatically plays the video with *ffplay*, a free and lightweight video player well suited for checking animations.

It is a *headless* player: it doesn't have any user interface, but you can easily interact with the video anyway:

- *Right click*: seeks in time
- *Space*: play/pause
- *S*: go one frame forward
- *→*: go 0.10s forward
- *←*: go 0.10s backward
- *↑*: go to end
- *↓*: go to start

### Other

There's no option (yet) to the command so you can't set the options programmatically to create the playblast without showing the options dialog. But that should change in a near future.
