from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST


def generate_endpoint():
    '''Create the SPARQL Endpoint with the Graph update protocol/rights'''

    # Endpoint to be queried
    sparql = SPARQLWrapper('http://131.180.205.92:8890/sparql')
    sparql.setHTTPAuth(DIGEST)
    # login info (Default username and password is 'dba', 'dba' )
    sparql.setCredentials('dba', 'piresearch')
    sparql.setMethod(POST)
    # default graph
    sparql.addDefaultGraph('http://131.180.205.92:8890/test')
    return sparql


def clear_graph(sparql):
    '''Delete all stored triples.'''

    sparql.setQuery(
        '''
        DELETE
        WHERE{
        ?s ?p ?o.
        }
        ''')
    sparql.query()


def insert_query(sparql, triple):
    # inserts the given triple into the graph defined within pre

    # create prefixes and select the Graph
    pre = '''  
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>  
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            INSERT DATA 
            { GRAPH <http://131.180.205.92:8890/test> 
            { '''
    post = ' } }'
    sparql.setQuery(pre + triple + post)  # set query
    sparql.query()


def basic_query(sparql, s=None, p=None, o=None):
    # one line query for the desired combination of subject, predicate,
    # & object

    pre = 'SELECT * WHERE{'
    # if no subject, predicate or object are given then use general variables
    if s is None:
        s = '?s'
    if p is None:
        p = '?p'
    if o is None:
        o = '?o'
    sparql.setQuery(pre + s + ' ' + p + ' ' + o + '. }')
    sparql.setReturnFormat(JSON)  # JSON format best for reading output
    results = sparql.query().convert()
    if len(results['results']['bindings']) == 0:  # if no result return nothing
        return None
    else:
        # [i]['s'/'o'/'p']['value'] syntax for accessing the result
        return results['results']['bindings']


def complex_query(sparql, triple, var=None, limit=None):
    # Set which variables the query should return
    if var is not None:
        if type(var).__name__ == 'str':
            pre = 'SELECT ?' + var + ' WHERE{ '
        elif type(var).__name__ == 'list':
            pre = 'SELECT '
            for v in var:
                pre += '?' + v + ' '
            pre += 'WHERE{ '
        else:
            pre = 'SELECT * WHERE{ '
    else:
        pre = 'SELECT * WHERE{ '

    post = ' }'

    # Add limit statement to query if desired
    if limit is not None:
        post2 = 'LIMIT ' + str(limit)
    else:
        post2 = ''

    sparql.setQuery(pre+triple+post+post2)

    sparql.setReturnFormat(JSON)  # JSON format best for reading output
    results = sparql.query().convert()
    if len(results['results']['bindings']) == 0:  # if no result return nothing
        return None
    else:
        return results['results']['bindings']  # [i]['s'/'o'/'p']['value'] syntax for accessing the result


def describe_query(sparql, subject):
    '''Query all triples which have the given 'subject' as the subject.'''

    query = 'CONSTRUCT { ' + entity_format(subject) + ' ?p ?o. } WHERE { ' + entity_format(subject) + ' ?p ?o. }'
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)  # JSON format best for reading output
    results = sparql.query().convert()

    if len(results['results']['bindings']) == 0:  # if no result return nothing
        return None
    else:
        return results['results']['bindings']  # [i]['s'/'o'/'p']['value'] syntax for accessing the result


def delete_query_triple(sparql, triple):
    # delete the given triple for the knowledge graph

    pre = '''
    DELETE
    WHERE{
    '''
    post = '}'
    sparql.setQuery(pre + triple + post)
    sparql.query()


def delete_query_var(sparql, s=None, p=None, o=None):
    # delete all triples with the given combination of subject, predicate, object

    pre = '''
       DELETE
       WHERE{
       '''
    if s is None:  # if no subject, predicate or object are given then use general variables
        s = '?s'
    if p is None:
        p = '?p'
    if o is None:
        o = '?o'
    sparql.setQuery(pre + s + ' ' + p + ' ' + o + '. }')
    sparql.query()


def purge_entity(sparql, entity):
    # delete all triples with entity as the subject and return all objects to which entity was connected to
    sub_triples = basic_query(sparql, s=entity_format(entity))
    obj_triples = basic_query(sparql, o=entity_format(entity))

    # TODO: changed to single line delete queries because the endpoint could not handle large blocks of text...
    #  Takes a While
    # Could implement that every third triples get put together and is deleted to increase functioning time
    if sub_triples is not None:
        for triple in sub_triples:
            delete = entity_format(entity) + entity_format(triple['p']['value']) + entity_format(triple['o']['value']) + '. '
            delete_query_triple(sparql, delete)

    if obj_triples is not None:
        for triple in obj_triples:
            delete = entity_format(triple['s']['value']) + entity_format(triple['p']['value']) + entity_format(entity) + '. '
            delete_query_triple(sparql, delete)


def entity_format(entity):
    # Structures the entity as an IRI
    return '<' + entity + '> '


def literal_format(value):
    # Structures the value as a string literal
    return '\'' + value + '\''

# TODO: If I have extra time, write a function which uses rdflib and jupyterhub to visualize a downloaded set of
#  triples. Maybe using the construct function or something like that.

ep = generate_endpoint()

ep.clear_graph()