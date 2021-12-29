from neo4j import GraphDatabase
from dotenv import load_dotenv
import os 



class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response
    
class Neo4jConnectionFactory():
    
    _instance:Neo4jConnection = None
    
    
    def getInstance():
        if not Neo4jConnectionFactory._instance:
            Neo4jConnectionFactory._instance = Neo4jConnection(uri="bolt://35.170.185.163:7687", 
                                                               user="neo4j",              
                                                               pwd=password)
        return Neo4jConnectionFactory._instance
        
    
    
        
if __name__ == '__main__':
    load_dotenv()                    #for python-dotenv method

    user_name = os.environ.get('USER')
    password = os.environ.get('password')


    conn = Neo4jConnectionFactory.getInstance()

