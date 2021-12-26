import pytest

from tree_node import TreeNode

# def test_tree_can_refresh_jagged_array():
#     thirdChild = TreeNode(f'Leaf{3}')
#     firstChild = TreeNode(f'Leaf{1}', children=[thirdChild])
#     secondChild = TreeNode(f'Leaf{2}')
#     tree = TreeNode(name='TestTree', children=[firstChild, secondChild])
#     tree._refreshNodeJaggedArr()
#     assert tree._nodeJaggedArr == [
#         [tree],
#         [firstChild, secondChild],
#         [thirdChild],
#     ], 'Node Jagged Array has refreshed with the wrong shape'
#     thirdChild._refreshNodeJaggedArr()
#     assert thirdChild._nodeJaggedArr == [
#         [tree],
#         [firstChild, secondChild],
#         [thirdChild],
#     ], 'Node Jagged Array does not correctly refresh from child nodes.'




def test_can_add_child_to_tree():
    tree = TreeNode(name='TestTree')
    tree.appendChild(TreeNode('FirstLeaf'))
    assert len(tree.children) == 1, 'TestTree appendChild failed to add one child'
    assert isinstance(tree.children[0], TreeNode), 'TestTree appendChild doesnt add child of type TreeNode'
    assert tree.children[0].name == 'FirstLeaf', 'TestTree appendChild, child incorrectly named'

def _test_generate_child_node(level:int, childNo: int):
    return TreeNode(name=f'TreeNode_Layer_{level}_child{childNo}')

def test_can_get_tree_leaves():
    tree = TreeNode(name='RootTreeNode')
    numChildren = 2
    layer1 = [_test_generate_child_node(1, i+1) for i in range(numChildren)]
    for i,n in enumerate(layer1):
        tree.appendChild(n)
        layer2n = [_test_generate_child_node(2,(i*numChildren)+j+1) for j in range(numChildren)]
        for j,nn in enumerate(layer2n):
            n.appendChild(nn)
    leaves = tree.getLeaves()
    for n in leaves:
        # assert(f'TreeNode_Layer_2_child' in n.name, 'Tree.getLeaves returns nodes that arent leaves')
        assert(not(n.children), 'getLeaves() returns nodes with children')
    assert(len(leaves)==4, 'getLeaves() return incorrect number of leaves in the tree')

def test_tree_can_count_its_layers():
    tree = TreeNode(name='RootTreeNode')
    layer1 = [_test_generate_child_node(1, i+1) for i in range(2)]
    for i,n in enumerate(layer1):
        tree.appendChild(n)
        numChildren = 2
        layer2n = [_test_generate_child_node(2,(i*numChildren)+j+1) for j in range(numChildren)]
        for j,nn in enumerate (layer2n):
            n.appendChild(nn)
    assert(tree.numberOfLayers == 3, 'Tree cannot correctly count its layers, should be 3.')
    


def test_can_initialise_tree():
    tree = TreeNode(name='TestTree')
    assert tree.name == 'TestTree', 'Tree node initialisation failed.'