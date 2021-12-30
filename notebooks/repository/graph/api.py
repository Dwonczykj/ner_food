import time

from uint.uint import Uint

from connection import Neo4jConnectionFactory
from tree_node import TreeRootNodeBase
import re


# def add_categories(categories:pd.DataFrame):
#     # Adds category nodes to the Neo4j graph.
#     query = '''
#             UNWIND $rows AS row
#             MERGE (c:Category {category: row.category})
#             RETURN count(*) as total
#             '''
#     return conn.query(query, parameters = {'rows':categories.to_dict('records')}) # 'records' orientation : list like [{column -> value}, … , {column -> value}]


# def add_authors(rows:pd.DataFrame, batch_size=10000):
#     # Adds author nodes to the Neo4j graph as a batch job.
#     query = '''
#             UNWIND $rows AS row
#             MERGE (:Author {name: row.author})
#             RETURN count(*) as total
#             '''
#     return insert_data(query, rows, batch_size)

class Neo4jApi():
    def __init__(self) -> None:
        self._conn = Neo4jConnectionFactory.getInstance()

    def drop_tree_from_graph(self,node:TreeRootNodeBase):
        allNodesIds = node.traversePostorder(lambda n: n.id)
        query = '''
                UNWIND $nodeIds AS nodeId
                MATCH (n {id: nodeId})
                DETACH DELETE n
                
                RETURN count(*) as total
                '''
        def params(batch:Uint): 
            return {
                'nodeIds': allNodesIds
            }
        paramsInQuery = re.findall(r'\$([0-9A-Za-z]+)', query)
        unInitialisedQueryParameters = [m for m in paramsInQuery if m not in params(1).keys()]
        assert unInitialisedQueryParameters == [], 'Ensure that all Query String Params are Initialised;\nCheck param: \n[\n\t' + ',\n\t'.join(unInitialisedQueryParameters) + '\n]'
        
        
        start = time.time()
        
        res = self._conn.query(query, 
                        parameters = params(1))
        total = res[0]['total']
        result = {
            "total":total,
            "time":time.time()-start
        }
        return result

    def add_tree_to_graph(self,node:TreeRootNodeBase, batch_size=100000):
        # Adds child nodes to the Neo4j graph as a batch job.
        allNodes = node.traversePreorder(lambda n: {'name':n.name, **n.data, 'id': str(n.id)})
        
        query = '''
                UNWIND $nodes AS node
                MERGE (n:Node {id: node.id}) 
                    ON CREATE SET n.name = node.name
                    ON CREATE SET n.isRegexNode = node.isRegexNode
                
                // Connect to children
                WITH distinct node, n // reduce cardinality
                UNWIND node.children as childNode
                MATCH (c:Node {id: childNode.id})
                MERGE (n)-[:HAS_CHILD]->(c)
                RETURN count(distinct n) as total
                '''
        def params(batch:Uint): 
            return {
                'nodes': allNodes[batch*batch_size:(batch+1)*batch_size]
            }
        paramsInQuery = re.findall(r'\$([0-9A-Za-z]+)', query)
        unInitialisedQueryParameters = [m for m in paramsInQuery if m not in params(1).keys()]
        assert unInitialisedQueryParameters == [], 'Ensure that all Query String Params are Initialised;\nCheck param: \n[\n\t' + ',\n\t'.join(unInitialisedQueryParameters) + '\n]'
        
        total = 0
        batch = 0
        start = time.time()
        result = None
        while batch * batch_size < len(allNodes):

            res = self._conn.query(query, 
                            parameters = params(batch))
            print(res)
            total += res[0]['total']
            batch += 1
            result = {"total":total, 
                    "batches":batch, 
                    "time":time.time()-start}
            print(result)
            
        return result


# def insert_data(query:str, rows:list, batch_size = 10000):
#     # Function to handle the updating the Neo4j database in batch mode.
    
#     total = 0
#     batch = 0
#     start = time.time()
#     result = None
    
#     while batch * batch_size < len(rows):

#         res = conn.query(query, 
#                          parameters = {'rows': rows[batch*batch_size:(batch+1)*batch_size]})
#         total += res[0]['total']
#         batch += 1
#         result = {"total":total, 
#                   "batches":batch, 
#                   "time":time.time()-start}
#         print(result)
        
#     return result

# def add_papers(rows, batch_size=5000):
#    # Adds paper nodes and (:Author)--(:Paper) and 
#    # (:Paper)--(:Category) relationships to the Neo4j graph as a 
#    # batch job.
 
#    query = '''
#    UNWIND $rows as row
#    MERGE (p:Paper {id:row.id}) ON CREATE SET p.title = row.title
 
#    // connect categories
#    WITH row, p
#    UNWIND row.category_list AS category_name
#    MATCH (c:Category {category: category_name})
#    MERGE (p)-[:IN_CATEGORY]->(c)
 
#    // connect authors
#    WITH distinct row, p // reduce cardinality
#    UNWIND row.cleaned_authors_list AS author
#    MATCH (a:Author {name: author})
#    MERGE (a)-[:AUTHORED]->(p)
#    RETURN count(distinct p) as total
#    '''
 
#    return insert_data(query, rows, batch_size)