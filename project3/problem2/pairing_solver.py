import sys

def parse_dataset(filename):
    pairings = []
    with open(filename, 'r') as f:
        first_line = f.readline().split()
        if not first_line: return 0, []
        
        num_flights = int(first_line[0])
        # Το δεύτερο νούμερο είναι το πλήθος pairings (M), δεν το χρειαζόμαστε άμεσα
        
        # Μετρητής για να δίνουμε εμείς ID (1, 2, 3...)
        current_id = 1
        
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            # --- ΔΙΟΡΘΩΣΗ ΕΔΩ ---
            # 1η στήλη: Κόστος
            cost = int(parts[0])
            
            # 2η στήλη: Πλήθος πτήσεων (μας είναι άχρηστο αφού θα τις διαβάσουμε όλες, αλλά υπάρχει)
            # count = int(parts[1]) 
            
            # Από την 3η στήλη και μετά: Οι Πτήσεις
            flights = set(int(x) for x in parts[2:])
            
            pairings.append({
                'id': current_id,   # Δικό μας ID
                'cost': cost,       # Το σωστό κόστος
                'flights': flights
            })
            
            current_id += 1 # Αυξάνουμε το ID για τον επόμενο
            
    return num_flights, pairings
class SetPartitionSolver:
    def __init__(self, num_flights, pairings):
        # Αποθηκεύουμε τα βασικά δεδομένα
        self.num_flights = num_flights
        self.pairings = pairings 
        
        # --- ΜΕΤΑΒΛΗΤΕΣ ΒΕΛΤΙΣΤΟΠΟΙΗΣΗΣ ---
        # Εδώ θα φυλάμε την καλύτερη λύση που βρήκαμε μέχρι στιγμής.
        # Αρχικοποιούμε το κόστος στο 'άπειρο' (float('inf')), 
        # ώστε η πρώτη έγκυρη λύση που θα βρούμε να είναι σίγουρα μικρότερη.
        self.best_solution = []
        self.best_cost = float('inf')
        
        # --- ΤΟ ΕΥΡΕΤΗΡΙΟ (INDEXING) ---
        # Φτιάχνουμε έναν γρήγορο χάρτη.
        # Δομή: Λεξικό (Dictionary).
        # Κλειδί (Key): Αριθμός Πτήσης (int)
        # Τιμή (Value): Λίστα με τα Pairings που την καλύπτουν.
        
        # 1. Δημιουργούμε κενές λίστες για κάθε πτήση (από 1 έως N)
        self.flight_index = {i: [] for i in range(1, num_flights + 1)}
        
        # 2. Γεμίζουμε το ευρετήριο
        for p in pairings:
            # Για κάθε πτήση που υπάρχει μέσα σε αυτό το pairing...
            for flight in p['flights']:
                # ...πρόσθεσε αυτό το pairing στη λίστα της συγκεκριμένης πτήσης.
                self.flight_index[flight].append(p)

    def solve(self):    
    
        """
        Ξεκινάει τη διαδικασία επίλυσης.
        """
        # 1. Ποιες πτήσεις πρέπει να καλύψουμε; Στην αρχή, ΟΛΕΣ (1 έως N).
        # Χρησιμοποιούμε set για να αφαιρούμε εύκολα όσες καλύπτουμε.
        all_flights = set(range(1, self.num_flights + 1))
        
        print(f"Start solving for {self.num_flights} flights...")
        
        # 2. Καλούμε την αναδρομική μέθοδο (θα τη γράψουμε στο επόμενο βήμα).
        # Ορίσματα: 
        #   - uncovered_flights: Πτήσεις που μένουν να καλυφθούν
        #   - current_cost: Πόσο έχουμε ξοδέψει μέχρι τώρα (0 αρχικά)
        #   - current_solution: Η λίστα με τα ID των pairings που διαλέξαμε (κενή αρχικά)
        self._search(all_flights, 0, [])
        
        # 3. Επιστρέφουμε το αποτέλεσμα
        return self.best_cost, self.best_solution
    
    def _search(self, uncovered_flights, current_cost, current_solution):
        """
        Η καρδιά του αλγορίθμου.
        - uncovered_flights: Set με τις πτήσεις που δεν έχουν καλυφθεί ακόμα.
        - current_cost: Το κόστος μέχρι στιγμής.
        - current_solution: Λίστα με τα ID των pairings που έχουμε διαλέξει.
        """
        
        # --- 1. BASE CASE (ΕΠΙΤΥΧΙΑ) ---
        # Αν το σύνολο uncovered_flights είναι άδειο, σημαίνει καλύψαμε τα πάντα!
        if not uncovered_flights:
            # Βρήκαμε μια λύση. Είναι καλύτερη από την προηγούμενη;
            if current_cost < self.best_cost:
                self.best_cost = current_cost
                # Αποθηκεύουμε αντίγραφο (list(...)) της λύσης
                self.best_solution = list(current_solution)
                print(f"Βρέθηκε νέα καλύτερη λύση! Κόστος: {self.best_cost}")
            return # Τέλος αυτού του μονοπατιού.

        # --- 2. PRUNING (ΚΛΑΔΕΜΑ) ---
        # Branch & Bound: Αν ήδη έχουμε ξεπεράσει το κόστος της καλύτερης λύσης
        # που βρήκαμε νωρίτερα, δεν υπάρχει λόγος να συνεχίσουμε. Σταματάμε.
        if current_cost >= self.best_cost:
            return

        # --- 3. HEURISTIC MRV (Η Στρατηγική) ---
        # Ποια πτήση να προσπαθήσουμε να καλύψουμε τώρα;
        # ΟΧΙ την πρώτη τυχαία. Διαλέγουμε την "πιο δύσκολη".
        # Δηλαδή, αυτή που έχει τις ΛΙΓΟΤΕΡΕΣ επιλογές (pairings) στο ευρετήριο.
        
        # Η εντολή min ψάχνει μέσα στο uncovered_flights.
        # Το key=lambda f: ... λέει "σύγκρινε τες με βάση το μήκος της λίστας τους στο ευρετήριο".
        chosen_flight = min(
            uncovered_flights, 
            key=lambda f: len(self.flight_index[f])
        )

        # --- 4. RECURSION (ΔΟΚΙΜΕΣ) ---
        # Παίρνουμε τους υποψήφιους συνδυασμούς για αυτή τη δύσκολη πτήση
        candidates = self.flight_index[chosen_flight]
        
        for p in candidates:
            # ΕΛΕΓΧΟΣ ΕΓΚΥΡΟΤΗΤΑΣ (CONSTRAINT CHECK):
            # Για να διαλέξουμε αυτό το pairing, πρέπει ΟΛΕΣ οι πτήσεις του
            # να είναι ακόμα ακάλυπτες. Αν έστω και μία έχει καλυφθεί ήδη,
            # τότε έχουμε σύγκρουση (overlap).
            if p['flights'].issubset(uncovered_flights):
                
                # Υπολογίζουμε τη νέα κατάσταση
                # Αφαιρούμε τις πτήσεις του pairing από τις ακάλυπτες
                remaining_flights = uncovered_flights - p['flights']
                
                # Καλούμε το ρομπότ ξανά (Αναδρομή) για το επόμενο βήμα
                self._search(
                    remaining_flights, 
                    current_cost + p['cost'], 
                    current_solution + [p['id']]
                )
                
# Στην αρχή του αρχείου σου, σιγουρέψου ότι έχεις: import sys

if __name__ == "__main__":
    import sys
    
    # Ελέγχουμε αν ο χρήστης έδωσε όνομα αρχείου
    if len(sys.argv) < 2:
        print("Usage: python3 pairing_solver.py <filename>")
        sys.exit(1)

    filename = sys.argv[1] 
    
    # Προαιρετικό: Τυπώνουμε μήνυμα μόνο αν τρέχουμε ένα αρχείο (όχι στο batch mode του Make)
    # print(f"--- Solving {filename} ---")
    
    try:
        # 1. Διάβασμα
        N, data = parse_dataset(filename)
        
        # 2. Επίλυση
        solver = SetPartitionSolver(N, data)
        cost, sol = solver.solve()
        
        # 3. Αποτέλεσμα (ΤΡΟΠΟΠΟΙΗΣΗ ΓΙΑ ΝΑ ΤΥΠΩΝΕΙ ΤΗ ΛΙΣΤΑ)
        # Τυπώνουμε σε μία γραμμή: Αρχείο, Κόστος, Πλήθος, και μετά τη Λίστα των IDs
        print(f"RESULT | File: {filename} | Cost: {cost} | Count: {len(sol)} | Selected Pairings: {sorted(sol)}")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")