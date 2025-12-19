def parse_dataset(filename):
    """
    Διαβάζει το αρχείο δεδομένων και επιστρέφει:
    1. num_flights (int): Το συνολικό πλήθος των πτήσεων (N)
    2. pairings (list): Μια λίστα από dictionaries, όπου κάθε dict έχει:
       {'id': int, 'cost': int, 'flights': set}
    """
    pairings = []
    
    with open(filename, 'r') as f:
        # Διάβασε την πρώτη γραμμή: π.χ. "17 197"
        first_line = f.readline().split()
        if not first_line:
            return 0, []
            
        num_flights = int(first_line[0]) # Το N
        total_pairings = int(first_line[1]) # Το M (δεν το πολυχρειαζόμαστε, αλλά υπάρχει)
        
        # Διάβασε τις υπόλοιπες γραμμές
        for line in f:
            parts = line.strip().split()
            if not parts: 
                continue # Προσπερνάμε κενές γραμμές
            
            # Το format στο αρχείο είναι: [ID] [COST] [FLIGHT_1] [FLIGHT_2] ...
            p_id = int(parts[0])
            cost = int(parts[1])
            
            # Όλα τα υπόλοιπα νούμερα είναι οι πτήσεις. Τις βάζουμε σε SET.
            flights = set(int(x) for x in parts[2:])
            
            # Αποθηκεύουμε τα δεδομένα σε ένα λεξικό (dictionary)
            pairings.append({
                'id': p_id,
                'cost': cost,
                'flights': flights
            })
            
    return num_flights, pairings

# --- TEST CODE (Για να δούμε αν δουλεύει) ---
if __name__ == "__main__":
    # Βεβαιώσου ότι το αρχείο 17x197.txt είναι στον ίδιο φάκελο
    try:
        N, data = parse_dataset("17x197.txt")
        print(f"Επιτυχία! Διαβάστηκαν {N} πτήσεις και {len(data)} συνδυασμοί.")
        print("Δείγμα πρώτου συνδυασμού:", data[0])
    except FileNotFoundError:
        print("Προσοχή: Δεν βρέθηκε το αρχείο .txt!")