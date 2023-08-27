import dataclasses
from .rq_utils import *

all_dataclass_objs = {}

'''
@dataclasses.dataclass
class SHACLProperty:
    type_pred: str # sh:datatype, sh:class, sh:nodeKind
    type_obj: str # correspong to type_pred e.g. sh:datatype xsd:int
    min_count: int
    max_count: int

@dataclasses.dataclass
class SHACLClass:
    py_classname: str
    properties: List[SHACLProperty]
'''

def get_py_type(g, type_uri, is_class):
    ret = None
    if is_class.toPython() == False:
        if type_uri == rdflib.XSD.string:
            ret = str
        elif type_uri == rdflib.XSD.integer:
            ret = int
        else:
            raise Exception(f"can't find datatype for URI {type_uri}")

    return ret

class ClassStoreEntry:
    def __init__(self, rdfs_class_uri, rdfs_class_def, dataclass_def):
        self.rdfs_class_uri = rdfs_class_uri
        self.rdfs_class_def = rdfs_class_def
        self.dataclass_def = dataclass_def

class ClassStore:
    """
    ClassStore will store both python and shacl definitions of loaded classes.
    It will be possible to do lookup by either class URI or python name
    The result of lookup will be pair (ref to SHACLClass, ref to python class)
    NOTE that all python classes will be dataclasses i.e. dataclasses.is_dataclass(x) == True
    where x is any handled python type.
    """
    def __init__(self):
        self.dataclasses = {} # key -> ClassStoreEntry

    def get_dataclass(self, dataclass_name):
        return self.dataclasses.get(dataclass_name).dataclass_def

    """
    NB: this version will fail if member ref recursion will be longer than one (self-refential case)
    E.g. class A: ref_b: B; class B: ref_a: A; -- is not going to work
    Covered case: class A: ref_a: A;
    """
    def create_dataclass__(self, g, rdfs_class_uri, path, incomplete_classes):
        curie = g.namespace_manager.normalizeUri(rdfs_class_uri).replace(":", '__', 1)
        if curie in self.dataclasses:            
            return self.dataclasses.get(curie)

        path.append(rdfs_class_uri)
        
        rq = """
        select ?m_name ?m_typename ?m_is_class { 
          ?rdfs_class sh:property ?sh_prop.
          ?sh_prop sh:path ?m_name.
          optional {?sh_prop sh:datatype ?m_typename. bind(false as ?m_is_class) }
          optional {?sh_prop sh:class ?m_typename. bind(true as ?m_is_class) }
        }
        """
        rdfs_class_def = rq_df(g, rq, {"rdfs_class": rdfs_class_uri})
        
        class_name = g.namespace_manager.normalizeUri(rdfs_class_uri).replace(':', '__', 1)
        if not class_name in self.dataclasses:
            fields = []
            rdfs_class_def['m_dataclass_field_name'] = None
            rdfs_class_def['m_dataclass_field_type'] = None
            for r in rdfs_class_def.itertuples():
                field = (g.namespace_manager.normalizeUri(r.m_name).replace(':', '__', 1), get_py_type(g, r.m_typename, r.m_is_class))
                rdfs_class_def.loc[r.Index, 'm_dataclass_field_name'] = field[0]
                rdfs_class_def.loc[r.Index, 'm_dataclass_field_type'] = field[1]

            l_rdfs_class_def = rdfs_class_def.set_index('m_dataclass_field_name')

            print("making dataclass:", class_name)
            print(rdfs_class_def)
            dataclass_obj = dataclasses.make_dataclass(class_name, [(r[0], r[1]) for _, r in rdfs_class_def.loc[:, ['m_dataclass_field_name', 'm_dataclass_field_type']].iterrows()])
            for fn, t in dataclass_obj.__dataclass_fields__.items():
                if t.type is None:
                    m_rdfs_class_uri = l_rdfs_class_def.loc[fn, 'm_typename']
                    #ipdb.set_trace()
                    if m_rdfs_class_uri in path:
                        incomplete_classes.add(rdfs_class_uri)
                    else:
                        new_t_class_store_entry = self.create_dataclass__(g, m_rdfs_class_uri, path, incomplete_classes)
                        dataclass_obj.__dataclass_fields__[fn].type = new_t_class_store_entry.dataclass_def

            #ipdb.set_trace()
            self.dataclasses[class_name] = ClassStoreEntry(rdfs_class_uri, rdfs_class_def, dataclass_obj)

            '''
            # check if some dataclasses were not loaded due to ref to itself
            for fn, t in dataclass_obj.__dataclass_fields__.items():
                if t.type is None:
                    #ipdb.set_trace()
                    new_t_class_store_entry = self.create_dataclass__(g, m_rdfs_class_uri)
                    dataclass_obj.__dataclass_fields__[fn].type = new_t_class_store_entry.dataclass_def
            '''
            path.pop()
            
        return self.dataclasses.get(class_name)
        
    def load_dataclass(self, g, rdfs_class_uri):
        rdfs_class_uri = rq_value(g, """
        select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
        """, {'rdfs_class': rdfs_class_uri})

        path = []
        incomplete_classes = set()
        class_store_entry = self.create_dataclass__(g, rdfs_class_uri, path, incomplete_classes)

        if len(incomplete_classes) > 0:
            print("incomplete_classes not empty")
            #ipdb.set_trace()
            for rdfs_class_uri in incomplete_classes:
                dataclass_name = g.namespace_manager.normalizeUri(rdfs_class_uri).replace(":", "__", 1)
                dataclass_obj = self.dataclasses[dataclass_name].dataclass_def
                rdfs_class_def = self.dataclasses[dataclass_name].rdfs_class_def.set_index('m_dataclass_field_name')
                for fn, t in dataclass_obj.__dataclass_fields__.items():
                    if t.type is None:
                        m_rdfs_class_uri = rdfs_class_def.loc[fn, 'm_typename']
                        curie = g.namespace_manager.normalizeUri(m_rdfs_class_uri).replace(":", '__', 1)
                        #ipdb.set_trace()
                        dataclass_obj.__dataclass_fields__[fn].type = self.dataclasses.get(curie).dataclass_def
        
        return class_store_entry

    def load_all_dataclasses(self, g, rdfs_class_uris = None):
        if rdfs_class_uris is None:
            rr = rq_ntuples(g, """
            select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
            """)

            rdfs_class_uris = [x.rdfs_class for x in rq_ntuples(g, """
            select ?rdfs_class { ?rdfs_class rdf:type rdfs:Class; rdf:type sh:NodeShape }
            """)]

        for rdfs_class_uri in rdfs_class_uris:
            self.load_dataclass(g, rdfs_class_uri)

        return self

    def load_object_local_parts__(self, g, class_store_entry, o_uri, path, incomplete_o_uris):
        global all_dataclass_objs
        if o_uri in all_dataclass_objs:
            return all_dataclass_objs.get(o_uri)

        path.append(o_uri)
        
        rq = "select ?m_name ?m_value { ?o ?m_name ?m_value }"
        rq_res = rq_ntuples(g, rq, init_bindings = {'o': o_uri})
        
        rq_res_d = {t.m_name:t.m_value.toPython() for t in rq_res}
        dataclass_init_d = {}
        for r in class_store_entry.rdfs_class_def.itertuples():
            field_name = r.m_dataclass_field_name
            dataclass_init_d[field_name] = None if not r.m_name in rq_res_d else rq_res_d.get(r.m_name)

        o = class_store_entry.dataclass_def(**dataclass_init_d)

        rdfs_class_def = class_store_entry.rdfs_class_def.set_index('m_dataclass_field_name')
        for f_name, f_type_descr in o.__dataclass_fields__.items():
            if f_type_descr.type is None:
                raise Exception(f"dataclass member without type: {f_name}")

            if not o.__dict__[f_name] is None and not isinstance(o.__dict__[f_name], f_type_descr.type):
                print(o.__dict__.get(f_name), f_name)
                m_o_uri = rdflib.URIRef(o.__dict__.get(f_name))
                if m_o_uri in path:
                    incomplete_o_uris.add(o_uri)
                else:
                    #ipdb.set_trace()
                    rdfs_class_uri = rdfs_class_def.loc[f_name, 'm_typename']
                    expected_m_t = self.create_dataclass__(g, rdfs_class_uri, None, None)
                    loaded_m_o = self.load_object_local_parts__(g, expected_m_t, m_o_uri, path, incomplete_o_uris)
                    if not isinstance(loaded_m_o, expected_m_t.dataclass_def):
                        raise Exception(f"type of member {f_name} is not what expected: {type(loaded_m_o)} {rdfs_class_uri}")
                    o.__dict__[f_name] = loaded_m_o

        all_dataclass_objs[o_uri] = o

        path.pop()
        return o
        
    def load_object(self, g, o_uri, o_rdfs_class_uri = None):
        if o_rdfs_class_uri is None:
            o_rdfs_class_uri = rq_value(g, "select ?o_class { ?o rdf:type ?o_class }", init_bindings = {"o": o_uri})

        #ipdb.set_trace()
        class_store_entry = self.load_dataclass(g, o_rdfs_class_uri)
        path = []
        incomplete_o_uris = set()
        ret = self.load_object_local_parts__(g, class_store_entry, o_uri, path, incomplete_o_uris)

        if len(incomplete_o_uris) > 0:
            print("incomplete_o_uris not empty", incomplete_o_uris)
            #ipdb.set_trace()
            rdfs_class_def = class_store_entry.rdfs_class_def.set_index('m_dataclass_field_name')
            for o_uri in incomplete_o_uris:
                o = all_dataclass_objs.get(o_uri)
                for f_name, f_type_descr in o.__dataclass_fields__.items():
                    if f_type_descr.type is None:
                        raise Exception(f"dataclass member without type: {f_name}")

                    if not o.__dict__[f_name] is None and not isinstance(o.__dict__[f_name], f_type_descr.type):
                        print(o.__dict__.get(f_name), f_name)
                        m_o_uri = rdflib.URIRef(o.__dict__.get(f_name))
                        loaded_m_o = all_dataclass_objs.get(m_o_uri)
                        o.__dict__[f_name] = loaded_m_o


        return ret
    
    
all_dataclasses = ClassStore()    

def load_dataclass(g, rdfs_class_uri):
    global all_dataclasses
    return all_dataclasses.load_dataclass(g, rdfs_class_uri)

def load_all_dataclasses(g):
    global all_dataclasses
    return all_dataclasses.load_all_dataclasses(g)

def load_object(g, o_uri):
    global all_dataclasses
    return all_dataclasses.load_object(g, o_uri)
