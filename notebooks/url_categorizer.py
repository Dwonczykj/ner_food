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
