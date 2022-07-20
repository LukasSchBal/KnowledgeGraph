import rdflib

# SELECT query

g = rdflib.Graph()
g.parse("http://danbri.org/foaf.rdf#")

knows_query = """
SELECT DISTINCT ?aname ?bname
WHERE {
    ?a foaf:knows ?b .
    ?a foaf:name ?aname .
    ?b foaf:name ?bname .
}"""

qres = g.query(knows_query)
for row in qres:
    print(f"{row.aname} knows {row.bname}")

# Query SPARQL endpoint

g = rdflib.Graph()
qres = g.query(
    """
    SELECT ?s
    WHERE {
      SERVICE <http://dbpedia.org/sparql> {
        ?s a ?o .
      }
    }
    LIMIT 3
    """
)

for row in qres:
    print(row.s)