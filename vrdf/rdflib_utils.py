import ipdb
import glob, os.path
import rdflib

def load_rdf_graph(rdf_fn):
    if isinstance(rdf_fn, str):
        rdf_fns = [rdf_fn]
    elif isinstance(rdf_fn, list):
        rdf_fns = rdf_fn
    else:
        raise Exception("rdf_fn should be either str or list")
    
    g = rdflib.Graph()
    
    for rdf_fn in rdf_fns:
        if not os.path.exists(rdf_fn):
            fns = glob.glob(rdf_fn)
        else:
            fns = [rdf_fn]
        for fn in fns:
            #print(f"loading {fn}")
            with open(fn, "r") as fd:
                g.parse(fd)

    #for ns in g.namespaces():
    #    print(ns)
    #    g.namespace_manager.bind(ns[0], ns[1])
                
    return g
