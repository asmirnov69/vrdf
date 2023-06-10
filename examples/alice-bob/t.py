import ipdb
import vrdf
import sys
from collections import namedtuple

def get_class_details(g, c_uri, c_doc):
    rq = """
    select ?c_member_name ?c_member_type ?is_class { 
    ?c_uri rdf:type rdfs:Class;
           rdf:type sh:NodeShape;
           sh:property ?c_member.
    ?c_member sh:path ?c_member_name.
    optional { ?c_member sh:datatype ?c_member_type. bind(false as ?is_class) }
    optional { ?c_member sh:class ?c_member_type. bind(true as ?is_class) }
    optional { ?c_member sh:node ?c_member_type. bind(false as ?is_class) }
    }
    """
    class_members = vrdf.rq_df(g, rq, init_bindings = {"c_uri": c_uri})
    return namedtuple("ClassDef", ["c_uri", "c_doc", "c_members"])(c_uri, c_doc, class_members)

def uri_to_dot_id(uri):
    return 'n' + str(hash(uri)).replace("-", "d")

def dump_shacl_diagram(g, shacl_classes_d):
    out_fd = sys.stdout
    print(f"digraph {{", file = out_fd)
    print(f"  node [shape=plaintext];", file = out_fd)

    # nodes
    for v in shacl_classes_d.values():
        c_uri = v.c_uri
        c_doc = v.c_doc
        c_dets = v.c_members
        print(f"  {uri_to_dot_id(c_uri)} [", file = out_fd)

        if c_doc:
            print(f'     tooltip="{c_doc}"', file = out_fd)
        print(f"     label=<", file = out_fd)

        #ipdb.set_trace()
        print(f'     <table border="0" cellborder="1" cellspacing="0">', file = out_fd)
        class_title = c_uri.n3(g.namespace_manager)
        print(f'       <tr><td colspan="2" bgcolor="#C0C0C0"><b>{class_title}</b></td></tr>', file = out_fd)
        for r in c_dets.iterrows():
            member_name = r[1][0].n3(g.namespace_manager)
            member_type = r[1][1].n3(g.namespace_manager)
            print(f'        <tr><td>{member_name}</td><td><i>{member_type}</i></td></tr>', file = out_fd)
        print(f'     </table>', file = out_fd)

        print(f"   >", file = out_fd)
        print(f"  ];", file = out_fd)


    # edges
    for v in shacl_classes_d.values():
        c_uri = v.c_uri
        c_doc = v.c_doc
        c_dets = v.c_members
        #ipdb.set_trace()
        for r in c_dets.iterrows():
            member_name = r[1][0].n3(g.namespace_manager)
            member_type = r[1][1] # MUST BE as-is (i.e. no n3 or other normalizaitions) since is used to make node id using uri
            is_class = r[1][2].toPython()
            if is_class:
                print(f'    {uri_to_dot_id(c_uri)} -> {uri_to_dot_id(member_type)} [label = "{member_name}", fontsize=8, fontcolor=blue, fontname="Arial"]', file = out_fd)
        
    print(f"}}", file = out_fd)        
    
if __name__ == "__main__":
    g = vrdf.load_rdf(["./alice-bob.ttl", "./alice-bob-shacl.ttl"])

    rq = "select ?c ?c_doc { ?c rdf:type rdfs:Class. optional {?c vrdf:comment ?c_doc} }"
    _, res = vrdf.rq_rows(g, rq)
    
    shacl_classes = {}
    for c_uri, c_doc in res:
        #print("c_uri:", c_uri, ", c_doc:", c_doc)
        shacl_classes[c_uri] = get_class_details(g, c_uri, c_doc)
    
    dump_shacl_diagram(g, shacl_classes)
