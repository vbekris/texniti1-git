import time
from csp import backtracking_search, forward_checking, mac, mrv
from rlfap_csp import RLFA_CSP
from solvers import dom_wdeg, fc_cbj

def run_experiment():
    # Λίστα με τα IDs των instances που έχουμε στα data (βάσει των αρχείων που ανέβασες)
    # Μπορείς να σχολιάσεις κάποια αν θες να τρέξεις πιο γρήγορα τεστ
    instances = [
        '2-f24', '2-f25', 
        '3-f10', '3-f11', 
        '6-w2', 
        '7-w1-f4', '7-w1-f5',
        '8-f10', '8-f11',
        '11',
        '14-f27', '14-f28'
    ]

    print(f"{'Instance':<15} | {'Algorithm':<10} | {'Time (s)':<10} | {'Assigns':<10} | {'Result':<10}")
    print("-" * 65)

    for inst_id in instances:
        try:
            # 1. Φόρτωση του Προβλήματος
            # Φτιάχνουμε ένα φρέσκο αντικείμενο για κάθε αλγόριθμο για να μην κρατάει "σκουπίδια"
            # (π.χ. βάρη από προηγούμενες εκτελέσεις)
            
            # --- ΑΛΓΟΡΙΘΜΟΣ 1: FC (Forward Checking) με dom/wdeg ---
            problem = RLFA_CSP(inst_id, 'data')
            start_time = time.time()
            
            # Χρησιμοποιούμε την έτοιμη backtracking_search του AIMA
            # select_unassigned_variable: Η ευρετική μας (dom/wdeg)
            # inference: Ο μηχανισμός Forward Checking
            result = backtracking_search(
                problem, 
                select_unassigned_variable=dom_wdeg, 
                inference=forward_checking
            )
            elapsed = time.time() - start_time
            n_assigns = problem.nassigns # Μετρητής αναθέσεων του AIMA
            status = "SOLVED" if result else "FAIL"
            
            print(f"{inst_id:<15} | {'FC':<10} | {elapsed:<10.4f} | {n_assigns:<10} | {status:<10}")

            # --- ΑΛΓΟΡΙΘΜΟΣ 2: MAC (Maintaining Arc Consistency) με dom/wdeg ---
            problem = RLFA_CSP(inst_id, 'data') # Ξανά φόρτωση για καθαρή αρχή
            start_time = time.time()
            
            # Ίδια συνάρτηση, αλλά αλλάζουμε το inference σε MAC
            result = backtracking_search(
                problem, 
                select_unassigned_variable=dom_wdeg, 
                inference=mac
            )
            elapsed = time.time() - start_time
            n_assigns = problem.nassigns
            status = "SOLVED" if result else "FAIL"
            
            print(f"{inst_id:<15} | {'MAC':<10} | {elapsed:<10.4f} | {n_assigns:<10} | {status:<10}")

            # --- ΑΛΓΟΡΙΘΜΟΣ 3: FC-CBJ (Custom Solver) με dom/wdeg ---
            problem = RLFA_CSP(inst_id, 'data') # Ξανά φόρτωση
            start_time = time.time()
            
            # Εδώ καλούμε τον δικό μας solver από το solvers.py
            result = fc_cbj(problem)
            
            elapsed = time.time() - start_time
            n_assigns = problem.nassigns
            status = "SOLVED" if result else "FAIL"
            
            print(f"{inst_id:<15} | {'FC-CBJ':<10} | {elapsed:<10.4f} | {n_assigns:<10} | {status:<10}")
            print("-" * 65)

        except FileNotFoundError:
            print(f"Skipping {inst_id}: Files not found in 'data' folder.")
        except Exception as e:
            print(f"Error on {inst_id}: {e}")

if __name__ == "__main__":
    run_experiment()