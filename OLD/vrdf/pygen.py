import vrdf
import sys

        

if __name__ == "__main__":
    g = vrdf.load_rdf("./secmaster.shacl.ttl")
    gen_py_defs(g)
    
    
