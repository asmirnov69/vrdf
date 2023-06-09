import vrdf

base_uri = "http://example.org/"

def get_class_details(g, c_uri):
    rq = """
    select ?c_uri ?c_member_name ?c_member_type { 
    ?c_uri rdf:type rdfs:Class;
           rdf:type sh:NodeShape;
           sh:property ?c_member.
    ?c_member sh:path ?c_member_name.
    optional { ?c_member sh:datatype ?c_member_type }
    optional { ?c_member sh:class ?c_member_type }
    optional { ?c_member sh:node ?c_member_type }
    }
    """
    res = vrdf.rq_df(g, rq, init_bindings = {"c_uri": c_uri}, base_uri = base_uri)
    return res

if __name__ == "__main__":
    g = vrdf.load_rdf(["./alice-bob.ttl", "./alice-bob-shacl.ttl"])

    rq = "select ?c (count(?i) as ?ic) { ?c rdf:type rdfs:Class. optional {?i rdf:type ?c} } group by ?c"
    _, res = vrdf.rq_rows(g, rq)
    
    for c_uri, ic in res:
        print("c_uri:", c_uri, ", ic:", ic)
        print(get_class_details(g, c_uri))
    

    

