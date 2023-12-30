from neo4j import GraphDatabase
import json

class Neo4jPopulator:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def populate_data(self):
        with self._driver.session() as session:
            # Define aquí tus consultas Cypher para poblar la base de datos
            queries = []

            queries.append("CREATE CONSTRAINT FOR (a:Author) REQUIRE a.name IS UNIQUE;")
            queries.append("CREATE CONSTRAINT FOR (j:Journal) REQUIRE j.name IS UNIQUE;")

            with open('test.json') as json_data:
                data = json.load(json_data)

            for element in data:
                
                result = session.run("MATCH (a:Author) RETURN a")                

                #Paper
                pid = element['paper_id']
                doi = element['paper_doi']
                title = element['paper_title']
                pub = element['paper_publication_date']
                upd = element['paper_update_date']
                nop = str(element['paper_number_of_pages'])
                cat = element['paper_category']

                queries.append("CREATE (p:Paper {paper_id: '" + pid + "', doi: '" + doi + "', title: '" + title + "', publication_date: '" + pub + "', update_date: '" + upd + "', number_of_pages: '" + nop + "', category: '" + cat + "'})")


                #Journal
                jname = element['journal_name']
                queries.append(f"CREATE (j:Journal {{name: '{jname}'}})")

                #Create the relation
                queries.append("MATCH (jn:Journal {name: '"+ jname +"'}), (pn:Paper {paper_id: '"+ pid +"'}) CREATE (jn)-[:publishes]->(pn)")
                queries.append("MATCH (jn:Journal {name: '"+ jname +"'}), (pn:Paper {paper_id: '"+ pid +"'}) CREATE (jn)<-[:is_published_in]-(pn)")


                #Authors
                aff =  element['author_affiliation']
                
                it=0
                for auth in element['author_name']:
                    if it==0:
                        gender=element['author_gender']
                    else:
                        gender='Unknown'
                    
                    queries.append("CREATE (a:Author {name: '"+ auth +"', affiliation:'"+ aff +"',gender:'"+ gender +"' })")
                    
                    
                    queries.append("MATCH (a:Author {name: '"+ auth +"'}), (pn:Paper {paper_id: '"+ pid +"'}) CREATE (a)-[:writes]->(pn)")
                    queries.append("MATCH (a:Author {name: '"+ auth +"'}), (pn:Paper {paper_id: '"+ pid +"'}) CREATE (a)<-[:is_written_by]-(pn)")
                    queries.append("MATCH (a:Author {name: '"+ auth +"'}), (jn:Journal {name: '"+ jname +"'}) CREATE (a)-[:has_published_in]->(jn)")
                    
                    it += 1





            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    print(e)
                    print('Ya existe ese autor')
                

if __name__ == "__main__":
    neo4j_uri = "bolt://127.0.0.1:7687"
    neo4j_user = "neo4j"
    neo4j_password = "bitnami1"

    populator = Neo4jPopulator(neo4j_uri, neo4j_user, neo4j_password)

    try:
        populator.populate_data()
    finally:
        populator.close()