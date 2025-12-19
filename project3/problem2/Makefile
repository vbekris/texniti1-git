# --- ΜΕΤΑΒΛΗΤΕΣ (Variables) ---
# Ορίζουμε ποια python θα τρέξουμε (python ή python3)
PYTHON = python3
# Το όνομα του αρχείου script που έφτιαξες
SCRIPT = pairing_solver.py

# Η λίστα με όλα τα αρχεία δεδομένων που θέλουμε να τρέξουμε
INSTANCES = 17x197.txt \
            19x294.txt \
            19x404.txt \
            19x711.txt \
            22x685.txt \
            23x619.txt \
            24x434.txt \
            25x577.txt \
            27x626.txt \
            31x467.txt

# --- ΚΑΝΟΝΕΣ (Rules) ---

# 1. Ο default κανόνας. Αν γράψεις σκέτο 'make', θα τρέξει αυτό.
all: run_all

# 2. Κανόνας για να τρέξουν ΟΛΑ τα instances σειριακά
# Το '@' μπροστά από την εντολή κρύβει την εκτύπωση της εντολής στο terminal
run_all:
	@echo "========================================"
	@echo "Starting Batch Execution for Problem 2"
	@echo "========================================"
	@for file in $(INSTANCES); do \
		echo "Processing $$file ..."; \
		$(PYTHON) $(SCRIPT) $$file; \
		echo "----------------------------------------"; \
	done
	@echo "All instances processed."

# 3. Κανόνας για να τρέξεις ΜΟΝΟ ΕΝΑ αρχείο συγκεκριμένα
# Χρήση: make run FILE=17x197.txt
run:
	$(PYTHON) $(SCRIPT) $(FILE)

# 4. Κανόνας για να αποθηκεύσεις τα αποτελέσματα σε αρχείο (για την αναφορά)
# Θα δημιουργήσει το αρχείο 'results.log'
save_results:
	@echo "Running all and saving to results.log..."
	@$(MAKE) run_all > results.log
	@echo "Done! Check results.log"

# 5. Κανόνας βοήθειας (τυπώνει οδηγίες)
help:
	@echo "Available commands:"
	@echo "  make           -> Runs all instances and prints to screen"
	@echo "  make run FILE=x.txt -> Runs a specific file (e.g., 17x197.txt)"
	@echo "  make save_results   -> Runs all and saves output to results.log"