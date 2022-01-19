# -*- coding: utf-8 -*-
"""Better Playblasts for Maya"""

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
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

import os, sys, platform, tempfile, subprocess, shutil
from PySide2.QtWidgets import ( # pylint: disable=no-name-in-module
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QSpinBox,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSlider,
    QApplication
)
from PySide2.QtCore import ( # pylint: disable=no-name-in-module
    Slot,
    Qt
)
import maya.cmds as cmds # pylint: disable=import-error
import maya.mel as mel # pylint: disable=import-error
import maya.api.OpenMaya as om # pylint: disable=import-error

vendor = "RxLaboratory"
version = "1.0.0"

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

def baseName( node, keepNameSpace = False ):
    nodeName = node.split('|')[-1]
    if not keepNameSpace:
        nodeName = nodeName.split(':')[-1]
    return nodeName

def getMayaWindow():
        app = QApplication.instance() #get the qApp instance if it exists.
        if not app:
            app = QApplication(sys.argv)
        try:
            mayaWin = next(w for w in app.topLevelWidgets() if w.objectName()=='MayaWindow')
            return mayaWin
        except:
            return None

def getTempDir():
    """Creates and returns a tempdir. For some reason, sometimes the user folder is incorrect in TEMP on windows"""
    tempDir = tempfile.mkdtemp()
    if platform.system() == 'Windows':
        userDir = os.getenv('USERPROFILE')
        tempDir = userDir + '/AppData/Local/Temp/' + os.path.basename(tempDir)
    return tempDir

def createPlayblast(filePath, size):

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
    cmds.refresh(cv=True, fn = filePath)

class PreviewDialog( QDialog ):

    def __init__(self, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.modelEditor = None
        self.pbWin = 'duPlayblasterWin'
        self.pbLayout = 'duPlayblasterLayout'
        self.modelPanel = 'duPlayblasterPanel'

        self.__setupUi()
        self.__loadCameras()
        self.showRenderer()
        self.__connectEvents()

    def __setupUi(self):
        self.setWindowTitle( "Create preview" )

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(6,6,6,6)
        mainLayout.setSpacing(3)

        topLayout = QFormLayout()
        topLayout.setFieldGrowthPolicy( QFormLayout.AllNonFixedFieldsGrow )
        topLayout.setSpacing(3)

        self.cameraBox = QComboBox()
        topLayout.addRow("Camera:", self.cameraBox)

        sizeWidget = QWidget()
        sizeLayout = QHBoxLayout()
        sizeLayout.setContentsMargins(0,1,0,0)
        sizeLayout.setSpacing(3)
        self.sizeEdit = QSpinBox()
        self.sizeEdit.setMaximum(100)
        self.sizeEdit.setMinimum(10)
        self.sizeEdit.setSuffix(' %')
        self.sizeEdit.setValue(50)
        sizeLayout.addWidget(self.sizeEdit)
        self.sizeSlider = QSlider()
        self.sizeSlider.setOrientation( Qt.Horizontal )
        self.sizeSlider.setMaximum(100)
        self.sizeSlider.setMinimum(10)
        self.sizeSlider.setValue(50)
        sizeLayout.addWidget(self.sizeSlider)
        sizeWidget.setLayout(sizeLayout)
        topLayout.addRow("Size:", sizeWidget)

        renderOptionsWidget = QWidget()
        renderOptionsLayout = QVBoxLayout()
        renderOptionsLayout.setContentsMargins(0,1,0,0)
        renderOptionsLayout.setSpacing(3)
        self.displayAppearenceBox = QComboBox()
        self.displayAppearenceBox.addItem("Smooth Shaded", 'smoothShaded')
        self.displayAppearenceBox.addItem("Flat Shaded", 'flatShaded')
        self.displayAppearenceBox.addItem("Bounding Box", 'boundingBox')
        self.displayAppearenceBox.addItem("Points", 'points')
        self.displayAppearenceBox.addItem("Wireframe", 'wireframe')
        renderOptionsLayout.addWidget(self.displayAppearenceBox)
        self.useLightsBox = QComboBox( )
        self.useLightsBox.addItem( "Default Lighting", 'default' )
        self.useLightsBox.addItem( "Silhouette", 'none' )
        self.useLightsBox.addItem( "Scene Lighting", 'all' )
        renderOptionsLayout.addWidget(self.useLightsBox)
        self.displayTexturesBox = QCheckBox( "Display Textures")
        self.displayTexturesBox.setChecked(True)
        renderOptionsLayout.addWidget(self.displayTexturesBox)
        self.displayShadowsBox = QCheckBox("Display Shadows")
        self.displayShadowsBox.setChecked(True)
        renderOptionsLayout.addWidget(self.displayShadowsBox )
        self.aoBox = QCheckBox("Ambient Occlusion")
        self.aoBox.setChecked(True)
        renderOptionsLayout.addWidget(self.aoBox)
        self.aaBox = QCheckBox("Anti-Aliasing")
        self.aaBox.setChecked(True)
        renderOptionsLayout.addWidget(self.aaBox)
        self.onlyPolyBox = QCheckBox("Only Polygons")
        self.onlyPolyBox.setChecked(True)
        renderOptionsLayout.addWidget(self.onlyPolyBox)
        self.motionTrailBox = QCheckBox("Show Motion Trails")
        renderOptionsLayout.addWidget(self.motionTrailBox)
        renderOptionsWidget.setLayout( renderOptionsLayout )
        topLayout.addRow("Renderer:", renderOptionsWidget)

        self.commentEdit = QLineEdit()
        self.commentEdit.setMaxLength(20)
        topLayout.addRow("Comment:", self.commentEdit)

        mainLayout.addLayout(topLayout)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(2)
        self._playblastButton = QPushButton("Playblast")
        buttonsLayout.addWidget( self._playblastButton )
        self._thumbnailButton = QPushButton("Thumbnail")
        buttonsLayout.addWidget( self._thumbnailButton )
        self._cancelButton = QPushButton("Cancel")
        buttonsLayout.addWidget( self._cancelButton )
        mainLayout.addLayout( buttonsLayout )

        self.setLayout(mainLayout)

    def __connectEvents(self):
        self._playblastButton.clicked.connect( self.__ok )
        self._playblastButton.clicked.connect( self.accept )
        self._thumbnailButton.clicked.connect( self.__ok )
        self._thumbnailButton.clicked.connect( self.__thumbnail )
        self._cancelButton.clicked.connect( self.reject )
        self.rejected.connect(self.hideRenderer)
        self.displayAppearenceBox.currentIndexChanged.connect( self.__updateLightsBox )
        self.displayAppearenceBox.currentIndexChanged.connect( self.__updateRenderer )
        self.useLightsBox.currentIndexChanged.connect( self.__updateRenderer )
        self.displayTexturesBox.clicked.connect( self.__updateRenderer )
        self.motionTrailBox.clicked.connect( self.__updateRenderer )
        self.displayShadowsBox.clicked.connect( self.__updateRenderer )
        self.cameraBox.currentIndexChanged.connect( self.__updateRenderer )
        self.aaBox.clicked.connect( self.__updateRenderer )
        self.aoBox.clicked.connect( self.__updateRenderer )
        self.sizeSlider.valueChanged.connect( self.sizeEdit.setValue )
        self.sizeEdit.valueChanged.connect( self.sizeSlider.setValue )

    def __updateRenderer(self):
        cmds.modelEditor(self.modelEditor,
            camera=self.cameraBox.currentData(), 
            displayAppearance=self.displayAppearenceBox.currentData(),
            displayLights= self.useLightsBox.currentData(),
            displayTextures=self.displayTexturesBox.isChecked(),
            motionTrails=self.motionTrailBox.isChecked(),
            shadows=self.displayShadowsBox.isChecked(),
            edit=True)

        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable',self.aaBox.isChecked() ) # AA
        cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', self.aoBox.isChecked() ) # AO

    def showRenderer(self):
        # Get/Create window
        if not cmds.window( self.pbWin, exists=True, query=True):
            cmds.window( self.pbWin )
            # Workaround to make windowPref available later: show and delete and recreate the window
            # show
            cmds.showWindow( self.pbWin )
            # and delete :)
            cmds.deleteUI( self.pbWin )
            # and get it back
            cmds.window( self.pbWin )
            # add the layout
            cmds.paneLayout( self.pbLayout )

        # Set window title
        cmds.window(self.pbWin, title= 'DuBlast', edit=True)

        # Set window size to the renderer size
        # Prepare viewport
        cmds.windowPref(self.pbWin, maximized=True,edit=True)

        # Get/Create new model panel
        if not cmds.modelPanel(self.modelPanel,exists=True,query=True):
            cmds.modelPanel(self.modelPanel)
        cmds.modelPanel(self.modelPanel, parent=self.pbLayout, menuBarVisible=False, edit=True)

        # The model editor with default values
        self.modelEditor = cmds.modelPanel(self.modelPanel, modelEditor=True, query=True)
        # Adjust render setting
        cmds.modelEditor(self.modelEditor, activeView=True, edit=True)
        self.__updateRenderer()
        
        # Adjust cam
        cmds.camera(self.cameraBox.currentData(),e=True,displayFilmGate=False,displayResolution=False,overscan=1.0)
        # Clear selection
        cmds.select(clear=True)

        # Show window
        cmds.showWindow( self.pbWin )

    def __ok(self):
        if self.onlyPolyBox.isChecked():
            cmds.modelEditor(self.modelEditor, e=True, alo=False) # only polys, all off
            cmds.modelEditor(self.modelEditor, e=True, polymeshes=True) # polys
            cmds.modelEditor(self.modelEditor, e=True, motionTrails=self.motionTrailBox.isChecked() )

    Slot()
    def __updateLightsBox(self, index):
        self.useLightsBox.setEnabled( index < 2 )

    Slot()
    def __thumbnail(self):
        self.done(2)

    def __loadCameras(self):
        cameras = cmds.ls(type='camera')
        renderableCameras = []
        perspCameras = []
        orthoCameras = []
        for camera in cameras:
            # get the transform node
            camera = cmds.listRelatives(camera, parent=True, f=True, type='transform')[0]
            if cmds.getAttr( camera + '.renderable'):
                renderableCameras.append(camera)
                continue
            if cmds.camera(camera, orthographic=True, query=True):
                orthoCameras.append(camera)
                continue
            perspCameras.append(camera)
                
        numRenderCam = len(renderableCameras)
        if numRenderCam > 0:
            for camera in renderableCameras:
                cameraName = baseName(camera)
                self.cameraBox.addItem( cameraName, camera)
            self.cameraBox.insertSeparator( numRenderCam )
        numPerspCam = len( perspCameras )
        if numPerspCam > 0:
            for camera in perspCameras:
                cameraName = baseName(camera)
                self.cameraBox.addItem( cameraName, camera)
            self.cameraBox.insertSeparator( numRenderCam+numPerspCam )

        for camera in orthoCameras:
            cameraName = baseName(camera)
            self.cameraBox.addItem( cameraName, camera)
    
    def comment(self):
        return self.commentEdit.text()

    def camera(self):
        return self.cameraBox.currentData()

    def getSize(self):
        return self.sizeEdit.value() / 100.0

    Slot()
    def hideRenderer(self):
        cmds.window( self.pbWin, visible=False, edit=True)

    def setWindowSize(self):
        s = self.getSize()
        w = cmds.getAttr("defaultResolution.width") * s - 4
        h = cmds.getAttr("defaultResolution.height") * s - 23
        cmds.windowPref(self.pbWin, maximized=False, edit=True)
        cmds.window(self.pbWin, width=w, height=h, edit=True)
        cmds.refresh(cv=True)

class DuBlastCmd( om.MPxCommand ):
    name = "dublast"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def createCommand():
        return DuBlastCmd()

    @staticmethod
    def createSyntax():
        syntax = om.MSyntax()
        return syntax

    def doIt(self, args):

        # Check file
        currentFilePath = cmds.file( q=True, sn=True )
        if currentFilePath == '':
            cmds.warning("You need to save the current scene first.")
            cmds.inViewMessage( msg='You need to <hl>save the current scene</hl> first, sorry.', pos='midCenter', fade=True )
            return
   
        # Keep current SETTINGS
        currentAA = cmds.getAttr('hardwareRenderingGlobals.multiSampleEnable')
        currentAO = cmds.getAttr('hardwareRenderingGlobals.ssaoEnable')

        # show UI
        dialog = PreviewDialog( getMayaWindow() )
        result = dialog.exec_()
        if not result:
            return

        # Options
        comment = dialog.comment()
        cam = dialog.camera()
        size = dialog.getSize()

        # Remove all current HUD
        currentHuds = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        if currentHuds:
            for hud in currentHuds:
                cmds.headsUpDisplay(hud, remove=True)
        # Add ours
        # Collect info
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

        if result == 1:
            pbFilePath = pbFilePath + '/' + pbFileName + '.mp4'
            createPlayblast(pbFilePath, size)
        else:
            pbFilePath = pbFilePath + '/' + pbFileName + '.png'
            # Attempt to set window size
            dialog.setWindowSize()
            createThumbnail(pbFilePath)

        # Hide window
        dialog.hideRenderer()
        
        # Set back render SETTINGS
        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable',currentAA)
        cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',currentAO)

        # Remove all current HUD
        currentHuds = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        if currentHuds:
            for hud in currentHuds:
                cmds.headsUpDisplay(hud, remove=True)

def initializePlugin( obj ):
    plugin = om.MFnPlugin(obj, vendor, version)

    plugin.registerCommand( DuBlastCmd.name, DuBlastCmd.createCommand, DuBlastCmd.createSyntax )

def uninitializePlugin( obj ):
    plugin = om.MFnPlugin(obj, vendor, version)

    plugin.deregisterCommand( DuBlastCmd.name )
