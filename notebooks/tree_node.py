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
class ITreeNode(abc.ABC):
    def __init__(self, name:str) -> None:
        self.data = None
        self.name = name
    
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
    def appendChild(self, node):
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
    def getChildren(self) -> list:
        pass

    @property
    @abc.abstractmethod
    def children() -> list:
        pass

    @abc.abstractmethod
    def rightChildren() -> list:
        pass

    @abc.abstractmethod
    def leftChildren() -> list:
        pass


        

# @abc.ABC
class ITreeChildNode(ITreeNode):
    @abc.abstractmethod
    def acceptParent(self, parentNode:ITreeNode) -> bool:
        pass

class TreePrintable(ITreeNode):

    #TODO: Add tests for Ancestory functions.
    def ancestorAtLevel(self, level:Uint) -> ITreeNode:
        '''Root is level 1'''
        level = max(1,level)
        ancestry = self.ancestry()
        
        if level > len(ancestry):
            return self
        return ancestry[level-1]

    def ancestorGenerationsBefore(self, generationsAgo:Uint) -> ITreeNode:
        generationsAgo = max(0,generationsAgo)
        ancestor = self
        for i in range(0,generationsAgo):
            if hasattr(ancestor, 'parent'):
                ancestor = getattr(ancestor, 'parent')
            else:
                # hit root
                return ancestor
        return ancestor

    def ancestry(self):
        ancestor = self
        ancestry:list[TreePrintable] = []
        i = 0
        while i <= 99 and hasattr(ancestor, 'parent'):
            i += 1
            ancestry = [ancestor] + ancestry
            ancestor = getattr(ancestor, 'parent')
        return ancestry

    def rightChildren(self) -> list:
        # Get number of children to root
        n = 0
        if self.children:
            n = len(self.children)
        return self.children[:int((n+1)/2.0)-1]

    def leftChildren(self) -> list:
        # Get number of children to root
        n = 0
        if self.children:
            n = len(self.children)
        return self.children[int((n+1)/2.0)-1:]
        


    def isRightOf(self,ancestor:ITreeNode):
        ancestry = self.ancestry()
        assert ancestor != self, 'ancestor cant be self'
        assert ancestor in ancestry, f'ancestor passed: {ancestor.name} must be in ancestry of self: {self.name}'
        childToAncestorInAncestry = next(anc for anc in ancestor.children if anc in ancestry)
        return childToAncestorInAncestry in self.rightChildren()

    def isLeftOf(self,ancestor:ITreeNode):
        return not self.isRightOf(ancestor)


    PRINT_SPACE_COUNT = [8] # == 2 tabs
    PRINT_HYPHEN_COUNT = int(PRINT_SPACE_COUNT[0]/2)
    # Function to print binary tree in 2D
    # It does reverse inorder traversal
    def print2DUtil(root, space:int) -> str:

        output = ''

        # Base case
        if (root == None):
            return ''

        # Increase distance between levels
        space += TreeRootNodeBase.PRINT_SPACE_COUNT[0]

        # Get number of children to root
        n = 0
        if root.children:
            n = len(root.children)

        # print(f'Root {root.data} has {n} kids')
        # print(f'{n} kids -> {(n+1)/2.0} -> {(n+1)/2.0 - 1} -> {int((n+1)/2.0)}')
        # rightKids = ', '.join([str(k.data) for k in root.children[:int((n+1)/2.0):-1]])
        # print(f'Start printing right children from index: {int((n+1)/2.0)}: [{rightKids}]')
        
        # Process right children: First view tree:
        #        --- ChildRight
        #       |
        # Root -
        #       |
        #        --- ChildLeft
        #      2 456 8     ---
        #     1     7      \s\s\s 
        #       3          ||| 
        # 12345678-2345678--345678
        #         
        # Process right children first (To be printed in lines above root, as print flips tree to left):
        rightChildren = root.rightChildren()[::-1]
        for childRoot in rightChildren:
            output += TreeNode.print2DUtil(childRoot, space)

        # Print current node after space
        # count
        output += '\n' # print()
        #Calculate the length of the space
        longSpace = ''
        for i in range(TreeNode.PRINT_SPACE_COUNT[0], space):
            # print(end = " ") # end parameter tells it to append to end of current line rather than create a new line
            longSpace += ' '
#           longSpace += '-'
        
        # remove last few spaces and replace with hyphens
        if len(longSpace) >= (TreePrintable.PRINT_HYPHEN_COUNT*2):
            longSpace = longSpace[:-1*TreePrintable.PRINT_HYPHEN_COUNT] + ('-'*TreePrintable.PRINT_HYPHEN_COUNT)
        
        # add line spacer edges '|' where parent nodes have further right siblings.
        def _addSpacers(longSpace, ancestry):
            for i,char in enumerate(range(TreePrintable.PRINT_HYPHEN_COUNT, len(longSpace), TreePrintable.PRINT_SPACE_COUNT)):
                # First check for 
                _parentNodeAtLvl = ancestry[i] # root.ancestorAtLevel(1) is root node
                _parentsChildNodeAtLvl = ancestry[i+1] # Should be guaranteed this index by only enumerating the length of longSpace
                
                # Check if parentsChildNode is not the furthest right sibling:
                if not _parentsChildNodeAtLvl.isLeftMostSibling():
                    longSpace[char] = '|'

                if -1 < _parentNodeAtLvl.children.index(_parentsChildNodeAtLvl) and _parentNodeAtLvl.children.index(_parentsChildNodeAtLvl) < len(_parentNodeAtLvl.children):
                    # Not furthest right child, add '|'.
                    longSpace[char] = '|'
            return longSpace
        
        ancestry = root.ancestry()
        longSpace = _addSpacers(longSpace, ancestry)
            

        output += longSpace
        
        # add the tree node label
        output += f'{root.name}' # print(root.name)
        
        # append to short tree labels
        output += ('-'*max(TreePrintable.PRINT_HYPHEN_COUNT-len(f'{root.name}'),0)) + ('|' if len(f'{root.name}') <= TreePrintable.PRINT_HYPHEN_COUNT else '')
        output += '\n'
        longSpace = _addSpacers(longSpace, ancestry)
        output += re.sub(r'-{'+str(TreePrintable.PRINT_HYPHEN_COUNT-1)+r'}$', '', longSpace, count=1)

        # Process left child
        leftChildren = root.leftChildren()[::-1]
        for childRoot in leftChildren:
            output += TreeNode.print2DUtil(childRoot, space)

        return output

    # Wrapper over print2DUtil()
    def print2D(root) :
        
        # space=[0]
        # Pass initial space count as 0
        return TreeNode.print2DUtil(root, 0)

class TreeTraversable(ITreeNode):

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




class TreeRootNodeBase(TreeRootNode, TreePrintable, TreeTraversable):
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


    # PRINT_SPACE_COUNT = [8] # == 2 tabs

    # # Function to print binary tree in 2D
    # # It does reverse inorder traversal
    # def print2DUtil(root, space:int) -> str:

    #     output = ''

    #     # Base case
    #     if (root == None):
    #         return ''

    #     # Increase distance between levels
    #     space += TreeRootNodeBase.PRINT_SPACE_COUNT[0]

    #     # Get number of children to root
    #     n = 0
    #     if root.children:
    #         n = len(root.children)

    #     # print(f'Root {root.data} has {n} kids')
    #     # print(f'{n} kids -> {(n+1)/2.0} -> {(n+1)/2.0 - 1} -> {int((n+1)/2.0)}')
    #     # rightKids = ', '.join([str(k.data) for k in root.children[:int((n+1)/2.0):-1]])
    #     # print(f'Start printing right children from index: {int((n+1)/2.0)}: [{rightKids}]')
        
    #     # Process right children first
    #     for childRoot in root.children[:int((n+1)/2.0)-1:-1]:
    #         output += TreeNode.print2DUtil(childRoot, space)

    #     # Print current node after space
    #     # count
    #     output += '\n' # print()
    #     for i in range(TreeNode.PRINT_SPACE_COUNT[0], space):
    #         # print(end = " ") # end parameter tells it to append to end of current line rather than create a new line
    #         output += ' '
    #     output += f'{root.name}' # print(root.name)

    #     # Process left child
    #     for childRoot in root.children[int((n+1)/2.0)-1::-1]:
    #         output += TreeNode.print2DUtil(childRoot, space)

    #     return output

    # # Wrapper over print2DUtil()
    # def print2D(root) :
        
    #     # space=[0]
    #     # Pass initial space count as 0
    #     return TreeNode.print2DUtil(root, 0)

    # # A function to do inorder tree traversal
    # def traverseInorder(self):

    #     output:list[TreeNode] = []

    #     if self:

    #         # Get number of children to root
    #         n = 0
    #         if self.children:
    #             n = len(self.children)

    #         # First recur on left child
    #         for childRoot in self.children[int((n+1)/2.0)-1::-1]:
    #             output += childRoot.traverseInorder()

    #         # then print the name of node
    #         output += [self]

    #         # now recur on right child
    #         for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
    #             output += childRoot.traverseInorder()
            
        
    #     return output


    # # A function to do postorder tree traversal
    # def traversePostorder(self):

    #     output:list[TreeNode] = []

    #     if self:

    #         # Get number of children to self
    #         n = 0
    #         if self.children:
    #             n = len(self.children)

    #         # First recur on left child
    #         for childRoot in self.children[int((n+1)/2.0)-1::-1]:
    #             output += childRoot.traversePostorder()

    #         # the recur on right child
    #         for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
    #             output += childRoot.traversePostorder()

    #         # now print the data of node
    #         output += [self]

    #     return output

    # # A function to do preorder tree traversal
    # def traversePreorder(self):

    #     output:list[TreeNode] = []

    #     if self:

    #         # Get number of children to root
    #         n = 0
    #         if self.children:
    #             n = len(self.children)

    #         # First print the data of node
    #         output += [self]

    #         # Then recur on left child
    #         for childRoot in self.children[int((n+1)/2.0)-1::-1]:
    #             output += childRoot.traversePreorder()

    #         # Finally recur on right child
    #         for childRoot in self.children[:int((n+1)/2.0)-1:-1]:
    #             output += childRoot.traversePreorder()

    #     return output
    
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

    
   