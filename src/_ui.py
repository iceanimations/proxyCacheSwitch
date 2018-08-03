'''
Created on Jan 7, 2016

@author: qurban.ali
'''

from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog, QIcon, qApp
from PyQt4.QtCore import QSize
import qtify_maya_window as qtfy
import os.path as osp
import backend
import appUsageApp
import subprocess
import cui
import shutil

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
        self.selectionHLButton.hide()
        self.selectionPGButton.hide()
        self.selectionReloadButton.hide()
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
                          self.selectionDeleteButton: 'X.png',
                          self.selectionSeparateProxiesButton: 'S.png' }
        for btn, img in buttonsMapping.items():
            btn.setIcon(QIcon(osp.join(icon_path, img)))
            
        self.bbButton.setText('BB')
        self.pmButton.setText('PM')
        self.removeDuplicateProxyButton.setText('MD')
        
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
        self.selectionSeparateProxiesButton.clicked.connect(self.separate)
        self.refreshButton.clicked.connect(self.refresh)
        self.exportButton.clicked.connect(self.exportPaths)
        self.bbButton.clicked.connect(self.switchToBB)
        self.pmButton.clicked.connect(self.switchToPM)
        self.removeDuplicateProxyButton.clicked.connect(self.removeDuplicateProxies)
        self.exportProxiesButton.clicked.connect(self.exportProxies)
        self.loadProxiesButton.clicked.connect(self.loadProxies)
        
        self.populate()
        self.progressBar.hide()

        appUsageApp.updateDatabase('proxyCacheSwitch')
        
    def exportProxies(self):
        errors = {}
        path = QFileDialog.getExistingDirectory(self, __title__, '', QFileDialog.ShowDirsOnly)
        if path:
            if osp.exists(path):
                try:
                    pPaths = set()
                    for item in self.proxyItems:
                        pPaths.add(item.getFileName())
                    existingProxies = []
                    missingProxies = []
                    for pPath in pPaths:
                        if osp.exists(pPath):
                            existingProxies.append(pPath)
                        else:
                            missingProxies.append(pPath)
                    if missingProxies:
                        btn = self.showMessage(msg='Some proxy files do not exist\n\n' + '\n'.join(missingProxies),
                                               ques='Do you want to continue?',
                                               icon=QMessageBox.Question,
                                               btns=QMessageBox.Yes|QMessageBox.No)
                        if btn != QMessageBox.Yes:
                            return
                    self.progressBar.show()
                    self.progressBar.setMaximum(len(existingProxies))
                    self.progressBar.setMinimum(0)
                    self.progressBar.setValue(0)
                    count = 1
                    for pPath in existingProxies:
                        if not osp.exists(osp.join(path, osp.basename(pPath))):
                            shutil.copy2(pPath, path)
                        self.progressBar.setValue(count)
                        count += 1
                        qApp.processEvents()
                except Exception as ex:
                    self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
                finally:
                    self.progressBar.hide()
                    
                
    
    def loadProxies(self):
        files = QFileDialog.getOpenFileNames(self, __title__, '', '*.rs')
        if files:
            try:
                missingFiles = set()
                for pItem in self.proxyItems:
                    basename = osp.basename(pItem.getFileName())
                    for phile in files:
                        if basename.lower() == osp.basename(phile).lower():
                            pItem.setFileName(phile)
                            break
                    else:
                        missingFiles.add(pItem.getFileName())
                self.refresh()
                if missingFiles:
                    self.showMessage(msg='Could not find files matching the following paths\n\n' +
                                     '\n'.join(missingFiles))
            except Exception as ex:
                self.showMessage(msg=str(ex))
                
        
    def removeDuplicateProxies(self):
        try:
            backend.removeDuplicateProxies()
            self.populate()
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        
    def switchToBB(self):
        for pItem in self.proxyItems:
            pItem.switchToBB()
    
    def switchToPM(self):
        for pItem in self.proxyItems:
            pItem.switchToPM()
        
    def helpSort(self, path):
        if 'vegetation' in path.lower(): return 0
        else: return 1
        
    def exportPaths(self):
        try:
            filename = QFileDialog.getSaveFileName(self, 'Save File', '', '*.txt')
            if filename:
                pPaths = set()
                for item in self.proxyItems:
                    pPaths.add(item.getFileName())
                gPaths = set()
                for item in self.gpuItems:
                    gPaths.add(item.getFileName())
                with open(filename, 'w') as f:
                    if pPaths:
                        f.write('PROXIES'+'\r\n'*2+ '\r\n'.join(sorted(pPaths, key=self.helpSort)))
                    if gPaths:
                        f.write('\r\n'*3+'GPU CACHE'+'\r\n'*2+ '\r\n'.join(sorted(gPaths, key=self.helpSort)))
                if osp.exists(filename):
                    subprocess.Popen('notepad %s'%osp.normpath(filename))
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
            
        
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
        try:
            backend.tearSelection()
            self.populate()
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)

    def separate(self):
        try:
            backend.separateProxies()
            self.populate()
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
    
    def getItemFromSelection(self):
        '''returns GPUItem/ProxyItem from selected object in the scene'''
        item = None
        for pItem in self.proxyItems:
            if pItem.hasSelection():
                item = pItem
                break
        for gpuItem in self.gpuItems:
            if gpuItem.hasSelection():
                item = gpuItem
                break
        return item
        
    def focusSelection(self):
        item = self.getItemFromSelection()
        if item:
            item.highlight()
            item.parentWidget().parentWidget().parentWidget().ensureWidgetVisible(item)
        else:
            self.showMessage(msg='No UI Item found for the selected object',
                             icon=QMessageBox.Information)
        
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
        
    def getFileName(self):
        return self.item.getFileName()
    
    def setFileName(self, filename):
        self.item.setFileName(filename)
        
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
            
    def hasSelection(self):
        return self.item.hasSelection()
    
    def highlight(self):
        self.pathBox.setFocus()

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
        self.bbButton.setText('BB')
        self.pmButton.setText('PM')
        
        self.bbButton.clicked.connect(self.switchToBB)
        self.pmButton.clicked.connect(self.switchToPM)
        
    def delete(self):
        self.item.delete()
        self.parentWin.proxyItems.remove(self)
        self.deleteLater()
        
    def switchToBB(self):
        self.item.switchToBB()
        
    def switchToPM(self):
        self.item.switchToPM()
        
    def switch(self, refresh=True):
        self.item.switchToGPU()
        if refresh: self.parentWin.refresh()

class GPUItem(BaseItem):
    def __init__(self, parent, gpuItem):
        super(GPUItem, self).__init__(parent, gpuItem)
        
        self.bbButton.hide()
        self.pmButton.hide()

        self.switchButton.setIcon(QIcon(osp.join(icon_path, 'P.png')))
        self.switchButton.setToolTip('Switch to Proxy')
    
    def delete(self):
        self.item.delete()
        self.parentWin.gpuItems.remove(self)
        self.deleteLater()
        
    def switch(self, refresh=True):
        self.item.switchToProxy()
        if refresh: self.parentWin.refresh()
