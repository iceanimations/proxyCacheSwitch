'''
Created on Jan 7, 2016

@author: qurban.ali
'''
import pymel.core as pc
import appUsageApp
import qtify_maya_window as qtfy
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog
import msgBox
import os.path as osp
import qutil
import imaya
import maya.cmds as cmds
import os

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

__title__ = 'Proxy & GPU Cache Switch'

pathKey = 'proxyCacheSwitch_pathKey'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class UI(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(__title__)
        path = qutil.getOptionVar(pathKey)
        self.lastPath = path if path else ''
        
        self.editButton.clicked.connect(self.edit)
        self.reloadButton.clicked.connect(self.reload)
        self.showProxyButton.clicked.connect(self.showRedshiftProxy)
        self.showGPUButton.clicked.connect(self.showGPUCache)
        self.browseButton.clicked.connect(self.setPath)
        self.exportButton.clicked.connect(self.export)
        
        appUsageApp.updateDatabase('proxyCacheSwitch')
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=__title__, **kwargs)
    
    def setPath(self):
        filename = QFileDialog.getExistingDirectory(self, 'Select Folder', self.lastPath)
        if filename:
            self.pathBox.setText(filename)
            self.lastPath = filename
            qutil.addOptionVar(pathKey, filename)
            
    def getPath(self):
        path = self.pathBox.text()
        if not path or not osp.exists(path):
            self.showMessage(msg='The system could not find the path specified',
                             icon=QMessageBox.Information)
            path = ''
        return path

    def getSelectedMesh(self):
        sl = pc.ls(sl=True, type='mesh', dag=True)
        if not sl:
            self.showMessage(msg='No Mesh found in the selection',
                             icon=QMessageBox.Information)
        if len(sl) > 1:
            self.showMessage(msg='More than one meshes are not allowed',
                             icon=QMessageBox.Information)
            return []
        return [mesh.firstParent() for mesh in sl]
    
    def getDirPath(self):
        path = cmds.file(q=True, location=True)
        if path and osp.exists(path):
            return osp.dirname(path)

    def export(self):
        try:
            path = self.getPath()
            if path:
                meshes = self.getSelectedMesh()
                if meshes:
                    for mesh in meshes:
                        name = qutil.getNiceName(mesh.name())
                        filePath = osp.join(path, name)
                        pc.select(mesh)
                        pc.mel.eval('file -force -options \"\" -typ \"Redshift Proxy\" -pr -es \"%s\";'%filePath.replace('\\', '/'))
                        pc.mel.rsProxy(filePath.replace('\\', '/') +'.rs', fp=True, sl=True)
                        pc.mel.gpuCache(mesh, startTime=1, endTime=1, optimize=True,
                                        optimizationThreshold=40000,
                                        writeMaterials=True, dataFormat="ogawa",
                                        directory=path, fileName=name)
                        pc.exportSelected(filePath, f=True, options="v=0",
                                          typ=imaya.getFileType(), pr=True)
                    if self.deleteButton.isChecked():
                        if self.showProxyButton.isChecked():
                            self.createReshiftProxy(filePath +'.rs').displayMode.set(0)
                        else:
                            self.createGPUCache(filePath +'.abc')
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)

    def createReshiftProxy(self, filePath):
        node = pc.PyNode(pc.mel.redshiftCreateProxy()[0])
        node.fileName.set(filePath)
        return node

    def createGPUCache(self, filePath):
        xformNode = pc.createNode('transform', name='pCube1')
        pc.createNode('gpuCache', name='pCube1Shape', parent=xformNode).cacheFileName.set(filePath)
        pc.xform(xformNode, centerPivots=True)

    def reload(self):
        try:
            node = self.getSelectionType()
            if not node: return
            if type(node) == pc.nt.GpuCache:
                filename = node.cacheFileName.get()
                node.cacheFileName.set('')
                node.cacheFileName.set(filename)
            else:
                filename = node.fileName.get()
                node.fileName.set('')
                node.fileName.set(filename)
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
    
    def getSelectionType(self):
        sl = pc.ls(sl=True, dag=True, type='gpuCache')
        if sl:
            return sl[0]
        else:
            try:
                sl = pc.ls(sl=True, type='mesh', dag=True, ni=True)[0].inMesh.inputs()[0]
            except:
                self.showMessage(msg='Could not find a valid selection',
                                 icon=QMessageBox.Information)
                return
            if type(sl) != pc.nt.RedshiftProxyMesh:
                self.showMessage(msg='Could not find a Proxy Node',
                                 icon=QMessageBox.Information)
                return
            return sl

    def edit(self):
        try:
            node = self.getSelectionType()
            if not node: return
            if type(node) == pc.nt.GpuCache:
                filename = node.cacheFileName.get()
            else:
                filename = node.fileName.get()
            if filename and osp.exists(filename):
                filename = osp.splitext(filename)[0] + '.ma'
                if not osp.exists(filename):
                    filename = osp.splitext(filename)[0] + '.mb'
                if osp.exists(filename):
                    os.system('start %s'%osp.normpath(filename))
                else:
                    self.showMessage(msg='Could not find Maya file',
                                     icon=QMessageBox.Critical)
            else:
                self.showMessage(msg='Could not find linked file',
                                 icon=QMessageBox.Critical)
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
    
    def showRedshiftProxy(self):
        try:
            node = self.getSelectionType()
            if not node: return
            if type(node) == pc.nt.GpuCache:
                filename = node.cacheFileName.get()
                filename = osp.splitext(filename)[0] + '.rs'
                if osp.exists(filename):
                    pc.delete(node.firstParent())
                    self.createReshiftProxy(filename)
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
    
    def showGPUCache(self):
        try:
            node = self.getSelectionType()
            if not node: return
            if type(node) == pc.nt.RedshiftProxyMesh:
                filename = node.fileName.get()
                filename = osp.splitext(filename)[0] + '.abc'
                if osp.exists(filename):
                    pc.delete(node.outMesh.outputs()[0])
                    self.createGPUCache(filename)
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)