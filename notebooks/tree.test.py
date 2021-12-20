import pytest

from notebooks.tree import newNode, print2D, Node, traverseInorder, traversePostorder, traversePreorder



def test_print2D():
    root = newNode(1)
    root.appendChild(newNode(2))
    root.appendChild(newNode(3))


    root.children[0].appendChild(newNode(4))
    root.children[0].appendChild(newNode(5))
    root.children[-1].appendChild(newNode(6))
    root.children[-1].appendChild(newNode(7))

    root.children[0].children[0].appendChild(newNode(8))
    root.children[0].children[0].appendChild(newNode(9))
    root.children[0].children[0].appendChild(newNode(9.1))
    root.children[0].children[0].appendChild(newNode(9.2))
    root.children[0].children[-1].appendChild(newNode(10))
    root.children[0].children[-1].appendChild(newNode(11))
    root.children[-1].children[0].appendChild(newNode(12))
    root.children[-1].children[0].appendChild(newNode(13))
    root.children[-1].children[-1].appendChild(newNode(14))
    root.children[-1].children[-1].appendChild(newNode(15))

    output = print2D(root)
    correctOutput = '''                              15

                    7

                              14

          3

                              13

                    6

                              12

1

                              11

                    5

                              10

          2

                              9.2

                              9.1

                    4

                              9

                              8'''
    assert output == correctOutput


def _test_get_tree_traverse():
    root = Node(1)
    root.appendChild(Node(2))
    root.appendChild(Node(3))


    root.children[0].appendChild(Node(4))
    root.children[0].appendChild(Node(5))

    return root

def test_traverse_tree_postorder():
    root = _test_get_tree_traverse()
    output = traversePostorder(root)
    correctOutput = [4, 5, 2, 3, 1]
    assert output == correctOutput


def test_traverse_tree_preorder():
    root = _test_get_tree_traverse()
    output = traversePreorder(root)
    correctOutput = [1, 2, 4, 5, 3]
    assert output == correctOutput


def test_traverse_tree_inorder():
    root = _test_get_tree_traverse()
    output = traverseInorder(root)
    correctOutput = [4, 2, 5, 1, 3]
    assert output == correctOutput

    