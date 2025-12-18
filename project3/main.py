import sys
from csp import CSP, min_conflicts, backtracking_search, forward_checking, mac

# ---------------------------------------------------------
# 1. PARSER: Διαβάζει τα αρχεία .txt
# ---------------------------------------------------------
def parse_rlfap(dom_file, var_file, ctr_file):
    # --- Διαβάζουμε τα Domains ---
    domains_map = {}
    with open(dom_file, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts: continue
            # Format: dom_id count v1 v2 ... (Συνήθως έτσι είναι σε αυτά τα datasets)
            # Αν δεν υπάρχει το count, θα χρειαστεί μικρή αλλαγή.
            d_id = int(parts[0])
            # Παίρνουμε τα values. Αν το 2ο στοιχείο είναι το πλήθος, ξεκινάμε από το 2
            values = [int(x) for x in parts[2:]] 
            domains_map[d_id] = values

    # --- Διαβάζουμε τις Μεταβλητές ---
    variables = []
    domains = {}
    with open(var_file, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts: continue
            # Format: var_id dom_id
            v_id = int(parts[0])
            d_id = int(parts[1])
            variables.append(v_id)
            domains[v_id] = domains_map[d_id]

    # --- Διαβάζουμε τους Περιορισμούς ---
    constraints_data = [] # Λίστα με (var1, var2, k)
    neighbors = {v: [] for v in variables}
    
    with open(ctr_file, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts: continue
            # Format: var1 var2 type operator k  (ή παρόμοιο)
            # Θα ψάξουμε για τα var1, var2 και το k (τελευταίο στοιχείο)
            v1 = int(parts[0])
            v2 = int(parts[1])
            k = int(parts[-1]) # Το k είναι συνήθως στο τέλος
            
            # Αν ο τελεστής είναι '>', το k είναι το κατώφλι
            # Αν είναι '=', το k είναι η ακριβής διαφορά (σπάνιο στο RLFAP, συνήθως >)
            
            constraints_data.append((v1, v2, k))
            neighbors[v1].append(v2)
            neighbors[v2].append(v1)

    return variables, domains, neighbors, constraints_data

# ---------------------------------------------------------
# 2. Η Κλάση του Προβλήματος (CSP)
# ---------------------------------------------------------
class RLFAP(CSP):
    def __init__(self, dom_file, var_file, ctr_file):
        vars_list, domains, neighbors, ctr_data = parse_rlfap(dom_file, var_file, ctr_file)
        
        self.ctr_data = ctr_data # Αποθηκεύουμε τα k για κάθε ζεύγος
        
        # Φτιάχνουμε ένα dictionary για γρήγορη εύρεση του k: (v1, v2) -> k
        self.constraint_map = {}
        for (v1, v2, k) in ctr_data:
            self.constraint_map[(v1, v2)] = k
            self.constraint_map[(v2, v1)] = k # Συμμετρικό
            
        super().__init__(vars_list, domains, neighbors, self.constraints_check)

    def constraints_check(self, A, a, B, b):
        """
        Ελέγχει αν η ανάθεση A=a και B=b παραβιάζει τον περιορισμό.
        Ο περιορισμός είναι: |a - b| > k
        """
        if (A, B) in self.constraint_map:
            k = self.constraint_map[(A, B)]
            return abs(a - b) > k
        return True

# ---------------------------------------------------------
# 3. MAIN: Δοκιμή (Sanity Check)
# ---------------------------------------------------------
if __name__ == '__main__':
    # ΔΙΑΛΕΞΕ ΕΝΑ ΖΕΥΓΑΡΙ ΑΡΧΕΙΩΝ ΠΟΥ ΕΧΕΙΣ (π.χ. Instance 2)
    # Βεβαιώσου ότι τα ονόματα είναι σωστά όπως τα έχεις στον φάκελο
    print("Φόρτωση Instance 2...")
    
    # ΠΡΟΣΟΧΗ: Άλλαξε τα ονόματα αρχείων αν διαφέρουν
    problem = RLFAP('dom2-f24.txt', 'var2-f24.txt', 'ctr14-f28.txt') 
    # ΣΗΜΕΙΩΣΗ: Έβαλα τυχαία το ctr14 με το var2, ΠΡΕΠΕΙ ΝΑ ΒΡΕΙΣ ΤΟ ΣΩΣΤΟ ΖΕΥΓΑΡΙ 
    # από το αρχείο odigies.txt ή από τα ονόματα των αρχείων.
    # Συνήθως τα αρχεία πάνε πακέτο π.χ. var2-f24, dom2-f24, ctr2...
    
    print(f"Μεταβλητές: {len(problem.variables)}")
    print(f"Περιορισμοί που διαβάστηκαν: {len(problem.ctr_data)}")
    
    # Δοκιμή μιας γρήγορης επίλυσης (αν είναι μικρό)
    # print("Προσπάθεια επίλυσης με Min-Conflicts...")
    # result = min_conflicts(problem, max_steps=1000)
    # print("Αποτέλεσμα:", result)