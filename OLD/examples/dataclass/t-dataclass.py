import ipdb
import uuid
import dataclasses
import vrdf, rdflib

def get_obj_uri(g, obj):
    if obj is None:
        return rdflib.RDF.nil
    
    if not hasattr(obj, 'obj_uri'):
        type_name = type(obj).__name__
        obj.obj_uri = rdflib.URIRef(type_name + '#' + str(uuid.uuid4()))
        g.add((obj.obj_uri, rdflib.RDF.type, rdflib.URIRef(":" + type_name)))

    return obj.obj_uri

def save_obj(g, obj):
    obj_uri = get_obj_uri(g, obj)
    obj_attrs = type(obj).__annotations__

    #ipdb.set_trace()
    for m, m_typename in obj_attrs.items():
        print(m, m_typename)
        v = getattr(obj, m)
        if m_typename in ['str', 'int']:
            if not v is None:
                g.add((obj_uri, rdflib.URIRef(m), rdflib.Literal(v)))
        else:
            m_type = globals().get(m_typename)
            if m_type is None:
                raise Exception(f"unclear how to save {m}")                
            if not dataclasses.is_dataclass(m_type):
                raise Exception(f"{m_type} is not dataclass")
            if not v is None:
                m_uri = get_obj_uri(g, v)
                g.add((obj_uri, rdflib.URIRef(m), m_uri))
                save_obj(g, v)

                
if __name__ == "__main__":
    g = vrdf.load_rdf_graph("ttl-files/*.ttl")
    out_g = rdflib.Graph()

    if 0:
        Person = vrdf.load_dataclass(g, rdflib.URIRef("foaf:Person")).dataclass_def
        Movie = vrdf.load_dataclass(g, rdflib.URIRef("wd:Movie")).dataclass_def
        print(Person)
        print(Movie)
        p = Person(foaf__name = 'Ura', __watched = None, foaf__knows = None, foaf__age = 39)
        print(p, [(k, v.type) for k, v in p.__dataclass_fields__.items()])
        ipdb.set_trace()
        m = Movie(wd__title = 'Utki')
        print(m, [(k, v.type) for k, v in m.__dataclass_fields__.items()])

    if 0:
        dataclasses = vrdf.load_all_dataclasses(g)
        #ipdb.set_trace()
        Person = dataclasses.get_dataclass('foaf__Person')
        Movie = dataclasses.get_dataclass("wd__Movie")
        print(Person)
        print(Movie)

    if 0:
        #vrdf.load_all_dataclasses(g)
        o_uri = vrdf.rq_value(g, 'select ?o { ?o rdf:type foaf:Person; foaf:name "Alice" }')
        o = vrdf.load_object(g, o_uri)
        print(type(o))
        print(o)
        print(o.foaf__name, 'watched', o.__watched.wd__title)
        
    if 1:
        o_uris = vrdf.rq_values(g, 'select ?o { ?o rdf:type foaf:Person }')
        for o_uri in o_uris:
            print("o:", o_uri)
            o = vrdf.load_object(g, o_uri)
            print("o:", o)
            print(o.foaf__name, 'watched', o.__watched.wd__title)
        
        
    if 0: # example of how to override get/set attr on dataclass
        old_setattr = Person.__setattr__
        def new_setattr(this, m, v):
            print("new_setattr", id(this), m, v)
            return old_setattr(this, m, v)
        Person.__setattr__ = new_setattr

        old_getattr = Person.__getattribute__
        def new_getattr(this, m):
            if not m in type(this).__annotations__:
                return old_getattr(this, m)
            
            print("new_getattr", id(this), m)
            return old_getattr(this, m)
        Person.__getattribute__ = new_getattr

    if 0: # define Person and Movie classes in shacl
        from alice_bob_shacl import Person, Movie
        save_shacl_defs(out_g, [Person, Movie])

    if 0: # adding Alice and Bob along with their watched movies
        from alice_bob_shacl import Person, Movie
        alice = Person(name = 'Alice', age = 45)
        alice.watched = Movie(title = 'Matrix')

        bob = Person(name = 'Bob', age = 40)
        bob.knows = alice
        alice.knows = bob
        bob.watched = Movie(title = 'Titanic')

        save_obj(out_g, alice)
        save_obj(out_g, bob)

    r"""
    if 0: # adding one more movie for Bob
        obj_uri = ...
        bob = load_obj(g, obj_uri)

        movie_uri = ...
        
        bob.watched.add(movie_uri)
        for m in bob.watched:
            print(m)

        save_obj(out_g, bob)
        
    if 0: # adding Dan who watched unknown till now 'Dark City'
        from alice_bob_shacl import Person

        p = Person()
        print(Person.__annotations__)
        #ipdb.set_trace()
    
        print("id(p):", id(p))
        p.name = 'Dan'
        p.age = 28
        print(p)
        print(p.name)
        #save_obj(out_g, p)

        m = create_obj(':Movie')
        m.title = 'Dark City'
        p.watched.add(m)
        
        save_obj(out_g, p)

    if 0: # adding Sam who wanted Matrix (was defined before)
        out_g = rdflib.Graph()

        p = Person()
        print(Person.__annotations__)
        #ipdb.set_trace()
    
        print("id(p):", id(p))
        p.name = 'Sam'
        p.age = 34
        print(p)
        print(p.name)
        #save_obj(out_g, p)

        m_uri = rq..("select ?m_uri { ?m_uri rdf:type :Movie; :title 'Matrix' }")
        m = load_obj(g, m_uri)
        p.watched.add(m)
        
        save_obj(out_g, p)

        for x in out_g:
            print(x)
    """
            
    if 0:
        g = vrdf.load_rdf_graph(["../alice-bob/alice-bob.shacl.ttl", "../alice-bob/alice-bob.ttl"])

        r"""
        del Person
        del Movie
        g.qeuery("select ?c_uri { ?c_uri rdf:type rdfs:Class; rdf:type sh:NodeShape }")
        dataclasses.make_dataclass(...) # https://docs.python.org/3/library/dataclasses.html#dataclasses.make_dataclass
        uri = ... g.query("select ?uri { ?uri rdf:type :Person; foaf:name 'Alice' }")
        p = load_obj(g, uri)
        print(type(p))
        print(p)
        p.name = p.name.upper()
        save_obj(g, p)
        """
    
