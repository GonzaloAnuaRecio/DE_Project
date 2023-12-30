import json
from langdetect import detect
import crossref_commons.retrieval
import random
import requests
import sys

n = 5000 #Number of data to take
if len(sys.argv) > 2:
    n = int(sys.argv[2])

crossrefs = {}
def openData():
    data = []
    with open('../arxiv-metadata-oai-snapshot.json', 'r') as file:
        for line in file:
            if len(data) <= n:
                data.append(json.loads(line))
    return data

def cleansing(data):
    def check_pages(paper):
        #Articles where the comments follow structure: comments = n pages .... and n > 4
        try:
            if int(paper["comments"][0:paper["comments"].index("pages")]) > 4:
                return True
        except:
            return False #Half of n follow the structure
    
    def check_authors(paper):
        #Articles with authors
        return bool(paper["authors"])

    def check_doi(paper):
        #Articles with doi
        return bool(i["doi"])

    def remove(paper):
        attr_delete = ["report-no", "license", "created", "submitter", "versions", "abstract", "authors_parsed"]
        for i in  attr_delete:
            try: # It may happen that a paper doesn't have all the attributes
                del paper[i]
            except:
                pass

    def clean_author(crossref):
        #Normalize author names using crossref API
        given, family = [], []
        for i in crossref["author"]:
            try:
                given.append(i["given"].lower())
            except:
                given.append("Unkown")
            try:
                family.append(i["given"].lower())
            except:
                family.append("Unkown")
        return ["".join(f"{i} {j}".split()) for i, j in zip(given, family)]
    dois = set()
    clean = []
    for idx, i in enumerate(data):
        if check_pages(i) and check_authors(i) and check_doi(i) and not i["doi"] in dois:
            try: # It may happen that crossref doesn't have the DOI and raises an error
                crossref = crossref_commons.retrieval.get_publication_as_json(i["doi"])
            except:
                continue
            crossrefs[i["doi"]] = crossref # So we don't have to request again to the API
            if "author" in crossref:
                i["authors"] = clean_author(crossref)
            remove(i)

            if not i["journal-ref"]:
                i["journal-ref"] = "None"
            clean.append(i)
            dois.add(i["doi"])
    return clean

def transformation(data):
    def get_number_pages(paper):
         # Get the number of pages of a given paper
        return int(paper["comments"][0:paper["comments"].index("pages")])

    def get_type(paper):
         # Get the correct type of publication in crossref format
        return crossrefs[paper["doi"]]["type"]
    def get_affiliation(paper):
        # api-endpoint
        URL = "https://dblp.org/search/author/api?"
        
        # defining a params dict for the parameters to be sent to the API
        try:
            PARAMS = {"q":paper["authors"][0], "format":"json"}

            r = requests.get(url = URL, params = PARAMS)
            # extracting data in json format
            data = r.json()
            return data["result"]["hits"]["hit"][0]["info"]["notes"]["note"]["text"]
        except:
            return "Unknown"
    def get_citation(paper):
        references = []
        if "reference" in crossrefs[paper["doi"]]:
            for i in crossrefs[paper["doi"]]["reference"]:
                if "DOI" in i:
                    references.append(i["DOI"])
        return references

    def name_change(paper):
        names = {"id": "paper_id", 
                "authors": "author_name", 
                "title": "paper_title",
                "journal-ref": "journal_name",
                "doi": "paper_doi",
                "update_date": "paper_update_date",
                "categories": "paper_category"}
        for i, j in names.items():
            paper[j] = paper.pop(i) 
        return paper
    def get_publish_date(paper):
        try:
            date = (crossrefs[paper["doi"]]["published"]["date-parts"][0])
            if len(date) < 3: #Sometimes only year is available
                y, m ,d = (crossrefs[paper["doi"]]["published"]["date-parts"][0][0], 1, 1)
            else:
                y, m, d = crossrefs[paper["doi"]]["published"]["date-parts"][0]
            date = f"{y}-{m}-{d}"
        except:
            date = "0-0-0"
        return (date)

    for i in data:
        i["journal_type"] = get_type(i)
        i["paper_number_of_pages"] = get_number_pages(i)
        i["author_affiliation"] = get_affiliation(i)
        i["citations"] = get_citation(i)
        i["paper_publication_date"] = get_publish_date(i) 
        del i["comments"]
        i["author_gender"] = "Unkown"

        i = name_change(i)
    return data
data = openData()
data = cleansing(data)
data=  transformation(data)
with open('test.json', 'w') as fout:
    json.dump(data , fout)
