from csp import count, first
import sys

# -------------------------------------------------------------------------
# 1. VARIABLE ORDERING HEURISTIC: dom/wdeg (OPTIMIZED)
# -------------------------------------------------------------------------

def dom_wdeg(assignment, csp):
    unassigned = [v for v in csp.variables if v not in assignment]
    
    best_var = None
    best_ratio = float('inf')
    
    for var in unassigned:
        if csp.curr_domains:
            dom_size = len(csp.curr_domains[var])
        else:
            dom_size = len(csp.domains[var])
        
        if dom_size == 0:
            return var
            
        wdeg = 0
        # Πλέον κάνουμε iterate απευθείας και lookup με tuple
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment:
                # O(1) lookup χωρίς δημιουργία frozenset
                wdeg += csp.constraint_weights.get((var, neighbor), 1)
        
        if wdeg == 0: wdeg = 1
        ratio = dom_size / wdeg
        
        if ratio < best_ratio:
            best_ratio = ratio
            best_var = var
            
    return best_var


# -------------------------------------------------------------------------
# 2. SOLVER: FC-CBJ (OPTIMIZED)
# -------------------------------------------------------------------------

def fc_cbj(csp):
    conf_set = {v: set() for v in csp.variables}
    csp.curr_domains = {v: list(csp.domains[v]) for v in csp.variables}
    result, _ = fc_cbj_recursive(csp, {}, conf_set)
    return result

def fc_cbj_recursive(csp, assignment, conf_set):
    if len(assignment) == len(csp.variables):
        return assignment, None

    var = dom_wdeg(assignment, csp)
    
    for value in list(csp.curr_domains[var]):
        if 0 == csp.nconflicts(var, value, assignment):
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
                        
                        # UPDATE WEIGHTS (Bidirectional)
                        csp.constraint_weights[(var, neighbor)] += 1
                        csp.constraint_weights[(neighbor, var)] += 1
                        break 
            
            if not dwo_occurred:
                result, jump_back_to = fc_cbj_recursive(csp, assignment, conf_set)
                if result is not None: return result, None 
                
                if jump_back_to is not None and jump_back_to != var:
                    csp.restore(removals)
                    csp.unassign(var, assignment)
                    return None, jump_back_to
            else:
                conf_set[var].update(conf_set[failed_neighbor])

            csp.restore(removals)
            csp.unassign(var, assignment)
    
    most_recent_conflict = None
    for assigned_var in list(assignment.keys())[::-1]:
        if assigned_var in conf_set[var]:
            most_recent_conflict = assigned_var
            break
            
    return None, most_recent_conflict