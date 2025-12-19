import time
import sys
import signal
from csp import backtracking_search, forward_checking, mac, min_conflicts
from rlfap_csp import RLFA_CSP
from solvers import dom_wdeg, fc_cbj

class TimeoutException(Exception): pass

def timeout_handler(signum, frame):
    raise TimeoutException

# 60 δευτερόλεπτα Timeout
TIMEOUT_SECONDS = 60

def run_algorithm(name, func, *args, **kwargs):
    problem = args[0]
    start_time = time.time()
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)
    
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        signal.alarm(0)
        
        status = "SOLVED" if result else "FAIL"
        n_assigns = problem.nassigns
        
        print(f"{problem.instance_id:<15} | {name:<13} | {elapsed:<10.4f} | {n_assigns:<10} | {status:<10}")
        
    except TimeoutException:
        print(f"{problem.instance_id:<15} | {name:<13} | {'> ' + str(TIMEOUT_SECONDS) + 's':<10} | {'-':<10} | {'TIMEOUT':<10}")
    except Exception as e:
        signal.alarm(0)
        print(f"{problem.instance_id:<15} | {name:<13} | {'ERROR':<10} | {'-':<10} | {str(e):<10}")

def run_experiment(specific_instance=None):
    all_instances = [
        '2-f24', '2-f25', 
        '3-f10', '3-f11', 
        '6-w2', 
        '7-w1-f4', '7-w1-f5',
        '8-f10', '8-f11',
        '11',
        '14-f27', '14-f28'
    ]

    instances = [specific_instance] if specific_instance else all_instances

    print(f"{'Instance':<15} | {'Algorithm':<13} | {'Time (s)':<10} | {'Assigns':<10} | {'Result':<10}")
    print("-" * 65)

    for inst_id in instances:
        try:
            # --- 1. FC ---
            p1 = RLFA_CSP(inst_id, 'data')
            p1.instance_id = inst_id 
            run_algorithm('FC', backtracking_search, p1, select_unassigned_variable=dom_wdeg, inference=forward_checking)

            # --- 2. MAC ---
            p2 = RLFA_CSP(inst_id, 'data')
            p2.instance_id = inst_id
            run_algorithm('MAC', backtracking_search, p2, select_unassigned_variable=dom_wdeg, inference=mac)

            # --- 3. FC-CBJ ---
            p3 = RLFA_CSP(inst_id, 'data')
            p3.instance_id = inst_id
            run_algorithm('FC-CBJ', fc_cbj, p3)

            # --- 4. MIN-CONFLICTS (STANDARD) ---
            p4 = RLFA_CSP(inst_id, 'data')
            p4.instance_id = inst_id
            # Χωρίς restarts, απλή κλήση με όριο βημάτων
            run_algorithm('MIN-CONFLICTS', min_conflicts, p4, max_steps=100000)
            
            print("-" * 65)

        except FileNotFoundError:
            print(f"Skipping {inst_id}: Files not found.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    run_experiment(target)