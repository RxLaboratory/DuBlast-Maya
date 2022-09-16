"""
General functions
"""

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either VERSION 3
#  of the License, or (at your option) any later VERSION.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import os
import tempfile
import platform
import subprocess
import shutil

from maya import cmds # pylint: disable=import-error
from maya import mel # pylint: disable=import-error

from dublast import dumaf

def check_update():
    """Checks if an update is available"""
    from dublast import TOOL_NAME, VERSION, IS_PRERELEASE
    dumaf.utils.checkUpdate( TOOL_NAME, VERSION, discreet=True, preRelease=IS_PRERELEASE )

def getTempDir():
    """Creates and returns a tempdir. For some reason, sometimes the user folder is incorrect in TEMP on windows"""
    tempDir = tempfile.mkdtemp()
    if platform.system() == 'Windows':
        userDir = os.getenv('USERPROFILE')
        tempDir = userDir + '/AppData/Local/Temp/' + os.path.basename(tempDir)
    return tempDir

def createPlayblast(filePath, size):
    """Creates a playblast"""
    # Warning, That's for win only ! Needs work on MAC/Linux
    # TODO MAC: open playblast at the end
    # TODO MAC/LINUX: video (audio) playblast format must not be avi
    # TODO MAC/LINUX: call to ffmpeg without .exe
    if platform.system() != 'Windows':
        return

    # Get bin dir
    pluginFolder = os.path.dirname( cmds.pluginInfo('DuBlast', query=True, path=True) )
    ffmpegFile = pluginFolder + '/ffmpeg.exe'
    ffplayFile = pluginFolder + '/ffplay.exe'

    # Get a temp dir for rendering the playblast
    tempDir = getTempDir()
    # The tempDir may not exist
    if not os.path.isdir(tempDir):
        os.makedirs(tempDir)
    imageFile = tempDir + '/' + 'dublast'

    # Create jpg frame sequence
    w = cmds.getAttr("defaultResolution.width") * size
    h = cmds.getAttr("defaultResolution.height") * size
    w = w - w % 4
    h = h - h % 4
    imageFile = cmds.playblast( filename=imageFile,
        format='image',
        clearCache=True,
        framePadding= 5,
        viewer=False,
        showOrnaments=True,
        percent=100,
        compression="jpg",
        quality=50, 
        width = w,
        height = h )

    # if there's sound, create a sound file
    soundFile = ''
    sounds = cmds.ls(type='audio')
    # If there are sounds in the scene
    if sounds:
        timeCtrl = mel.eval('$tmpVar=$gPlayBackSlider')
        # And sounds are used by the timeline
        if cmds.timeControl(timeCtrl, displaySound=True, query=True):
            soundFile = tempDir + '/' + 'blast.avi'
            soundFile = cmds.playblast(filename=soundFile, format='avi', clearCache=True, useTraxSounds=True, framePadding= 5, viewer=False, showOrnaments=False, percent=10,compression="none", quality=10)

    # Get framerate
    framerate = mel.eval('float $fps = `currentTimeUnitToFPS`') # It's not in cmds!!

    # Transcode using ffmpeg
    ffmpegArgs = [
        ffmpegFile,
        '-loglevel', 'error', # limit output to errors
        '-y', # overwrite
        '-start_number', str(cmds.playbackOptions(q=True,minTime=True)),
        '-framerate', str(framerate),
        '-i', imageFile.replace('####', "%5d"), # Image file
    ]
    if soundFile != '':
        ffmpegArgs = ffmpegArgs + [
            '-i', soundFile,
            '-map', '0:0', # map video to video
            '-map', '1:1', # map audio to audio
            '-b:a', '131072', # "Bad" quality
        ]
    ffmpegArgs = ffmpegArgs + [
        '-f', 'mp4', # Codec
        '-c:v', 'h264', # Codec
        '-level', '3.0', # Compatibility
        '-crf', '25', # "Bad" quality
        '-preset', 'ultrafast', # We're in a hurry to playblast!
        '-tune', 'fastdecode', # It needs to be easy to play
        '-profile:v', 'baseline', # Compatibility
        '-x264opts', 'b_pyramid=0', # Needed to decode in Adobe Apps
        '-pix_fmt', 'yuv420p', # Because ffmpeg does 422 by default, which causes compatibility issues
        '-intra', # Intra frame for frame by frame playback
        filePath # Output file
    ]

    ffmpegProcess = subprocess.Popen(ffmpegArgs,shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Launch!

    output = ffmpegProcess.communicate()

    # Remove temp files
    shutil.rmtree(tempDir)
    subprocess.Popen([ffplayFile, '-seek_interval', '0.1', filePath])
    return

    # TEST
    # Open playblast
    if platform.system() == "Windows":
        os.startfile(filePath)
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", filePath])

def createThumbnail(filePath):
    """Creates a thumbnail"""
    cmds.refresh(cv=True, fn = filePath)
