from __future__ import annotations
from operator import countOf
from os import path
import io
import os
import re
from typing import Literal, Tuple, overload
import requests
import numpy as np
import matplotlib.pyplot as plt
from collections import UserList, defaultdict
from collections.abc import Sequence
from uint import Uint, Int
from enum import Enum, IntEnum
import debugpy as debug
import warnings
from pprint import pprint
from tree_node import ITreeNode
import abc
from url_parser import UrlMatchEnum
from py_utils import predicatePipe


from tree_node import TreeNode, TreeNodeRoot, TreeRootNodeBase
from url_parser import ParsedUrlParser


class RankTreeBuilderFlags(Enum):
    AllowMultipleDomains = 2^0
    AllowMultipleRegexLeavesPerParent = 2^1
    

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
    childrenAsRankPairNodes:list[RankPairTreeNode] = property(getChildren)

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

class RankPairTreeUrlBuilder(abc.ABC):

    @abc.abstractmethod
    def _getUrlSegment(self):
        pass

    urlSegment = property(_getUrlSegment)


class RankPairTreeNode(TreeNode, RankPairTreeNodeSortable, RankPairTreeUrlBuilder):
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
    parent:RankPairTreeRootNode = property(getParent)
    
    def getParentIfGrandParent(self):
        parentIfGrandParent:RankPairTreeNode = None
        if hasattr(self.parent, 'parent') and self.parent.parent is not None:
            parentIfGrandParent = self.parent
        
        return parentIfGrandParent
    parentWithParents:RankPairTreeNode = property(getParentIfGrandParent)
    
    def getChildren(self:type[RankPairTreeRootNode]):
        return super().getChildren()
    
    children:list[RankPairTreeNode] = property(getChildren)

    def getSiblingsOfPathType(self) -> list[RankPairTreeTextNode]:
        return [n for n in self.parent.children if not n.data['isRegexNode']]

    def _getUrlSegmentType(self) -> UrlMatchEnum:
        otherChildren = self.getSiblingsOfPathType()
        if otherChildren:
            otherChild = otherChildren[0]
            if isinstance(otherChild, RankPairTreePathNode):
                return UrlMatchEnum.URL_PATH
            elif isinstance(otherChild, RankPairTreeQueryKeyNode):
                return UrlMatchEnum.URL_QUERY_KEY
            elif isinstance(otherChild, RankPairTreeQueryValueNode):
                return UrlMatchEnum.URL_QUERY_VALUE
            elif isinstance(otherChild, RankPairTreeQueryFlagNode):
                return UrlMatchEnum.URL_PARSING_SYMBOL
            elif isinstance(otherChild, RankPairTreeDomainNode):
                return UrlMatchEnum.URL_DOMAIN
            else:
                return UrlMatchEnum.URL_PROTOCOL # TODO: Add Undefined Flag
        else:
            return UrlMatchEnum.URL_DOMAIN

    nodeType:UrlMatchEnum = property(_getUrlSegmentType)

    def _getUrlSegment(self):
        return f'{self.name}'
    
    urlSegment = property(_getUrlSegment)

    def withChildrenState(state:RankPairTreeNode) -> RankPairTreeNode:
        instance = RankPairTreeNode(name=state.name)
        instance.data = state.data
        for child in state.children:
            instance.appendChild(RankPairTreeNode.withChildrenState(child.children))
        return instance
        # instance._children = state._children 

    def ancestry(self) -> list[RankPairTreeNode]:
        ancestor = self
        ancestry:list[RankPairTreeNode] = [ancestor]
        i = 0
        while i <= 99 and hasattr(ancestor, 'parent'):
            i += 1
            ancestor = getattr(ancestor, 'parent')
            ancestry = [ancestor] + ancestry
        return ancestry
    
    def isRegexInAncestry(self, ignoreSelf:bool=False) -> bool:
        return any(c.data['isRegexNode'] == True for c in self.ancestry()[:(-1 if ignoreSelf else None)])
    

    def getFullNameFromRoot(self):
        return ''.join([(f'{a.urlSegment}') for a in self.ancestry()])

    fullNameFromRoot:str = property(getFullNameFromRoot)
                

class RankPairTreeRootNode(TreeNodeRoot, RankPairTreeNodeSortable, RankPairTreeUrlBuilder):
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

    def getFullNameFromRoot(self):
        return self.name

    fullNameFromRoot:str = property(getFullNameFromRoot)

    def _getUrlSegment(self):
        if self.nodeType == UrlMatchEnum.MULTI_URL_CONTAINER:
            return ''
        return f'{self.name}'
    
    urlSegment = property(_getUrlSegment)

    def _getUrlSegmentType(self) -> UrlMatchEnum:
        if any((c.nodeType == UrlMatchEnum.URL_DOMAIN for c in self.children)):
            return (UrlMatchEnum.MULTI_URL_CONTAINER if self.name == RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME else UrlMatchEnum.UNDEFINED)
        else:
            return UrlMatchEnum.URL_DOMAIN

    nodeType:UrlMatchEnum = property(_getUrlSegmentType)





    

class RankPairTreeTextNode(RankPairTreeNode):
    def __init__(self, sisterRegexNode:RankPairTreeRegexNode, name='root'):
        super().__init__(name=name)
        self.sisterRegexNode = sisterRegexNode
        self.data = {'isRegexNode': False}

    def filterPathNodesFromTreeNodes(nodes:list[RankPairTreeNode]):
        result:list[RankPairTreeTextNode] = [n for n in nodes if not n.data['isRegexNode']]
        return result
    
class RankPairTreePathNode(RankPairTreeTextNode):
    def _getUrlSegment(self):
        return f'/{self.name}'
    urlSegment = property(_getUrlSegment)

class RankPairTreeQueryKeyNode(RankPairTreeTextNode):
    # def __init__(self, sisterRegexNode: RankPairTreeRegexNode, name='root'):
    #     super().__init__(sisterRegexNode, name=name)

    
    def _getUrlSegment(self):
        arg = ''
        if self.parent.nodeType == UrlMatchEnum.URL_PATH:
            arg = '?'
        elif self.parent.nodeType == UrlMatchEnum.URL_QUERY_VALUE:
            arg = '&'
        elif self.parent.nodeType == UrlMatchEnum.URL_DOMAIN:
            arg = '?'
        else:
            arg = ''
        return f'{arg}{self.name}'
    
    urlSegment = property(_getUrlSegment)
    
class RankPairTreeQueryValueNode(RankPairTreeTextNode):
    
    def _getUrlSegment(self):
        return f'={self.name}'
    
    urlSegment = property(_getUrlSegment)

class RankPairTreeDomainNode(RankPairTreeTextNode):

    def _getUrlSegment(self):
        return f'{self.name}'
    
    urlSegment = property(_getUrlSegment)

class RankPairTreeQueryFlagNode(RankPairTreeTextNode):

    def _getUrlSegment(self):
        return '?'
    
    urlSegment:Literal['?'] = property(_getUrlSegment)


class RankPairTreeRegexNode(RankPairTreeNode):
    def __init__(self, name='root'):
        super().__init__(name=name)
        self.data = {'isRegexNode': True}

    def _getUrlSegment(self):
        otherChild = self.getSiblingsOfPathType()[0]
        if otherChild.nodeType == UrlMatchEnum.URL_PATH:
            arg = '/'
        elif otherChild.nodeType == UrlMatchEnum.URL_QUERY_KEY:
            if otherChild.parent.nodeType == UrlMatchEnum.URL_PATH:
                arg = '?'
            elif otherChild.parent.nodeType == UrlMatchEnum.URL_QUERY_VALUE:
                arg = '&'
            elif otherChild.parent.nodeType == UrlMatchEnum.URL_DOMAIN:
                arg = '?'
            else:
                arg = ''
        elif otherChild.nodeType == UrlMatchEnum.URL_QUERY_VALUE:
            arg = '='
        else:
            arg = ''
        return f'{arg}<regex>{self.name}</regex>'
    
    urlSegment = property(_getUrlSegment)


class RankPairTree(object):

    def __init__(self, url:str=None):
        # super.__init__(self)
        self._urlParser:ParsedUrlParser = None
        self._treeState:RankPairTreeRootNode = None
        self.initialised:bool = False
        self.rankTreeBuilderFlags = [
            RankTreeBuilderFlags.AllowMultipleDomains
        ]
        if url is not None:
            self.embedUrl(url)
            self.initialised = True
        
    def fromState(treeState:RankPairTreeRootNode) -> RankPairTree:
        instance = RankPairTree()
        instance._treeState = treeState.copyDeep()
        instance.initialised = (treeState.name is not None)
        return instance

    def copyDeep(self) -> RankPairTree:
        return RankPairTree.fromState(self._treeState)


    def embedUrl(self, url:str):
        return self._processUrl(url, embed=True)[0]

    def containsGeneralisationOf(self, url:str):
        return bool(self._processUrl(url, embed=False, filterRegexNodesFromMatches=False)[1]) if self.initialised else False

    def getExampleGeneralisationOf(self, url:str, removeRegexNodes:bool=True):
        return predicatePipe(self.getAllExampleGeneralisationsOf(url=url, removeRegexNodes=removeRegexNodes), lambda o: bool(o), lambda x: x[0])
    
    def getAllExampleGeneralisationsOf(self, url:str, removeRegexNodes:bool=True) -> list[str|None]:
        return ([s for s in self._processUrl(url, embed=False, filterRegexNodesFromMatches=removeRegexNodes)[1] if s is not None]) if self.initialised else [None]

    def _processUrl(self, url:str, embed:bool, filterRegexNodesFromMatches:bool=True) -> Tuple[RankPairTree,list[str]]:
        '''If embed, bake url into self and return self, else bake url into a copy of self and return the copy.'''
        instance:RankPairTree=None
        
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
            assert self != instance
        
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
                name=RankPairTree.TREE_ROOT_MULTI_DOMAIN_NAME
                )
            instance.appendChild(RankPairTreeNode.withChildrenState(instance._treeState) if embed else instance._treeState)
            instance.appendChild(RankPairTreeNode(instance._urlParser.parsedUrl.domain))
        
        nodeToAddTo = instance.getDomainNode()

        def _f(p:str,regx:str, nodesToAddTo:list[RankPairTreeNode], urlMatchEnum:UrlMatchEnum):
            '''We are only adding text and regex nodes on all leaves when it is a new domain tree.\n
            Otherwise we only add paths and potentially regex when the tree does NOT already contain them.'''
            
            if urlMatchEnum == UrlMatchEnum.URL_DOMAIN:
                T = RankPairTreeDomainNode
            elif urlMatchEnum == UrlMatchEnum.URL_PATH:
                T = RankPairTreePathNode
            elif urlMatchEnum == UrlMatchEnum.URL_QUERY_KEY:
                T = RankPairTreeQueryKeyNode
            elif urlMatchEnum == UrlMatchEnum.URL_QUERY_VALUE:
                T = RankPairTreeQueryValueNode
            elif urlMatchEnum == UrlMatchEnum.URL_PARSING_SYMBOL:
                T = RankPairTreeQueryFlagNode
            else:
                T = RankPairTreeTextNode


            # todo change it to do nodes in nodesToAddto individually:
            matches:list[Tuple[RankPairTreeNode,str]] = []
            for nodeToAddTo in nodesToAddTo:
                if not nodeToAddTo.children:
                    # Add new text node and new regex node:
                    pathRegexNode = RankPairTreeRegexNode(name=(RankPairTree._getSubRePattern(p) or regx))
                    pathTextNode = T(sisterRegexNode=pathRegexNode, name=p)
                    (nodeToAddTo
                     .appendChild(pathTextNode, atPosition=None)
                     .appendChild(pathRegexNode, atPosition=None))
                    matches += [
                        (pathTextNode,None), 
                        (pathRegexNode,None)
                    ]
                    continue
                
                textMatches = [x for n in T.filterPathNodesFromTreeNodes(nodeToAddTo.children) if n.name == p for x in (n,n.sisterRegexNode)]
                if textMatches:
                    # Contains a child with a matching text node so no nodes to add, 
                    # but keep iterating down this branch for both the text node and its sister regex node.
                    for t in textMatches:
                        matches.append((t, t.fullNameFromRoot))
                    continue

                regexMatches = [n for n in nodeToAddTo.children if n.data['isRegexNode'] and re.match(n.name, p)]
                if regexMatches:
                    # Contains a child with a matching regex node but not a matching text node, 
                    # so we add a text node to the tree here and then follow both the regex node and the new text node.
                    for regexNode in regexMatches:
                        pathnode = T(sisterRegexNode=regexNode, name=p)
                        atPos = nodeToAddTo.children.index(regexNode)
                        nodeToAddTo.appendChild(pathnode, atPosition=atPos)
                        matches.append((pathnode, None))
                        matches.append((regexNode, regexNode.fullNameFromRoot))
                    continue
                
                if nodeToAddTo.children and not regexMatches:
                    if RankTreeBuilderFlags.AllowMultipleRegexLeavesPerParent in self.rankTreeBuilderFlags:
                        # Add new text node and new regex node:
                        pathRegexNode = RankPairTreeRegexNode(name=(RankPairTree._getSubRePattern(p) or regx))
                        pathTextNode = T(sisterRegexNode=pathRegexNode, name=p)
                        nodeToAddTo.sortChildren()
                        textNodeAtPos = next(i for i,node in enumerate(nodeToAddTo.children) if node.data['isRegexNode'] == True)
                        (nodeToAddTo
                        .appendChild(pathTextNode, atPosition=textNodeAtPos)
                        .appendChild(pathRegexNode, atPosition=textNodeAtPos+1))
                        matches += [
                            (pathTextNode,None), 
                            (pathRegexNode,None)
                        ]
                        continue
                    else:
                        # Find a more generic regex pattern for the regex child of nodeToAddTo and replace it.
                        currentRegexNode:RankPairTreeRegexNode = next((rgxNode for rgxNode in nodeToAddTo.children if rgxNode.data['isRegexNode'] == True))
                        pathRegexNode = RankPairTreeRegexNode(
                            name=(
                                regx if all(
                                    (re.match(regx, c.name) 
                                     for c in [*nodeToAddTo.children, RankPairTreePathNode(currentRegexNode,name=p)]
                                     )) else RankPairTree._getSubRePattern(*[n.name for n in nodeToAddTo.children if n.data['isRegexNode'] == False])
                                )
                            )
            return matches


        nodesToAddTo = [nodeToAddTo]
        alreadyExistingPathSoFar = nodeToAddTo.fullNameFromRoot
        generalisationOfUrl:str=None
        for ind,trgx in enumerate(instance._urlParser.parsedUrl.paths):
            p,regx = (trgx.text, trgx.regexPatrn)
            matches = _f(p, regx, nodesToAddTo, UrlMatchEnum.URL_PATH)
            nodesToAddTo, alreadyExistingPathSoFar = (
                [m[0] for m in matches], 
                [
                    (m[0].getSiblingsOfPathType()[0].fullNameFromRoot if m[0].data['isRegexNode'] == True and m[1] is not None else m[1]) 
                    for m in matches if m[0].isRegexInAncestry(ignoreSelf=True) == (not filterRegexNodesFromMatches)
                ]
            )
            
            

        for ind,(qk_trgx, qv_trgx) in enumerate(instance._urlParser.parsedUrl.queries):
            (qk, qkRgx),(qv, qvRgx) = (qk_trgx.text, qk_trgx.regexPatrn), (qv_trgx.text, qv_trgx.regexPatrn)
            matches = _f(qk, qkRgx, nodesToAddTo, UrlMatchEnum.URL_QUERY_KEY)
            nodesToAddTo, alreadyExistingPathSoFar = (
                [m[0] for m in matches], 
                [
                    (m[0].getSiblingsOfPathType()[0].fullNameFromRoot if m[0].data['isRegexNode'] == True and m[1] is not None else m[1]) 
                    for m in matches if m[0].isRegexInAncestry(ignoreSelf=True) == (not filterRegexNodesFromMatches)
                ]
            )
            if qv:
                matches = _f(qv, qvRgx, nodesToAddTo, UrlMatchEnum.URL_QUERY_VALUE)
                nodesToAddTo, alreadyExistingPathSoFar = (
                    [m[0] for m in matches], 
                    [
                        (m[0].getSiblingsOfPathType()[0].fullNameFromRoot if m[0].data['isRegexNode'] == True and m[1] is not None else m[1]) 
                        for m in matches if m[0].isRegexInAncestry(ignoreSelf=True) == (not filterRegexNodesFromMatches)
                    ]
                )
                
        if not instance.initialised:
            instance.initialised = True

        if embed:
            assert self.__hash__() == instance.__hash__()
        
        return (instance, alreadyExistingPathSoFar)

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
        atPos = None
        if self.children and isinstance(self.children[-1], RankPairTreeRegexNode):
            atPos = -1
        self._treeState.appendChild(node, atPosition=atPos)
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

    def _getSubRePattern(*testStrings:str) -> str:
        '''
        decreasing order of specificity rules: ['[0-9]', '[A-Z]', '[A-Za-z]', '[0-9A-Za-z]', r'[0-9A-Za-z\-]', r'[^\/]', '', '', '', ]
        
        to match: ['forum', 'p', 'sid', '0193Q']
        '''
        
        tryPatternsDecreasingSpecificity = {
            '^[0-9]+$': False,
            '^[A-Z]+$': False,
            '^[A-Za-z]+$': False,
            '^[0-9A-Za-z]+$': False,
            r'^[0-9A-Za-z\-]+$': False,
            r'^[^\/]+$': False,
            r'^[^=]+$': False,
        }
        
        if not testStrings:
            return None

        for testStr in testStrings:
            for pattern in tryPatternsDecreasingSpecificity.keys():
                if re.match(pattern, testStr):
                    tryPatternsDecreasingSpecificity[pattern] = True
                
        for pattern in tryPatternsDecreasingSpecificity.keys():
            if tryPatternsDecreasingSpecificity[pattern] == True:
                return pattern
        else:
            return None
    


if __name__ == '__main__':
    pass
    
    