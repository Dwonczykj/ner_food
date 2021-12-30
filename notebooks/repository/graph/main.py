import pytest
from pprint import pprint
import sys
import os
x = os.path.abspath(os.path.join(os.getcwd(),'notebooks'))

if x not in sys.path:
    sys.path.append(x)
    print(x + ' added to path')
    
from rank_pair_tree import RankPair, RankPairTreeNode, RankPairTree, RankPairTreeRank

urls = [
    'https://groceries.asda.com', 
    'https://groceries.asda.com/promotion',
    'https://groceries.asda.com/product', 
    'https://groceries.asda.com/promotion/2-for-7/ls91300',
    'https://groceries.asda.com/product/1000338629556', 
    'https://groceries.asda.com/super_dept/veganuary/1215686171560', 
    'https://groceries.asda.com/cat/fresh-food-bakery/103099', 
    'https://groceries.asda.com/product/1000334423970',
]
rankTree = RankPairTree(urls[0])
for url in urls[1:]:
    rankTree.embedUrl(url)
rankTree.drawGraph()
from api import Neo4jApi
neo4jApi = Neo4jApi()
neo4jApi.add_tree_to_graph(rankTree.treeState)