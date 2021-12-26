
import pytest
from pprint import pprint
from pytest import CaptureFixture

from rank_pair_tree import RankPairTree

def test_rankTree_builds_correct_layers():
    
    _testUrl = 'https://groceries.asda.com/product/natural-plain-organic/fage-total-fat-free-greek-recipe-natural-yogurt/24771357?sid=12534Q&style=green'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    assert rankTree.depth == 9, f'RankTree should have 9 layers for url: {_testUrl}, not {rankTree.depth}'


def test_rankTree_builds_correct_layers(capfd:CaptureFixture[str]):
    
    _testUrl = 'https://acme.com/forum?sid=QZ932'
    rankTree = RankPairTree(_testUrl)
    pprint(rankTree)
    out, err = capfd.readouterr()
#     assert out == (
#         '''                    ----^[0-9A-Za-z]+$
#             ----^[A-Za-z]+$
#             |       ----QZ932
#     ----^[A-Za-z]+$
#     |       |       ----^[0-9A-Za-z]+$
#     |       ----sid-|
#     |               ----QZ932
# https://acme.com
#     |               ----^[0-9A-Za-z]+$
#     |       ----^[A-Za-z]+$
#     |       |       ----QZ932
#     ----forum
#             |       ----^[0-9A-Za-z]+$
#             ----sid-|
#                     ----QZ932''')
    print(rankTree.TreeRank)
    # capfd.
    # out, err = capfd.readouterr()
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
    assert rankTree._treeState.children[1].fullNameFromRoot.startswith('https://acme.com/')
    _testUrl2 = 'https://acme.com/forum?sid=QZ933'
    rankTree.embedUrl(_testUrl2)
    treeRank = rankTree.TreeRank
    assert treeRank['isRegexNode'] == True, 'treeRank[\'isRegexNode\'] should be True'
    assert treeRank['pathFrequency'] == 2, 'treeRank[\'pathFrequency\'] should be 2'
    assert treeRank['regexNodesInTreeDescendency'] == 1, 'treeRank[\'regexNodesInTreeDescendency\'] should be 1'
    rankTree.sortTree()
    pprint(rankTree)

def test_rankTree_multi_urls():
    urls = [
        'https://groceries.asda.com/promotion/2-for-4/ls91619', 
        'https://groceries.asda.com/cat/vegan-plant-based/617635960', 
        'https://groceries.asda.com/product/910000879998', 
        'https://groceries.asda.com/product/1000005036703', 
        'https://groceries.asda.com/accessibility', 
        'https://groceries.asda.com/cat/fresh-food-bakery/103099', 
        'https://groceries.asda.com/product/1000275697716', 
        'https://groceries.asda.com/super_dept/food-cupboard/1215337189632', 
        'https://groceries.asda.com/product/1000329097857', 
        'https://groceries.asda.com/recipes/Crunchy-cheese-bites/384e188d-2aff-11e9-8802-7daf07a34f81'
        ]
    rankTree = RankPairTree(urls[0])
    for url in urls[1:]:
        rankTree.embedUrl(url)
        rankTree.sortTree()
    assert rankTree.__repr__() == ('                    ----^[0-9A-Za-z]+$\n                    ----103099\n            ----^[0-9A-Za-z\\-]+$\n            |       ----617635960\n            |       ----ls91619\n                    ----^[0-9A-Za-z\\-]+$\n            ----Crunchy-cheese-bites\n            |       ----384e188d-2aff-11e9-8802-7daf07a34f81\n            ----1000329097857\n            ----1000275697716\n                    ----^[0-9]+$\n            ----fresh-food-bakery\n            |       ----103099\n    ----^[A-Za-z]+$\n    |       ----1000005036703\n    |       ----910000879998\n    |       |       ----^[0-9]+$\n    |       ----vegan-plant-based\n    |               ----617635960\n    |       |       ----^[0-9A-Za-z]+$\n    |       ----2-for-4\n    |               ----ls91619\n                    ----^[0-9A-Za-z\\-]+$\n            ----^[0-9A-Za-z\\-]+$\n            |       ----384e188d-2aff-11e9-8802-7daf07a34f81\n    ----recipes\n    |       |       ----^[0-9A-Za-z\\-]+$\n    |       ----Crunchy-cheese-bites\n    |               ----384e188d-2aff-11e9-8802-7daf07a34f81\n    ----accessibility\nhttps://groceries.asda.com\n    |       ----^[0-9]+$\n    |       ----1000329097857\n    |       ----1000275697716\n    ----product\n            ----1000005036703\n            ----910000879998\n    |               ----^[0-9]+$\n    |               ----103099\n    |       ----^[0-9A-Za-z\\-]+$\n    |       |       ----617635960\n    |               ----^[0-9]+$\n    |       ----fresh-food-bakery\n    |       |       ----103099\n    ----cat-|\n            |       ----^[0-9]+$\n            ----vegan-plant-based\n                    ----617635960\n    |               ----^[0-9A-Za-z]+$\n    |       ----^[0-9A-Za-z\\-]+$\n    |       |       ----ls91619\n    ----promotion\n            |       ----^[0-9A-Za-z]+$\n            ----2-for-4\n                    ----ls91619')

def test_rankTree_get_example_generalisation():
    urls = [
        'https://groceries.asda.com/product/910000879998', 
        'https://groceries.asda.com/product/1000005036703',
        'https://groceries.asda.com/product/3120005036743',
    ]
    rankTree = RankPairTree(urls[0])
    url = urls[1]
    exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisations[0] == 'https://groceries.asda.com/product/910000879998'
    # exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=False)
    # assert 'https://groceries.asda.com/<regex>^[A-Za-z]+$</regex>/1000005036703' in exampleUrlGeneralisations[0] 
    # assert exampleUrlGeneralisations[0] == 'https://groceries.asda.com/<regex>^[A-Za-z]+$</regex>/1000005036703'
    
    rankTree.embedUrl(url)
    rankTree.sortTree()
    url = urls[2]
    exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisations[0] == 'https://groceries.asda.com/product/910000879998'
    # exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=False)
    # assert exampleUrlGeneralisations[0] == 'https://groceries.asda.com/product/910000879998'
    pass
    
def test_ranktree_get_example_generalisations_no_default():
    urls = [
        'https://groceries.asda.com', 
        'https://groceries.asda.com/promotion/2-for-7/ls91300'
    ]
    rankTree = RankPairTree(urls[0])
    url = urls[1]
    exampleUrlGeneralisation = rankTree.getExampleGeneralisationOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisation is None
    exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisations is None or exampleUrlGeneralisations == []
    
def test_ranktree_get_example_generalisations_should_not_match():
    urls = [
        'https://groceries.asda.com/promotion/2-for-7/ls91300', 
        'https://groceries.asda.com/product/1000338629556', 
        # 'https://groceries.asda.com/super_dept/veganuary/1215686171560', 
        # 'https://groceries.asda.com/cat/fresh-food-bakery/103099', 
        # 'https://groceries.asda.com/product/1000334423970', 
        # 'https://groceries.asda.com/product/18883', 
        # 'https://groceries.asda.com/product/1000330481079', 
        # 'https://groceries.asda.com/product/1000237774511', 
        # 'https://groceries.asda.com/event/gino_dacampo_view_all', 
        # 'https://money.asda.com/insurance/car-insurance/?utm_source=ghs&utm_medium=footer&utm_campaign=car-insurance'
    ]
    rankTree = RankPairTree(urls[0])
    url = urls[1]
    exampleUrlGeneralisations = rankTree.getAllExampleGeneralisationsOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisations is None or exampleUrlGeneralisations == []
    exampleUrlGeneralisation = rankTree.getExampleGeneralisationOf(url,removeRegexNodes=True)
    assert exampleUrlGeneralisation is None
    
    
    