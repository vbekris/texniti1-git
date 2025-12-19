from csp import count, first
import sys

# -------------------------------------------------------------------------
# 1. VARIABLE ORDERING HEURISTIC: dom/wdeg
# -------------------------------------------------------------------------

def dom_wdeg(assignment, csp):
    """
    Επιλέγει την επόμενη μεταβλητή προς εξέταση χρησιμοποιώντας την ευρετική dom/wdeg.
    ΠΡΟΣΟΧΗ: Η σειρά ορισμάτων πρέπει να είναι (assignment, csp) για να είναι
    συμβατή με το AIMA csp.py.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    best_var = None
    best_ratio = float('inf')
    
    for var in unassigned:
        # dom: Πλήθος τιμών στο τρέχον πεδίο
        dom_size = len(csp.curr_domains[var]) if csp.curr_domains else len(csp.domains[var])
        
        if dom_size == 0:
            return var
            
        # wdeg: Υπολογισμός weighted degree
        wdeg = 0
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment:
                constraint_key = frozenset([var, neighbor])
                weight = csp.constraint_weights.get(constraint_key, 1)
                wdeg += weight
        
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
    """
    conf_set = {v: set() for v in csp.variables}
    csp.curr_domains = {v: list(csp.domains[v]) for v in csp.variables}
    
    result, _ = fc_cbj_recursive(csp, {}, conf_set)
    return result

def fc_cbj_recursive(csp, assignment, conf_set):
    """
    Η αναδρομική καρδιά του FC-CBJ.
    """
    # 1. Goal Test
    if len(assignment) == len(csp.variables):
        return assignment, None

    # 2. Επιλογή μεταβλητής (ΔΙΟΡΘΩΣΗ: Περνάμε τα ορίσματα με τη σωστή σειρά)
    var = dom_wdeg(assignment, csp)
    
    # 3. Δοκιμή τιμών
    for value in list(csp.curr_domains[var]):
        
        if 0 == csp.nconflicts(var, value, assignment):
            
            # --- FORWARD CHECKING STEP ---
            removals = []
            dwo_occurred = False 
            failed_neighbor = None
            
            csp.assign(var, value, assignment)
            
            for neighbor in csp.neighbors[var]:
                if neighbor not in assignment:
                    for val_n in list(csp.curr_domains[neighbor]):
                        if not csp.constraints(var, value, neighbor, val_n):
                            csp.prune(neighbor, val_n, removals)
                            conf_set[neighbor].add(var)
                    
                    if not csp.curr_domains[neighbor]:
                        dwo_occurred = True
                        failed_neighbor = neighbor
                        # ΕΝΗΜΕΡΩΣΗ ΒΑΡΩΝ (dom/wdeg logic)
                        key = frozenset([var, neighbor])
                        csp.constraint_weights[key] += 1
                        break 
            
            if not dwo_occurred:
                result, jump_back_to = fc_cbj_recursive(csp, assignment, conf_set)
                
                if result is not None:
                    return result, None 
                
                if jump_back_to is not None and jump_back_to != var:
                    csp.restore(removals)
                    csp.unassign(var, assignment)
                    return None, jump_back_to
                
            else:
                # DWO: Update Conflict Set
                conf_set[var].update(conf_set[failed_neighbor])

            # Restore
            csp.restore(removals)
            csp.unassign(var, assignment)
    
    # 4. BACKJUMPING LOGIC
    most_recent_conflict = None
    for assigned_var in list(assignment.keys())[::-1]:
        if assigned_var in conf_set[var]:
            most_recent_conflict = assigned_var
            break
            
    return None, most_recent_conflict