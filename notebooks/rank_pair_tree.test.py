
import pytest
from pprint import pprint

from notebooks.rank_pair_tree import RankPairTree

def rest_rankTree_builds_correct_layers():
    
    _testUrl = 'https://groceries.asda.com/product/natural-plain-organic/fage-total-fat-free-greek-recipe-natural-yogurt/24771357?sid=12534Q&style=green'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    assert rankTree.depth == 9, f'RankTree should have 9 layers for url: {_testUrl}, not {rankTree.depth}'


rest_rankTree_builds_correct_layers()