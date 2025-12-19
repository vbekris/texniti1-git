import os
from csp import CSP

def parse_instance(instance_id, data_folder='data'):
    var_file = None
    dom_file = None
    ctr_file = None
    
    for f in os.listdir(data_folder):
        if f"var{instance_id}" in f: var_file = os.path.join(data_folder, f)
        elif f"dom{instance_id}" in f: dom_file = os.path.join(data_folder, f)
        elif f"ctr{instance_id}" in f: ctr_file = os.path.join(data_folder, f)

    if not (var_file and dom_file and ctr_file):
        raise FileNotFoundError(f"Could not find all files for instance {instance_id}")

    domain_definitions = {} 
    with open(dom_file, 'r') as f:
        next(f)
        for line in f:
            parts = list(map(int, line.strip().split()))
            dom_id = parts[0]
            values = parts[2:]
            domain_definitions[dom_id] = values

    variables = []
    domains = {}
    with open(var_file, 'r') as f:
        next(f)
        for line in f:
            var_id, dom_id = map(int, line.strip().split())
            variables.append(var_id)
            domains[var_id] = domain_definitions[dom_id]

    neighbors = {v: set() for v in variables}
    constraints_data = {}
    
    with open(ctr_file, 'r') as f:
        next(f)
        for line in f:
            parts = line.strip().split()
            v1, v2 = int(parts[0]), int(parts[1])
            op = parts[2]
            k = int(parts[3])
            
            neighbors[v1].add(v2)
            neighbors[v2].add(v1)
            
            constraints_data[(v1, v2)] = (op, k)
            constraints_data[(v2, v1)] = (op, k)

    return variables, domains, neighbors, constraints_data


class RLFA_CSP(CSP):
    def __init__(self, instance_id, data_folder='data'):
        vars_list, doms_dict, neighbors_dict, ctr_data = parse_instance(instance_id, data_folder)
        
        self.constraints_data = ctr_data
        
        # --- ΒΕΛΤΙΣΤΟΠΟΙΗΣΗ ---
        # Αποθηκεύουμε τα βάρη με κλειδί tuple (u, v) αντί για frozenset.
        # Έχουμε και τις δύο κατευθύνσεις (u,v) και (v,u) για O(1) πρόσβαση.
        self.constraint_weights = {}
        for (v1, v2) in ctr_data.keys():
            self.constraint_weights[(v1, v2)] = 1

        super().__init__(vars_list, doms_dict, neighbors_dict, self.rlfa_constraints_check)

    def rlfa_constraints_check(self, A, a, B, b):
        if (A, B) not in self.constraints_data:
            return True
        op, k = self.constraints_data[(A, B)]
        diff = abs(a - b)
        if op == '=': return diff == k
        elif op == '>': return diff > k
        else: raise ValueError(f"Unknown operator: {op}")