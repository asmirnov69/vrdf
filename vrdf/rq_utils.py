import rdflib
import pandas as pd
import re

def is_curie(string):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*:[a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, string))

def fix_init_bindings(g, init_bindings):
    if init_bindings is None:
        return None
    
    ret = {}
    for k, v in init_bindings.items():
        uri_s = v.toPython()
        if is_curie(uri_s):
            ret[k] = g.namespace_manager.expand_curie(uri_s)
        else:
            ret[k] = v
    return ret

def rq_df(g, rq, init_bindings = None):
    #ipdb.set_trace()
    rq_res = g.query(rq, initBindings=fix_init_bindings(g, init_bindings))
    if len(rq_res) == 0:
        ret = pd.DataFrame(columns=rq_res.vars)
    else:
        ret = pd.DataFrame.from_dict(rq_res.bindings)
        for c in rq_res.vars:
            if not c in ret.columns:
                ret[c] = None
        ret = ret.loc[:, rq_res.vars]
    #print(ret)

    ret.columns = [v[0:] for v in ret.columns]
    return ret
