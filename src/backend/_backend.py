'''
Created on Feb 25, 2016

@author: qurban.ali
'''

import pymel.core as pc
import os.path as osp
import iutil
import subprocess
import os

reload(iutil)

def switchHLPath(path):
    ext = osp.splitext(path)[-1]
    dirPath = osp.dirname(path)
    if 'low_res' in os.listdir(dirPath):
        dirPath = osp.join(dirPath, 'low_res')
    else:
        dirPath = osp.dirname(dirPath)
    files = os.listdir(dirPath)
    files = [phile for phile in files if phile.endswith(ext)]
    files = [osp.join(dirPath, phile) for phile in files]
    try:
        return iutil.getLatestFile(files)
    except: pass
        

def getProxyItems():
    errors = []
    items = []
    try:
        proxies = pc.ls(exactType=pc.nt.RedshiftProxyMesh)
        if proxies:
            for proxy in proxies:
                items.append(ProxyItem(proxy))
    except Exception as ex:
        errors.append(str(ex))
    return items, errors

def getGPUItems():
    errors = []
    items = []
    try:
        gpuCaches = pc.ls(exactType=pc.nt.GpuCache)
        if gpuCaches:
            for gpuCache in gpuCaches:
                items.append(GPUItem(gpuCache))
    except Exception as ex:
        errors.append(str(ex))
    return items, errors

class ProxyList(list):
    def __init__(self, parentWin=None):
        self.parentWin=parentWin
        
    def switchToHL(self):
        pass
    
    def switchToGPU(self):
        pass
    
    def select(self):
        pass
    
    def reload(self):
        pass

class GPUList(list):
    def __init__(self, parentWin=None):
        self.parentWin=parentWin
        
    def switchToHL(self):
        pass
    
    def switchToProxy(self):
        pass
    
    def select(self):
        pass
    
    def reload(self):
        pass
    
class BaseItem(object):
    def __init__(self, node=None):
        self.node = node

    def getFileName(self):
        pass

    def setFileName(self, name):
        pass

    def browse(self):
        path = self.getFileName()
        if path:
            if osp.exists(path):
                subprocess.call('explorer %s'%osp.normpath(osp.dirname(path)), shell=True)
                return
        return 'The system could not find the path specified'

    def switchToHL(self):
        path = switchHLPath(self.getFileName())
        if path:
            if osp.exists(path):
                self.setFileName(path)
                return
        return 'The system could not find the path specified\n%s'%path
    
    def setupTransformation(self):
        pass
        

class ProxyItem(BaseItem):
    def __init__(self, node=None):
        super(ProxyItem, self).__init__(node)
    
    def setFileName(self, name):
#         nodes = self.getAllInstances()
#         if nodes:
#             positions = {node: [node.t.get(), node.s.get(), node.r.get()] for node in nodes}
        self.node.fileName.set(name)
#         if nodes:
#             for node, pos in positions.items():
#                 node.t.set(pos[0])
#                 node.s.set(pos[1])
#                 node.r.set(pos[2])
    
    def getFileName(self):
        return self.node.fileName.get()
    
    def switchToGPU(self):
        pass
    
    def getAllInstances(self):
        for transform in self.node.outMesh.outputs():
            try:
                return transform.getShapes(ni=True)[0].listRelatives(ap=True)
            except:
                pass
    
    def select(self, add=False):
        nodes = self.getAllInstances()
        if nodes: pc.select(nodes, add=add)
    
    def reload(self):
        pass

class GPUItem(BaseItem):
    def __init__(self, node=None):
        super(GPUItem, self).__init__(node)
    
    def setFileName(self, name):
        self.node.cacheFileName.set(name)
        
    def getFileName(self):
        return self.node.cacheFileName.get()
    
    def switchToProxy(self):
        pass
    
    def select(self, add=False):
        pc.select(self.node.listRelatives(ap=True), add=add)
    
    def reload(self):
        pass