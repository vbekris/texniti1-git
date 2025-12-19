from csp import count, first
import sys

# -------------------------------------------------------------------------
# 1. VARIABLE ORDERING HEURISTIC: dom/wdeg
# -------------------------------------------------------------------------

def dom_wdeg(csp, assignment):
    """
    Επιλέγει τη μεταβλητή με τον ελάχιστο λόγο dom/wdeg.
    """
    # 1. Βρίσκουμε ποιες μεταβλητές δεν έχουν πάρει ακόμα τιμή.
    # ΓΙΑΤΙ: Δεν έχει νόημα να εξετάσουμε μεταβλητές που έχουμε ήδη λύσει.
    unassigned = [v for v in csp.variables if v not in assignment]
    
    best_var = None
    best_ratio = float('inf') # Αρχικοποίηση με άπειρο για να βρούμε το ελάχιστο
    
    for var in unassigned:
        # 2. Υπολογισμός του 'dom' (Domain Size).
        # ΓΙΑΤΙ: Αν έχουμε κάνει pruning (διαγραφές) με FC, το μέγεθος του πεδίου έχει μειωθεί.
        # Το 'curr_domains' περιέχει τα τρέχοντα "κουτσουρεμένα" πεδία.
        # Αν δεν υπάρχει curr_domains (π.χ. στην αρχή), παίρνουμε το αρχικό μέγεθος.
        dom_size = len(csp.curr_domains[var]) if csp.curr_domains else len(csp.domains[var])
        
        # FAIL-FIRST PRINCIPLE:
        # Αν το πεδίο είναι άδειο (0), έχουμε αδιέξοδο ΤΩΡΑ. 
        # Επιστρέφουμε αμέσως τη μεταβλητή για να κάνει ο αλγόριθμος backtrack.
        if dom_size == 0:
            return var
            
        # 3. Υπολογισμός του 'wdeg' (Weighted Degree).
        # ΓΙΑΤΙ: Θέλουμε να δούμε πόσο "επικίνδυνη" είναι η μεταβλητή.
        # Αθροίζουμε τα βάρη των περιορισμών της ΜΟΝΟ με αταίριαστους γείτονες.
        wdeg = 0
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment:
                # Χρησιμοποιούμε frozenset([var, neighbor]) ως κλειδί.
                # ΓΙΑΤΙ: Ο γράφος είναι μη κατευθυνόμενος. Η ακμή (A, B) είναι ίδια με την (B, A).
                # Το frozenset αγνοεί τη σειρά, άρα βρίσκουμε το σωστό βάρος.
                constraint_key = frozenset([var, neighbor])
                
                # Παίρνουμε το βάρος (default 1 αν δεν το έχουμε αυξήσει ποτέ).
                weight = csp.constraint_weights.get(constraint_key, 1)
                wdeg += weight
        
        # Safety check: Αν wdeg=0 (σπάνιο, αν δεν έχει γείτονες), βάζουμε 1 για να μην διαιρέσουμε με το 0.
        if wdeg == 0:
            wdeg = 1
            
        # 4. Ο Τύπος της Ευρετικής.
        # ΓΙΑΤΙ: Αναζητούμε το ελάχιστο πηλίκο.
        # Μικρότερο ratio σημαίνει:
        # - Είτε πολύ μικρό domain (κίνδυνος να ξεμείνουμε από επιλογές -> Fail First).
        # - Είτε πολύ μεγάλο wdeg (πολλοί/δύσκολοι περιορισμοί -> Most Constrained).
        ratio = dom_size / wdeg
        
        if ratio < best_ratio:
            best_ratio = ratio
            best_var = var
            
    return best_var

# -------------------------------------------------------------------------

# 2. SOLVER: FC-CBJ (Forward Checking with Conflict-Directed Backjumping)

def fc_cbj(csp):
    # 1. Αρχικοποίηση Conflict Sets (CS).
    # ΓΙΑΤΙ: Το CBJ χρειάζεται μνήμη "ποιος φταίει".
    # Φτιάχνουμε ένα set για κάθε μεταβλητή, που θα γεμίζει με τους "προγόνους" που της διέγραψαν τιμές.
    conf_set = {v: set() for v in csp.variables}
    
    # 2. Αντίγραφο των Domains.
    # ΓΙΑΤΙ: Το AIMA χρησιμοποιεί το `curr_domains` για να κάνει pruning (διαγραφές).
    # Πρέπει να το αρχικοποιήσουμε με όλες τις τιμές, γιατί ο αλγόριθμος θα αρχίσει να σβήνει.
    csp.curr_domains = {v: list(csp.domains[v]) for v in csp.variables}
    
    # 3. Εκκίνηση της αναδρομής.
    # Ξεκινάμε με κενό assignment {}.
    result, _ = fc_cbj_recursive(csp, {}, conf_set)
    return result

def fc_cbj_recursive(csp, assignment, conf_set):
    """
    Επιστρέφει (result, jump_back_to).
    - jump_back_to: Σε ποια μεταβλητή πρέπει να γυρίσουμε πίσω (αν αποτύχαμε).
    """
    
    # 1. Goal Test (Τερματισμός).
    # Αν έχουμε δώσει τιμή σε όλες τις μεταβλητές, νικήσαμε!
    if len(assignment) == len(csp.variables):
        return assignment, None

    # 2. Επιλογή Μεταβλητής.
    # Εδώ "κουμπώνουμε" την ευρετική dom/wdeg που φτιάξαμε.
    var = dom_wdeg(csp, assignment)
    
    # 3. Δοκιμή Τιμών (Loop over values).
    # Παίρνουμε τις τιμές από το curr_domains (όσες έχουν επιζήσει από προηγούμενα FC).
    # ΠΡΟΣΟΧΗ: Κάνουμε `list(...)` για να δημιουργήσουμε αντίγραφο, γιατί μέσα στη loop μπορεί να αλλάξει η δομή.
    for value in list(csp.curr_domains[var]):
        
        # Τυπικός έλεγχος (αν και το FC θεωρητικά έχει αφήσει μόνο σωστές τιμές).
        if 0 == csp.nconflicts(var, value, assignment):
            
            # --- FORWARD CHECKING (Προνοητικός Έλεγχος) ---
            
            # Δίνουμε προσωρινά την τιμή.
            csp.assign(var, value, assignment)
            
            # Λίστα για να θυμόμαστε ποιες τιμές σβήσαμε (για να τις επαναφέρουμε αν κάνουμε backtrack).
            removals = []
            dwo_occurred = False  # Σημαία: Έγινε Domain Wipeout (άδειασε κάποιο πεδίο);
            failed_neighbor = None # Ποιος γείτονας πέθανε;
            
            # Ελέγχουμε όλους τους γείτονες που δεν έχουν πάρει ακόμα τιμή.
            for neighbor in csp.neighbors[var]:
                if neighbor not in assignment:
                    
                    # Ελέγχουμε κάθε διαθέσιμη τιμή του γείτονα.
                    for val_n in list(csp.curr_domains[neighbor]):
                        # Αν η τιμή του γείτονα (val_n) συγκρούεται με τη δικιά μας (value)...
                        if not csp.constraints(var, value, neighbor, val_n):
                            
                            # ...ΤΗ ΣΒΗΝΟΥΜΕ! (Pruning)
                            csp.prune(neighbor, val_n, removals)
                            
                            # *** CBJ LOGIC ***
                            # Ο γείτονας έχασε μια τιμή εξαιτίας ΜΟΥ (var).
                            # Άρα μπαίνω στη "μαύρη λίστα" (Conflict Set) του γείτονα.
                            conf_set[neighbor].add(var)
                    
                    # Έλεγχος DWO: Άδειασε τελείως το πεδίο του γείτονα;
                    if not csp.curr_domains[neighbor]:
                        dwo_occurred = True
                        failed_neighbor = neighbor
                        
                        # *** WDEG LOGIC ***
                        # Αυτός ο περιορισμός προκάλεσε αδιέξοδο.
                        # Αυξάνουμε το βάρος του κατά 1!
                        # Την επόμενη φορά η dom/wdeg θα δώσει προτεραιότητα σε αυτές τις μεταβλητές.
                        key = frozenset([var, neighbor])
                        csp.constraint_weights[key] += 1
                        
                        break # Δεν χρειάζεται να δούμε άλλους γείτονες, ήδη αποτύχαμε.
            
            # --- ΑΠΟΦΑΣΗ: Συνεχίζουμε ή Γυρνάμε; ---
            
            if not dwo_occurred:
                # Αν το FC πέτυχε (δεν άδειασε κανείς), καλούμε αναδρομικά για την επόμενη μεταβλητή.
                result, jump_back_to = fc_cbj_recursive(csp, assignment, conf_set)
                
                # ΠΕΡΙΠΤΩΣΗ 1: Βρήκαμε τη λύση!
                if result is not None:
                    return result, None
                
                # ΠΕΡΙΠΤΩΣΗ 2: Backjumping (Κάποιος από κάτω απέτυχε και μας είπε πού να γυρίσουμε).
                
                # Αν το jump_back_to ΔΕΝ είμαι εγώ (var), σημαίνει ότι το πρόβλημα είναι πιο ψηλά.
                # Π.χ. Είμαι ο Level 10, και το λάθος έγινε στο Level 5.
                # Δεν προσπαθώ άλλη τιμή! Πρέπει να κάνω return αμέσως για να φτάσει το μήνυμα στο 5.
                if jump_back_to is not None and jump_back_to != var:
                    csp.restore(removals) # Αναίρεση διαγραφών FC
                    csp.unassign(var, assignment) # Αναίρεση ανάθεσης
                    return None, jump_back_to
                
                # Αν το jump_back_to είμαι ΕΓΩ (ή None που σημαίνει απλό backtrack),
                # τότε απλά συνεχίζω τη loop για να δοκιμάσω την επόμενη τιμή μου (value).
                # (Εδώ θα μπορούσαμε να κάνουμε merge τα conflict sets, αλλά για απλότητα το αφήνουμε).
            
            else:
                # ΠΕΡΙΠΤΩΣΗ 3: DWO (Αποτυχία στο Forward Checking).
                # Κάποιος γείτονας (failed_neighbor) έμεινε χωρίς τιμές.
                
                # *** CBJ LOGIC ***
                # Γιατί πέθανε ο γείτονας; Επειδή του σβήσαμε τιμές εμείς (var) ΚΑΙ οι πρόγονοί μας.
                # Οπότε, οι εχθροί του γείτονα γίνονται τώρα ΚΑΙ δικοί μου εχθροί.
                # Ενημερώνω το δικό μου Conf Set με το Conf Set του γείτονα.
                conf_set[var].update(conf_set[failed_neighbor])
                
                # Δεν καλούμε αναδρομικά, πάμε για επόμενη τιμή (ή backtrack).

            # Αναίρεση αλλαγών (Backtracking step) για να δοκιμάσουμε την επόμενη τιμή.
            csp.restore(removals)
            csp.unassign(var, assignment)
    
    # 4. ΤΕΛΟΣ LOOP (Εξαντλήθηκαν όλες οι τιμές).
    # Αν φτάσαμε εδώ, καμία τιμή της `var` δεν δούλεψε. Πρέπει να γυρίσουμε πίσω.
    
    # Σε ποιον γυρνάμε; (Backjump Target)
    # Κοιτάμε το Conflict Set μας (`conf_set[var]`).
    # Θέλουμε τον πιο "πρόσφατο" πρόγονο (αυτόν που βρίσκεται πιο βαθιά στο δέντρο αναζήτησης).
    # Αν κάναμε απλό Backtracking, θα γυρνούσαμε στον αμέσως προηγούμενο.
    # Τώρα μπορεί να πηδήξουμε 5 επίπεδα πάνω!
    
    most_recent_conflict = None
    # Ψάχνουμε στο assignment (που έχει τη σειρά ανάθεσης) από το τέλος προς την αρχή.
    for assigned_var in list(assignment.keys())[::-1]:
        if assigned_var in conf_set[var]:
            most_recent_conflict = assigned_var
            break
            
    # Επιστρέφουμε None (αποτυχία) και τον στόχο του άλματος.
    return None, most_recent_conflict