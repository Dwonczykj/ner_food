# from time import time
# # default configurations are for http port 7474 and for bolt 7687 , 
# # Suppose one neo4j is running with http port 7474 , now we can not run another neo4j instance with 7474 ,
# # we have to change the port in neo4j.conf then we can start another instance , to resolve this

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind(("", 0))
# sock.listen(1)
# port = sock.getsockname()[1]

# # It will give you the free port and need to change this in neo4j.conf in runtime now lets see this pytest fixture

# @pytest.fixture(scope="session")
# def neo4j_graph_instance(csv_node_file, csv_relation_file):
#     instancesDirectory = os.path.join(PATH_TEST_DIR, "neo4j_instance_acceptance")
# if not os.path.exists(instancesDirectory):
#     os.makedirs(instancesDirectory)

# archive_file = "neo4j-community-3.2.1-unix.tar.gz"
# filename = instancesDirectory + "/" + archive_file

# if (os.path.isfile(filename)) == True:
#     try:
# with TarFile.open(filename, "r:gz") as archive:
#             archive.extractall(instancesDirectory)
#             print ("successfully extracted")

#     except IOError:
#         print "file is not there"
# else:
#     try:
#         uri = "http://dist.neo4j.org/neo4j-community-3.2.1-unix.tar.gz"
#         urlretrieve(uri, filename)
#         try:
#             with TarFile.open(filename, "r:gz") as archive:
#                 archive.extractall(instancesDirectory)
#         except IOError:
#             print "file is not there"
#     except IOError:
#         print "Could not connect to internet to download the file"

# neo4j_home = os.path.join(instancesDirectory, "neo4j-community-3.2.1")
# neo4j_import_dir = os.path.join(neo4j_home, "import")
# neo4j_inst = Neo4jInstance(home=neo4j_home)

# neo4j_inst.set_config("dbms.connector.http.listen_address", ":%s" % get_open_port())
# neo4j_inst.set_config("dbms.connector.bolt.listen_address", ":%s" % get_open_port())
# neo4j_inst.set_config("dbms.security.auth_enabled", "false")
# neo4j_inst.set_config("dbms.connector.https.enabled", "false")

# # db loading mechanism #
# # Rajib: I am getting csv files fixture and copying them in neo4j import dir  in run time.
# # Then getting bolt uri for that active instance  , and executing the command 'load_db_script'.
# # At the end I am returning one Graph instance with fully loaded with csv files.


# neo4j_inst.start_neo4j_instance()
# time.sleep(15)
# #:todo need to avoid sleep , instead check socket connection to desired host and port
# print "copying csv files to neo4j import directory"

# copy_script = "cp %s %s %s" % (
#     csv_node_file, csv_relation_file,  neo4j_import_dir)
# call(copy_script, shell=True)
# print "successfully copied to neo4j import directory "
# neo4j_inst_bolt_uri = "bolt://localhost:%d" % neo4j_inst.get_bolt_port()
# load_cypher_file = os.path.join(DMS_PATH, "load_csv.cypher")
# load_db_script = "cat %s | %s -a %s --format verbose --debug" % (
#     load_cypher_file, neo4j_inst.cypher_shell_script(), neo4j_inst_bolt_uri)
# call(load_db_script, shell=True)
# neo4j_inst_http_port = neo4j_inst.get_http_port()

# yield Graph(host='localhost', http_port=neo4j_inst_http_port, bolt=False)

# print "running teardown methods"

# neo4j_inst.stop_neo4j_instance()
# neo4j_inst.delete_store()