import ipdb
import pandas as pd

def rq_rows(g, rq, init_bindings = None):
    df = rq_df(g, rq, init_bindings = init_bindings)
    return list(df.columns), [list(x[1]) for x in df.iterrows()]

def rq_df(g, rq, init_bindings = None):
    rq_res = g.query(rq, initBindings=init_bindings)
    return (
        pd.DataFrame.from_dict(rq_res.bindings).loc[:, rq_res.vars]
        if len(rq_res) > 0
        else pd.DataFrame(columns=rq_res.vars)
    )
