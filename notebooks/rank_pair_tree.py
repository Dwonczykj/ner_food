from operator import countOf
from os import path
import io
import os
import re
from typing import overload
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

from tree_node import TreeNode, TreeNodeRoot
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


class RankPairTreeRootNode(TreeNodeRoot):
    def __init__(self, name='root'):
        # assert isinstance(data, RankPair) or data is None
        super().__init__(name=name)
        # self.dataAsRankPair: RankPair = data
    def getChildren(self):
        return super().getChildren()
    childrenAsRankPairNodes:list[IRankPairTreeRootNode] = property(getChildren)
        

    def getChildrenOfPathType(self):
        return [n for n in self.childrenAsRankPairNodes if not n.data['isRegexNode']]


class RankPairTreeNode(TreeNode):
    def __init__(self, name='root'):
        # assert isinstance(data, RankPair) or data is None
        super().__init__(name=name)
        # self.dataAsRankPair: RankPair = data
        
        
    def getChildren(self):
        return super().getChildren()
    childrenAsRankPairNodes:list[IRankPairTreeNode] = property(getChildren)

    def getParent(self):
        x:RankPairTreeNode = super().getParent()
        return x
    parentAsRankPairNode:list[IRankPairTreeNode] = property(getParent)

    def withChildrenState(state:TreeNode):
        instance = RankPairTreeNode(name=state.name)
        instance.data = state.data
        #TODO: FIX this
        instance._children = state._children 


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

    def __init__(self, url:str):
        # super.__init__(self)
        self._urlParser = None
        self._treeState = None
        self.embedUrl(url)

    def embedUrl(self, url:str):
        self._urlParser = ParsedUrlParser(url)
        self._urlParser.parseUrl()
        
        if self._treeState is None:
            self._treeState = RankPairTreeRootNode(
                name=self._urlParser.parsedUrl.domain
                )
        elif self._treeState.name != self._urlParser.parsedUrl.domain:
            self._treeState = RankPairTreeRootNode(
                name=RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME,
                children=[
                    RankPairTreeNode.withChildrenState(self._treeState),
                    RankPairTreeNode(self._urlParser.parsedUrl.domain)
                ])
        
        nodeToAddTo = self.getDomainNode()

        def _f(p:str,regx:str, nodesToAddTo:list[RankPairTreeNode]):
            '''We are only adding text and regex nodes on all leaves when it is a new domain tree.\n
            Otherwise we only add paths and potentially regex when the tree does NOT already contain them.'''
            
            
            # Case 1
            # get child nodes if domain has already been embedded with other url(s)
            childNodesToAddTo = [childNode for nodeToAddTo in nodesToAddTo for childNode in nodeToAddTo.childrenAsRankPairNodes]
            pathNodes = RankPairTreePathNode.filterPathNodesFromTreeNodes(childNodesToAddTo)
            matchingPathLeaves = [x for n in pathNodes if n.name == p for x in [n,n.sisterRegexNode]]
            if matchingPathLeaves:
                existingNodesContainingUrlPath = matchingPathLeaves
                return existingNodesContainingUrlPath
            
            # Case 2
            # get child nodes if domain has already been embedded with other url(s)
            childNodesToAddTo = [childNode for nodeToAddTo in nodesToAddTo for childNode in nodeToAddTo.childrenAsRankPairNodes]
            reNodes = [lrg for lrg in childNodesToAddTo if lrg.dataAsRankPair.isRegexNode and re.match(lrg.name, p)]
            if reNodes:
                newNodes = []
                for rgxNode in reNodes:
                    # add new path node to rgxLeaf.parent
                    pathnode = RankPairTreePathNode(sisterRegexNode=rgxNode,name=p) #link the path node to regexLeaf
                    rgxNode.parent.appendChild(pathnode) 
                    # rgxNode.dataAsRankPair.incrementPathFreq()
                    newNodes.append(pathnode)
                    newNodes.append(rgxNode)
                return newNodes
            
            # Case 3
            newNodes = []
            for nodeToAddTo in nodesToAddTo:
                # 1. Add a PathRegexnode to parent
                # 2. create a path node with access to the regexCount of the regexNode
                    # Instead, update the data property on the node when adding the child to its parent.
                # 3. add the path node
                # 4. readd the regex node again
                # 5. REFACTOR:- RootNode is different Type to TreeNode which is the generic type. RootNode and TreeNode inherit from ITreeNode
                #       Then enforce all parent adding logic to be done through the TreeNode.addChild function on TreeNodeWChildren class and remove all parent setting capability
                #       Additionallyy, add teh data attribute in the rankPairTree.addChild function.
                #TODO! TreeNodebase dont inherit treeChildNode as can be a rootnode...
                parentNode = nodeToAddTo
                pathRegexNode = RankPairTreeRegexNode(name=(RankPairTree._getSubRePattern(p) or regx))
                pathTextNode = RankPairTreePathNode(sisterRegexNode=pathRegexNode, name=p)
                (parentNode
                .appendChild(pathTextNode)
                .appendChild(pathRegexNode))
                newNodes += [pathTextNode, pathRegexNode]
            return newNodes

        nodesToAddTo = [nodeToAddTo]
        
        for trgx in self._urlParser.parsedUrl.paths:
            p,regx = (trgx.text, trgx.regexPatrn)
            nodesToAddTo = _f(p, regx, nodesToAddTo)
            

        for (qk_trgx, qv_trgx) in self._urlParser.parsedUrl.queries:
            (qk, qkRgx),(qv, qvRgx) = (qk_trgx.text, qk_trgx.regexPatrn), (qv_trgx.text, qv_trgx.regexPatrn)
            nodesToAddTo = _f(qk, qkRgx, nodesToAddTo)
            if qv:
                nodesToAddTo = _f(qv, qvRgx, nodesToAddTo)

        return self

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
                if node.data['pathFrequency'] >= maxRank['pathFrequency'] and node.data['regexNodesInTreeDescendency'] <= maxRank['regexNodesInTreeDescendency']:
                    maxRank = node.data

            
            
        # Return the max rank pair       
        return maxRank

    TreeRank = property(getTreeRank)



    def __repr__(self) -> str:
        return self._treeState.__repr__()
    
    def __str__(self) -> str:
        return self._treeState.__str__()
    
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
    

def rest_rankTree_builds_correct_layers():
    
    _testUrl = 'https://acme.com/forum'#?sid=QZ932'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    print(rankTree.TreeRank)
    # assert rankTree.depth == 4, f'RankTree should have 4 layers for url: {_testUrl}, not {rankTree.depth}'

def rest_rankTree_builds_correct_layers_complex():
    
    _testUrl = 'https://groceries.asda.com/product/natural-plain-organic/fage-total-fat-free-greek-recipe-natural-yogurt/24771357?sid=12534Q&style=green'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    print(rankTree.TreeRank)

if __name__ == '__main__':
    rest_rankTree_builds_correct_layers_complex()
    # TODO: Build rankpair data by traversing the tree in a get fashion
    