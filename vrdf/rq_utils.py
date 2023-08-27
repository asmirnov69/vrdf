import ipdb, rdflib
import pandas as pd
import re
from collections import namedtuple

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

def rq_value(g, rq, init_bindings = None, default = None):
    rq_res = g.query(rq, initBindings = fix_init_bindings(g, init_bindings))
    if len(rq_res) == 0 or (len(rq_res) == 1 and rq_res.bindings[0] == {}):
        raise Exception(f"rq_tuple: nothing returned, rq was '{rq}'")
    if len(rq_res) > 1:
        raise Exception(f"rq_tuple: {len(rq_res)} rows returned, rq was {rq}")
    if len(rq_res.vars) != 1:
        raise Exception(f"rq_value: must be only one value")

    return [x[0] for x in rq_res][0]

def rq_values(g, rq, init_bindings = None):
    rq_res = g.query(rq, initBindings = fix_init_bindings(g, init_bindings))
    if len(rq_res.vars) != 1:
        raise Exception(f"rq_value: must be only one value")

    return [x[0] for x in rq_res]


def rq_ntuple(g, rq, init_bindings = None):
    rq_res = g.query(rq, initBindings = fix_init_bindings(g, init_bindings))
    if len(rq_res) == 0:
        raise Exception(f"rq_tuple: nothing returned, rq was {rq}")
    if len(rq_res) > 1:
        raise Exception(f"rq_tuple: {len(rq_res)} rows returned, rq was {rq}")
    ret_nt = namedtuple('NT', [x[0:] for x in rq_res.vars])

    raise Exception("not tested") # NB: finish and test
    return ret_nt([x[0] for x in rq_res][0])

def rq_ntuples(g, rq, init_bindings = None):
    rq_res = g.query(rq, initBindings = fix_init_bindings(g, init_bindings))
    ret_nt = namedtuple('NT', [x[0:] for x in rq_res.vars])
    return [ret_nt(*x) for x in rq_res]

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
