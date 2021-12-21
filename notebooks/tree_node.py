from operator import add
from os import path, setpgid
import io
import os
import re
import requests
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from collections.abc import Sequence
from uint import Uint, Int
from enum import Enum, IntEnum
import debugpy as debug
import warnings
from pprint import pprint
import abc

# @abc.ABC
class ITreeNode():
    def __init__(self, name:str) -> None:
        pass
    
    COUNT:list[int]

    @abc.abstractmethod
    def print2DUtil(root, space:int) -> str:
        pass

    def print2D(root) :
        pass

    def traverseInorder(self):
        pass

    def traversePostorder(self):
        pass

    def traversePreorder(self):
        pass
    
    def __repr__(self):
        return TreeNode.print2D(self)

    def __str__(self) -> str:
        return str([node.name for node in self.traverseInorder()])

    def __hash__(self) -> int:
        return hash(str(self))
    
    @abc.abstractmethod
    def addChild(self, node):
        pass

    @abc.abstractmethod
    def getDepth(self) -> int:
        pass

    @abc.abstractmethod
    def numberOfLayers():
        pass

    @abc.abstractmethod
    def getLeaves(self):
        pass

    @abc.abstractmethod
    def getChildren(self):
        pass

    @property
    @abc.abstractmethod
    def children():
        pass
        

# @abc.ABC
class ITreeChildNode(ITreeNode):
    # def __init__(self, parent) -> None:
    #     super().__init__()
    #     self._parent = parent
    
    @abc.abstractmethod
    def getParent(self):
        pass
    
    # @abc.abstractmethod
    # def setParent(self,parent:ITreeNode):
    #     pass

    @property
    @abc.abstractmethod
    def parent():
        pass

    @abc.abstractmethod
    def appendChild(self, node):
        pass

    @abc.abstractmethod
    def acceptParent(self, parentNode:ITreeNode) -> bool:
        pass

    
class TreeRootNode(ITreeChildNode):



    def __init__(self, name:str) -> None:
        super().__init__(name)
        self.name = name
        
        self._children = []

    # def getParent(self):
    #     return self._parent
    # # def setParent(self,parent):
    # #     self._parent = parent
    # parent = property(getParent)

    def getChildren(self):
        return self._children
    children = property(getChildren)

    def appendChild(self, node:ITreeChildNode):
        assert isinstance(node, ITreeChildNode), 'can only add TreeNode children'
        assert node.parent is None or node.parent == self, f'TreeNode: ({node.name}) can only have one parent. Already has parent with name: {node.parent.name}, so cant set self as parent with name: {self.name}'
        
        if node not in self._children:
            self._children.append(node)
            node.acceptParent(self)
        else:
            debug.breakpoint()
            print('warning')
        
        return self
    
    def appendChildren(self, addChilds:list):
        for c in addChilds:
            self.appendChild(c)

    def acceptParent(self, parentNode:ITreeChildNode) -> bool:
        if self in parentNode.children:
            self._parent  = parentNode
            return True
        return False




class TreeRootNodeBase(TreeRootNode):
    "Generic tree node."
    def __init__(self, name='root', data=None, children:list[ITreeChildNode]=None):
        super().__init__(name)
        if data is None:
            self.data = self.name
        else:
            self.data = data
        
        if children is not None:
            for child in children:
                self.appendChild(child)

    # def addChild(self, node:TreeChildNode):
    #     self.appendChild(node)


    COUNT = [8] # == 2 tabs

    # Function to print binary tree in 2D
    # It does reverse inorder traversal
    def print2DUtil(root, space:int) -> str:

        output = ''

        # Base case
        if (root == None):
            return ''

        # Increase distance between levels
        space += TreeNode.COUNT[0]

        # Get number of children to root
        n = 0
        if root.children:
            n = len(root.children)

        # print(f'Root {root.data} has {n} kids')
        # print(f'{n} kids -> {(n+1)/2.0} -> {(n+1)/2.0 - 1} -> {int((n+1)/2.0)}')
        # rightKids = ', '.join([str(k.data) for k in root.children[:int((n+1)/2.0):-1]])
        # print(f'Start printing right children from index: {int((n+1)/2.0)}: [{rightKids}]')
        
        # Process right children first
        for childRoot in root.children[:int((n+1)/2.0)-1:-1]:
            output += TreeNode.print2DUtil(childRoot, space)

        # Print current node after space
        # count
        output += '\n' # print()
        for i in range(TreeNode.COUNT[0], space):
            # print(end = " ") # end parameter tells it to append to end of current line rather than create a new line
            output += ' '
        output += f'{root.name}' # print(root.name)

        # Process left child
        for childRoot in root.children[int((n+1)/2.0)-1::-1]:
            output += TreeNode.print2DUtil(childRoot, space)

        return output

    # Wrapper over print2DUtil()
    def print2D(root) :
        
        # space=[0]
        # Pass initial space count as 0
        return TreeNode.print2DUtil(root, 0)

    # A function to do inorder tree traversal
    def traverseInorder(self):

        output:list[TreeNode] = []

        if self:

            # Get number of children to root
            n = 0
            if self.children:
                n = len(self.children)

            # First recur on left child
            for childRoot in self.children[int((n+1)/2.0)-1::-1]:
                output += childRoot.traverseInorder()

            # then print the name of node
            output += [self]

            # now recur on right child
            for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
                output += childRoot.traverseInorder()
            
        
        return output


    # A function to do postorder tree traversal
    def traversePostorder(self):

        output:list[TreeNode] = []

        if self:

            # Get number of children to self
            n = 0
            if self.children:
                n = len(self.children)

            # First recur on left child
            for childRoot in self.children[int((n+1)/2.0)-1::-1]:
                output += childRoot.traversePostorder()

            # the recur on right child
            for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
                output += childRoot.traversePostorder()

            # now print the data of node
            output += [self]

        return output

    # A function to do preorder tree traversal
    def traversePreorder(self):

        output:list[TreeNode] = []

        if self:

            # Get number of children to root
            n = 0
            if self.children:
                n = len(self.children)

            # First print the data of node
            output += [self]

            # Then recur on left child
            for childRoot in self.children[int((n+1)/2.0)-1::-1]:
                output += childRoot.traversePreorder()

            # Finally recur on right child
            for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
                output += childRoot.traversePreorder()

        return output
    
    def __repr__(self):
        return TreeNode.print2D(self)

    def __str__(self) -> str:
        return str([node.name for node in self.traverseInorder()])

    def __hash__(self) -> int:
        return hash(str(self))
    
    def getNumberLayers(self):
        return self.getDepth()

    def getDepth(self) -> int:
        if self.children:
            return max((c.getDepth() for c in self.children))+1
        else:
            return 1

    numberOfLayers = property(getNumberLayers)

    def getLeaves(self):
        _leaves = []
        if not self.children:
            return [self]
        return [x for c in self.children for x in c.getLeaves()]

class TreeChildNode(TreeRootNodeBase):
    def __init__(self, name:str) -> None:
        super().__init__()
        self.name = name
        self._parent = None
        self._children = []

    def getParent(self):
        return self._parent
    # def setParent(self,parent):
    #     self._parent = parent
    parent = property(getParent)

    def getSiblingsOfPathType(self):
        return [n for n in self.parent.childrenAsRankPairNodes if not n.data['isRegexNode']]

    def getNumSiblingsOfPathType(self):
        return len(self.getSiblingsOfPathType())

# class TreeNodeBase(TreeChildNode):
#     pass

class TreeNodeRoot(TreeRootNodeBase):
    def __init__(self, name='root'):
        super().__init__(name=name)
        self.data = {
            'regexNodesInTreeDescendency': 0,
            'isRegexNode':False,
            'pathFrequency': 1
        }

class TreeNode(TreeChildNode):
    def __init__(self, name='root', data=None):
        super().__init__(name=name)
        self.data = data
        if data is None:
            data = {}
        # assert parent is None or isinstance(parent, TreeNode), 'parent must be a TreeNode'
        # self._parent = parent
        # if parent is not None:
        #     parent.addChild(self)

    
   