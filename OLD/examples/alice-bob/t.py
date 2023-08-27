import ipdb
import vrdf
import sys
from collections import namedtuple
import inspect

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

def dump_py_defs(g, shacl_classes_d):
    out_fd = sys.stdout
    rq = "select ?c ?c_doc { ?c rdf:type rdfs:Class. optional {?c vrdf:comment ?c_doc} }"
    _, res = vrdf.rq_rows(g, rq)

    for v in shacl_classes_d.values():
        c_uri = v.c_uri
        c_doc = v.c_doc
        c_dets = v.c_members
        
        print(f"@dataclass\nclass {c_uri.n3(g.namespace_manager)}:", file = out_fd)
        for i, r in c_dets.iterrows():
            member_name = r[0].n3(g.namespace_manager)
            member_type = r[1].n3(g.namespace_manager)
            print(f"\t{member_name}: {member_type}", file = out_fd)
        print(f"", file = out_fd)
        print("\tdef load(self, o_uri):", file = out_fd)
        rq = """
        select ?m1 ?m2 {{ ?o_uri rdf:type ?c_uri; {member_name} ?m1 }}
        """

def create_py_defs(g, shacl_classes_d):
    rq = "select ?c ?c_doc { ?c rdf:type rdfs:Class. optional {?c vrdf:comment ?c_doc} }"
    _, res = vrdf.rq_rows(g, rq)

    ret_new_class_defs = []
    for v in shacl_classes_d.values():
        c_uri = v.c_uri
        c_doc = v.c_doc
        c_dets = v.c_members

        new_class_def = type(c_uri.n3(), (object,), {
            # data members
        })
        ret_new_class_defs.append(new_class_def)

    return ret_new_class_defs        
        
if __name__ == "__main__":
    g = vrdf.load_rdf_graph(["./alice-bob.ttl", "./alice-bob.shacl.ttl"])

    rq = "select ?c ?c_doc { ?c rdf:type rdfs:Class. optional {?c vrdf:comment ?c_doc} }"
    _, res = vrdf.rq_rows(g, rq)
    
    shacl_classes = {}
    for c_uri, c_doc in res:
        #print("c_uri:", c_uri, ", c_doc:", c_doc)
        shacl_classes[c_uri] = get_class_details(g, c_uri, c_doc)
    
    dump_shacl_diagram(g, shacl_classes)
    #dump_py_defs(g, shacl_classes)
    class_defs = create_py_defs(g, shacl_classes)

    for MyClass in class_defs:
        attributes = MyClass.__dict__
        bases = ', '.join(base.__name__ for base in MyClass.__bases__)

        # Generate the class definition
        definition = f"class {MyClass.__name__}({bases}):\n"
        for name, value in attributes.items():
            definition += f"    {name} = {repr(value)}\n"

        # Print the generated class definition
        print(definition)
        
