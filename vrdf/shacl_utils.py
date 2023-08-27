import dataclasses
from .rq_utils import *
from .class_store import *

'''
def get_py_type(g, type_uri, is_class):
    ret = None
    if is_class.toPython() == False:
        if type_uri == rdflib.XSD.string:
            ret = str
        elif type_uri == rdflib.XSD.integer:
            ret = int
    else:
        print(type_uri)
        #ipdb.set_trace()
        curie = g.namespace_manager.normalizeUri(type_uri)
        ret = curie.replace(':', '__', 1)
        
    return ret

def create_py_dataclass__(g, rdfs_class_uri, rdfs_class_dets):
    class_name = g.namespace_manager.normalizeUri(rdfs_class_uri).replace(':', '__', 1)
    fields = []
    for r in rdfs_class_dets.itertuples():
        field = (g.namespace_manager.normalizeUri(r.m_name).replace(':', '__', 1), get_py_type(g, r.m_typename, r.m_is_class))
        fields.append(field)

    print("making dataclass:", class_name, fields)
    class_obj = dataclasses.make_dataclass(class_name, fields)

    global all_shacl_def_classes
    all_shacl_def_classes[class_name] = class_obj

    return class_name, class_obj
    
def load_py_dataclass(g, rdfs_class_uri):
    rdfs_class_uri = rq_value(g, """
    select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
    """, {'rdfs_class': rdfs_class_uri})

    rq = """
    select ?m_name ?m_typename ?m_is_class { 
      ?rdfs_class sh:property ?sh_prop.
      ?sh_prop sh:path ?m_name.
      optional {?sh_prop sh:datatype ?m_typename. bind(false as ?m_is_class) }
      optional {?sh_prop sh:class ?m_typename. bind(true as ?m_is_class) }
    }
    """
    rdfs_class_dets = rq_df(g, rq, {"rdfs_class": rdfs_class_uri})

    class_name, class_obj = create_py_dataclass__(g, rdfs_class_uri, rdfs_class_dets)
    return class_obj


def load_py_dataclasses(g, rdfs_class_uris = None):
    if rdfs_class_uris is None:
        rr = rq_ntuples(g, """
        select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
        """)
        ipdb.set_trace()
        rdfs_class_uris = [x.rdfs_class for x in rq_ntuples(g, """
        select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
        """)]

    ret = []
    ipdb.set_trace()
    for rdfs_class_uri in rdfs_class_uris:
        rq = """
        select ?m_name ?m_typename ?m_is_class { 
        ?rdfs_class sh:property ?sh_prop.
        ?sh_prop sh:path ?m_name.
        optional {?sh_prop sh:datatype ?m_typename. bind(false as ?m_is_class) }
        optional {?sh_prop sh:class ?m_typename. bind(true as ?m_is_class) }
        }
        """
        rdfs_class_dets = rq_df(g, rq, {"rdfs_class": rdfs_class_uri})

        ret.append(create_py_dataclass__(g, rdfs_class_uri, rdfs_class_dets))        

    # replace all strings with correponding classes
    global all_shacl_def_classes
    for _, py_dataclass in ret:
        for f in py_dataclass.__dataclass_fields__.values():
            if isinstance(f.type, str):
                f.type = all_shacl_def_classes.get(f.type)
        
    return dict(ret)

def load_py_obj_local_details(g, o_uri, o_class_uri = None):
    if o_class_uri is None:
        o_class_uri = rq_value(g, "select ?o_class { ?o rdf:type ?o_class }", init_bindings = {"o": o_uri})
        
    o_class_name = g.namespace_manager.normalizeUri(o_class_uri).replace(':', '__', 1)
    global all_shacl_def_classes
    py_class = all_shacl_def_classes.get(o_class_name)

    rq = "
    
    init_params = {}
    for p_name, p_v in ...:
        init_params[p_name] = p_v
        
    ret_o = py_class(... data to initialize obj ...)
    return ret_o
'''

