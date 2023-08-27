from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Person:
    name: str = None
    watched: Set[Movie] = Set() # shacl_or(Movie, shacl_IRI)
    knows: Set[Person] = Set()
    age: int = None

@dataclass(init = False)
class Movie:
    title: str = None
    
