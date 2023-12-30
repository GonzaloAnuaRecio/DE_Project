import mysql.connector
import json

con = mysql.connector.connect(
    host="0.0.0.0",
    user="root",
    password="root",
)

executor = con.cursor()


executor.execute("CREATE DATABASE IF NOT EXISTS PapersDB")
executor.execute("USE PapersDB")


#Creacion de la base de datos 
executor.execute("""
CREATE TABLE IF NOT EXISTS Authors (
    Author_ID INT PRIMARY KEY,
    Author_Name VARCHAR(100) NOT NULL,
    Author_Affiliation VARCHAR(100) NOT NULL,
    Author_Gender  VARCHAR(20) NOT NULL
); """)

executor.execute("""
CREATE TABLE IF NOT EXISTS Papers (
    Paper_ID VARCHAR(200) PRIMARY KEY,
    Doi VARCHAR(45) NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Update_Date DATE NOT NULL,
    Number_Of_Pages INT NOT NULL,
    Publish_Date DATE NOT NULL ,
    Category VARCHAR(200) NOT NULL
); """)

executor.execute("""
CREATE TABLE IF NOT EXISTS Journals (
    Journal_ID INT PRIMARY KEY,
    Journal_Name VARCHAR(200) NOT NULL,
    Journal_Type VARCHAR(50) NOT NULL
); """)
executor.execute("""
CREATE TABLE IF NOT EXISTS Citations (
    Paper1 VARCHAR(200),
    Paper2 VARCHAR(200),

    PRIMARY KEY(Paper1, Paper2),
    FOREIGN KEY (Paper1) REFERENCES Papers(Paper_ID )
    
); """)

executor.execute("""
CREATE TABLE IF NOT EXISTS Papers_ID (
    Paper_ID VARCHAR(200),
    Author_ID INT,
    Journal_ID INT,
    PRIMARY KEY (Paper_id, Journal_ID, Author_ID),
    
    FOREIGN KEY (Paper_ID) REFERENCES Papers(Paper_ID),
    FOREIGN KEY (Author_ID) REFERENCES Authors(Author_ID),
    FOREIGN KEY (Journal_ID) REFERENCES Journals(Journal_ID)
); """)

known_authors_name = []
known_authors_id = []
known_journals_names = []
known_journals_ids = []

#In case there is not journal the fk points here
try:
    executor.execute("""
                INSERT INTO Journals (Journal_ID, Journal_Name, Journal_Type) VALUES
                (%s, %s, %s)
            """, (1, "Non", "Non"))
    known_journals_ids.append(1)
except Exception as e:
    print(e)
    print('Already exists')

print("a")
#Insercion de los datos
with open('ejemplo2.json') as json_data:
    data = json.load(json_data)


#In case it is not the first iteration we must void repeating ids
#Authors
executor.execute("SELECT Author_ID, Author_Name from Authors")
author_results = executor.fetchall()

for id_name in author_results:
    known_authors_id.append(id_name[0])
    known_authors_name.append(id_name[1])



if len(known_authors_id) == 0:
    idAuthor=1
else: 
    idAuthor = known_authors_id[len(known_authors_id)-1] + 1


#Journals
executor.execute("SELECT Journal_ID, Journal_Name from Journals")
journal_results = executor.fetchall()

for id_name in journal_results:
    known_journals_ids.append(id_name[0])
    known_journals_names.append(id_name[1])

idJournal = known_journals_ids[len(known_journals_ids)-1] + 1
if idJournal == 1:
    idJournal += 1


for element in data: 
    iterationAuthors = []
    it = 0 
    #Entrada en autores, no tiene posibles nulls
    #Asumimos que no hay mas de una afiliacion
    for auth in element['author_name']:


        if auth not in known_authors_name:
        
            #We only know the submitter's gender
            if it == 0:
                gender =  element['author_gender']
            else:
                gender = "Unknown"
            

            executor.execute("""
                INSERT INTO Authors (Author_ID, Author_Name, Author_Affiliation, Author_Gender) VALUES
                (%s, %s, %s, %s)
            """, (idAuthor, auth, element['author_affiliation'], gender))

            known_authors_name.append(auth)
            known_authors_id.append(idAuthor)

            #Contadores
            auxAuth = idAuthor
            idAuthor +=1
        else: 
            position = known_authors_name.index(auth)
            auxAuth= known_authors_id[position]
            
        iterationAuthors.append(auxAuth)
        it +=1
    
    #Entrada de paper
    try:
        executor.execute("""
            INSERT INTO Papers (Paper_ID, Doi, Title, Update_Date, Number_Of_Pages, Publish_Date, Category) VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        """, (element['paper_id'], element['paper_doi'], element['paper_title'], element['paper_update_date'], 
        element['paper_number_of_pages'], element['paper_publication_date'], element['paper_category']))
    except Exception as e:
        print(e)
       # print(f'The paper is already in the DB. The id is: {element['paper_id']}')
    print('-------------------------------')
    
    #Citations
    for cit in element['citations']:
        executor.execute("""
                    INSERT INTO Citations (paper1, paper2) VALUES
                    (%s, %s)
                """, (element['paper_id'], cit))

    #Entrada Journal
    auxId = idJournal

    if element['journal_name'] != 'Non':
        if element['journal_name'] not in known_journals_names: 
            executor.execute("""
                INSERT INTO Journals (Journal_ID, Journal_Name, Journal_type) VALUES
                (%s, %s, %s)
            """, (auxId, element['journal_name'], element['journal_type']))

            known_journals_names.append(element['journal_name'])
            known_journals_ids.append(auxId)
        else:

            position = known_journals_names.index(element['journal_name'])
            auxId = known_journals_ids[position]

    else:
        auxId = 1
   
    con.commit()
    #Fact Table
    for authID in iterationAuthors:
        print(element['paper_id'], authID , auxId)
        executor.execute("""
                INSERT INTO Papers_ID (Paper_ID, Author_ID, Journal_ID) VALUES
                (%s, %s, %s)
            """, (element['paper_id'], authID , auxId))

    
    idJournal += 1 






con.commit()
con.close()
