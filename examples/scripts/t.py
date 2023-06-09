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
    res = g.query(rq, initBindings = {"c_uri": c_uri}, base = base_uri)
    return res

if __name__ == "__main__":
    g = vrdf.load_rdf(["./alice-bob.ttl", "./alice-bob-shacl.ttl"])
    #print([spo for spo in g])

    rq = "select ?c (count(?i) as ?ic) { ?c rdf:type rdfs:Class. ?i rdf:type ?c } group by ?c"
    res = g.query(rq)
    for c_uri, ic in res:
        print(ic, [r for r in get_class_details(g, c_uri)])
    

    

