import pandas as pd

def rq_rows(g, rq, init_bindings = None, base_uri = None):
    rq_res = g.query(rq, base=base_uri, initBindings=init_bindings)
    cols = [k for k in rq_res.bindings[0].keys()]
    rows = [list(v.values()) for v in rq_res.bindings]
    return cols, rows


def rq_df(g, rq, init_bindings = None, base_uri = None):
    rq_res = g.query(rq, base=base_uri, initBindings=init_bindings)
    return (
        pd.DataFrame.from_dict(rq_res.bindings).loc[:, rq_res.vars]
        if len(rq_res) > 0
        else pd.DataFrame(columns=rq_res.vars)
    )
