from MayaUtils import *
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget
import maya.cmds as mc


def TryAction(action):
    def wrapper(*args, **kwargs):
        try:
            action(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")

        return wrapper


class AnimClip:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True)
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True


class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = []
        self.animationClips : list[AnimClip] = []

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("Nothing Selected, please select the ROOT JOINT of the Rig")
        
        selectedJnt = selection[0]
        if not IsJoint(selectedJnt):
            raise Exception("{selectedJnt} is not a joint, please select the ROOT JOINT of the Rig")
        
        self.rootJnt = selectedJnt

    def AddRootJoint(self):
        if not self.rootJnt or not mc.objExists(self.rootJnt):
            raise Exception("no Root joint assigned, please set the current root joint of the rig first")
        
        currentRootJntPosX, currentRootJntPosY, currentRootJntPosZ = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootJntPosX == 0 and currentRootJntPosY == 0 and currentRootJntPosZ == 0:
            raise Exception("current root joint is already in origin, no need to make a new one")
        
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName

    def AddMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No mesh selected")
        
        meshes = set()

        for sel in selection:
            if IsMesh(sel):
                meshes.add(sel)

        if len(meshes) == 0:
            raise Exception("No mesh selected")
        
        self.meshes = list(meshes)


class AnimClipEntryWidget(QWidget):
    def __init__(self, animClip: AnimClip):
        super ().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        shouldExportCheckBox = QCheckBox()
        shouldExportCheckBox.setChecked(self.animClip.shouldExport)
        self.masterLayout.addWidget(shouldExportCheckBox)
        shouldExportCheckBox.toggled.connect(self.ShouldExportCheckboxToggled)
        
        self.masterLayout.addWidget(QLabel("Subfix: "))

        subfixLineEdit = QLineEdit()
        subfixLineEdit.setValidator(QRegExpValidator("[a-zA-Z0-9_]+"))
        subfixLineEdit.setText(self.animClip.subfix)
        subfixLineEdit.textChanged.connect(self.SubfixTextChanged)
        self.masterLayout.addWidget(subfixLineEdit)

        self.masterlayout.addWidget(QLabel("Min: "))
        minFrameLineEdit = QLineEdit()
        minFrameLineEdit.setValidator(QIntValidator())
        minFrameLineEdit.setText(str(int(self.animClip.frameMin)))
        minFrameLineEdit.textChanged.connect(self.MinFrameChanged)
        self.masterLayout.addWidget(minFrameLineEdit)

        self.masterlayout.addWidget(QLabel("Max: "))
        maxFrameLineEdit = QLineEdit()
        maxFrameLineEdit.setValidator(QIntValidator())
        maxFrameLineEdit.setText(str(int(self.animClip.frameMax)))
        maxFrameLineEdit.textChanged.connect(self.MaxFrameChanged)
        self.masterLayout.addWidget(maxFrameLineEdit)

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRangeBtn)

        deleteBtn = QPushButton("[X]")
        deleteBtn.clicked.connect(self.DeleteButtonClicked)
        self.masterLayout.addWidget(deleteBtn)

    def DeleteButtonClicked(self):
        self.deleteLater()

    def SetRangeBtnClicked(self):
        mc.playbackOptions(e=True, min=self.animClip.frameMin, max=self.animClip.frameMax)
        mc.playbackOptions(e=True, ast=self.animClip.frameMin, aet=self.animClip.frameMax)

    def MinFrameChanged(self, newVal):
        self.animClip.frameMin = int(newVal)

    def MaxFrameChanged(self, newVal):
        self.animClip.frameMax = int(newVal)

    def SubfixTextChanged(self, newText):
        self.animClip.subfix = newText


    def ShouldExportCheckboxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport
        

class MayaToUEWidget (QMayaWindow):
    def GetWindowHash(self):
        return "MayaToUEjYIFI753IHIi90"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya to UE")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Jnt")
        setSelectionAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntButtonClicked)
        self.masterLayout.addWidget(addRootJntBtn)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setFixedHeight(80)
        addMeshBtn = QPushButton("addMeshes")
        addMeshBtn.clicked.connect(self.AddMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)

        addNewAnimClipEntryBtn = QPushButton("Add Animation Clip")
        addNewAnimClipEntryBtn.clicked.connect(self.AddNewAnimCliEntryBtnClicked)

    def AddNewAnimCliEntryBtnClicked(self):
        newEntry = self.mayaToUE.AddNewAnimEntry()


    @TryAction
    def AddMeshBtnClicked(self):
        self.mayaToUE.AddMeshes()
        self.meshList.clear()
        self.meshList.addItems(self.mayaToUE.meshes)

    @TryAction
    def AddRootJntButtonClicked(self):
        self.mayaToUE.AddRootJoint()
        self.rootJntText.setText(self.mayaToUE.rootJnt)
    
    @TryAction
    def SetSelectionAsRootJntBtnClicked(self):
        self.mayaToUE.SetSelectedAsRootJnt()
        self.rootJntText.setText(self.mayaToUE.rootJnt)
        

MayaToUEWidget().show()
