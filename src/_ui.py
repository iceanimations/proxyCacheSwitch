'''
Created on Jan 7, 2016

@author: qurban.ali
'''

from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog, QIcon
from PyQt4.QtCore import QSize
import qtify_maya_window as qtfy
import os.path as osp
import backend
import appUsageApp
import cui

reload(backend)
reload(cui)

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')
icon_path = osp.join(root_path, 'icons')

__title__ = 'Proxy GPU Cache Switch'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class UI(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.proxyDeleteButton.hide()
        self.gpuDeleteButton.hide()
        self.selectionDeleteButton.hide()
        self.setWindowTitle(__title__)
        
        self.proxyLow = False
        self.gpuLow = False
        self.proxyItems = []
        self.gpuItems = []
        
        buttonsMapping = {self.proxyHLButton: 'HL.png',
                          self.proxyToGPUButton: 'G.png',
                          self.proxySelectButton: 'S.png',
                          self.proxyReloadButton: 'R.png',
                          self.proxyDeleteButton: 'X.png',
                          self.gpuHLButton: 'HL.png',
                          self.gpuToProxyButton: 'P.png',
                          self.gpuSelectButton: 'S.png',
                          self.gpuReloadButton: 'R.png',
                          self.gpuDeleteButton: 'X.png',
                          self.selectionHLButton: 'HL.png',
                          self.selectionPGButton: 'PG.png',
                          self.selectionFocusButton: 'F.png',
                          self.selectionTearButton: 'T.png',
                          self.selectionReloadButton: 'R.png',
                          self.selectionDeleteButton: 'X.png'}
        for btn, img in buttonsMapping.items():
            btn.setIcon(QIcon(osp.join(icon_path, img)))
        
        self.proxyHLButton.clicked.connect(self.switchProxiesToHL)
        self.proxyToGPUButton.clicked.connect(self.switchProxiesToGPU)
        self.proxySelectButton.clicked.connect(self.selectAllProxies)
        self.proxyReloadButton.clicked.connect(self.reloadAllProxies)
        self.proxyDeleteButton.clicked.connect(self.delelteAllProxies)
        self.gpuHLButton.clicked.connect(self.switchGPUToHL)
        self.gpuToProxyButton.clicked.connect(self.switchGPUToProxy)
        self.gpuSelectButton.clicked.connect(self.selectAllGPUs)
        self.gpuReloadButton.clicked.connect(self.reloadAllGPUs)
        self.gpuDeleteButton.clicked.connect(self.deleteAllGPUs)
        self.selectionHLButton.clicked.connect(self.switchSelectionToHL)
        self.selectionPGButton.clicked.connect(self.switchSelectionPG)
        self.selectionFocusButton.clicked.connect(self.focusSelection)
        self.selectionTearButton.clicked.connect(self.tearSelection)
        self.selectionReloadButton.clicked.connect(self.reloadSelection)
        self.selectionDeleteButton.clicked.connect(self.deleteSelection)
        self.refreshButton.clicked.connect(self.refresh)
        
        self.populate()

        appUsageApp.updateDatabase('proxyCacheSwitch')
        
    def populate(self):
        errors = []
        for item in self.proxyItems:
            item.deleteLater()
        del self.proxyItems[:]
        for item in self.gpuItems:
            item.deleteLater()
        del self.gpuItems[:]
        pItems, err = backend.getProxyItems()
        if err: errors.extend(err)
        self.proxyNumberLabel.setText("("+ str(len(pItems)) +")")
        for pItem in pItems:
            item = ProxyItem(self, pItem)
            item.update()
            self.proxyLayout.addWidget(item)
            self.proxyItems.append(item)
        gpuItems, err = backend.getGPUItems()
        if err: errors.extend(err)
        self.gpuCacheNumberLabel.setText("("+ str(len(gpuItems)) +")")
        for gpuItem in gpuItems:
            item = GPUItem(self, gpuItem)
            item.update()
            self.gpuCacheLayout.addWidget(item)
            self.gpuItems.append(item)
        if errors:
            self.showMessage(msg='Errors occurred while populating the window',
                             details='\n'.join(errors),
                             icon=QMessageBox.Critical)
            
    def deleteAllGPUs(self):
        pass
    
    def delelteAllProxies(self):
        pass
            
    def deleteSelection(self):
        pass
        
    def refresh(self):
        self.populate()
        
    def reloadSelection(self):
        pass
    
    def tearSelection(self):
        pass
        
    def focusSelection(self):
        pass
        
    def switchSelectionPG(self):
        pass
        
    def switchSelectionToHL(self):
        pass
        
    def reloadAllGPUs(self):
        for item in self.gpuItems:
            item.reload()
        
    def selectAllGPUs(self):
        for item in self.gpuItems:
            item.select(add=True)
        
    def switchGPUToProxy(self):
        for item in self.gpuItems:
            item.switch(refresh=False)
        self.refresh()
        
    def switchGPUToHL(self):
        errors = []
        for item in self.gpuItems:
            if self.gpuLow:
                err = item.switchToLow()
                if err: errors.append(err)
            else:
                err = item.switchToHi()
                if err: errors.append(err)
        self.gpuLow = not self.gpuLow
        if errors:
            self.showMessage(msg='Errors occurred while switching',
                             details='\n'.join(errors),
                             icon=QMessageBox.Critical)
        
    def reloadAllProxies(self):
        for item in self.proxyItems:
            item.reload()
        
    def selectAllProxies(self):
        for item in self.proxyItems:
            item.select(add=True)
        
    def switchProxiesToHL(self):
        '''switch all the proxies to H/L'''
        errors = []
        for item in self.proxyItems:
            if self.proxyLow:
                err = item.switchToLow()
                if err: errors.append(err)
            else:
                err = item.switchToHi()
                if err: errors.append(err)
        self.proxyLow = not self.proxyLow
        if errors:
            self.showMessage(msg='Errors occurred while switching',
                             details='\n'.join(errors),
                             icon=QMessageBox.Critical)

    def switchProxiesToGPU(self):
        for item in self.proxyItems:
            item.switch(refresh=False)
        self.refresh()
        
    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=__title__, **kwargs)
            
Form2, Base2 = uic.loadUiType(osp.join(ui_path, 'item.ui'))
class BaseItem(Form2, Base2):
    def __init__(self, parent=None, item=None):
        super(BaseItem, self).__init__(parent)
        self.setupUi(self)
        self.deleteButton.hide()
        self.parentWin = parent
        self.item = item
        
        buttonsMapping = {self.hlButton: 'HL.png',
                          self.selectButton: 'S.png',
                          self.reloadButton: 'R.png',
                          self.deleteButton: 'X.png'}
        for btn, img in buttonsMapping.items():
            btn.setIcon(QIcon(osp.join(icon_path, img)))
        
        self.hlButton.clicked.connect(self.switchToHL)
        self.switchButton.clicked.connect(lambda: self.switch())
        self.selectButton.clicked.connect(self.select)
        self.browseButton.clicked.connect(self.browse)
        self.reloadButton.clicked.connect(self.reload)
        self.pathBox.textChanged.connect(self.handlePathChange)
        self.deleteButton.clicked.connect(self.delete)
        
    def delete(self):
        pass # to be implemented in child class
    
    def update(self, item=None):
        if item is not None:
            self.item = item
        self.pathBox.setText(self.item.getFileName())
        self.numberLabel.setText(str(len(self.item.getAllInstances())))

    def handlePathChange(self, path):
        if self.item:
            self.item.setFileName(path)

    def reload(self):
        self.item.reload()

    def browse(self):
        error = self.item.browse()
        if error:
            self.parentWin.showMessage(msg=error, icon=QMessageBox.Critical)
        
    def select(self, add=False):
        self.item.select(add=add)
        
    def switchToHi(self):
        error = self.item.switchToHi()
        self.update()
        return error
    
    def switchToLow(self):
        error = self.item.switchToLow()
        self.update()
        return error
        
    def switch(self, refresh=True):
        '''switch to Proxy/GPU'''
        pass # to be implemented in child class
        
    def switchToHL(self):
        error = self.item.switchToHL()
        if error:
            self.parentWin.showMessage(msg=error,
                                       icon=QMessageBox.Critical)
            return
        self.update()
    
class ProxyItem(BaseItem):
    def __init__(self, parent, pItem):
        super(ProxyItem, self).__init__(parent, pItem)
        
        self.switchButton.setIcon(QIcon(osp.join(icon_path, 'G.png')))
        self.switchButton.setToolTip('Switch to GPU Cache')
        
    def delete(self):
        self.item.delete()
        self.parentWin.proxyItems.remove(self)
        self.deleteLater()
        
    def switch(self, refresh=True):
        self.item.switchToGPU()
        if refresh: self.parentWin.refresh()

class GPUItem(BaseItem):
    def __init__(self, parent, gpuItem):
        super(GPUItem, self).__init__(parent, gpuItem)

        self.switchButton.setIcon(QIcon(osp.join(icon_path, 'P.png')))
        self.switchButton.setToolTip('Switch to Proxy')
    
    def delete(self):
        self.item.delete()
        self.parentWin.gpuItems.remove(self)
        self.deleteLater()
        
    def switch(self, refresh=True):
        self.item.switchToProxy()
        if refresh: self.parentWin.refresh()