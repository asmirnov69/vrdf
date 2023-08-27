import pandas as pd

data_fn = "https://raw.githubusercontent.com/fja05680/sp500/master/sp500.csv"
data_df = pd.read_csv(data_fn)

g = rdflib.Graph()
for i, r in data_df.iterrows():
    eq_n = make_uri(g, r.Symbol, ":Equity")
    g.add(eq_n, ":ticker", r.Symbol)
    g.add(eq_n, ":name", r.Security)

g.serialize(destination = "a.ttl")
