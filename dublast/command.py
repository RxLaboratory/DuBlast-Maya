"""
The Maya command
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

import maya.cmds as cmds # pylint: disable=import-error
import maya.mel as mel # pylint: disable=import-error
import maya.api.OpenMaya as om # pylint: disable=import-error

from dublast.functions import createPlayblast, createThumbnail, check_update
from dublast.dumaf.ui import getMayaWindow
from dublast.dumaf.paths import baseName
from dublast.ui_previewDialog import PreviewDialog

class DuBlastCmd( om.MPxCommand ):
    """The maya dublast command"""
    name = "dublast"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def createCommand():
        """Creates the command"""
        return DuBlastCmd()

    @staticmethod
    def createSyntax():
        """Creates the MEL syntax"""
        syntax = om.MSyntax()
        return syntax

    def doIt(self, args):
        """Runs the command"""

        # Check updates for the plugin
        check_update()

        # Check file
        currentFilePath = cmds.file( q=True, sn=True )
        if currentFilePath == '':
            cmds.warning("You need to save the current scene first.")
            cmds.inViewMessage( msg='You need to <hl>save the current scene</hl> first, sorry.', pos='midCenter', fade=True )
            return

        # Keep current SETTINGS
        currentAA = cmds.getAttr('hardwareRenderingGlobals.multiSampleEnable')
        currentAO = cmds.getAttr('hardwareRenderingGlobals.ssaoEnable')
        prevCam = cmds.lookThru( q=True )

        # show UI
        dialog = PreviewDialog( getMayaWindow() )
        result = dialog.exec_()
        if not result:
            return

        # Options
        comment = dialog.comment()
        cam = dialog.camera()
        size = dialog.getSize()
        hud = dialog.showHUD()
        thumbnail = dialog.thumbnail()
        pb = dialog.playblast()

        # Set the cam
        cmds.lookThru( cam )

        # Remove all current HUD
        currentHuds = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        if currentHuds:
            for hud in currentHuds:
                cmds.headsUpDisplay(hud, remove=True)
        # Add ours
        if hud:
            camName = baseName(cam)
            focalLength = str(round(cmds.getAttr(cam + '.focalLength'))) + ' mm'
            if cmds.keyframe(cam, at='focalLength', query=True, keyframeCount=True):
                focalLength = 'Animated'

            if comment != '':
                cmds.headsUpDisplay('DuComment',section=5, block=0, blockSize='small', ba='left', label='Comment : ' + comment, labelFontSize='small')
            cmds.headsUpDisplay('DuCurrentFrame',section=0, block=0, blockSize='large', label='Frame ',pre='currentFrame', labelFontSize='large',dfs='large')
            cmds.headsUpDisplay('DuCam',section=7, block=0, blockSize='large', label='Camera: ' + camName, labelFontSize='large')
            cmds.headsUpDisplay('DuFocalLength',section=9, block=0, blockSize='large', label='Focal Length: ' + focalLength,labelFontSize='large')

        # Save path
        pbFilePath = os.path.dirname(currentFilePath)
        pbFileName = os.path.basename(currentFilePath)
        pbFileName = ".".join( pbFileName.split(".")[0:-1])
        if comment != "":
            pbFileName = pbFileName + "_" + comment

        if thumbnail:
            tnFilePath = pbFilePath + '/' + pbFileName + '.png'
            # Attempt to set window size
            dialog.setWindowSize()
            createThumbnail(tnFilePath)
            print("Thumbnail saved: " + tnFilePath)

        if pb:
            # Extension
            filePath = pbFilePath + '/' + pbFileName + '.mp4'
            cmds.refresh()
            createPlayblast(filePath, size)
            print("Playblast saved: " + filePath)

        # Hide window
        dialog.hideRenderer()

        # Set back render SETTINGS
        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable',currentAA)
        cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',currentAO)
        cmds.lookThru( prevCam )
        mel.eval("lookThroughModelPanel " + prevCam + " modelPanel4;")

        # Remove all current HUD
        currentHuds = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        if currentHuds:
            for hud in currentHuds:
                cmds.headsUpDisplay(hud, remove=True)
