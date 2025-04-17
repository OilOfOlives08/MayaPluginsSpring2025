from MayaUtils import IsJoint, QMayaWindow
from PySide2.QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc
class MayaToUE:
    def __init__(self):
        self.rootJnt = ""

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


class MayaToUEWidget (QMayaWindow):
    def GetWindowHash(self):
        return "MayaToUEjYIFI753IHIi90"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya to UE")

        self.masterLayout + QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addwidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Jnt")
        setSelectionAsRootJntBtn.clicked.connect(self.setSelectionAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntButtonClicked)
        self.masterLayout.addWidget(addRootJntBtn)

    def AddRootJntButtonClicked(self):
        try:
            self.mayaToUE.AddRootJoint()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")

    def SetSelectionAsRootJntBtnClicked(self):
        try:
            self.mayaToUE.SetSelectedAsRootJnt()
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")

MayaToUEWidget().show()