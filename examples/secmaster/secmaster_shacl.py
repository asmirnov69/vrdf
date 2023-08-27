@dataclass
class Security:
    name: str

@dataclass
class Equity(Security):
    ticker: str
    sector: GICSSector

@dataclass
class GICSSector:
    name: str
    code: str

o_uri = ...
pyo = load_py_object(o_uri)
pyo.name = "newname"
save_py_object(pyo)
