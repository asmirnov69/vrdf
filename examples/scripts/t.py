import vrdf

if __name__ == "__main__":
    g = vrdf.load_rdf(["./alice-bob.ttl", "./alice-bob-shacl.ttl"g])
    print([spo for spo in g])
    

