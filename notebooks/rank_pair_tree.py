from __future__ import annotations
from operator import countOf
from os import path
import io
import os
import re
from typing import Tuple, overload
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
from tree_node import ITreeNode
import abc


from tree_node import TreeNode, TreeNodeRoot, TreeRootNodeBase
from url_parser import ParsedUrlParser




class RankPair():
    def __init__(self, pathFrequencyCounter: Uint, numberRegexNodes: Uint, isRegexNode: bool) -> None:
        self._pathFrequencyCounter: Uint = pathFrequencyCounter
        self._numberRegexNodes: Uint = numberRegexNodes
        self._isRegexNode: bool = isRegexNode

    def getPathFreq(self):
        return self._pathFrequencyCounter

    def incrementPathFreq(self):
        self._pathFrequencyCounter += 1

    def getIsRegexNode(self):
        return self._pathFrequencyCounter

    def getNumRegexNodes(self):
        return self._isRegexNode

    pathFrequencyCounter:Uint = property(getPathFreq)

    isRegexNode:bool = property(getIsRegexNode)

    numberRegexNodes:Uint = property(getNumRegexNodes)

class IRankPairTreeRootNode(ITreeNode):
    @property
    @abc.abstractmethod
    def childrenAsRankPairNodes(self):
        pass

    @abc.abstractmethod
    def getChildrenOfPathType(self):
        pass

class IRankPairTreeNode(IRankPairTreeRootNode):
    @property
    @abc.abstractmethod
    def parentAsRankPairNode(self):
        pass

    @abc.abstractmethod
    def getNumSiblingsOfPathType(self):
        pass

class RankPairTreeNodeSortable(TreeRootNodeBase):

    def getChildren(self):
        return super().getChildren()
    childrenAsRankPairNodes:list[IRankPairTreeRootNode] = property(getChildren)

    def sortChildren(self, sortPathsAlphabetically:bool=False):
        '''Ensure the regex child is furthest right'''
        if not self.children:
            return
        # for ind,cNode in enumerate(self.childrenAsRankPairNodes):
        #     if cNode.data['isRegexNode'] == True:
        if sortPathsAlphabetically:
            self._children.sort(key=lambda c: c.name)
        self._children.sort(key=lambda c: c.data['isRegexNode'])

    def traversePreorder(self):
        result: list[RankPairTreeNode] = super().traversePreorder()
        return result

    def traverseInorder(self):
        result: list[RankPairTreeNode] = super().traverseInorder()
        return result
                
    def traversePostorder(self):
        result: list[RankPairTreeNode] = super().traversePostorder()
        return result



class RankPairTreeNode(TreeNode, RankPairTreeNodeSortable):
    def __init__(self, name='root'):
        # assert isinstance(data, RankPair) or data is None
        super().__init__(name=name)
        # self.dataAsRankPair: RankPair = data
        
        
    # def getChildren(self):
    #     return super().getChildren()
    # childrenAsRankPairNodes:list[IRankPairTreeNode] = property(getChildren)

    def getParent(self) -> RankPairTreeRootNode:
        return super().getParent()
        
    parentAsRankPairNode:RankPairTreeRootNode = property(getParent)
    
    def getChildren(self:type[RankPairTreeRootNode]):
        return super().getChildren()
    
    children:list[RankPairTreeNode] = property(getChildren)

    def withChildrenState(state:RankPairTreeNode) -> RankPairTreeNode:
        instance = RankPairTreeNode(name=state.name)
        instance.data = state.data
        for child in state.children:
            instance.appendChild(RankPairTreeNode.withChildrenState(child.children))
        return instance
        # instance._children = state._children 

    # def sortChildren(self, sortPathsAlphabetically:bool=False):
    #     '''Ensure the regex child is furthest right'''
    #     if not self.children:
    #         return
    #     # for ind,cNode in enumerate(self.childrenAsRankPairNodes):
    #     #     if cNode.data['isRegexNode'] == True:
    #     self._children.sort(key=lambda c: c.data['isRegexNode'])


    # def traversePreorder(self):
    #     result: list[RankPairTreeNode] = super().traversePreorder()
    #     return result

    # def traverseInorder(self):
    #     result: list[RankPairTreeNode] = super().traverseInorder()
    #     return result
                
    # def traversePostorder(self):
    #     result: list[RankPairTreeNode] = super().traversePostorder()
    #     return result
                

class RankPairTreeRootNode(TreeNodeRoot, RankPairTreeNodeSortable):
    def __init__(self, name='root'):
        # assert isinstance(data, RankPair) or data is None
        super().__init__(name=name)
        # self.dataAsRankPair: RankPair = data
    def getChildren(self:type[RankPairTreeRootNode]):
        return super().getChildren()
    # childrenAsRankPairNodes:list[IRankPairTreeRootNode] = property(getChildren)
    children:list[RankPairTreeNode] = property(getChildren)       

    def withChildrenState(state) -> RankPairTreeRootNode:
        instance = RankPairTreeRootNode(name=state.name)
        instance.data = state.data
        for child in state.children:
            instance.appendChild(RankPairTreeNode.withChildrenState(child.children))
        return instance


class RankPairTreeRegexNode(RankPairTreeNode):
    def __init__(self, name='root'):
        super().__init__(name=name)
        self.data = {'isRegexNode': True}

class RankPairTreePathNode(RankPairTreeNode):
    def __init__(self, sisterRegexNode:RankPairTreeRegexNode, name='root'):
        super().__init__(name=name)
        self.sisterRegexNode = sisterRegexNode
        self.data = {'isRegexNode': False}

    def filterPathNodesFromTreeNodes(nodes:list[RankPairTreeNode]):
        result:list[RankPairTreePathNode] = [n for n in nodes if not n.data['isRegexNode']]
        return result
    


class RankPairTree(object):

    def __init__(self, url:str=None):
        # super.__init__(self)
        self._urlParser:ParsedUrlParser = None
        self._treeState:RankPairTreeRootNode = None
        self.initialised:bool = False
        if url is not None:
            self.embedUrl(url)
            self.initialised = True
        
    def fromState(treeState:RankPairTreeRootNode) -> RankPairTree:
        instance = RankPairTree()
        instance._treeState = treeState
        instance.initialised = (treeState.name is not None)
        return instance

    def copyDeep(self) -> RankPairTree:
        return RankPairTree.fromState(self._treeState)


    def embedUrl(self, url:str):
        return self._processUrl(url, embed=True)[0]

    def containsGeneralisationOf(self, url:str):
        return self._processUrl(url, embed=False)[1] if self.initialised else False

    def _processUrl(self, url:str, embed:bool) -> Tuple[RankPairTree,bool]:
        '''If embed, bake url into self and return self, else bake url into a copy of self and return the copy.'''
        instance:RankPairTree=None
        containsGeneralisationOfUrl:bool = False
        if embed:
            # _treeState:RankPairTreeRootNode = self._treeState
            instance = self
            assert self.__hash__() == instance.__hash__()
        else:
            # _treeState:RankPairTreeRootNode=RankPairTreeNode.withChildrenState(self._treeState)
            if self.initialised:
                instance = self.copyDeep()
            else:
                instance = RankPairTree(url)
        
        _urlParser = ParsedUrlParser(url)
        _urlParser.parseUrl()
        
        self._urlParser = _urlParser
        instance._urlParser = _urlParser

        assert self._urlParser.__hash__() == instance._urlParser.__hash__()

        if instance._treeState is None:
            instance._treeState = RankPairTreeRootNode(
                name=instance._urlParser.parsedUrl.domain
                )
        elif instance._treeState.name != instance._urlParser.parsedUrl.domain:
            instance._treeState = RankPairTreeRootNode(
                name=RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME,
                children=[
                    RankPairTreeNode.withChildrenState(instance._treeState) if embed else instance._treeState,
                    RankPairTreeNode(instance._urlParser.parsedUrl.domain)
                ])
        
        nodeToAddTo = instance.getDomainNode()

        def _f(p:str,regx:str, nodesToAddTo:list[RankPairTreeNode]) -> Tuple[list[RankPairTreeNode],bool]:
            '''We are only adding text and regex nodes on all leaves when it is a new domain tree.\n
            Otherwise we only add paths and potentially regex when the tree does NOT already contain them.'''
            
            
            # Case 1
            # get child nodes if domain has already been embedded with other url(s)
            childNodesToAddTo = [childNode for nodeToAddTo in nodesToAddTo for childNode in nodeToAddTo.childrenAsRankPairNodes]
            pathNodes = RankPairTreePathNode.filterPathNodesFromTreeNodes(childNodesToAddTo)
            matchingPathLeaves = [x for n in pathNodes if n.name == p for x in [n,n.sisterRegexNode]]
            if matchingPathLeaves:
                existingNodesContainingUrlPath = matchingPathLeaves
                return (existingNodesContainingUrlPath, True)
            
            # Case 2
            # get child nodes if domain has already been embedded with other url(s)
            childNodesToAddTo = [childNode for nodeToAddTo in nodesToAddTo for childNode in nodeToAddTo.childrenAsRankPairNodes]
            reNodes = [lrg for lrg in childNodesToAddTo if lrg.data['isRegexNode'] and re.match(lrg.name, p)]
            if reNodes:
                newNodes:list[RankPairTreeNode] = []
                for rgxNode in reNodes:
                    # add new path node to rgxLeaf.parent
                    pathnode = RankPairTreePathNode(sisterRegexNode=rgxNode, name=p) #link the path node to regexLeaf
                    rgxNode.parent.appendChild(pathnode) 
                    # rgxNode.dataAsRankPair.incrementPathFreq()
                    newNodes.append(pathnode)
                    newNodes.append(rgxNode)
                return (newNodes, True)
            
            # Case 3
            newNodes:list[RankPairTreeNode] = []
            for nodeToAddTo in nodesToAddTo:
                parentNode = nodeToAddTo
                pathRegexNode = RankPairTreeRegexNode(name=(RankPairTree._getSubRePattern(p) or regx))
                pathTextNode = RankPairTreePathNode(sisterRegexNode=pathRegexNode, name=p)
                (parentNode
                .appendChild(pathTextNode)
                .appendChild(pathRegexNode))
                newNodes += [pathTextNode, pathRegexNode]
            return (newNodes, False)

        nodesToAddTo = [nodeToAddTo]
        pathMatchedGeneralisation = True
        for trgx in instance._urlParser.parsedUrl.paths:
            p,regx = (trgx.text, trgx.regexPatrn)
            nodesToAddTo, pathMatchedGeneralisation = _f(p, regx, nodesToAddTo)
        containsGeneralisationOfUrl = pathMatchedGeneralisation
            

        for (qk_trgx, qv_trgx) in instance._urlParser.parsedUrl.queries:
            (qk, qkRgx),(qv, qvRgx) = (qk_trgx.text, qk_trgx.regexPatrn), (qv_trgx.text, qv_trgx.regexPatrn)
            nodesToAddTo,pathQueryMatchedGeneralisation = _f(qk, qkRgx, nodesToAddTo)
            if qv:
                nodesToAddTo,pathQueryMatchedGeneralisation = _f(qv, qvRgx, nodesToAddTo)

        if not instance.initialised:
            instance.initialised = True

        if embed:
            assert self.__hash__() == instance.__hash__()
        
        return (instance, containsGeneralisationOfUrl)

    def sortTree(self, sortPathsAlphabetically:bool=False):
        allNodes = self._treeState.traversePreorder()
        for node in allNodes:
            if node.children:
                node.sortChildren()

    def getTreeRank(self):
        allNodes = self._treeState.traversePreorder()
        # leafRanks = []
        maxRank = {
            'isRegexNode':False,
            'pathFrequency': 0, 
            'regexNodesInTreeDescendency': 0
            }
        
        for ind, node in enumerate(allNodes):
            # Calculate the rank pair for each node, traverseInOrder guarantees that the parent is calculated first. Set on the data attribute not removing whats already there.
            if node.data['isRegexNode'] != True:
                pathFrequency = 1 #as not a regex generalisation so can only refer to one path
                if isinstance(node, RankPairTreeRootNode):
                    regexNodesInTreeDescendency = 0 
                elif isinstance(node, RankPairTreeNode):
                    regexNodesInTreeDescendency = node.parent.data['regexNodesInTreeDescendency']
                else:
                    regexNodesInTreeDescendency = 0
            else:
                pathFrequency = node.getNumSiblingsOfPathType()
                assert isinstance(node, RankPairTreeNode), f'Regex Nodes must be of type {RankPairTreeNode.__name__}, not {type(node)}'
                regexNodesInTreeDescendency = node.parent.data['regexNodesInTreeDescendency'] + 1
            node.data = {
                **node.data, 
                **{
                    'pathFrequency': pathFrequency, 
                    'regexNodesInTreeDescendency': regexNodesInTreeDescendency
                }
            }

            # If node is a leaf, i.e. no children, then record the rankpair result in an array
            if not node.children:
                # leafRanks.append(node.data)

                if node.data['pathFrequency'] > maxRank['pathFrequency']:
                    maxRank = node.data
                elif node.data['pathFrequency'] == maxRank['pathFrequency'] and node.data['regexNodesInTreeDescendency'] < maxRank['regexNodesInTreeDescendency']:
                    maxRank = node.data
        

            
            
        # Return the max rank pair       
        return maxRank

    TreeRank = property(getTreeRank)

    def _getData(self):
        return self._treeState.data
    
    data = property(_getData)

    def __repr__(self) -> str:
        return self._treeState.__repr__()
    
    def __str__(self) -> str:
        return self._treeState.__str__()

    # def __hash__(self) -> int:
    #     return self._treeState.__hash__()
    
    def getChildren(self):
        return self._treeState.children

    children: list[RankPairTreeNode] = property(getChildren)

    # def getRankPairForRegexChildNode(self) -> RankPair:
    #     return RankPair(pathFrequencyCounter=self._treeState.getNumSiblingsOfPathType(), 
    #                     numberRegexNodes=self._treeState.dataAsRankPair.numberRegexNodes + 1,
    #                     isRegexNode=True)

    # def getRankPairForTextChildNode(self) -> RankPair:
    #     return RankPair(pathFrequencyCounter=self._treeState.getNumSiblingsOfPathType(), 
    #                     numberRegexNodes=self._treeState.dataAsRankPair.numberRegexNodes,
    #                     isRegexNode=True)


    def appendChild(self, node:RankPairTreeNode):
        # node.data = RankPair(pathFrequencyCounter=node.data.path)
        self._treeState.appendChild(node)
        return self
    
    def getDomainNode(self):
        domain = self._urlParser.parsedUrl.domain
        if self._treeState.name == domain:
            return self._treeState
        elif self._treeState.name == RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME:
            domainNode = [n for n in self._treeState.children if n.name == domain]
            if domainNode:
                return domainNode[0]
        else:
            return None

    def getLeaves(self) -> list[RankPairTreeNode]:
        domain = self._urlParser.parsedUrl.domain
        if self._treeState.name == domain:
            return self._treeState.getLeaves()
        elif self._treeState.name == RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME:
            domainNode = [n for n in self._treeState.children if n.name == domain]
            if domainNode:
                return domainNode[0].getLeaves()
        else:
            return []

    def getLeavesByRegx(self) -> list[RankPairTreeNode]:
        return self.getLeaves()    
    
    def getDepth(self):
        return self._treeState.numberOfLayers
    
    depth = property(getDepth)

    TREE_ROOT_DEFAULT_NAME = 'root'

    TREE_ROOT_MULTI_DOMAIN_NAME = 'MULTI_DOMAIN'

    def _getSubRePattern(testStr:str) -> str:
        '''
        decreasing order of specificity rules: ['[0-9]', '[A-Z]', '[A-Za-z]', '[0-9A-Za-z]', r'[0-9A-Za-z\-]', r'[^\/]', '', '', '', ]
        
        to match: ['forum', 'p', 'sid', '0193Q']
        '''
        tryPatternsDecreasingSpecificity = [
            '^[0-9]+$',
            '^[A-Z]+$',
            '^[A-Za-z]+$',
            '^[0-9A-Za-z]+$',
            r'^[0-9A-Za-z\-]+$',
            r'^[^\/]+$',
            r'^[^=]+$',
        ]

        for pattern in tryPatternsDecreasingSpecificity:
            if re.match(pattern, testStr):
                return pattern
        else:
            return None
    

def test_rankTree_builds_correct_layers():
    
    _testUrl = 'https://acme.com/forum?sid=QZ932'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    print(rankTree.TreeRank)
    assert rankTree.depth == 4, f'RankTree should have 4 layers for url: {_testUrl}, not {rankTree.depth}'
    assert rankTree.data['pathFrequency'] == 1 and rankTree.data['regexNodesInTreeDescendency'] == 0 

def test_rankTree_builds_correct_layers_complex():
    
    _testUrl = 'https://groceries.asda.com/product/natural-plain-organic/fage-total-fat-free-greek-recipe-natural-yogurt/24771357?sid=12534Q&style=green'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    print(rankTree.TreeRank)

def test_rankTree_2_urls():
    
    _testUrl = 'https://acme.com/forum?sid=QZ932'
    rankTree = RankPairTree(_testUrl)
    _testUrl2 = 'https://acme.com/forum?sid=QZ933'
    rankTree.embedUrl(_testUrl2)
    treeRank = rankTree.TreeRank
    assert treeRank['isRegexNode'] == True, 'treeRank[\'isRegexNode\'] should be True'
    assert treeRank['pathFrequency'] == 2, 'treeRank[\'pathFrequency\'] should be 2'
    assert treeRank['regexNodesInTreeDescendency'] == 1, 'treeRank[\'regexNodesInTreeDescendency\'] should be 1'
    rankTree.sortTree()
    pprint(rankTree)

if __name__ == '__main__':
    test_rankTree_2_urls()
    
    