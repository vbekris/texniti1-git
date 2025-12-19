import os
from csp import CSP  # Αυτό είναι το αρχείο από το GitHub του AIMA

def parse_instance(instance_id, data_folder='data'):
    """
    Διαβάζει τα αρχεία var, dom, ctr και επιστρέφει τις δομές που χρειάζεται ο CSP.
    
    Returns:
        variables (list): H λίστα με τα ονόματα (IDs) των μεταβλητών.
        domains (dict): Λεξικό {var_id: [τιμές]}.
        neighbors (dict): Λεξικό {var_id: {neighbor_1, neighbor_2...}}.
        constraints_data (dict): Λεξικό {(var1, var2): (operator, k)}.
    """
    
    # Κατασκευή των μονοπατιών των αρχείων
    # Π.χ. data/var2-f24.txt
    # Ψάχνουμε τα αρχεία που περιέχουν το instance_id στο όνομά τους
    var_file = None
    dom_file = None
    ctr_file = None
    
    # Απλή λογική για να βρούμε τα σωστά αρχεία στον φάκελο data
    # (Υποθέτουμε ότι έχεις ονομάσει τα αρχεία όπως τα ανέβασες)
    for f in os.listdir(data_folder):
        if f"var{instance_id}" in f: var_file = os.path.join(data_folder, f)
        elif f"dom{instance_id}" in f: dom_file = os.path.join(data_folder, f)
        elif f"ctr{instance_id}" in f: ctr_file = os.path.join(data_folder, f)

    if not (var_file and dom_file and ctr_file):
        raise FileNotFoundError(f"Could not find all files for instance {instance_id}")

    # --- 1. Parsing Domains (Πεδία Ορισμού) ---
    # Δομή αρχείου: domain_id value1 value2 ...
    # Στόχος: Να ξέρουμε τι περιέχει το Domain 0, το Domain 1 κλπ.
    domain_definitions = {} 
    with open(dom_file, 'r') as f:
        next(f) # Skip την πρώτη γραμμή (header count)
        for line in f:
            parts = list(map(int, line.strip().split()))
            dom_id = parts[0]
            values = parts[2:] # Τα values ξεκινάνε μετά το 2ο στοιχείο (βάσει format)
            domain_definitions[dom_id] = values

    # --- 2. Parsing Variables (Μεταβλητές - X) ---
    # Δομή αρχείου: var_id domain_id
    # Στόχος: Να φτιάξουμε το variables list και το domains dictionary του CSP
    variables = []
    domains = {}
    with open(var_file, 'r') as f:
        next(f) # Skip header
        for line in f:
            var_id, dom_id = map(int, line.strip().split())
            variables.append(var_id)
            # Αντιστοιχίζουμε στη μεταβλητή τις τιμές του domain της
            domains[var_id] = domain_definitions[dom_id]

    # --- 3. Parsing Constraints (Περιορισμοί - C) ---
    # Δομή αρχείου: var1 var2 operator k
    # Στόχος: Να φτιάξουμε τον γράφο γειτνίασης και να αποθηκεύσουμε τους κανόνες
    neighbors = {v: set() for v in variables}
    constraints_data = {}
    
    with open(ctr_file, 'r') as f:
        next(f) # Skip header
        for line in f:
            parts = line.strip().split()
            v1, v2 = int(parts[0]), int(parts[1])
            op = parts[2]
            k = int(parts[3])
            
            # Ενημερώνουμε τον γράφο (neighbors)
            # Ο γράφος περιορισμών είναι μη κατευθυνόμενος
            neighbors[v1].add(v2)
            neighbors[v2].add(v1)
            
            # Αποθηκεύουμε τον κανόνα και για τις δύο κατευθύνσεις
            # ώστε να τον βρίσκουμε εύκολα είτε ελέγχουμε (v1, v2) είτε (v2, v1)
            constraints_data[(v1, v2)] = (op, k)
            constraints_data[(v2, v1)] = (op, k)

    return variables, domains, neighbors, constraints_data


class RLFA_CSP(CSP):
    def __init__(self, instance_id, data_folder='data'):
        """
        Αρχικοποίηση του προβλήματος RLFA.
        """
        # 1. Φόρτωση δεδομένων από τα αρχεία
        vars_list, doms_dict, neighbors_dict, ctr_data = parse_instance(instance_id, data_folder)
        
        # 2. Αποθήκευση των "κανόνων" (k και operator) για χρήση στον έλεγχο
        self.constraints_data = ctr_data
        
        # 3. Αρχικοποίηση βαρών για την ευρετική dom/wdeg
        # Κλειδί είναι το ζεύγος μεταβλητών (περιορισμός), Τιμή είναι το βάρος (αρχικά 1)
        # Χρησιμοποιούμε frozenset για να μην μας νοιάζει η σειρά (v1, v2) vs (v2, v1)
        self.constraint_weights = {}
        for (v1, v2) in ctr_data.keys():
            key = frozenset([v1, v2])
            self.constraint_weights[key] = 1

        # 4. Κλήση του constructor της γονικής κλάσης CSP
        # Περνάμε τη δική μας συνάρτηση ελέγχου `rlfa_constraints_check`
        super().__init__(vars_list, doms_dict, neighbors_dict, self.rlfa_constraints_check)

    def rlfa_constraints_check(self, A, a, B, b):
        """
        Ελέγχει αν η ανάθεση A=a και B=b είναι συμβατή.
        Αυτή η συνάρτηση καλείται από τον αλγόριθμο (backtracking, FC, MAC).
        
        Args:
            A (int): Η πρώτη μεταβλητή
            a (int): Η τιμή της πρώτης μεταβλητής
            B (int): Η δεύτερη μεταβλητή
            b (int): Η τιμή της δεύτερης μεταβλητής
        
        Returns:
            bool: True αν ικανοποιείται ο περιορισμός, False αν παραβιάζεται.
        """
        # Αν δεν υπάρχει περιορισμός μεταξύ τους, όλα καλά
        if (A, B) not in self.constraints_data:
            return True
            
        # Ανάκτηση του κανόνα (operator, k) από το λεξικό μας
        op, k = self.constraints_data[(A, B)]
        
        # Υπολογισμός της διαφοράς συχνοτήτων
        diff = abs(a - b)
        
        # Έλεγχος βάσει του τελεστή
        if op == '=':
            return diff == k
        elif op == '>':
            return diff > k
        else:
            raise ValueError(f"Unknown operator: {op}")