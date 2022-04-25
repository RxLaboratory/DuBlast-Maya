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
**Status:**  
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/RxLaboratory/DuBlast-Maya?color=brightgreen)](https://github.com/RxLaboratory/DuBlast-Maya/releases) [![GitHub Release Date](https://img.shields.io/github/release-date/RxLaboratory/DuBlast-Maya)](https://github.com/RxLaboratory/DuBlast-Maya/releases) [![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/v/tag/RxLaboratory/DuBlast-Maya?include_prereleases&label=testing)](https://github.com/RxLaboratory/DuBlast-Maya/tags)
<!-- end:status -->

**Documentation:**  
[![Website](https://img.shields.io/badge/website-RxLab-informational)](https://rxlaboratory.org/tools/dublast-for-maya/)

<!-- statistics -->
**Statistics:**  
[![GitHub all releases](https://img.shields.io/github/downloads/RxLaboratory/DuBlast-Maya/total)](https://github.com/RxLaboratory/DuBlast-Maya/releases) [![GitHub release (latest by SemVer)](https://img.shields.io/github/downloads/RxLaboratory/DuBlast-Maya/latest/total?sort=semver)](https://github.com/RxLaboratory/DuBlast-Maya/releases) [![GitHub issues](https://img.shields.io/github/issues-raw/RxLaboratory/DuBlast-Maya)](https://github.com/RxLaboratory/DuBlast-Maya/issues) [![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/RxLaboratory/DuBlast-Maya?color=lightgrey)](https://github.com/RxLaboratory/DuBlast-Maya/issues?q=is%3Aissue+is%3Aclosed) [![GitHub commit activity](https://img.shields.io/github/commit-activity/m/RxLaboratory/DuBlast-Maya)](https://github.com/RxLaboratory/DuBlast-Maya/graphs/commit-activity)<!-- end:statistics -->  

<!-- progress -->
**Progress**:  
[![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/RxLaboratory/DuBlast-Maya/1)](https://github.com/RxLaboratory/DuBlast-Maya/milestone/1) [![GitHub milestone](https://img.shields.io/github/milestones/issues-open/RxLaboratory/DuBlast-Maya/1)](https://github.com/RxLaboratory/DuBlast-Maya/milestone/1) [![GitHub milestone](https://img.shields.io/github/milestones/issues-closed/RxLaboratory/DuBlast-Maya/1)](https://github.com/RxLaboratory/DuBlast-Maya/milestone/1?closed=1) [![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/RxLaboratory/DuBlast-Maya/latest)](https://github.com/RxLaboratory/DuBlast-Maya/network)<!-- end:progress --><!-- {1} -->

<!-- funding -->
**Funding:**  
[![Donate Now!](https://img.shields.io/badge/donate%20now!-donate.rxlab.info-blue?logo=heart)](http://donate.rxlab.info) [![Income](https://img.shields.io/endpoint?url=https%3A%2F%2Fversion.rxlab.io%2Fshields%2F%3FmonthlyIncome)](http://donate.rxlab.info) [![Sponsors](https://img.shields.io/endpoint?url=https%3A%2F%2Fversion.rxlab.io%2Fshields%2F%3FnumBackers)](http://donate.rxlab.info)  
<!-- end:funding -->

<!-- community -->
**Community:**  
[![Discord](https://img.shields.io/discord/480782642825134100)](http://chat.rxlab.info) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md) [![GitHub contributors](https://img.shields.io/github/contributors-anon/RxLaboratory/DuBlast-Maya)](https://github.com/RxLaboratory/DuBlast-Maya/graphs/contributors)  
[![Discord](https://img.shields.io/discord/480782642825134100?logo=discord&style=social&label=Discord)](http://chat.rxlab.info)
[![Facebook](https://img.shields.io/badge/Facebook-1877F2?logo=facebook&style=social)](https://www.facebook.com/rxlaboratory) [![Instagram](https://img.shields.io/badge/Instagram-E4405F?logo=instagram&style=social)](https://www.instagram.com/rxlaboratory/) [![Twitter Follow](https://img.shields.io/twitter/follow/RxLaboratory?label=Twitter&style=social)](https://www.twitter.com/rxlaboratory/) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&style=social)](https://www.linkedin.com/company/RxLaboratory/) [![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UC64qGypBbyM-ia-yf0nFSTg?label=Youtube)](https://www.youtube.com/channel/UC64qGypBbyM-ia-yf0nFSTg) [![Github](https://img.shields.io/github/stars/RxLaboratory?style=social&label=Github)](https://github.com/RxLaboratory)
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
