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

def switchHLPath(path, hi=False, low=False):
    ext = osp.splitext(path)[-1]
    dirPath = osp.dirname(path)
    if 'low_res' in os.listdir(dirPath):
        if hi:
            return path
        dirPath = osp.join(dirPath, 'low_res')
    else:
        if low:
            return path
        dirPath = osp.dirname(dirPath)
    try:
        return iutil.getLatestFile([osp.join(dirPath, phile) for phile in os.listdir(dirPath) if phile.endswith(ext)])
    except: pass

def getProxyItems():
    errors = []
    items = []
    try:
        proxies = pc.ls(exactType=pc.nt.RedshiftProxyMesh)
        if proxies:
            for proxy in proxies:
                try:
                    if proxy.outMesh.outputs()[0].visibility.get():
                        items.append(ProxyItem(proxy))
                except: pass
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
                try:
                    if gpuCache.firstParent().visibility.get():
                        items.append(GPUItem(gpuCache))
                except: pass
    except Exception as ex:
        errors.append(str(ex))
    return items, errors
    
class BaseItem(object):
    def __init__(self, node=None):
        self.node = node

    def getFileName(self):
        pass # to be implemented in child class

    def setFileName(self, name):
        pass # to be implemented in child class
    
    def getAllInstances(self):
        pass # to be implemented in child class
    
    def hasSelection(self):
        instances = self.getAllInstances()
        if len(set(pc.ls(sl=True)).intersection(set(instances))) > 0:
            return True
    
    def copyTransform(self, source, target):
        # Get the translation, rotation and scale in world space, of the source
        trans = pc.xform(source, worldSpace=True, q=True, translation=True)
        rot = pc.xform(source, worldSpace=True, q=True, rotation=True)
        scal = pc.xform(source, worldSpace=True, q=True, scale=True)

        # And apply to the target
        pc.xform(target, worldSpace=True, translation=trans)
        pc.xform(target, worldSpace=True, rotation=rot)
        pc.xform(target, worldSpace=True, scale=scal)

    def browse(self):
        path = self.getFileName()
        if path:
            if osp.exists(path):
                subprocess.call('explorer %s'%osp.normpath(osp.dirname(path)), shell=True)
                return
        return 'The system could not find the path specified'
    
    def switchToHi(self):
        path = switchHLPath(self.getFileName(), hi=True)
        if path:
            if osp.exists(path):
                self.setFileName(path)
                return
        return 'The system could not find the path specified\n%s'%path
    
    def switchToLow(self):
        path = switchHLPath(self.getFileName(), low=True)
        if path:
            if osp.exists(path):
                self.setFileName(path)
                return
        return 'The system could not find the path specified\n%s'%path

    def switchToHL(self):
        path = switchHLPath(self.getFileName())
        if path:
            if osp.exists(path):
                self.setFileName(path)
                return
        return 'The system could not find the path specified\n%s'%path
    
    def removeAttr(self):
        for node in self.getAllInstances():
            if node.hasAttr('swn'):
                if not node.swn.outputs() and not node.swn.inputs():
                    pc.deleteAttr(node.swn)
                    
    def reload(self):
        filename = self.getFileName()
        self.setFileName('')
        self.setFileName(filename)
        
    def delete(self):
        pc.delete(self.getAllInstances())
        pc.delete(self.node)

class ProxyItem(BaseItem):
    def __init__(self, node=None):
        super(ProxyItem, self).__init__(node)
    
    def setFileName(self, name):
        self.node.fileName.set(name)
    
    def getFileName(self):
        return self.node.fileName.get()
    
    def createGPUCacheNode(self, filePath):
        pc.select(cl=True)
        xformNode = pc.createNode('transform')
        pc.createNode('gpuCache', parent=xformNode).cacheFileName.set(filePath)
        pc.xform(xformNode, centerPivots=True)
        return xformNode
    
    def switchToGPU(self):
        self.removeAttr()
        nodes = self.getAllInstances()
        if nodes:
            gpuGroup = pc.ls('switchable_gpus')
            if not gpuGroup: gpuGroup = pc.group(em=True, n='switchable_gpus')
            else: gpuGroup = gpuGroup[0]
            gpuNode = None
            for node in nodes:
                if node.hasAttr('switchNode'):
                    try:
                        gpuNode = node.swn.inputs()[0]
                    except IndexError:
                        gpuNode = node.swn.outputs()[0]
                    gpuNode.visibility.set(1)
                    node.visibility.set(0)
                else:
                    if gpuNode:
                        gpuNode = pc.instance(gpuNode)[0]
                    else:
                        gpuNode = self.createGPUCacheNode(osp.splitext(self.getFileName())[0] +'.abc')
                    pc.parent(gpuNode, gpuGroup)
                    pc.addAttr(node, sn='swn', ln='switchNode', at='message', h=True)
                    if not gpuNode.hasAttr('switchNode'):
                        pc.addAttr(gpuNode, sn='swn', ln='switchNode', at='message', h=True)
                    node.swn.connect(gpuNode.swn)
                    node.visibility.set(0)
                self.copyTransform(node, gpuNode)
    
    def getAllInstances(self):
        for transform in self.node.outMesh.outputs():
            try:
                nodes = transform.getShapes(ni=True)[0].listRelatives(ap=True)
                tempNodes = []
                for node in nodes:
                    if not node.hasAttr('swn'):
                        tempNodes.append(node)
                for node in tempNodes:
                    nodes.remove(node)
                for node in tempNodes:
                    nodes.append(node)
                return nodes
            except:
                pass
    
    def select(self, add=False):
        nodes = self.getAllInstances()
        if nodes: pc.select(nodes, add=add)

class GPUItem(BaseItem):
    def __init__(self, node=None):
        super(GPUItem, self).__init__(node)
    
    def setFileName(self, name):
        self.node.cacheFileName.set(name)
        
    def getFileName(self):
        return self.node.cacheFileName.get()
    
    def createRedshiftProxyNode(self, filePath):
        pc.select(cl=True)
        node = pc.PyNode(pc.mel.redshiftCreateProxy()[0])
        node.useFrameExtension.set(0)
        node.fileName.set(filePath)
        return node.outMesh.outputs()[0]
    
    def switchToProxy(self):
        self.removeAttr()
        nodes = self.getAllInstances()
        if nodes:
            proxyGroup = pc.ls('switchable_proxies')
            if not proxyGroup: proxyGroup = pc.group(em=True, n='switchable_proxies')
            else: proxyGroup = proxyGroup[0]
            pNode = None
            for node in nodes:
                if node.hasAttr('switchNode'):
                    try:
                        pNode = node.swn.outputs()[0]
                    except IndexError:
                        pNode = node.swn.inputs()[0]
                    pNode.visibility.set(1)
                    node.visibility.set(0)
                else:
                    if pNode:
                        pNode = pc.instance(pNode)[0]
                    else:
                        pNode = self.createRedshiftProxyNode(osp.splitext(self.getFileName())[0] +'.rs')
                    pc.parent(pNode, proxyGroup)
                    pc.addAttr(node, sn='swn', ln='switchNode', at='message', h=True)
                    if not pNode.hasAttr('switchNode'):
                        pc.addAttr(pNode, sn='swn', ln='switchNode', at='message', h=True)
                    node.swn.connect(pNode.swn)
                    node.visibility.set(0)
                self.copyTransform(node, pNode)
                
    def getAllInstances(self):
        nodes = self.node.listRelatives(ap=True)
        tempNodes = []
        for node in nodes:
            if not node.hasAttr('swn'):
                tempNodes.append(node)
        for node in tempNodes:
            nodes.remove(node)
        for node in tempNodes:
            nodes.append(node)
        return nodes

    def select(self, add=False):
        pc.select(self.getAllInstances(), add=add)