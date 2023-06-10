import ipdb
import rdflib

base_uri = "http://example.org/"

def load_rdf(rdf_fn):
    if isinstance(rdf_fn, str):
        rdf_fns = [rdf_fn]
    elif isinstance(rdf_fn, list):
        rdf_fns = rdf_fn
    else:
        raise Exception("rdf_fn should be either str or list")
    
    g = rdflib.Graph()
    g.namespace_manager.bind("", rdflib.Namespace(base_uri))
    
    for rdf_fn in rdf_fns:
        with open(rdf_fn, "r") as fd:
            g.parse(fd)

    return g
