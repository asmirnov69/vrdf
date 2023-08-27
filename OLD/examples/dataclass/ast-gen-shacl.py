import ipdb
import sys
import ast

def member_type_to_string(x):
    if isinstance(x, ast.Name):
        ret = x.id        
    elif isinstance(x, ast.Call):
        func_name = x.func.id
        func_args = [(type(aa), aa.id) for aa in x.args]
        ret = f"{func_name} {func_args}"
    else:
        raise Exception(f"member_type_to_string: unknown obj type {type(x)}")
    
    return ret

class SHACLClassDef:
    def __init__(self, shacl_class_name):
        self.shacl_class_name = shacl_class_name
        self.members = []

if __name__ == "__main__":
    mod_fn = sys.argv[1]
    source_code = "\n".join(open(mod_fn).readlines())
    pt = ast.parse(source_code)

    shacl_classes = {}
    for node in ast.iter_child_nodes(pt):
        if isinstance(node, ast.ClassDef):
            shacl_class = SHACLClassDef(node.name)
            for ann in filter(lambda x: isinstance(x, ast.AnnAssign), node.body):
                #ipdb.set_trace()
                member_name = ann.target.id
                member_type = member_type_to_string(ann.annotation)
                shacl_class.members.append((member_name, member_type))
            shacl_classes[shacl_class.shacl_class_name] = shacl_class

    for shacl_class in shacl_classes.values():
        print(shacl_class.shacl_class_name)
        for m in shacl_class.members:
            print(m)
        
        
