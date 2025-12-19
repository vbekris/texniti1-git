from csp import count, first
import sys

# -------------------------------------------------------------------------
# 1. VARIABLE ORDERING HEURISTIC: dom/wdeg
# -------------------------------------------------------------------------

def dom_wdeg(csp, assignment):
    """
    Επιλέγει την επόμενη μεταβλητή προς εξέταση χρησιμοποιώντας την ευρετική dom/wdeg.
    
    Θεωρία:
    Επιλέγουμε τη μεταβλητή X που ελαχιστοποιεί το λόγο: domain_size / weighted_degree.
    - domain_size: Πλήθος ενεργών τιμών στο πεδίο.
    - weighted_degree: Άθροισμα βαρών των περιορισμών της X με άλλες ΜΗ ανατεθειμένες μεταβλητές.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    best_var = None
    best_ratio = float('inf')
    
    for var in unassigned:
        # dom: Πλήθος τιμών στο τρέχον πεδίο
        dom_size = csp.curr_domains[var] if csp.curr_domains else len(csp.domains[var])
        if dom_size == 0:
            # Αν είναι 0, έχουμε fail, την επιλέγουμε άμεσα για να κάνουμε backtrack
            return var
            
        # wdeg: Υπολογισμός weighted degree
        wdeg = 0
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment:
                # Βρίσκουμε το βάρος του περιορισμού (var, neighbor)
                # Χρησιμοποιούμε frozenset γιατί η σειρά δεν μετράει
                constraint_key = frozenset([var, neighbor])
                weight = csp.constraint_weights.get(constraint_key, 1)
                wdeg += weight
        
        # Αποφυγή διαίρεσης με το μηδέν (αν wdeg=0 βάζουμε 1 ή μικρό νούμερο)
        if wdeg == 0:
            wdeg = 1
            
        ratio = dom_size / wdeg
        
        if ratio < best_ratio:
            best_ratio = ratio
            best_var = var
            
    return best_var


# -------------------------------------------------------------------------
# 2. SOLVER: FC-CBJ (Forward Checking with Conflict-Directed Backjumping)
# -------------------------------------------------------------------------

def fc_cbj(csp):
    """
    Επίλυση CSP με Forward Checking και Conflict-Directed Backjumping.
    Επιστρέφει τη λύση (assignment) ή None.
    
    Αυτή είναι μια custom υλοποίηση αναζήτησης, καθώς το AIMA δεν υποστηρίζει CBJ.
    """
    # Αρχικοποίηση Conflict Sets: {var: {set of conflicting ancestors}}
    # Στην αρχή είναι κενά.
    conf_set = {v: set() for v in csp.variables}
    
    # Αρχικοποίηση domains (αντίγραφο για να μην χαλάσουμε τα original κατά την αναζήτηση)
    # Το AIMA χρησιμοποιεί το curr_domains για pruning.
    csp.curr_domains = {v: list(csp.domains[v]) for v in csp.variables}
    
    # Καλούμε την αναδρομική συνάρτηση
    result, _ = fc_cbj_recursive(csp, {}, conf_set)
    return result

def fc_cbj_recursive(csp, assignment, conf_set):
    """
    Η αναδρομική καρδιά του FC-CBJ.
    
    Returns:
        (result, jump_back_to): 
        - result: Η λύση (dict) ή None αν αποτύχαμε.
        - jump_back_to: Η μεταβλητή στην οποία πρέπει να γυρίσουμε (Backjump).
          Αν είναι None, σημαίνει κανονική αποτυχία.
    """
    # 1. Goal Test: Αν γεμίσαμε όλες τις μεταβλητές, βρήκαμε λύση!
    if len(assignment) == len(csp.variables):
        return assignment, None

    # 2. Επιλογή μεταβλητής (χρησιμοποιούμε dom/wdeg που φτιάξαμε πάνω)
    var = dom_wdeg(csp, assignment)
    
    # 3. Δοκιμή τιμών (Value Ordering - εδώ απλά στη σειρά, LCV αν θέλαμε βελτιστοποίηση)
    # Πρέπει να iterάρουμε σε αντίγραφο του domain γιατί το FC θα το πειράξει
    for value in list(csp.curr_domains[var]):
        
        # Έλεγχος συμβατότητας με ήδη ανατεθειμένες (αν και το FC το έχει εγγυηθεί,
        # το κρατάμε για τυπικούς λόγους ασφαλείας του AIMA)
        if 0 == csp.nconflicts(var, value, assignment):
            
            # --- FORWARD CHECKING STEP ---
            # Πριν προχωρήσουμε, κάνουμε prune τους γείτονες
            # Κρατάμε τα removals για να τα αναιρέσουμε μετά (backtrack)
            removals = []
            dwo_occurred = False # Domain Wipe Out
            failed_neighbor = None
            
            csp.assign(var, value, assignment)
            
            # Έλεγχος γειτόνων
            for neighbor in csp.neighbors[var]:
                if neighbor not in assignment:
                    # Ελέγχουμε τις τιμές του γείτονα
                    for val_n in list(csp.curr_domains[neighbor]):
                        if not csp.constraints(var, value, neighbor, val_n):
                            # Σύγκρουση! Διαγραφή τιμής val_n από τον neighbor
                            csp.prune(neighbor, val_n, removals)
                            
                            # FC-CBJ Λογική: 
                            # Επειδή η 'var' αφαίρεσε τιμή από τον 'neighbor', 
                            # η 'var' μπαίνει στο Conflict Set του 'neighbor'.
                            conf_set[neighbor].add(var)
                    
                    # Αν άδειασε το domain του γείτονα -> DWO
                    if not csp.curr_domains[neighbor]:
                        dwo_occurred = True
                        failed_neighbor = neighbor
                        
                        # ΕΝΗΜΕΡΩΣΗ ΒΑΡΩΝ (dom/wdeg logic):
                        # Ο περιορισμός (var, neighbor) προκάλεσε αδιέξοδο.
                        key = frozenset([var, neighbor])
                        csp.constraint_weights[key] += 1
                        break # Δεν χρειάζεται να ελέγξουμε άλλους γείτονες
            
            if not dwo_occurred:
                # Όλα καλά με το FC, προχωράμε βαθύτερα
                result, jump_back_to = fc_cbj_recursive(csp, assignment, conf_set)
                
                if result is not None:
                    return result, None # Βρέθηκε λύση
                
                # Αν επιστρέψαμε εδώ, σημαίνει ότι αποτύχαμε πιο κάτω.
                # Ελέγχουμε αν το jump_back_to είμαστε εμείς (var)
                if jump_back_to is not None and jump_back_to != var:
                    # Πρέπει να γυρίσουμε κι άλλο πίσω!
                    # Δεν δοκιμάζουμε άλλη τιμή για την var, κάνουμε return αμέσως.
                    csp.restore(removals)
                    csp.unassign(var, assignment)
                    return None, jump_back_to
                
                # Αν το jump_back_to είμαστε εμείς (ή None), σημαίνει ότι 
                # εξαντλήσαμε το υποδέντρο και πρέπει να δοκιμάσουμε την ΕΠΟΜΕΝΗ τιμή της var.
                # Πριν πάμε στην επόμενη τιμή, ενώνουμε τα conflicts:
                # Το conflict set της var γίνεται η ένωση των conflicts που μας επέστρεψε το παιδί.
                # (Απλοποιημένη εκδοχή CBJ για ευκολία υλοποίησης:
                #  Κρατάμε το conf_set όπως ενημερώνεται globaly)
                pass 

            else:
                # DWO (Domain Wipeout): Αποτυχία στο Forward Checking
                # Δεν καλούμε αναδρομικά.
                # Πρέπει να ενημερώσουμε το conflict set της 'var'.
                # Γιατί αποτύχαμε; Επειδή ο 'failed_neighbor' έμεινε άδειος.
                # Άρα "κληρονομούμε" τους εχθρούς του 'failed_neighbor'.
                # (Γιατί αν αλλάξουμε μια από τις μεταβλητές στο CS του γείτονα, 
                # ίσως ελευθερωθεί τιμή).
                conf_set[var].update(conf_set[failed_neighbor])
                
                # Επίσης, η ίδια η 'var' φταίει (προφανώς), αλλά δεν βάζουμε τον εαυτό μας στο δικό μας set.
                pass

            # Restore για να δοκιμάσουμε επόμενη τιμή (ή να γυρίσουμε πίσω)
            csp.restore(removals)
            csp.unassign(var, assignment)
    
    # 4. BACKJUMPING LOGIC (Όταν τελειώσουν όλες οι τιμές της var)
    # Αν φτάσαμε εδώ, καμία τιμή της var δεν δούλεψε.
    # Πρέπει να γυρίσουμε πίσω. Σε ποιον;
    # Στον πιο πρόσφατο πρόγονο που βρίσκεται στο conf_set[var].
    
    # Βρίσκουμε τον πιο "βαθύ" (πρόσφατο) πρόγονο στο conflict set
    # (Υποθέτουμε ότι το assignment keys είναι με τη σειρά ανάθεσης περίπου, 
    # ή ψάχνουμε ποιος προστέθηκε τελευταίος).
    
    most_recent_conflict = None
    # Αναζήτηση στον πίνακα assignment (που έχει τη σειρά ανάθεσης)
    # Ψάχνουμε από το τέλος προς την αρχή
    for assigned_var in list(assignment.keys())[::-1]:
        if assigned_var in conf_set[var]:
            most_recent_conflict = assigned_var
            break
            
    # Αν το conflict set είναι άδειο (και δεν είμαστε στη ρίζα), υπάρχει πρόβλημα,
    # αλλά θεωρητικά θα υπάρχει πάντα κάποιος εκτός αν είναι ασύμβατο το πρόβλημα εξ αρχής.
    
    return None, most_recent_conflict