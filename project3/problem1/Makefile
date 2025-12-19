PYTHON = python3
SCRIPT = main.py

.PHONY: all help run-all clean

# Default target: Τρέχει όταν γράφεις σκέτο 'make'
help:
	@echo "Διαθέσιμες εντολές:"
	@echo "  make run-all        : Τρέχει τα πειράματα για ΟΛΑ τα instances"
	@echo "  make run-<instance> : Τρέχει πειράματα για συγκεκριμένο instance"
	@echo "                        Π.χ. make run-2-f24"
	@echo "                        Π.χ. make run-11"
	@echo "  make clean          : Καθαρίζει τα __pycache__"

# Τρέχει τα πάντα
run-all:
	$(PYTHON) $(SCRIPT)

# Τρέχει για συγκεκριμένο instance
run-%:
	$(PYTHON) $(SCRIPT) $*

# Καθαρισμός προσωρινών αρχείων python
clean:
	rm -rf __pycache__
	rm -rf */__pycache__