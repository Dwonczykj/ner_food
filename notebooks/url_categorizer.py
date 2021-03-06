# workout how to save a url embedding, pickle? -> fast to write to, slow to read, easy to store in a db.
#   tojson() ? 

# Find each different path / query category in the tree automatically, using regex patterns? / tree depth etc when traversing the tree. 
#   Start by taking a simple printout of a tree with muytlipe url types from a unit test.
#       Traverse to leaf notes: get the regex partner for each leaf section, get the winning regex node for each category.
#       To decide if this a subtree is a new category, this is done by path, not by query, 
#       now if the last element of the path is say an id variable, rather than a different route, 
#       we can define a new category at the node[-2] of the paths in the url because all sub nodes (which are paths and have to be) fit to the same regex. => Subtree. 
#       Other situation is that the last path is just the name of the page, 
#       and the query differentiates it, this can be determined by if there is only one last text node in the path part of the url. 
#       So the new category starts at the path[-1] (i.e. final unique text path with all the query strings before).

# For each url TEXT Path in the url embedding, categroise the category of urls by checking the rankpair for 
#   that subtree (ensure can calculate rankpair of subtreenodes too w/ tests).

# 
# 
# 
# 
# 
# 
# 
# 

from rank_pair_tree import RankPairTreeRegexNode
from rank_pair_tree import RankPairTree, RankPairTreeNode


urls = [
    'https://groceries.asda.com', 
        'https://groceries.asda.com', 
        'https://groceries.asda.com/promotion/2-for-7/ls91300', 
        'https://groceries.asda.com/promotion/3-for-1/87435', 
        'https://groceries.asda.com/promotion/buy-one-get-one-free/xt9875', 
        'https://groceries.asda.com/product/1000338629556', 
        'https://groceries.asda.com/super_dept/veganuary/1215686171560', 
        'https://groceries.asda.com/cat/fresh-food-bakery/103099', 
        'https://groceries.asda.com/product/1000334423970', 
        'https://groceries.asda.com/cat/fresh-food-bakery/107823', 
        'https://groceries.asda.com/cat/fresh-food-bakery/997463', 
        'https://groceries.asda.com/cat/lader/123765', 
        'https://groceries.asda.com/product/18883', 
        'https://groceries.asda.com/product/1000330481079', 
        'https://groceries.asda.com/product/1000237774511', 
        'https://groceries.asda.com/cat/lader/198354', 
        'https://groceries.asda.com/event/gino_dacampo_view_all/?sid=uxvtr',
        'https://groceries.asda.com/event/gino_dacampo_view_all/?sid=1834f', 
]
rankTree = RankPairTree(urls[0])
for url in urls[1:]:
    rankTree.embedUrl(url)

rankTree.drawGraph(outFileName='Hello.png')

# def _f(rankTreeChildren:list[RankPairTreeNode]):
#     for c in rankTreeChildren:
#         if c.children and c.children[0].getNumSiblingsOfPathType() > 1:
#             pathSibs = c.getSiblingsOfPathType()
#             for pathSib in pathSibs:
#                 subTreeRefs.append(pathSib)
#             for ancestor in pathSibs[0].ancestry()[:-1]:
#                 if ancestor in subTreeRefs:
#                     subTreeRefs.remove(ancestor)
#             _f(pathSibs)
#             break
#         _f(c.children)

def getTextChildNodes(rankTree:RankPairTreeNode):
    return [cNode for cNode in rankTree.children if not isinstance(cNode, RankPairTreeRegexNode)]

# [grandChild for child in rankTree.children for grandChild in child.children]


def getCategoryNodes(rankTree:RankPairTreeNode):
    def _getCategoryNodes(rankTree:RankPairTreeNode):
        pathChildren = [cNode for cNode in rankTree.children if not isinstance(cNode, RankPairTreeRegexNode)]
        if pathChildren and len(pathChildren)>1:
            return list(set([x for child in pathChildren for x in _getCategoryNodes(child)]))
        else:
            return [rankTree.parent if hasattr(rankTree, 'parent') else rankTree]
        
    categoryNodes = _getCategoryNodes(rankTree)
    ancestors = [a for c in categoryNodes for a in c.ancestry()[:-1]]
    filteredNodes = [c for c in categoryNodes if c not in ancestors]
    return filteredNodes

def getHighestRankSubPath(rankTree:RankPairTreeNode):
    # leaves = rankTree.getLeaves()
    return rankTree.treeRank.fullUrl
    # get corresponding url

categoryNodes = getCategoryNodes(rankTree)
categoryRepUrls = [(node, node.name, getHighestRankSubPath(node)) for node in categoryNodes]
    
pass


