

# Python3 Program to print binary tree in 2D
COUNT = [10]

# Binary Tree Node
""" utility that allocates a newNode
with the given key """
class newNode:

    # Construct to create a newNode
    def __init__(self, key):
        self.data = key
        self.left = None
        self.right = None

# Function to print binary tree in 2D
# It does reverse inorder traversal
def print2DUtil(root, space) :

    # Base case
    if (root == None) :
        return

    # Increase distance between levels
    space += COUNT[0]

    # Process right child first
    print2DUtil(root.right, space)

    # Print current node after space
    # count
    print() # Line spacing between nodes.
    for i in range(COUNT[0], space):
        print(end = "-")
    print(root.data)

    # Process left child
    print2DUtil(root.left, space)

# Wrapper over print2DUtil()
def print2D(root) :
    
    # space=[0]
    # Pass initial space count as 0
    print2DUtil(root, 0)

# Driver Code
if __name__ == '__main__':

    root = newNode(1)
    root.left = newNode(2)
    root.right = newNode(3)

    root.left.left = newNode(4)
    root.left.right = newNode(5)
    root.right.left = newNode(6)
    root.right.right = newNode(7)

    root.left.left.left = newNode(8)
    root.left.left.right = newNode(9)
    root.left.right.left = newNode(10)
    root.left.right.right = newNode(11)
    root.right.left.left = newNode(12)
    root.right.left.right = newNode(13)
    root.right.right.left = newNode(14)
    root.right.right.right = newNode(15)
    
    print2D(root)

# This code is contributed by
# Shubham Singh(SHUBHAMSINGH10)


# Python program to for tree traversals

# A class that represents an individual node in a
# Binary Tree


class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key


# A function to do inorder tree traversal
def printInorder(root):

    if root:

        # First recur on left child
        printInorder(root.left)

        # then print the data of node
        print(root.val),

        # now recur on right child
        printInorder(root.right)


# A function to do postorder tree traversal
def printPostorder(root):

    if root:

        # First recur on left child
        printPostorder(root.left)

        # the recur on right child
        printPostorder(root.right)

        # now print the data of node
        print(root.val),


# A function to do preorder tree traversal
def printPreorder(root):

    if root:

        # First print the data of node
        print(root.val),

        # Then recur on left child
        printPreorder(root.left)

        # Finally recur on right child
        printPreorder(root.right)


# Driver code
if __name__ == '__main__':
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    print("Preorder traversal of binary tree is")
    printPreorder(root)

    print("\nInorder traversal of binary tree is")
    printInorder(root)

    print("\nPostorder traversal of binary tree is")
    printPostorder(root)
