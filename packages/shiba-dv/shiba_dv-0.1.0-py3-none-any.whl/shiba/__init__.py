# ---------------------------
# Shiba - Linguaggio italiano
# ---------------------------

# Stampa
def stampa(*args, **kwargs):
    print(*args, **kwargs)

# Se / Altrimenti se / Altrimenti
def se(condizione, allora, altrimenti_se=None, altrimenti=None):
    if condizione:
        return allora()
    elif altrimenti_se:
        return altrimenti_se()
    elif altrimenti:
        return altrimenti()

# Mentre
def mentre(condizione, azione):
    while condizione():
        azione()

# Per (range)
def per(start, stop, azione, step=1):
    for i in range(start, stop, step):
        azione(i)

# Definisci funzione
def definisci(funzione):
    return funzione

# Ritorna valore
def ritorna(valore):
    return valore

# ---------------------------
# Messaggio iniziale
# ---------------------------

stampa("Inizio programma!")
